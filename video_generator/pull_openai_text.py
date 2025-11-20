import os
from openai import OpenAI

import path

# Assure-toi d'avoir défini OPENAI_API_KEY dans tes variables d'environnement
client = OpenAI()

def generate_animal_script(animal: str) -> str:
    """
    Génère un mini script pour ton reel :
    hook + fait intéressant + petite conclusion.
    """
    prompt = f"""
    Écris un texte très court pour un Reel Instagram sur {animal}.

    Objectif :
    - Durée : environ 15 secondes après une lecture accélérée en x1.4
    - Style : extrêmement agressif, dominant, frontal, mais éducatif
    - Le texte doit donner l’impression que je m’énerve contre l’auditeur.
    - Ton : percutant, direct, sans douceur, punchlines courtes.

    Structure obligatoire :
    1) Un hook qui attrape violemment l’attention.
    2) Un ou plusieurs faits intéressants, strictement vrais.
    3) Une mini conclusion qui frappe fort.

    Contraintes :
    - En français
    - 1 seule phrase par ligne
    - Pas d’émoticônes
    - Pas de politesses
    - Pas de “tu sais peut-être” ou formulations faibles
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
    text = response.output[0].content[0].text
    print("Script généré✅")
    return text.strip()

def text_to_speech(SUJET, text: str):
    """
    Transforme un texte en fichier audio (voix off).
    """

    out_path = path.VOICEOVER_PATH / f"{SUJET}.mp3"
    with open(out_path, "wb") as f:
        result = client.audio.speech.create(
            model="gpt-4o-mini-tts",  # modèle TTS
            voice="verse",            # une des voix dispo
            input=text,
            speed=1.4
        )
        f.write(result.read())
    print("Audio généré ✅")
    return out_path

if __name__ == "__main__":
    # 1. Générer un script
    script_text = generate_animal_script("un chat")
    print("Script généré :")
    print(script_text)
    print("-" * 40)

    # 2. Générer la voix off
    audio_path = text_to_speech("un chat", script_text)
    print("Audio généré :", audio_path)
