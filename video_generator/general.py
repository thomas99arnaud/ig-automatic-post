from mutagen.mp3 import MP3
import math
import path

import ajoute_overlay
import build_reel
import pexel_pull_videos
import pull_openai_text
import utils
import get_audio_timings

def lanceur(SUJET, NOMBRE_DE_VIDEOS):

    # Partie 1 - Récupération texte et son

    #script_text = pull_openai_text.generate_animal_script(SUJET)
    script_text ='''Écoute-moi bien, les écureuils ne sont pas là pour jouer !  
    Ils peuvent mémoriser des milliers d’emplacements de glands.
    Ils enterrent leur nourriture avec une précision chirurgicale, sans GPS, naturellement.
    Ils couvrent jusqu’à 3 kilomètres par jour pour survivre, bouge-toi un peu !
    Si tu crois que c’est juste un rongeur mignon, tu sous-estimes l’armée la plus organisée de la forêt.
    Réveille-toi : ces petites bêtes gèrent leur survie mieux que toi ta vie.'''
    
    #audio_path = pull_openai_text.text_to_speech(SUJET, script_text)
    audio_path = path.VOICEOVER_PATH / f"{SUJET}.mp3"

    audio = MP3(audio_path)
    duration_seconds = audio.info.length
    duration_ceil = math.ceil(duration_seconds) + 1 #On choisit de mettre une vidéo qui dure 1 seconde de plus que le speech

    # Partie 2 - Création de la vidéo
    urls = pexel_pull_videos.pick_video_urls_for_reel(SUJET, n=NOMBRE_DE_VIDEOS)
    paths = pexel_pull_videos.download_video(urls)
    reel_path = pexel_pull_videos.create_animal_base_reel(SUJET, paths, duration_ceil ,clip_duration=duration_ceil/NOMBRE_DE_VIDEOS)

    # Partie 3 - Build de la video avec le son
    final_reel = build_reel.add_voiceover_to_reel(SUJET)

    # Partir 4 - Génère les timings du son 
    timings = get_audio_timings.get_timings_from_audio(audio_path)
    
    # Partie 4 - Ajout de l'overlay
    reel_with_color = ajoute_overlay.add_subtitles_colorful_animated(
        SUJET,
        script_text,
        sentence_timings=timings,
    )

    # Partie 5 - Suppression des dossiers temporaires
    utils.vider_dossier_temporaires()