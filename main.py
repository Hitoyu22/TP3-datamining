from flask import Flask, render_template, request, jsonify
from app.api_client import APIClient
import pandas as pd
from app.data_processor import DataProcessor
from app.visualizer import Visualizer
from app.prediction import modeleDePrediction
from shapely.geometry import shape
from flask_cors import CORS

# Initialisation de l'application Flask
app = Flask(__name__)
api_client = APIClient(base_url='https://data.opendatasoft.com')

# Configuration de CORS (permettre les requêtes depuis n'importe quelle origine)
CORS(app)
cors = CORS(app, resource={
    r"/*":{
        "origins":"*"
    }
})

# Route pour la page d'accueil '/'
@app.route('/')
def index():
    """
    Ici on récupère par API la liste des dataset en fonction de la page et du nombre demandé et on les affiche sur le template index.html
    """

    # Récupération des paramètres de pagination
    offset = int(request.args.get('offset', 1))  
    limit = int(request.args.get('limit', 9))  

    # Récupération des datasets avec pagination
    datasets = api_client.liste_dataset_avec_pagination(offset=offset, limit=limit)
    
    total = datasets.get('total', 0) if datasets else 0
    
    offset_suivant = offset + 1 if offset + limit < total else None
    offset_precedent = offset - 1 if offset > -1 else None
    
    print(datasets.get('results', []))
    print('\n')
    for dataset in datasets.get('results', []):
        print(dataset.get('metas', {}))

    # Préparation du rendu HTML en envoyant les données nécessaires à l'html
    return render_template(
        'index.html',
        datasets=datasets.get('results', []),
        total_count=total,
        limit=limit,
        offset=offset,
        next_offset=offset_suivant,
        prev_offset=offset_precedent
    )

# Route pour la page de détails d'un dataset '/mon-dataset' qui correspond au dataset sur lequel j'ai travaillé
@app.route('/mon-dataset')
def dataset_details():
    """
    Ici plusieurs traitements sont effectués:
     - Téléchargement du dataset que j'ai choisi
     - Nettoyage des données de ce dataset (Adaptation des données, vérifications de la cohérence, colonnes renommées...)
     - Création d'un modèle de prédiction (pour permettre une simulation de prédiction de loyer)
     - Création de visualisations (carte choroplèthe, histogramme...) à partir du dataset clean 

     Plusieurs fichiers sont créées ici :
     - Un fichier csv des données nettoyées
     - un fichier de log avec toutes les étapes de nettoyages qui ont eu lieu 
     - Les images des visualisations
     - report.pdf : le rapport complet sur l'analyse des données, les colonnes utilisées, l'entraînement du modèle, son efficacité et le graphique
     - model.pkl : le modèle de prédiction sauvegardé
    """
    global cleaned_gdf

    #Définition de l'identifiant du dataset
    dataset_id = "logement-encadrement-des-loyers@parisdata"
    
    # Téléchargement du dataset
    dataset_path = api_client.telechargement_dataset(dataset_id, 'csv', force_download=False)

    # Récupération des détails du dataset pour les envoyer aux template mon-dataset.html pour afficher quelques informations sur le dataset
    dataset_details = api_client.recuperation_dataset_details(dataset_id)

    if dataset_path:
        try:
            # Lecture du dataset
            df = pd.read_csv(dataset_path, sep=';', encoding='utf-8')
            print("Dataset chargé avec succès.")
        except pd.errors.ParserError as e:
            print(f"Erreur lors de la lecture du CSV: {e}")
            return "Erreur lors du traitement du fichier."

        print("Début du nettoyage des données...")

        # Appel de la classe DataProcessor pour nettoyer les données
        processor = DataProcessor(df)
        processor.nettoyage()

        # Récupération des données nettoyées

        dataset_clean = processor.df

        # Récupération des données utiles pour le formulaire côté front au format JSON (plus facile à utiliser en JS)
        cleaned_json = processor.creation_json() 

        # Création du modèle de prédiction avec la classe modeleDePrediction
        model = modeleDePrediction(dataset_clean)

        # Entrainement du modèle et sauvegarde du modèle dans /static/model.pkl et création d'un rapport dans /static/report.pdf
        model.generation_du_modele(model_file_path="static/model.pkl", pdf_report_path="static/report.pdf")

        if 'geo_shape' in dataset_clean.columns:

            # Création de la colonne 'geometry' pour les données géographiques qui ont été adaptées pour être utilisées dans la carte choroplèthe
            dataset_clean['geometry'] = dataset_clean['geo_shape'].apply(lambda x: shape(eval(x)))

            # Création des visualisations avec la classe Visualizer
            visualizer = Visualizer()

            visualizer.creer_toutes_visualisations(dataset_clean, dataset_clean)

            print(cleaned_json)

            print(dataset_details)

            # Transmission des données nécessaires à l'html pour afficher les visualisations et les informations sur le dataset
            return render_template( 
                'mon-dataset.html',  
                dataset_details=dataset_details,
                json_data=cleaned_json 
            )
        else:
            return "Erreur : La colonne 'geo_shape' n'est pas présente dans le dataset."

    else:
        return "Erreur : Impossible de télécharger le dataset."

# Préparation des headers CORS pour permettre les requêtes depuis n'importe quelle origine
@app.after_request
def add_cors_headers(response):
    """Ajoute le header Access-Control-Allow-Origin."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    return response

# Route pour prédire les loyers '/predict', elle sera uniquement utilisé dans le javascript de la page
@app.route('/predict', methods=['POST'])
def predict():
    """Ici on récupère les informations envoyées par le formulaire de prédiction et on renvoie la prédiction de loyer."""


    # Chargement du modèle de prédiction
    model = modeleDePrediction(dataset=None) 
    model.load_model(file_path="static/model.pkl")
    

    try:
        data = request.json
        if not data:
            return jsonify({"error": "Aucune donnée envoyée"}), 400
        # Création d'un DataFrame à partir des données envoyées
        X_input = pd.DataFrame([data])

        # Prédiction du loyer
        prediction = model.prediction(X_input)[0]

        # Renvoi de la prédiction au format JSON
        return jsonify({"prediction": prediction})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

