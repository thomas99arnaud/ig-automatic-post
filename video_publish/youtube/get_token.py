from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = "./oauth/client_secret_1.json"

def generate_token(output_file):
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES
    )
    creds = flow.run_local_server(port=0)

    with open(output_file, "w") as f:
        f.write(creds.to_json())

    print(f"✅ Token créé : {output_file}")

if __name__ == "__main__":
    generate_token("TEMP_TOKEN.json")
