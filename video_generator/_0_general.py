from mutagen.mp3 import MP3
import math
import paths
import logs
from . import  _10_pull_openai_text, _20_pexel_pull_videos, _30_build_reel, _40_get_audio_timings, _50_ajoute_overlay, _60_generate_caption, _70_utils

def lanceur(SUJET, langues, NOMBRE_DE_VIDEOS):
    i = 1
    for langue in langues :
        script_text = _10_pull_openai_text.generate_animal_script(SUJET, langue)
        # script_text ='''Écoute-moi bien, les écureuils ne sont pas là pour jouer !  
        # Ils peuvent mémoriser des milliers d’emplacements de glands.
        # Ils enterrent leur nourriture avec une précision chirurgicale, sans GPS, naturellement.
        # Ils couvrent jusqu’à 3 kilomètres par jour pour survivre, bouge-toi un peu !
        # Si tu crois que c’est juste un rongeur mignon, tu sous-estimes l’armée la plus organisée de la forêt.
        # Réveille-toi : ces petites bêtes gèrent leur survie mieux que toi ta vie.'''
        
        audio_path = _10_pull_openai_text.text_to_speech(SUJET, langue, script_text)
        #audio_path = paths.VG_T_VOICEOVER / f"{SUJET}_{langue}.mp3"

        audio = MP3(audio_path)
        duration_seconds = audio.info.length
        duration_ceil = math.ceil(duration_seconds) + 1 #On choisit de mettre une vidéo qui dure 1 seconde de plus que le speech

        # # Partie 2 - Création de la vidéo
        urls = _20_pexel_pull_videos.pick_video_urls_for_reel(SUJET, n=NOMBRE_DE_VIDEOS)
        paths = _20_pexel_pull_videos.download_video(urls)
        reel_path = _20_pexel_pull_videos.create_animal_base_reel(SUJET, paths, duration_ceil ,clip_duration=duration_ceil/NOMBRE_DE_VIDEOS)

        # # Partie 3 - Build de la video avec le son
        final_reel = _30_build_reel.add_voiceover_to_reel(SUJET, langue)

        # Partie 4 - Génère les timings du son 
        timings = _40_get_audio_timings.get_timings_from_audio(audio_path, langue)
        print(timings)
        
        # Partie 5 - Ajout de l'overlay
        reel_with_color = _50_ajoute_overlay.add_subtitles_colorful_animated(
            SUJET,
            langue,
            script_text,
            sentence_timings=timings,
        )
        

        # Génération de la caption et écriture dans le csv
        
        caption = _60_generate_caption.generate_caption(SUJET, langue)
        _70_utils.maj_csv(langue, id=f"{SUJET}_{langue}", video_url=f"{logs.NETLIFY_URL}/{SUJET}_{langue}.mp4",caption=caption)
        print(f"Réél {i}/{len(langues)} terminé ({langue}) ✅")
        i+=1
        
        # Partie 6 - Suppression des dossiers temporaires
        _70_utils.vider_dossier_temporaires()