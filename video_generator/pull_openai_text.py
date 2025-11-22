import os
from openai import OpenAI

import path  # ton module local avec VOICEOVER_PATH

# Assure-toi d'avoir défini OPENAI_API_KEY dans tes variables d'environnement
client = OpenAI()


def generate_animal_script(animal: str, langue: str) -> str:
    """
    Génère un mini script pour ton reel :
    hook + fait intéressant + petite conclusion.
    """
    prompt = f"""
    Tu dois écrire un texte très court pour un Reel Instagram sur l'animal suivant : {animal}.

    IMPORTANT :
    - Le nom de l'animal est fourni en anglais, mais tu dois absolument le traduire en {langue} avant de l'utiliser dans le texte.
    - Utiliser uniquement la traduction correcte en {langue}.

    Objectif :
    - Commencer par un hook très court, percutant, énergique, du type "HOP HOP HOP !" "STOP !" "ATTENDS !" etc.
    - Après le hook, utiliser un rythme rapide basé sur des faits surprenants.
    - Intégrer 1 ou 2 formulations du type "Tu savais que... ?" ou "Est-ce que tu savais que... ?", mais pas à chaque phrase.
    - Varier les autres phrases avec des formulations comme "Incroyable mais vrai :", "Autre fait surprenant :", "Et le plus fou :", etc.
    - Chaque phrase doit présenter un fait réel, clair et vérifiable sur l'animal.

    Structure obligatoire :
    - 1 phrase de hook très court.
    - 4 phrases maximum de faits surprenants avec des formulations variées.
    - Parmi ces phrases, 1 ou 2 doivent contenir une variante de "Tu savais que... ?" ou "Est-ce que tu savais que... ?"
    - Puis les deux phrases finales obligatoires.

    Contraintes :
    - En {langue}
    - 1 seule phrase par ligne
    - Pas d'émoticônes
    - Pas d'humour absurde
    - Pas de comparaisons inutiles
    - Pas de phrases floues ou sans fait
    - Pas de répétition de la même structure à chaque phrase

    Éléments obligatoires à la fin, dans cet ordre, dans la langue {langue}, sans rien après :
    1) Une phrase qui signifie : "J'ai mis d'autres faits sur les <animal_traduit> dans la description"
    2) Une phrase qui signifie : "Tu connais un fait vraiment surprenant sur les <animal_traduit> ? Alors écris-le en commentaire !"
    3) Une phrase courte, douce et simple signifiant : "À bientôt !"
    Style verbal :
    - Clair, direct, rapide.
    - Variations naturelles des phrases.
    - Ton surprenant et entraînant.
    """


    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "system",
                "content": "Tu es un créateur de contenu Instagram, style concis et accrocheur."
            },
            {
                "role": "user",
                "content": prompt
            },
        ],
    )

    # Nouveau format de l’API Responses
    block = response.output[0].content[0]
    # Selon la version du client, le texte est souvent dans block.text.value
    try:
        text = block.text.value
    except AttributeError:
        # fallback au cas où (si c'est déjà une string)
        text = block.text

    print("Script généré ✅")
    return text.strip()


def text_to_speech(SUJET: str, langue: str, text: str):
    """
    Transforme un texte en fichier audio (voix off).
    """
    out_path = path.VOICEOVER_PATH / f"{SUJET}_{langue}.mp3"

    with open(out_path, "wb") as f:
        result = client.audio.speech.create(
            model="gpt-4o-mini-tts",  # modèle TTS
            voice="ballad",            # une des voix dispo
            input=text,
            speed=1.4
        )
        f.write(result.read())

    print(f"Audio généré ✅ -> {out_path}")
    return out_path


def main():
    # Tu peux changer ça pour tester d'autres animaux / langues
    animal = "cat"
    langue = "français"

    print(f"--- Génération du script pour {animal} ({langue}) ---")
    script = generate_animal_script(animal, langue)
    print("\n=== SCRIPT GÉNÉRÉ ===")
    print(script)
    print("=====================\n")

    # Génération de la voix off
    audio_path = text_to_speech(animal, langue, script)
    print(f"Fichier audio créé : {audio_path}")


if __name__ == "__main__":
    main()
