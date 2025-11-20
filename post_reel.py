import requests
import time
from config import ACCESS_TOKEN, IG_USER_ID, VIDEO_URL, CAPTION

def create_reel_container():
    """
    Étape 1 : on crée un 'container' de Reel (upload + préparation)
    """
    url = f"https://graph.facebook.com/v21.0/{IG_USER_ID}/media"
    payload = {
        "media_type": "REELS",
        "video_url": VIDEO_URL,
        "caption": CAPTION,
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
    # 1. Création du container
    creation_id = create_reel_container()

    # 2. On laisse Insta traiter la vidéo
    time.sleep(30)  # adapte si besoin

    # 3. Publication
    result = publish_reel(creation_id)
    print("Résultat final :", result)
