import requests
import time
import csv

def load_reels(csv_path):
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows


def drop_first_reel_line(csv_path: str):
    rows = []

    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)

    if len(rows) <= 1:
        return

    new_rows = [rows[0]] + rows[2:]  # on supprime juste la 1ère ligne de data

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(new_rows)


def create_reel_container(video_url, caption, ig_access_token, ig_user_id):
    url = f"https://graph.facebook.com/v21.0/{ig_user_id}/media"
    payload = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": ig_access_token,
    }

    r = requests.post(url, data=payload)
    print("Réponse création container :", r.text)
    r.raise_for_status()
    data = r.json()
    return data["id"]  # creation_id


def wait_until_container_ready(creation_id, ig_access_token, timeout=180, poll_interval=5):
    """
    Interroge régulièrement le container jusqu'à ce qu'il soit prêt
    ou que le timeout soit atteint.
    """
    url = f"https://graph.facebook.com/v21.0/{creation_id}"
    params = {
        "fields": "status,status_code",
        "access_token": ig_access_token,
    }

    start_time = time.time()
    last_status = None

    while True:
        r = requests.get(url, params=params)
        try:
            data = r.json()
        except Exception:
            print("Impossible de parser la réponse du statut container :", r.text)
            break

        status = data.get("status")
        status_code = data.get("status_code")
        if (status, status_code) != last_status:
            print("Statut container :", data)
            last_status = (status, status_code)

        # Selon la doc Meta, "FINISHED" ou "READY" = OK (les libellés varient)
        if status_code in ("FINISHED", "READY") or status in ("FINISHED", "READY"):
            print("✅ Container prêt à être publié.")
            return True

        # S'il y a une erreur explicite
        if status_code in ("ERROR", "FAILED") or status in ("ERROR", "FAILED"):
            print("❌ Erreur de traitement du container, abandon.")
            return False

        if time.time() - start_time > timeout:
            print("⏱ Timeout : le container n'est toujours pas prêt.")
            return False

        time.sleep(poll_interval)


def publish_reel(creation_id, ig_access_token, ig_user_id):
    """
    Étape 2 : on publie le container sur le feed Reels
    """
    url = f"https://graph.facebook.com/v21.0/{ig_user_id}/media_publish"
    payload = {
        "creation_id": creation_id,
        "access_token": ig_access_token,
    }

    r = requests.post(url, data=payload)
    print("Réponse publication :", r.text)
    r.raise_for_status()
    return r.json()


def post_intagram(langue, ig_access_token, ig_user_id):

    csv_path = f"./pipeline_csv/reels_{langue}_instagram.csv"

    reels = load_reels(csv_path)
    if not reels:
        print("Aucun reel à poster.")
        exit(0)

    reel = reels[0]
    video_url = reel["video_url"]
    caption = reel["caption"]

    print(f"Publication du reel : {video_url} | {caption}")

    creation_id = create_reel_container(video_url, caption, ig_access_token, ig_user_id)

    # On attend que le container soit vraiment prêt
    ok = wait_until_container_ready(creation_id, ig_access_token)
    if not ok:
        print("Le container n'est pas prêt, annulation de la publication.")
        return

    result = publish_reel(creation_id, ig_access_token, ig_user_id)
    print("Résultat final :", result)

    drop_first_reel_line(csv_path)
    print("Ligne supprimée du CSV.")
