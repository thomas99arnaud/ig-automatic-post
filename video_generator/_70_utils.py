import os
import shutil
import paths
import csv
from pathlib import Path


def maj_csv(langue, id=None, video_url=None, caption=None):
    """
    - Si seul 'id' est fourni → ajoute une nouvelle ligne avec cet ID.
    - Si 'id' + 'video_url' → met à jour seulement l'URL.
    - Si 'id' + 'caption' → met à jour seulement la caption.
    """
    csv_path = (Path(__file__).resolve().parent / f"../pipeline_csv/reels_{langue}.csv").resolve()
    if id is None:
        raise ValueError("Un 'id' est obligatoire pour ajouter ou modifier une ligne.")

    # Lire le CSV existant
    rows = []
    id_trouve = False

    if os.path.exists(csv_path):
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["id"] == id:
                    id_trouve = True
                    # Mise à jour si valeurs fournies
                    if video_url is not None:
                        row["video_url"] = video_url
                    if caption is not None:
                        row["caption"] = caption
                rows.append(row)

    # Si ID pas trouvé → ajouter une nouvelle ligne avec valeurs vides
    if not id_trouve:
        rows.append({
            "id": id,
            "video_url": video_url or "",
            "caption": caption or ""
        })

    # Écrire dans le CSV
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "video_url", "caption"])
        writer.writeheader()
        writer.writerows(rows)

    if id_trouve:
        print(f"Ligne mise à jour pour ID : {id}")
    else:
        print(f"Nouvelle ligne ajoutée pour ID : {id}")


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
    #dossiers_temporaires = [paths.VG_T_VIDEOS,paths.VG_T_VOICEOVER]
    dossiers_temporaires = [paths.VG_T_VIDEOS]
    for dossier in dossiers_temporaires :
        vider_dossier(dossier)
    print("Dossiers temporaires vidés ✅")