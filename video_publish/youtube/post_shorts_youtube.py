import os
import sys
import csv
import requests
from typing import List, Optional

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# ---------------------------------------------------------------------
# CONFIG YOUTUBE
# ---------------------------------------------------------------------

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = "./oauth/client_secret_1.json"
DEFAULT_TOKEN_FILE = "./oauth/youtube_token.json"


# ---------------------------------------------------------------------
# FONCTIONS CSV (même logique que ton script Instagram)
# ---------------------------------------------------------------------

def load_reels(csv_path: str):
    """
    Charge les lignes du CSV au format :
    id,video_url,caption
    """
    if not os.path.exists(csv_path):
        print(f"❌ CSV introuvable : {csv_path}")
        return []

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows


def drop_first_reel_line(csv_path: str):
    """
    Copie 100% ta logique : on supprime la première ligne de data, on garde le header.
    """
    rows = []

    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)

    if len(rows) <= 1:
        # juste le header ou vide
        return

    new_rows = [rows[0]] + rows[2:]

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(new_rows)


# ---------------------------------------------------------------------
# AUTHENTIFICATION YOUTUBE
# ---------------------------------------------------------------------

def get_authenticated_service(token_file: str = DEFAULT_TOKEN_FILE):
    """
    Renvoie un client YouTube authentifié pour UNE chaîne.

    La première fois :
      - ouvre le navigateur
      - tu choisis la chaîne
      - on enregistre token_file

    Ensuite :
      - réutilise le token + refresh automatique
    """
    creds = None

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print("🔄 Refresh du token...")
                creds.refresh(Request())
            except Exception as e:
                print("⚠️ Erreur de refresh du token, relance de l'auth complète :", e)
                creds = None

        if not creds:
            print("🌐 Ouverture du navigateur pour l'authentification Google...")
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

            with open(token_file, "w") as token:
                token.write(creds.to_json())
            print(f"✅ Token sauvegardé dans {token_file}")

    youtube = build("youtube", "v3", credentials=creds)
    return youtube


# ---------------------------------------------------------------------
# UPLOAD YOUTUBE
# ---------------------------------------------------------------------

def upload_video_to_youtube(
    token_file: str,
    file_path: str,
    title: str,
    description: str,
    tags: Optional[List[str]] = None,
    category_id: str = "22",
    privacy_status: str = "public",
):
    """
    Upload une vidéo locale sur YouTube.
    """
    if tags is None:
        tags = []

    if not os.path.exists(file_path):
        print(f"❌ Fichier vidéo introuvable : {file_path}")
        sys.exit(1)

    youtube = get_authenticated_service(token_file)

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy_status,
        },
    }

    media = MediaFileUpload(
        file_path,
        chunksize=-1,
        resumable=True,
    )

    print(f"🚀 Upload de la vidéo : {file_path}")
    print(f"   → Titre : {title}")
    print(f"   → Visibilité : {privacy_status}")
    print(f"   → Token : {token_file}")

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            progress = int(status.progress() * 100)
            print(f"   → Progression : {progress}%")

    print("✅ Upload terminé.")
    video_id = response.get("id")
    print(f"   → ID vidéo : {video_id}")
    print(f"   → URL : https://www.youtube.com/watch?v={video_id}")

    return response


# ---------------------------------------------------------------------
# DOWNLOADER LA VIDEO A PARTIR DE video_url DU CSV
# ---------------------------------------------------------------------

def download_video_to_temp(video_url: str, reel_id: str) -> str:
    """
    Télécharge la vidéo à partir de video_url (mp4 sur ton Netlify/CDN)
    et la sauvegarde dans ./tmp/{reel_id}.mp4

    Renvoie le chemin du fichier local.
    """
    os.makedirs("./tmp", exist_ok=True)
    local_path = os.path.join("tmp", f"{reel_id}.mp4")

    print(f"⬇️  Téléchargement de la vidéo depuis {video_url}")
    r = requests.get(video_url, stream=True)
    r.raise_for_status()

    with open(local_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    print(f"✅ Vidéo téléchargée : {local_path}")
    return local_path


# ---------------------------------------------------------------------
# FONCTION PRINCIPALE (équivalent de post_intagram)
# ---------------------------------------------------------------------

def post_youtube_from_csv(langue: str, token_file: str = DEFAULT_TOKEN_FILE):
    """
    Lit le CSV ./pipeline_csv/reels_{langue}.csv
    (format id,video_url,caption)

    1. Prend la 1ère ligne
    2. Télécharge video_url en local
    3. Uploade sur YouTube (title + description à partir du caption)
    4. Supprime la 1ère ligne du CSV
    """

    csv_path = f"./pipeline_csv/{langue}.csv"

    reels = load_reels(csv_path)
    if not reels:
        print("Aucun reel / vidéo à poster.")
        return

    reel = reels[0]

    reel_id = reel["id"]
    video_url = reel["video_url"]
    caption = reel["caption"]

    # Titre = première ligne du caption (avant le premier retour à la ligne)
    title = caption.splitlines()[0].strip() if caption else reel_id
    description = caption

    # Simple : pas de tags séparés, mais tu peux en dériver plus tard
    tags = []

    print(f"Publication YouTube depuis CSV : {reel_id} | {video_url}")
    print(f"Titre détecté : {title}")

    # 1) Télécharger la vidéo à partir de video_url
    local_video_path = download_video_to_temp(video_url, reel_id)

    try:
        # 2) Uploader sur YouTube
        result = upload_video_to_youtube(
            token_file=token_file,
            file_path=local_video_path,
            title=title,
            description=description,
            tags=tags,
            privacy_status="public",
        )
        print("Résultat final upload YouTube :", result)

        # 3) On supprime la première ligne du CSV
        drop_first_reel_line(csv_path)
        print("✅ Ligne supprimée du CSV.")

    finally:
        # 4) Nettoyage du fichier temporaire
        if os.path.exists(local_video_path):
            os.remove(local_video_path)
            print(f"🧹 Fichier temporaire supprimé : {local_video_path}")


# ---------------------------------------------------------------------
# EXECUTION DIRECTE
# ---------------------------------------------------------------------

if __name__ == "__main__":
    # Exemple : pour ton CSV portugais, si tu l'appelles reels_pt.csv
    post_youtube_from_csv(langue="reels_portugais", token_file=DEFAULT_TOKEN_FILE)
