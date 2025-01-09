import geopandas as gpd
import matplotlib.pyplot as plt
import os
import seaborn as sns
from shapely.geometry import shape

class Visualizer:
    def __init__(self):
        pass

    def create_map(self, gdf, column='loyers_reference'):
        """
        Crée une carte de type choroplète avec une colonne spécifiée du GeoDataFrame
        et sauvegarde l'image dans un dossier.
        :param gdf: GeoDataFrame contenant les données géographiques.
        :param column: Nom de la colonne à utiliser pour la visualisation des couleurs.
        :return: Chemin vers l'image sauvegardée.
        """
        print("Création de la carte...")

        if not isinstance(gdf, gpd.GeoDataFrame):
            print("Conversion en GeoDataFrame...")
            gdf['geometry'] = gdf['geo_shape'].apply(lambda x: shape(eval(x)))  
            gdf = gpd.GeoDataFrame(gdf, geometry='geometry')  
        
        gdf = gdf.set_crs("EPSG:4326")  
        gdf = gdf.to_crs(epsg=3857)  

        fig, ax = plt.subplots(1, 1, figsize=(10, 10))

        print(f"Affichage de la carte pour la colonne: {column}")
        gdf.plot(column=column, ax=ax, legend=True, cmap='coolwarm', linewidth=0.8)

        for _, geometry in gdf.iterrows():
            ax.plot(*geometry['geometry'].boundary.xy, color='black', linewidth=0.8)

        ax.set_title(f"Carte de la répartition du prix moyen du mètre carré en location sur Paris")
        ax.set_axis_off()

        image_folder = 'static/images'
        if not os.path.exists(image_folder):
            print(f"Le dossier {image_folder} n'existe pas. Création du dossier.")
            os.makedirs(image_folder)

        map_path = os.path.join(image_folder, 'map.png')
        print(f"Enregistrement de la carte à: {map_path}")
        try:
            plt.savefig(map_path, format='png')
            plt.close() 
            print(f"Carte sauvegardée avec succès à {map_path}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la carte: {e}")

        return map_path

    def create_histogram(self, data, column):
        """
        Crée un histogramme pour la colonne spécifiée du dataset.
        Sauvegarde l'image dans un dossier.
        :param data: DataFrame contenant les données à visualiser.
        :param column: Nom de la colonne à utiliser pour l'histogramme.
        :return: Chemin vers l'image sauvegardée.
        """
        print("Création de l'histogramme...")
        plt.figure(figsize=(10, 6))
        data[column].plot(kind='hist', bins=30, color='skyblue', edgecolor='black')
        plt.title(f"Histogramme des références du prix du mètre carré en location sur Paris")
        plt.xlabel(f"Prix du mètre carré par mois en location sur Paris")
        plt.ylabel("Fréquence")
        plt.grid(True)

        histogram_path = 'static/images/histogram.png'
        print(f"Enregistrement de l'histogramme à: {histogram_path}")
        try:
            plt.savefig(histogram_path, format='png')
            plt.close()
            print(f"Histogramme sauvegardé avec succès à {histogram_path}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de l'histogramme: {e}")

        return histogram_path
    
    def create_pie_chart(self, data, column='secteur_geographique'):
        """
        Crée un diagramme circulaire pour représenter la proportion des secteurs géographiques.
        :param data: DataFrame contenant les données.
        :param column: Nom de la colonne à analyser.
        """
        print("Création du diagramme circulaire...")
        
        sector_counts = data[column].value_counts()

        plt.figure(figsize=(8, 8))
        wedges, texts = plt.pie(sector_counts, 
                                startangle=90, 
                                colors=plt.cm.Paired.colors, 
                                labels=sector_counts.index, 
                                wedgeprops={'edgecolor': 'black'})
        
        for text in texts:
            text.set_visible(True)
        
        plt.title(f"Répartition des locations sur les secteurs de Paris")
        plt.ylabel("") 

        plt.legend(wedges, sector_counts.index, title="Secteurs", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        
        piechart_path = 'static/images/piechart.png'
        print(f"Enregistrement du diagramme circulaire à: {piechart_path}")
        try:
            plt.savefig(piechart_path, format='png', bbox_inches='tight')
            plt.close()
            print(f"Diagramme circulaire sauvegardé avec succès à {piechart_path}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du diagramme circulaire: {e}")

        return piechart_path

    
    def create_density_plot(self, data, column_x='loyers_reference', hue='epoque_construction'):
        """
        Crée un graphique de densité pour analyser la distribution des loyers selon l'époque.
        :param data: DataFrame contenant les données.
        :param column_x: Nom de la colonne pour les valeurs numériques.
        :param hue: Nom de la colonne pour la couleur (catégories).
        """
        label_mapping = {
            1991: "Après 1990",
            1980: "1971-1990",
            1958: "1946-1970",
            1945: "Avant 1946"
        }

        data[hue] = data[hue].map(label_mapping)

        print("Création du graphique de densité...")
        plt.figure(figsize=(10, 6))
        sns.kdeplot(data=data, x=column_x, hue=hue, fill=True, alpha=0.5, palette='muted')
        plt.title(f"Distribution des prix du mètre carré en location en fonction de l'époque de construction")
        plt.xlabel(f"Prix du mètre carré en location")
        plt.ylabel("Densité")
        plt.grid(True)

        densityplot_path = 'static/images/densityplot.png'
        print(f"Enregistrement du graphique de densité à: {densityplot_path}")
        try:
            plt.savefig(densityplot_path, format='png')
            plt.close()
            print(f"Graphique de densité sauvegardé avec succès à {densityplot_path}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du graphique de densité: {e}")

        return densityplot_path

    
    def create_all_visualizations(self, gdf, data):
        """
        Crée toutes les visualisations en une seule méthode et renvoie les chemins des fichiers créés.
        :param gdf: GeoDataFrame contenant les données géographiques.
        :param data: DataFrame contenant les données pour l'histogramme, le diagramme circulaire et le graphique de densité.
        :return: Dictionnaire avec les chemins des fichiers générés.
        """
        results = {}
        results['map'] = self.create_map(gdf)
        results['histogram'] = self.create_histogram(data, column='loyers_reference')
        results['pie_chart'] = self.create_pie_chart(data, column='secteur_geographique')
        results['density_plot'] = self.create_density_plot(data, column_x='loyers_reference', hue='epoque_construction')

        return results


