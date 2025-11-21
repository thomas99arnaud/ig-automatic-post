import requests
import time
import csv
from config import ACCESS_TOKEN, IG_USER_ID

def load_reels(csv_path):
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows

import csv

def drop_first_reel_line(csv_path: str):
    rows = []

    # Lire le CSV correctement (gère les multilignes)
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)

    # Si seulement header → rien à supprimer
    if len(rows) <= 1:
        return

    # Supprimer la 1ère entrée après le header
    new_rows = [rows[0]] + rows[1+1:]  # saute la ligne 1

    # Écrire proprement
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(new_rows)


def create_reel_container(video_url, caption):
    url = f"https://graph.facebook.com/v21.0/{IG_USER_ID}/media"
    payload = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": ACCESS_TOKEN,
    }

    r = requests.post(url, data=payload)
    print("Réponse création container :", r.text)
    r.raise_for_status()
    data = r.json()
    return data["id"]  # creation_id

def publish_reel(creation_id):
    """
    Étape 2 : on publie le container sur le feed Reels
    """
    url = f"https://graph.facebook.com/v21.0/{IG_USER_ID}/media_publish"
    payload = {
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN,
    }

    r = requests.post(url, data=payload)
    print("Réponse publication :", r.text)
    r.raise_for_status()
    return r.json()


def post_intagram(langue) :   

    csv_path=f"./pipeline_csv/reels_{langue}.csv"

    reels = load_reels(csv_path)
    if not reels:
        print("Aucun reel à poster.")
        exit(0)

    # On prend le premier reel de la liste
    reel = reels[0]
    video_url = reel["video_url"]
    caption = reel["caption"]

    print(f"Publication du reel : {video_url} | {caption}")

    creation_id = create_reel_container(video_url, caption)

    # On laisse Insta traiter la vidéo
    time.sleep(30)  # ajuste si besoin

    result = publish_reel(creation_id)
    print("Résultat final :", result)

    drop_first_reel_line(csv_path)
    print("Ligne supprimée du CSV.")