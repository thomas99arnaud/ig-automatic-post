import os
from moviepy import VideoFileClip, AudioFileClip
from openai import OpenAI

client = OpenAI()

def add_voiceover_to_reel(video_path: str, audio_path: str, out_path: str = "reel_final.mp4"):
    """
    Associe un fichier audio (voix off) à une vidéo existante.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Vidéo introuvable : {video_path}")
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio introuvable : {audio_path}")

    print(f"⚙️ Chargement vidéo : {video_path}")
    video = VideoFileClip(video_path)

    print(f"🎧 Chargement audio : {audio_path}")
    voice = AudioFileClip(audio_path)

    # Si la voix est plus longue que la vidéo → on coupe
    if voice.duration > video.duration:
        voice = voice.subclipped(0, video.duration)

    # Si la voix est plus courte, on laisse un peu de silence à la fin (c’est ok)
    final = video.with_audio(voice)

    print(f"💾 Export vers : {out_path}")
    final.write_videofile(out_path, codec="libx264", audio_codec="aac")

    return out_path

if __name__ == "__main__":
    final_reel = add_voiceover_to_reel("./videos_edited/reel_chat.mp4", "./voiceovers/chat_1.mp3", out_path="reel_chat_final.mp4")
    print("✅ Reel final prêt :", final_reel)