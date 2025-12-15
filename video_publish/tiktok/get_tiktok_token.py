import json
import requests
import urllib.parse
import webbrowser
import http.server
import socketserver
import config_tiktok

CLIENT_KEY = config_tiktok.CLIENT_KEY
CLIENT_SECRET = config_tiktok.CLIENT_SECRET

REDIRECT_URI = config_tiktok.REDIRECT_URI
SCOPES = config_tiktok.SCOPES

TOKEN_OUTPUT_FILE = "tiktok_token.json"  # tu renommeras ensuite (fr, en, etc.)

def extract_code_from_url(redirected_url: str) -> str:
    parsed = urllib.parse.urlparse(redirected_url)
    qs = urllib.parse.parse_qs(parsed.query)
    code = qs.get("code", [None])[0]
    if not code:
        raise ValueError("Impossible de trouver 'code' dans l'URL.")
    return code

def exchange_code_for_token(code: str):
    url = "https://open.tiktokapis.com/v2/oauth/token/"

    data = {
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
    }

    response = requests.post(url, data=data)
    print("Status:", response.status_code)
    print("Raw response:", response.text)

    response.raise_for_status()
    token_data = response.json()

    # Sauvegarder le token complet dans un fichier
    with open(TOKEN_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(token_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Token sauvegardé dans {TOKEN_OUTPUT_FILE}")
    return token_data

if __name__ == "__main__":
    redirected_url = input("Colle ici l'URL de redirection TikTok :\n> ").strip()
    code = extract_code_from_url(redirected_url)
    print("Code trouvé :", code)

    token_data = exchange_code_for_token(code)
    print("Token data :", token_data)
