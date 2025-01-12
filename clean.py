import os
import glob

def supprimer_fichiers_csv(dossier):
    fichiers_csv = glob.glob(os.path.join(dossier, '*.csv'))
    for fichier in fichiers_csv:
        try:
            os.remove(fichier)
            print(f"Fichier supprimé : {fichier}")
        except Exception as e:
            print(f"Erreur lors de la suppression du fichier {fichier}: {e}")

def supprimer_fichiers_png(dossier):
    fichiers_png = glob.glob(os.path.join(dossier, '*.png'))
    for fichier in fichiers_png:
        try:
            os.remove(fichier)
            print(f"Fichier supprimé : {fichier}")
        except Exception as e:
            print(f"Erreur lors de la suppression du fichier {fichier}: {e}")

def supprimer_modele_et_rapport(dossier):
    fichier_modele = os.path.join(dossier, 'model.pkl')
    if os.path.exists(fichier_modele):
        try:
            os.remove(fichier_modele)
            print(f"Fichier modèle supprimé : {fichier_modele}")
        except Exception as e:
            print(f"Erreur lors de la suppression du fichier modèle {fichier_modele}: {e}")
    else:
        print(f"Aucun fichier modèle trouvé à cet emplacement : {fichier_modele}")
    
    fichier_rapport = os.path.join(dossier, 'report.pdf')
    if os.path.exists(fichier_rapport):
        try:
            os.remove(fichier_rapport)
            print(f"Fichier rapport supprimé : {fichier_rapport}")
        except Exception as e:
            print(f"Erreur lors de la suppression du fichier rapport {fichier_rapport}: {e}")
    else:
        print(f"Aucun fichier rapport trouvé à cet emplacement : {fichier_rapport}")

def supprimer_fichiers_log(dossier):

    fichiers_log = glob.glob(os.path.join(dossier, '*.txt'))
    for fichier in fichiers_log:
        try:
            os.remove(fichier)
            print(f"Fichier log supprimé : {fichier}")
        except Exception as e:
            print(f"Erreur lors de la suppression du fichier log {fichier}: {e}")

if __name__ == "__main__":
    dossier_donnees = './data'
    dossier_images = './static/images'
    dossier_statique = './static'
    dossier_logs = './log'

    supprimer_fichiers_csv(dossier_donnees)
    supprimer_fichiers_png(dossier_images)
    supprimer_modele_et_rapport(dossier_statique)
    supprimer_fichiers_log(dossier_logs)
