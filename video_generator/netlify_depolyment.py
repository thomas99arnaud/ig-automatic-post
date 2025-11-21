import subprocess
from pathlib import Path
import shutil
import path

# 🔁 ADAPTE CES CHEMINS À TA MACHINE
# Dossier où tes nouvelles vidéos arrivent
INBOX = path.VIDEOS_EDITED_PATH

# Dossier lié à Netlify (celui que tu as déclaré comme base directory = deployment_folder)
DEPLOY_DIR = path.DEPLOYMENT_FOLDER

# Dossier d’archive pour les vidéos déjà envoyées
ARCHIVE = path.ARCHIVE_FOLDER


def deploy_videos():
    # 1️⃣ Récupérer la liste des vidéos à envoyer
    mp4_files = list(INBOX.glob("*.mp4"))

    if not mp4_files:
        print("Aucune nouvelle vidéo à envoyer.")
        return

    print(f"{len(mp4_files)} vidéo(s) trouvée(s) dans {INBOX}.")

    # 2️⃣ Copier les vidéos dans le dossier déployé par Netlify
    for src in mp4_files:
        dst = DEPLOY_DIR / src.name
        print(f"Copie de {src.name} vers {dst}")
        shutil.copy2(src, dst)

    # 3️⃣ Lancer le déploiement Netlify
    print("Déploiement vers Netlify...")
    cmd = [
        "netlify",
        "deploy",
        "--prod",
        "--dir", str(DEPLOY_DIR),
        "--message", "Sync videos from Python script",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    print("----- SORTIE NETLIFY -----")
    print(result.stdout)
    print("--------------------------")

    if result.returncode != 0:
        print("❌ Erreur pendant le déploiement Netlify :")
        print(result.stderr)
        return

    # 4️⃣ Déplacer les vidéos sources vers le dossier d'archive
    for src in mp4_files:
        dest = ARCHIVE / src.name
        print(f"Déplacement de {src.name} vers {dest}")
        shutil.move(str(src), dest)

    print("✅ Terminé : vidéos envoyées et déplacées dans 'videos déjà sur le serveur'.")


if __name__ == "__main__":
    deploy_videos()
