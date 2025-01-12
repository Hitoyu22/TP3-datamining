import os
import requests

class APIClient:
    def __init__(self, base_url, download_dir='data'):
        self.base_url = base_url
        self.download_dir = download_dir

        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)


    # Méthodes pour interagir avec l'API OpenDataSoft
    def telechargement_dataset(self, dataset_id, format='csv', force_download=False):
        """ 
            Ici je vais télécharger un dataset depuis l'API OpenDataSoft au format csv et le stocker dans un dossier data
        """
        filename = f'{dataset_id}.{format}'  
        filepath = os.path.join(self.download_dir, filename)


        # On check si le fichier existe déjà et en fonction de la valeur de force_download on supprime ou non le fichier
        if os.path.exists(filepath) and not force_download:
            print(f"Le fichier {filename} existe déjà. Téléchargement annulé.")
            return filepath  
        elif os.path.exists(filepath) and force_download:
            print(f"Le fichier {filename} existe déjà, suppression et téléchargement du fichier.")
            os.remove(filepath)  
            
        # On prépare l'appel API avec la librairie requests
        url = f'{self.base_url}/api/explore/v2.1/catalog/datasets/{dataset_id}/exports/{format}'  # API endpoint
        response = requests.get(url)
        
        # On vérifie si la requête a bien fonctionné et si oui, on écrit le contenu dans un fichier
        if response.status_code == 200:
            with open(filepath, 'wb') as file:
                file.write(response.content)
            print(f"Dataset téléchargé et sauvegardé sous : {filepath}")
            return filepath
        else:
            print(f"Erreur lors du téléchargement du dataset (Code {response.status_code})")
            return None
        

    def liste_dataset_avec_pagination(self, offset=0, limit=10):
        """
        Ici je récupère par API la liste des dataset en fonction de la page et du nombre demandé côté client html
        """
        url = f'{self.base_url}/api/explore/v2.1/catalog/datasets'

        # Préparation des paramètres de la requête par rapport à ce que j'ai testé sur cette page : 
        # https://data.opendatasoft.com/explore/dataset/logement-encadrement-des-loyers%40parisdata/api/?disjunctive.nom_quartier&disjunctive.piece&disjunctive.epoque&disjunctive.meuble_txt&disjunctive.id_zone&disjunctive.annee&sort=-id_quartier&location=12,48.85889,2.34692&basemap=jawg.streets
        params = {
            'limit': limit,
            'offset': offset,
            'timezone': 'Europe/Paris',
            'include_links': 'false',
            'include_app_metas': 'false'
        }

        # Appel API avec la librairie requests
        response = requests.get(url, params=params, headers={'accept': 'application/json; charset=utf-8'})

        if response.status_code == 200:
            print("Datasets récupérés avec succès.")
            return response.json() 
        else:
            print(f"Erreur lors de la récupération des datasets (Code {response.status_code})")
            return None
        

    def recuperation_dataset_details(self, dataset_id):
        """
        Ici je récupère par API les détails d'un dataset en fonction de son ID pour les envoyer au front
        """
        url = f'{self.base_url}/api/explore/v2.1/catalog/datasets/{dataset_id}'
        response = requests.get(url, headers={'accept': 'application/json; charset=utf-8'})

        if response.status_code == 200:
            print(f"Détails du dataset {dataset_id} récupérés avec succès.")
            return response.json()

