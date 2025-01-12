import geopandas as gpd
import matplotlib.pyplot as plt
import os
import seaborn as sns
from shapely.geometry import shape

chemin_dossier_images = 'static/images'

class Visualizer:
    def __init__(self):
        pass

    def carte_choroplethe(self, gdf, colonne='loyers_reference'):
        """
        Méthode pour créer une carte choroplèthe à partir d'un GeoDataFrame.
        """
        print("Création de la carte...")

        if not isinstance(gdf, gpd.GeoDataFrame):
            print("Conversion en GeoDataFrame...")
            gdf['geometry'] = gdf['geo_shape'].apply(lambda x: shape(eval(x)))  
            gdf = gpd.GeoDataFrame(gdf, geometry='geometry')  
        
        gdf = gdf.set_crs("EPSG:4326")  
        gdf = gdf.to_crs(epsg=3857)  

        figure, axe = plt.subplots(1, 1, figsize=(10, 10))

        print(f"Affichage de la carte pour la colonne: {colonne}")
        gdf.plot(column=colonne, ax=axe, legend=True, cmap='coolwarm', linewidth=0.8)

        for _, geometrie in gdf.iterrows():
            axe.plot(*geometrie['geometry'].boundary.xy, color='black', linewidth=0.8)

        axe.set_title("Carte de la répartition du prix moyen du mètre carré en location sur Paris")
        axe.set_axis_off()

        if not os.path.exists(chemin_dossier_images):
            print(f"Le dossier {chemin_dossier_images} n'existe pas. Création du dossier.")
            os.makedirs(chemin_dossier_images)

        chemin_carte = os.path.join(chemin_dossier_images, 'carte.png')
        print(f"Enregistrement de la carte à: {chemin_carte}")
        try:
            plt.savefig(chemin_carte, format='png')
            plt.close() 
            print(f"Carte sauvegardée avec succès à {chemin_carte}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la carte: {e}")

    def histogramme(self, donnees, colonne="loyers_reference"):
        """
        Méthode pour créer un histogramme à partir d'un DataFrame.
        """
        print("Création de l'histogramme...")
        plt.figure(figsize=(10, 6))
        donnees[colonne].plot(kind='hist', bins=30, color='skyblue', edgecolor='black')
        plt.title("Histogramme des références du prix du mètre carré en location sur Paris")
        plt.xlabel("Prix du mètre carré par mois en location sur Paris")
        plt.ylabel("Fréquence")
        plt.grid(True)

        chemin_histogramme = os.path.join(chemin_dossier_images, 'histogramme.png')
        print(f"Enregistrement de l'histogramme à: {chemin_histogramme}")
        try:
            plt.savefig(chemin_histogramme, format='png')
            plt.close()
            print(f"Histogramme sauvegardé avec succès à {chemin_histogramme}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de l'histogramme: {e}")
    
    def diagramme_circulaire(self, donnees, colonne='secteur_geographique'):
        """
        Méthode pour créer un diagramme circulaire à partir d'un DataFrame.
        """
        print("Création du diagramme circulaire...")
        
        repartition_secteurs = donnees[colonne].value_counts()

        plt.figure(figsize=(8, 8))
        parts, textes = plt.pie(repartition_secteurs, 
                                startangle=90, 
                                colors=plt.cm.Paired.colors, 
                                labels=repartition_secteurs.index, 
                                wedgeprops={'edgecolor': 'black'})
        
        for texte in textes:
            texte.set_visible(True)
        
        plt.title("Répartition des locations sur les secteurs de Paris")
        plt.ylabel("") 

        chemin_piechart = os.path.join(chemin_dossier_images, 'diagramme_circulaire.png')
        print(f"Enregistrement du diagramme circulaire à: {chemin_piechart}")
        try:
            plt.savefig(chemin_piechart, format='png', bbox_inches='tight')
            plt.close()
            print(f"Diagramme circulaire sauvegardé avec succès à {chemin_piechart}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du diagramme circulaire: {e}")

    def densite(self, donnees, colonne_x='loyers_reference', colonne_y='epoque_construction'):
        """
        Méthode pour créer un graphique de densité à partir d'un DataFrame.
        """
        etiquettes = {
            1991: "Après 1990",
            1980: "1971-1990",
            1958: "1946-1970",
            1945: "Avant 1946"
        }

        donnees[colonne_y] = donnees[colonne_y].map(etiquettes)

        print("Création du graphique de densité...")
        plt.figure(figsize=(10, 6))
        sns.kdeplot(data=donnees, x=colonne_x, hue=colonne_y, fill=True, alpha=0.5, palette='muted')
        plt.title("Distribution des prix du mètre carré en location en fonction de l'époque de construction")
        plt.xlabel("Prix du mètre carré en location")
        plt.ylabel("Densité")
        plt.grid(True)

        chemin_densityplot = os.path.join(chemin_dossier_images, 'graphe_densite.png')
        print(f"Enregistrement du graphique de densité à: {chemin_densityplot}")
        try:
            plt.savefig(chemin_densityplot, format='png')
            plt.close()
            print(f"Graphique de densité sauvegardé avec succès à {chemin_densityplot}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du graphique de densité: {e}")

    def graphique_courbe(self, donnees, colonne_annee="annee", colonne_secteur="secteur_geographique", colonne_loyers="loyers_reference"):
        """
        Méthode pour créer un graphique en courbes à partir d'un DataFrame.
        """
        donnees_groupes = donnees.groupby([colonne_annee, colonne_secteur])[colonne_loyers].mean().unstack()

        print("Création du graphique en courbes...")
        plt.figure(figsize=(12, 8))
        donnees_groupes.plot(kind="line", marker="o", figsize=(12, 8))
        plt.title("Prix des loyers références par secteur géographique et par année", fontsize=16)
        plt.xlabel("Année", fontsize=14)
        plt.ylabel("Loyers références (moyenne)", fontsize=14)
        plt.legend(title="Secteur Géographique", title_fontsize=12)
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.tight_layout()

        chemin_courbe = os.path.join(chemin_dossier_images, 'graphique_courbe.png')
        print(f"Enregistrement du graphique en courbes à: {chemin_courbe}")
        try:
            plt.savefig(chemin_courbe, format='png')
            plt.close()
            print(f"Graphique en courbes sauvegardé avec succès à {chemin_courbe}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du graphique en courbes: {e}")

    def creer_toutes_visualisations(self, gdf, donnees):
        """
        Méthode pour générer toutes les visualisations à partir des données.
        """
        self.carte_choroplethe(gdf)
        self.histogramme(donnees, colonne='loyers_reference')
        self.diagramme_circulaire(donnees, colonne='secteur_geographique')
        self.densite(donnees, colonne_x='loyers_reference', colonne_y='epoque_construction')
        self.graphique_courbe(donnees)
