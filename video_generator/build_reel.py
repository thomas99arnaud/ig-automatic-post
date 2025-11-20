import os
import path
from moviepy import VideoFileClip, AudioFileClip
from openai import OpenAI

client = OpenAI()

def add_voiceover_to_reel(SUJET):
    """
    Associe un fichier audio (voix off) à une vidéo existante.
    """
    video_path = path.TEMPORARY_VIDEOS_PATH / f"{SUJET}.mp4"
    audio_path = path.VOICEOVER_PATH / f"{SUJET}.mp3"

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Vidéo introuvable : {video_path}")
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio introuvable : {audio_path}")

    video = VideoFileClip(video_path)

    voice = AudioFileClip(audio_path)

    # Si la voix est plus courte, on laisse un peu de silence à la fin (c’est ok)
    final = video.with_audio(voice)

    out_path = path.TEMPORARY_VIDEOS_PATH / f"{SUJET}_full.mp4"
    final.write_videofile(out_path, codec="libx264", audio_codec="aac")
    print("Vidéo avec le son ✅")
    return out_path

if __name__ == "__main__":
    final_reel = add_voiceover_to_reel("chat")
    print("✅ Reel final prêt :", final_reel)