import os
import requests

class APIClient:
    def __init__(self, base_url, download_dir='datasets'):
        self.base_url = base_url
        self.download_dir = download_dir

        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    def download_dataset(self, dataset_id, format='csv', force_download=False):
        """Télécharge un dataset CSV directement à partir de l'API et l'enregistre dans le dossier spécifié.
        Si force_download=True, le fichier sera retéléchargé même s'il existe déjà.
        """
        filename = f'{dataset_id}.{format}'  
        filepath = os.path.join(self.download_dir, filename)
        
        if os.path.exists(filepath) and not force_download:
            print(f"Le fichier {filename} existe déjà. Téléchargement annulé.")
            return filepath  
        elif os.path.exists(filepath) and force_download:
            print(f"Le fichier {filename} existe déjà, suppression et téléchargement du fichier.")
            os.remove(filepath)  
            
        url = f'{self.base_url}/api/explore/v2.1/catalog/datasets/{dataset_id}/exports/{format}'  # API endpoint
        response = requests.get(url)
        
        if response.status_code == 200:
            with open(filepath, 'wb') as file:
                file.write(response.content)
            print(f"Dataset téléchargé et sauvegardé sous : {filepath}")
            return filepath
        else:
            print(f"Erreur lors du téléchargement du dataset (Code {response.status_code})")
            return None
        
    def get_datasets_with_pagination(self, offset=0, limit=10):
        """Récupère une liste de datasets avec pagination.
        
        Args:
            offset (int): Le décalage pour commencer la pagination.
            limit (int): Le nombre maximum de datasets à récupérer.
        
        Returns:
            dict: Une réponse JSON contenant les informations des datasets, ou None en cas d'erreur.
        """
        url = f'{self.base_url}/api/explore/v2.1/catalog/datasets'
        params = {
            'limit': limit,
            'offset': offset,
            'timezone': 'Europe/Paris',
            'include_links': 'false',
            'include_app_metas': 'false'
        }

        response = requests.get(url, params=params, headers={'accept': 'application/json; charset=utf-8'})

        if response.status_code == 200:
            print("Datasets récupérés avec succès.")
            return response.json() 
        else:
            print(f"Erreur lors de la récupération des datasets (Code {response.status_code})")
            return None
        
    def get_dataset_details(self, dataset_id):
        """Récupère les détails d'un dataset spécifique.
        
        Args:
            dataset_id (str): L'identifiant unique du dataset.
        
        Returns:
            dict: Une réponse JSON contenant les détails du dataset, ou None en cas d'erreur.
        """
        url = f'{self.base_url}/api/explore/v2.1/catalog/datasets/{dataset_id}'
        response = requests.get(url, headers={'accept': 'application/json; charset=utf-8'})

        if response.status_code == 200:
            print(f"Détails du dataset {dataset_id} récupérés avec succès.")
            return response.json()

