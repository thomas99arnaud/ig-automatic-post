from mutagen.mp3 import MP3
import math

import ajoute_overlay
import build_reel
import pexel_pull_videos
import pull_openai_text

SUJET = "squirrel"
NOMBRE_DE_VIDEOS = 7

# Partie 1 - Récupération texte et son
script_text = pull_openai_text.generate_animal_script(SUJET)
print("Script généré :")
print(script_text)
print("-" * 40)
audio_path = pull_openai_text.text_to_speech(script_text, out_path="voiceovers/"+SUJET+".mp3")
print("Audio généré :", audio_path)
audio = MP3(audio_path)
duration_seconds = audio.info.length
duration_ceil = math.ceil(duration_seconds) + 1

# Partie 2 - Création de la vidéo
urls = pexel_pull_videos.pick_video_urls_for_reel(SUJET, n=NOMBRE_DE_VIDEOS)
paths = [pexel_pull_videos.download_video(u) for u in urls]
reel_path = pexel_pull_videos.create_animal_base_reel(paths, duration_ceil ,clip_duration=duration_ceil/NOMBRE_DE_VIDEOS, out_path="./videos_edited/"+SUJET+".mp4")
print("Reel généré :", reel_path)


# Partie 3 - Build de la video avec le son

final_reel = build_reel.add_voiceover_to_reel("./videos_edited/"+SUJET+".mp4", "./voiceovers/"+SUJET+".mp3", out_path=SUJET+".mp4")
print("✅ Reel final prêt :", final_reel)

# Partie 4 - Ajout de l'overlay
reel_with_color = ajoute_overlay.add_subtitles_colorful_animated(
    SUJET+".mp4",
    script_text,
    out_path=SUJET+"caption_color.mp4",
)

print("🏁 Reel final coloré + font stylée :", reel_with_color)