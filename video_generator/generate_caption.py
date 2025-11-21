from openai import OpenAI

client = OpenAI()

def generate_caption(sujet, langue):
    """
    Génère une légende pour TikTok / Reels / YouTube Shorts :
    - accroche très visible en première ligne
    - énumération de faits peu connus
    - hashtags optimisés à la fin
    """

    system_msg = (
        "Tu es un expert en copywriting pour TikTok, Instagram Reels et YouTube Shorts. "
        "Tu écris des légendes courtes, percutantes, très visibles et optimisées pour la viralité."
    )

    user_msg = f"""
Langue : {langue}
Sujet : "{sujet}"

### FORMAT EXACT DE LA LÉGENDE :

1) **Première ligne SUPER ACCROCHEUSE**
   - Commence OBLIGATOIREMENT par un emoji très visible (🔥, 😳, 🚨, ⚡, 🧠…).
   - Doit annoncer un nombre de faits (entre 5 et 9, choisi par toi).
   - Doit créer un effet *“je dois absolument ouvrir la description”*.
   - Doit se terminer par une flèche vers le bas très visible (⬇️ ou ↓).
   - Exemple :  
     "😳 7 choses que tu ne savais (vraiment) pas sur les chats ⬇️"
   - **Reformule librement**, mais garde le style choc / intriguant.

2) Ensuite :
   - Écris **4 à 7 faits PEU connus** sur le sujet.
   - Un fait par ligne.
   - Chaque ligne doit commencer par un tiret "-".
   - Style simple, clair, dynamique et conversationnel.

3) AUCUN appel à l'action.

4) À la fin :
   - Mets une ligne vide.
   - Puis une dernière ligne avec **8 à 12 hashtags optimisés** :
     - mélange hashtags génériques (#reels, #foryou…) et hashtags liés au sujet
     - inclure un hashtag basé sur le sujet sans espaces :  
       #{sujet.replace(" ", "")}

Important :
- Écris tout dans la langue : {langue}.
- Ne renvoie que la légende finale, sans texte explicatif.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.95,
        max_tokens=400,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
    )

    caption = response.choices[0].message.content.strip()
    return caption

sujet = "cat"
langue = "francais"

caption = generate_caption(sujet, langue)
print(caption)
