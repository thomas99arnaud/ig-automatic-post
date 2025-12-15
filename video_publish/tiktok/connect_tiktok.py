import json
import requests
import webbrowser
import http.server
import socketserver
import config_tiktok

CLIENT_KEY = config_tiktok.CLIENT_KEY
CLIENT_SECRET = config_tiktok.CLIENT_SECRET

REDIRECT_URI = config_tiktok.REDIRECT_URI
SCOPES = config_tiktok.SCOPES

# TikTok OAuth URL
AUTH_URL = (
    f"https://www.tiktok.com/v2/auth/authorize/"
    f"?client_key={CLIENT_KEY}"
    f"&scope={SCOPES}"
    f"&response_type=code"
    f"&redirect_uri={REDIRECT_URI}"
)

# Simple local HTTP server to capture callback
class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if "code=" in self.path:
            code = self.path.split("code=")[1].split("&")[0]

            print(f"\n🔑 Code reçu : {code}\n")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"TikTok OAuth code received. You can close this tab.")

            exchange_token(code)
        return


def exchange_token(code):
    token_url = "https://open.tiktokapis.com/v2/oauth/token/"
    data = {
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
    }

    print("🔄 Échange du code contre un token...")

    response = requests.post(token_url, data=data)
    token_data = response.json()
    print("Réponse TikTok :", json.dumps(token_data, indent=2))

    # Save token
    filename = input("\nNom du fichier token (ex: token_fr.json) : ")
    with open(filename, "w") as f:
        json.dump(token_data, f, indent=2)

    print(f"\n✅ Token sauvegardé dans : {filename}\n")


if __name__ == "__main__":
    print("🌐 Ouverture de la fenêtre d'autorisation TikTok...")
    webbrowser.open(AUTH_URL)

    print("📡 Serveur local en attente du callback...")
    with socketserver.TCPServer(("", 8000), Handler) as httpd:
        httpd.serve_forever()
