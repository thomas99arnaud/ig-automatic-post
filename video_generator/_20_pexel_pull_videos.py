import requests
import random
import sys
import paths
import logs
import os
from typing import List, Dict
from moviepy import VideoFileClip, concatenate_videoclips

# Ajouter le dossier parent au path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def get_animal_videos(animal: str, max_results: int = 10) -> List[Dict]:
    """
    Retourne une liste de vidéos Pexels pour un animal donné.
    Chaque élément contient l'ID, l'URL de la vidéo, et la meilleure URL MP4.
    """
    url = "https://api.pexels.com/videos/search"
    params = {
        "query": animal,
        "per_page": max_results,
        "orientation": "portrait",
    }
    headers = {
        "Authorization": logs.PEXEL_API_KEY
    }

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    data = response.json()

    videos = data.get("videos", [])
    results = []

    for v in videos:
        files = v.get("video_files", [])
        if not files:
            continue
        best_file = max(files, key=lambda f: f.get("width", 0))
        results.append(
            {
                "id": v.get("id"),
                "page_url": v.get("url"),
                "video_url": best_file.get("link"),
            }
        )

    return results

def pick_video_urls_for_reel(animal: str, n: int = 5):
    all_videos = get_animal_videos(animal, max_results=20)
    if len(all_videos) < n:
        n = len(all_videos)
    chosen = random.sample(all_videos, n)
    return [c["video_url"] for c in chosen]

def download_video(urls: str):
    out_dir = paths.VG_T_VIDEOS
    paths_url=[]
    for url in urls :
        filename = url.split("?")[0].split("/")[-1]  # simple nom de fichier
        filepath = os.path.join(out_dir, filename)

        if os.path.exists(filepath):
            return filepath  # déjà téléchargée

        r = requests.get(url, stream=True)
        r.raise_for_status()
        with open(filepath, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        paths_url.append(filepath)
    return paths_url

def create_animal_base_reel(SUJET, video_paths,  video_duration, clip_duration=2):
    out_path = paths.VG_T_VIDEOS/ f"{SUJET}.mp4" 

    clips = []
    original_videos = []   # pour fermer les vidéos originales
    try:
        for path in video_paths:
            video = VideoFileClip(path)
            original_videos.append(video)

            if video.duration <= clip_duration:
                continue

            start = random.uniform(0, max(0, video.duration - clip_duration))
            sub = video.subclipped(start, start + clip_duration)

            sub = sub.resized(height=1920)
            w, h = sub.size
            target_ratio = 9/16
            current_ratio = w / h

            if current_ratio > target_ratio:
                new_width = int(h * target_ratio)
                x_center = w // 2
                x1 = x_center - new_width // 2
                x2 = x_center + new_width // 2
                sub = sub.cropped(x1=x1, x2=x2)

            clips.append(sub)

        if not clips:
            raise ValueError("Aucun clip valide")

        final = concatenate_videoclips(clips, method="compose")
        final = final.with_duration(video_duration)
        final.write_videofile(out_path, codec="libx264", audio_codec="aac")

        final.close()  # 🔴 IMPORTANT
        print("Vidéo générée ✅")
        return out_path

    finally:
        # 🔴 Ferme tous les clips sous-clips
        for c in clips:
            try:
                c.close()
            except:
                pass

        # 🔴 Ferme les vidéos originales
        for v in original_videos:
            try:
                v.close()
            except:
                pass


if __name__ == "__main__":
    urls = pick_video_urls_for_reel("cute cat", n=5)
    paths = [download_video(u) for u in urls]
    reel_path = create_animal_base_reel("cute cat", paths, clip_duration=2,)
    print("Reel généré :", reel_path)