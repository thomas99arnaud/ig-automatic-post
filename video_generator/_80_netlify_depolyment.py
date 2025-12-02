import subprocess
from pathlib import Path
import shutil
import csv
from urllib.parse import quote
import paths
import logs

# Dossier où tes nouvelles vidéos arrivent
INBOX = paths.VG_VIDEOS_EDITED

# Dossier lié à Netlify (celui que tu as déclaré comme base directory = deployment_folder)
DEPLOY_DIR = paths.VG_DEPLOYMENTFOLDER

# Dossier d’archive pour les vidéos déjà envoyées
ARCHIVE = paths.ARCHIVES_VIDEOS

# Chemin complet vers la commande Netlify sur Windows
NETLIFY_CMD = logs.NETLIFY_CMD

# URL de base de ton site Netlify
BASE_URL = logs.NETLIFY_URL

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

    # 3️⃣ Lancer le déploiement Netlify (SANS build)
    print("Déploiement vers Netlify...")

    cmd = [
        NETLIFY_CMD,
        "deploy",
        "--prod",
        "--dir", str(DEPLOY_DIR),
        "--no-build",  # 👈 pas de phase de build
        "--message", "Sync videos from Python script",
    ]

    # On lance la commande dans le dossier du script (lié au projet Netlify)
    result = subprocess.run(
        cmd,
        shell=False,
        cwd=Path(__file__).resolve().parent
    )

    print("Code retour Netlify :", result.returncode)

    if result.returncode != 0:
        print("❌ Erreur pendant le déploiement Netlify.")
        return

    # 5️⃣ Déplacer les vidéos sources vers le dossier d'archive
    for src in mp4_files:
        dest = ARCHIVE / src.name
        print(f"Déplacement de {src.name} vers {dest}")
        shutil.move(str(src), dest)

    print("✅ Terminé : vidéos envoyées, URLs ajoutées à reels.csv et vidéos déplacées dans 'videos déjà sur le serveur'.")


if __name__ == "__main__":
    deploy_videos()
