import os
import path
from moviepy import VideoFileClip, AudioFileClip

def add_voiceover_to_reel(SUJET, langue):
    """
    Associe un fichier audio (voix off) à une vidéo existante.
    Crée un fichier {SUJET}_{langue}_full.mp4 dans TEMPORARY_VIDEOS_PATH.
    """
    video_path = path.TEMPORARY_VIDEOS_PATH / f"{SUJET}.mp4"
    audio_path = path.VOICEOVER_PATH / f"{SUJET}_{langue}.mp3"

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Vidéo introuvable : {video_path}")
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio introuvable : {audio_path}")

    out_path = path.TEMPORARY_VIDEOS_PATH / f"{SUJET}_{langue}_full.mp4"

    # On garde les clips ouverts pendant tout le write_videofile
    with VideoFileClip(str(video_path)) as video, AudioFileClip(str(audio_path)) as voice:
        # Si tu veux, tu peux caler la durée vidéo sur la voix :
        # video = video.with_duration(voice.duration)

        final = video.with_audio(voice)  # <-- ICI le changement important
        final.write_videofile(str(out_path), codec="libx264", audio_codec="aac")
        final.close()

    print("Vidéo avec le son ✅", out_path)
    return out_path
