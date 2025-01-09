import pandas as pd
import geopandas as gpd
from shapely.geometry import shape

class DataProcessor:
    def __init__(self, df):
        """
        Initialise la classe avec un DataFrame.
        :param df: DataFrame à nettoyer
        """
        self.df = df

        print("Colonnes du DataFrame:", self.df.columns)
    
    def rename_columns(self):
        """
        Renomme les colonnes du DataFrame pour les rendre plus explicites et cohérentes.
        """
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
    
    def check_missing_values(self):
        """
        Vérifie si des valeurs manquantes existent dans le DataFrame et ajuste les colonnes si nécessaire.
        Remplit les valeurs manquantes avec la moyenne pour les colonnes numériques.
        """
        missing_values = self.df.isna().sum()
        print(f"Valeurs manquantes par colonne:\n{missing_values}")
        
        self.df['loyers_reference'] = self.df['loyers_reference'].fillna(self.df['loyers_reference'].mean())
        self.df['loyers_majorés'] = self.df['loyers_majorés'].fillna(self.df['loyers_majorés'].mean())
        self.df['loyers_minores'] = self.df['loyers_minores'].fillna(self.df['loyers_minores'].mean())
        self.df['nombre_pieces_principales'] = self.df['nombre_pieces_principales'].fillna(self.df['nombre_pieces_principales'].mean())
    
    def handle_furnishing(self):
        """
        Convertit la colonne 'type_location' en valeurs binaires : 1 pour meublé, 0 pour non meublé.
        Remplace les valeurs vides par None.
        """
        self.df['type_location'] = self.df['type_location'].map({'meublé': 1, 'non meublé': 0, '': None})
    
    def convert_to_numeric(self):
        """
        Convertit les colonnes pertinentes en types numériques.
        """
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

    def transform_geometries(self):
        """
        Transforme la colonne 'geo_shape' en objets géométriques.
        """
        self.df['geometry'] = self.df['geo_shape'].apply(lambda x: shape(eval(x)))  
    
    def prepare_geo_data(self):
        """
        Crée un GeoDataFrame et applique la projection appropriée pour la cartographie.
        """
        gdf = gpd.GeoDataFrame(self.df, geometry='geometry')
        gdf = gdf.set_crs("EPSG:4326")  
        return gdf.to_crs(epsg=3857)  
    
    def get_cleaned_json(self):
        """
        Retourne un DataFrame nettoyé avec les colonnes spécifiques et converti en format JSON.
        Supprime les doublons et garde uniquement 'nom_quartier', 'numero_quartier' et 'secteur_geographique'.
        """
        df_cleaned = self.df[['nom_quartier', 'numero_quartier', 'secteur_geographique']]

        df_cleaned = df_cleaned.drop_duplicates()

        return df_cleaned.to_json(orient='records', lines=False)

    def save_cleaned_data(self):

        path = "datasets/dataset_clean.csv"

        self.df.to_csv(path, index=False, sep=";")

        print(f"Le fichier {path} a été créé avec succès.")
    
    
    def clean_data(self):
        """
        Applique toutes les étapes de nettoyage aux données.
        """
        self.rename_columns()
        self.check_missing_values()
        self.handle_furnishing()
        self.convert_to_numeric()
        self.transform_geometries()
        self.save_cleaned_data()
        return self.prepare_geo_data()
