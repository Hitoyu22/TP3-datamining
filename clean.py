import os
import glob

def delete_csv_files(directory):
    csv_files = glob.glob(os.path.join(directory, '*.csv'))
    for file in csv_files:
        try:
            os.remove(file)
            print(f"Fichier supprimé : {file}")
        except Exception as e:
            print(f"Erreur lors de la suppression du fichier {file}: {e}")

def delete_png_files(directory):
    png_files = glob.glob(os.path.join(directory, '*.png'))
    for file in png_files:
        try:
            os.remove(file)
            print(f"Fichier supprimé : {file}")
        except Exception as e:
            print(f"Erreur lors de la suppression du fichier {file}: {e}")

if __name__ == "__main__":
    datasets_directory = './datasets'
    images_directory = './static/images'

    delete_csv_files(datasets_directory)
    delete_png_files(images_directory)
