import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import joblib
from fpdf import FPDF

class modeleDePrediction:
    def __init__(self, dataset):
        self.dataset = dataset
        self.model = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None

    def preparation_donnees(self):
        """
        Méhotde pour préparer les données en vue de l'entraînement du modèle.
        """
        X = self.dataset[['epoque_construction', 'nombre_pieces_principales', 'type_location', 'numero_quartier', 'secteur_geographique']]
        y = self.dataset['loyers_reference']
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    def entrainement_random_forest(self, n_estimators=100):
        """
        Méhotde pour entraîner un modèle de RandomForestRegressor.
        """
        self.model = RandomForestRegressor(n_estimators=n_estimators, random_state=42)
        self.model.fit(self.X_train, self.y_train)

    def prediction(self, X_input):
        """
        méthode pour prédire les loyers à partir des données d'entrée.
        """
        if self.model is None:
            raise ValueError("Le modèle n'a pas encore été entraîné.")
        
        predictions = self.model.predict(X_input)
        
        valeur_prediction = np.round(predictions, 2)
        
        return valeur_prediction

    def graphique_prediction(self):
        """
        Méthode pour générer un graphique comparant les loyers prédits et réels.
        """
        y_pred = self.prediction(self.X_test)

        plt.figure(figsize=(10, 6))
        sns.scatterplot(x=self.y_test, y=y_pred, color='blue', alpha=0.6, label='Prédictions vs Réelles')

        plt.plot([min(self.y_test), max(self.y_test)], [min(self.y_test), max(self.y_test)], color='red', linestyle='--', label='Prédiction parfaite')

        plt.xlabel('Loyers réels (€ / m²)')
        plt.ylabel('Loyers prédits (€ / m²)')
        plt.title('Prédiction des loyers vs Loyers réels')
        plt.legend()

        chemin_dossier = "static/images"
        if not os.path.exists(chemin_dossier):
            os.makedirs(chemin_dossier)

        image_path = os.path.join(chemin_dossier, 'prediction.png')

        plt.savefig(image_path)
        plt.close()

        print(f"Le graphique a été enregistré dans : {image_path}")
        return image_path

    def sauvegarder_modele(self, file_path="model.pkl"):
        """
        Méthode pour sauvegarder le modèle entraîné dans un fichier.
        """
        if self.model is not None:
            joblib.dump(self.model, file_path)
            print(f"Le modèle a été sauvegardé sous : {file_path}")
        else:
            print("Le modèle n'a pas encore été entraîné.")

    def load_model(self, file_path="model.pkl"):
        """
        Méthode pour charger un modèle entraîné depuis un fichier.
        """
        if os.path.exists(file_path):
            self.model = joblib.load(file_path)
            print(f"Le modèle a été chargé depuis : {file_path}")
        else:
            print("Aucun modèle trouvé à cet emplacement.")

    def rapport_en_pdf(self, pdf_path="static/report.pdf"):
        """
        Méthode pour générer un rapport PDF contenant les informations sur les données, le modèle et les prédictions.
        """
        pdf = FPDF()
        pdf.add_page()

        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, "Rapport d'analyse et de prédiction", ln=True, align="C")
        pdf.ln(10)

        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, "Analyse des données reçues:", ln=True)
        pdf.multi_cell(0, 10, str(self.dataset.describe()))

        pdf.ln(10)
        pdf.cell(200, 10, "Colonnes utilisées pour le modèle:", ln=True)
        pdf.multi_cell(0, 10, "Les colonnes utilisées sont :\n"
                              "- 'epoque_construction'\n"
                              "- 'nombre_pieces_principales'\n"
                              "- 'type_location'\n"
                              "- 'numero_quartier'\n"
                              "- 'secteur_geographique'")

        pdf.ln(10)
        pdf.cell(200, 10, "Entraînement du modèle et efficacité:", ln=True)
        self.entrainement_random_forest()
        predictions = self.prediction(self.X_test)
        mae = mean_absolute_error(self.y_test, predictions)
        pdf.multi_cell(0, 10, f"Le modèle a été entraîné avec un RandomForestRegressor.\n"
                              f"L'erreur absolue moyenne calculé pour le modèle est de : {mae:.2f} euros ")

        pdf.ln(10)
        pdf.cell(200, 10, "Graphique des prédictions:", ln=True)
        image_path = self.graphique_prediction()
        pdf.image(image_path, x=10, y=pdf.get_y(), w=180)

        pdf.output(pdf_path)

        print(f"Le rapport a été généré et sauvegardé dans : {pdf_path}")
        return pdf_path

    def generation_du_modele(self, model_file_path="model.pkl", pdf_report_path="static/report.pdf"):
        """
        Méthode globale pour entraîner le modèle, le sauvegarder et générer un rapport complet.
        """
        print("Préparation des données...")
        self.preparation_donnees()

        print("Entraînement du modèle...")
        self.entrainement_random_forest()

        print("Sauvegarde du modèle...")
        self.sauvegarder_modele(file_path=model_file_path)

        print("Génération du rapport PDF...")
        self.rapport_en_pdf(pdf_path=pdf_report_path)

        print(f"Le modèle et le rapport ont été générés avec succès.\nModèle sauvegardé sous {model_file_path}\nRapport PDF sauvegardé sous {pdf_report_path}")
