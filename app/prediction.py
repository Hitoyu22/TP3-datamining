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

        # Je créé un objet FPDF
        pdf = FPDF()
        pdf.add_page()

        # J'affiche le titre du rapport
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, "Rapport d'analyse et de prédiction", ln=True, align="C")
        pdf.ln(10)

        # Je créé une sous-section pour les informations sur les données
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, "Analyse des données reçues:", ln=True)

        # Je récupère les statistiques descriptives du dataset
        data_description = self.dataset.describe()

        # Je créé un tableau pour afficher les statistiques
        headers = ['Statistiques'] + list(data_description.columns)
        rows = data_description.reset_index().values.tolist()

        # Je calcule la largeur des colonnes
        col_widths = [60] + [40 for _ in range(len(data_description.columns))]
        max_columns_per_line = 4

        # Je dessine le tableau
        def draw_table(start_idx=0):
            """
            Fonction pour dessiner un tableau à partir de `start_idx`.
            Elle gère également l'ajout de pages si nécessaire.
            """
            # J'affiche les en-têtes du tableau
            for i, header in enumerate(headers[start_idx:start_idx + max_columns_per_line]):
                pdf.set_font("Arial", "B", 10)
                pdf.cell(col_widths[i], 10, header, border=1, align="C")
            pdf.ln()

            # J'affiche les lignes du tableau
            for row in rows:
                for i, cell in enumerate(row[start_idx:start_idx + max_columns_per_line]):
                    pdf.set_font("Arial", size=10)
                    pdf.cell(col_widths[i], 10, str(cell), border=1, align="C")
                pdf.ln()

            pdf.ln(5)

        # J'affiche le tableau des statistiques
        num_columns = len(data_description.columns)
        for i in range(0, num_columns, max_columns_per_line):
            if pdf.get_y() + 40 > 280:  # Je check si un saut de page est nécessaire
                pdf.add_page()
            draw_table(i)

        # Je créé une sous-section pour les colonnes utilisées dans le modèle
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, "Colonnes utilisées pour le modèle:", ln=True)
        pdf.multi_cell(0, 10, "Les colonnes utilisées sont :\n"
                            "- 'epoque_construction'\n"
                            "- 'nombre_pieces_principales'\n"
                            "- 'type_location'\n"
                            "- 'numero_quartier'\n"
                            "- 'secteur_geographique'")

        pdf.ln(10)

        # Je créé une sous-section pour l'entraînement du modèle et l'efficacité
        pdf.cell(200, 10, "Entraînement du modèle et efficacité:", ln=True)
        self.entrainement_random_forest()  # Entraînement du modèle
        predictions = self.prediction(self.X_test)  # Génération des prédictions
        mae = mean_absolute_error(self.y_test, predictions)  # Calcul de l'erreur

        # Affichage des résultats dans le PDF
        pdf.multi_cell(0, 10, f"Le modèle a été entraîné avec un RandomForestRegressor.\n"
                            f"L'erreur absolue moyenne calculée pour le modèle est de : {mae:.2f} euros ")

        # Vérifie si un saut de page est nécessaire avant la prochaine section
        if pdf.get_y() + 120 > 280:
            pdf.add_page()

        pdf.ln(10)

        # Section : Graphique des prédictions
        pdf.cell(200, 10, "Graphique des prédictions:", ln=True)
        image_path = self.graphique_prediction()  # Génération du graphique

        # Taille de l'image à insérer
        image_width = 180
        image_height = 100

        # Vérifie si un saut de page est nécessaire pour l'image
        if pdf.get_y() + image_height > 280:
            pdf.add_page()

        # Ajout de l'image dans le PDF
        pdf.image(image_path, x=10, y=pdf.get_y(), w=image_width, h=image_height)

        # Sauvegarde du PDF
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
