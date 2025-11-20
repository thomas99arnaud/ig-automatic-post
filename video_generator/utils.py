import os
import shutil
import path
from pathlib import Path

def vider_dossier(dossier):
    dossier = Path(dossier)

    if not dossier.exists():
        print(f"[INFO] Le dossier {dossier} n'existe pas.")
        return
    
    for item in dossier.iterdir():
        try:
            if item.is_file() or item.is_symlink():
                item.unlink()  # supprime un fichier
            elif item.is_dir():
                shutil.rmtree(item)  # supprime un dossier
        except Exception as e:
            print(f"[ERREUR] Impossible de supprimer {item}: {e}")

    print(f"[OK] Dossier vidé : {dossier}")

def vider_dossier_temporaires() :
    #dossiers_temporaires = [path.TEMPORARY_VIDEOS_PATH,path.VOICEOVER_PATH]
    dossiers_temporaires = [path.TEMPORARY_VIDEOS_PATH]
    for dossier in dossiers_temporaires :
        vider_dossier(dossier)
    print("Dossiers temporaires vidés ✅")