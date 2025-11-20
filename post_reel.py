import requests
import time
import csv
from config import ACCESS_TOKEN, IG_USER_ID, CSV_PATH

def load_reels(csv_path):
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows

def drop_first_reel_line(csv_path: str) -> None:
    with open(csv_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if len(lines) <= 2:

        new_lines = lines[:1]  # juste la première ligne (header)
    else:

        new_lines = [lines[0]] + lines[2:]

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        f.writelines(new_lines)

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

if __name__ == "__main__":
    reels = load_reels(CSV_PATH)
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

    drop_first_reel_line("reels.csv")
    print("Ligne supprimée du CSV.")