from sklearn.preprocessing import MinMaxScaler, StandardScaler
import geopandas as gpd
import pandas as pd
import os
from datetime import datetime
from shapely.geometry import shape


# Classe pour le traitement des données
class DataProcessor:
    def __init__(self, df):
        """
        Initialisation de la classe DataProcessor.

        """
        self.df = df
        self.report = {} 
        print("Colonnes du DataFrame:", self.df.columns)
    
    def ajouter_au_rapport(self, step_name, details):
        """
        
         Méthode que j'ai ajouté pour ajouter les informations du rapport pour écrire le fichier de log de nettoyage des données.

        """
        self.report[step_name] = details
    
    def renommer_colonnes(self):
        """
            Méthode pour renommer les colonnes du DataFrame.
                """
        old_columns = self.df.columns
        self.df.rename(columns={
            'annee': 'annee',
            'id_zone': 'secteur_geographique', 
            'id_quartier': 'numero_quartier', 
            'nom_quartier': 'nom_quartier',
            'piece': 'nombre_pieces_principales', 
            'epoque': 'epoque_construction',
            'meuble_txt': 'type_location',
            'ref': 'loyers_reference', 
            'max': 'loyers_majorés', 
            'min': 'loyers_minores', 
            'ville': 'ville', 
            'code_grand_quartier': 'numero_insee', 
            'geo_shape': 'geo_shape',
            'geo_point_2d': 'geo_point_2d',
        }, inplace=True)
        
        new_columns = self.df.columns
        self.ajouter_au_rapport('Renommage des colonnes', f"Colonnes renommées: {list(set(new_columns) - set(old_columns))}")
    
    def verifcer_valeurs_manquantes(self):
        """
        Méthode pour vérifier les valeurs manquantes dans le DataFrame et les remplacer par la moyenne.
        """

        missing_values = self.df.isna().sum()
        missing_report = missing_values[missing_values > 0].to_dict()
        
        self.df['loyers_reference'] = self.df['loyers_reference'].fillna(self.df['loyers_reference'].mean())
        self.df['loyers_majorés'] = self.df['loyers_majorés'].fillna(self.df['loyers_majorés'].mean())
        self.df['loyers_minores'] = self.df['loyers_minores'].fillna(self.df['loyers_minores'].mean())
        self.df['nombre_pieces_principales'] = self.df['nombre_pieces_principales'].fillna(self.df['nombre_pieces_principales'].mean())
        
        self.ajouter_au_rapport('Valeurs manquantes', missing_report)
    
    def conversion_type_location(self):
        """
        Méthode pour convertir la colonne 'type_location' en valeurs numériques (0 ou 1).
        """
        self.df['type_location'] = self.df['type_location'].map({'meublé': 1, 'non meublé': 0, '': None})
    
    def conversion_numerique(self):
        """
        Méhode pour convertir les colonnes pertinentes en types numériques.
        """
        conversion_report = {}
        self.df['loyers_reference'] = pd.to_numeric(self.df['loyers_reference'], errors='coerce')
        self.df['loyers_majorés'] = pd.to_numeric(self.df['loyers_majorés'], errors='coerce')
        self.df['loyers_minores'] = pd.to_numeric(self.df['loyers_minores'], errors='coerce')
        self.df['nombre_pieces_principales'] = pd.to_numeric(self.df['nombre_pieces_principales'], errors='coerce')
        self.df['epoque_construction'] = self.df['epoque_construction'].map({
            'Apres 1990': 1991,
            'Avant 1946': 1945,
            '1971-1990': 1980,
            '1946-1970': 1958
        })
        conversion_report['epoque_construction'] = self.df['epoque_construction'].dtype
        
        self.ajouter_au_rapport('Types de données après conversion', conversion_report)
    
    def conversion_geometrie(self):
        """
        Méthode pour transformer la colonne 'geo_shape' en objets géométriques avec la librairie shapely.
        """
        self.df['geometry'] = self.df['geo_shape'].apply(lambda x: shape(eval(x)))
        self.ajouter_au_rapport('Transformation des géométries', 'Géométries transformées avec succès.')
    
    def preparation_geoDataframe(self):
        """
        Méthode pour créer un GeoDataFrame et applique la projection appropriée pour la cartographie.
        """
        gdf = gpd.GeoDataFrame(self.df, geometry='geometry')
        gdf = gdf.set_crs("EPSG:4326")
        self.ajouter_au_rapport('Préparation des données géographiques', 'Projection appliquée à EPSG:4326.')
        return gdf.to_crs(epsg=3857)  
    
    def creation_json(self):
        """
        Méthode pour créer un fichier JSON à partir des données nettoyées pour les utiliser dans le front-end.
        """
        df_cleaned = self.df[['nom_quartier', 'numero_quartier', 'secteur_geographique']]
        df_cleaned = df_cleaned.drop_duplicates()
        return df_cleaned.to_json(orient='records', lines=False)

    def sauvegarde_nettoyage(self):
        """
        Méthode pour sauvegarder les données nettoyées dans un fichier CSV.
        """
        path = "data/dataset_clean.csv"
        self.df.to_csv(path, index=False, sep=";")
        print(f"Le fichier {path} a été créé avec succès.")
    
    def generation_rapport(self):
        """
        Méthode pour générer un rapport complet sur le nettoyage des données.
        """
        log_directory = "log"
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        
        # Création du nom du fichier de rapport avec la date et l'heure actuelle
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_file_path = os.path.join(log_directory, f"rapport_traitement_{current_time}.txt")
        
        report_str = "Compte Rendu du Traitement des Données:\n"
        
        for step, details in self.report.items():
            report_str += f"\n{step}:\n{details}\n"
        
        with open(report_file_path, "w") as report_file:
            report_file.write(report_str)
        
        print(f"Le rapport a été enregistré dans {report_file_path}")
        return report_file_path
    
    def normalisation(self):
        """
        Méthode pour normaliser les colonnes 'loyers_majorés' et 'loyers_minores' (pour montrer que je sais utiliser la normalisation).
        """
        scaler = MinMaxScaler()
        columns_to_normalize = ['loyers_majorés', 'loyers_minores']
        self.df[columns_to_normalize] = scaler.fit_transform(self.df[columns_to_normalize])
        
        self.ajouter_au_rapport('Normalisation', f"Les colonnes {columns_to_normalize} ont été normalisées entre 0 et 1.")
    
    def standardisation(self):
        """
        Méthode pour standardiser les colonnes 'loyers_majorés' et 'loyers_minores' (pour montrer que je sais utiliser la standardisation).
        """
        scaler = StandardScaler()
        columns_to_standardize = ['loyers_majorés', 'loyers_minores']
        self.df[columns_to_standardize] = scaler.fit_transform(self.df[columns_to_standardize])
        
        self.ajouter_au_rapport('Standardisation', f"Les colonnes {columns_to_standardize} ont été standardisées.")
    
    def nettoyage(self):
        """
        Methode pour nettoyer les données en utilisant les méthodes de nettoyage définies.
        """
        self.renommer_colonnes()
        self.verifcer_valeurs_manquantes()
        self.conversion_type_location()
        self.conversion_numerique()
        self.conversion_geometrie()
        self.normalisation()
        self.standardisation() 
        self.sauvegarde_nettoyage()
        self.generation_rapport()
        return self.preparation_geoDataframe()
