from flask import Flask, render_template, request, jsonify
from app.api_client import APIClient
import pandas as pd
from app.data_processor import DataProcessor
from app.visualizer import Visualizer
from app.prediction import RealEstateModel
from shapely.geometry import shape
from flask_cors import CORS

app = Flask(__name__)
api_client = APIClient(base_url='https://data.opendatasoft.com')

CORS(app)
cors = CORS(app, resource={
    r"/*":{
        "origins":"*"
    }
})


@app.route('/')
def index():
    """
    Affiche la page d'accueil avec la liste paginée des datasets.
    """
    offset = int(request.args.get('offset', 1))  
    limit = int(request.args.get('limit', 9))  
    
    datasets = api_client.get_datasets_with_pagination(offset=offset, limit=limit)
    
    total_count = datasets.get('total_count', 0) if datasets else 0
    
    next_offset = offset + 1 if offset + limit < total_count else None
    prev_offset = offset - 1 if offset > -1 else None
    
    print(datasets.get('results', []))
    print('\n')
    for dataset in datasets.get('results', []):
        print(dataset.get('metas', {}))

    return render_template(
        'index.html',
        datasets=datasets.get('results', []),
        total_count=total_count,
        limit=limit,
        offset=offset,
        next_offset=next_offset,
        prev_offset=prev_offset
    )

@app.route('/mon-dataset')
def dataset_details():
    """
    Affiche les détails d'un dataset spécifique avec une carte et un histogramme.
    """
    global cleaned_gdf

    dataset_id = "logement-encadrement-des-loyers@parisdata"
    
    dataset_path = api_client.download_dataset(dataset_id, 'csv', force_download=False)

    dataset_details = api_client.get_dataset_details(dataset_id)

    if dataset_path:
        try:
            df = pd.read_csv(dataset_path, sep=';', encoding='utf-8')
            print("Dataset chargé avec succès.")
        except pd.errors.ParserError as e:
            print(f"Erreur lors de la lecture du CSV: {e}")
            return "Erreur lors du traitement du fichier."

        print("Début du nettoyage des données...")
        processor = DataProcessor(df)
        processor.clean_data()

        dataset_clean = processor.df
        cleaned_json = processor.get_cleaned_json() 

        if 'geo_shape' in dataset_clean.columns:
            dataset_clean['geometry'] = dataset_clean['geo_shape'].apply(lambda x: shape(eval(x)))

            visualizer = Visualizer()

            visualizer.create_all_visualizations(dataset_clean, dataset_clean)

            print(cleaned_json)

            print(dataset_details)

            return render_template(
                'mon-dataset.html',  
                dataset_details=dataset_details,
                json_data=cleaned_json 
            )
        else:
            return "Erreur : La colonne 'geo_shape' n'est pas présente dans le dataset."

    else:
        return "Erreur : Impossible de télécharger le dataset."

@app.after_request
def add_cors_headers(response):
    """Ajoute le header Access-Control-Allow-Origin."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    return response


@app.route('/predict', methods=['POST'])
def predict():
    """API pour prédire les loyers."""

    dataset_clean = pd.read_csv('datasets/dataset_clean.csv', sep=';', encoding='utf-8') 
    model = RealEstateModel(dataset_clean)
    model.prepare_data()
    model.train_random_forest()


    try:
        data = request.json
        if not data:
            return jsonify({"error": "Aucune donnée envoyée"}), 400

        X_input = pd.DataFrame([data])

        predicted_rent = model.predict(X_input)[0]

        return jsonify({"predicted_rent": predicted_rent})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

