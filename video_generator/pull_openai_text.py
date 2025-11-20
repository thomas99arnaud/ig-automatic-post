import os
from openai import OpenAI

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
    return text.strip()

def text_to_speech(text: str, out_path: str = "voice.mp3"):
    """
    Transforme un texte en fichier audio (voix off).
    """
    # Créer le dossier de sortie si besoin
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with open(out_path, "wb") as f:
        result = client.audio.speech.create(
            model="gpt-4o-mini-tts",  # modèle TTS
            voice="verse",            # une des voix dispo
            input=text,
            speed=1.4
        )
        f.write(result.read())

    return out_path


if __name__ == "__main__":
    # 1. Générer un script
    script_text = generate_animal_script("un chat")
    print("Script généré :")
    print(script_text)
    print("-" * 40)

    # 2. Générer la voix off
    audio_path = text_to_speech(script_text, out_path="voiceovers/chat_1.mp3")
    print("Audio généré :", audio_path)
