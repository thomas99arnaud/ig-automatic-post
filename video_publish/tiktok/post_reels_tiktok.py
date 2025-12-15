import os
import csv
import json
import time
import requests
from typing import Dict, Any, List, Optional

import paths
from . import config_tiktok

# ---------------------------------------------------------------------
# CONFIG TIKTOK
# ---------------------------------------------------------------------

TOKEN_FR = paths.VP_TT_OAUTH / "tiktok_token_fr.json"
TOKEN_EN = paths.VP_TT_OAUTH / "tiktok_token_en.json"
TOKEN_ES = paths.VP_TT_OAUTH / "tiktok_token_es.json"
TOKEN_PT = paths.VP_TT_OAUTH / "tiktok_token_pt.json"

TOKENS_BY_LANG: Dict[str, os.PathLike] = {
    "francais": TOKEN_FR,
    "anglais": TOKEN_EN,
    "espagnol": TOKEN_ES,
    "portugais": TOKEN_PT,
}

TIKTOK_DIRECT_POST_URL = "https://open.tiktokapis.com/v2/post/publish/video/init/"
TIKTOK_OAUTH_TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
TIKTOK_CREATOR_INFO_URL = "https://open.tiktokapis.com/v2/post/publish/creator_info/query/"

CLIENT_KEY = config_tiktok.CLIENT_KEY
CLIENT_SECRET = config_tiktok.CLIENT_SECRET

REFRESH_SKEW_SECONDS = 5 * 60

# ---------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------

def load_csv(csv_path: str):
    if not os.path.exists(csv_path):
        print(f"❌ CSV introuvable : {csv_path}")
        return []
    with open(csv_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def drop_first_line(csv_path: str):
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))

    if len(rows) <= 1:
        return

    new_rows = [rows[0]] + rows[2:]

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(new_rows)

# ---------------------------------------------------------------------
# TOKENS (lecture / écriture / refresh)
# ---------------------------------------------------------------------

def _read_token_file(token_file: os.PathLike) -> Dict[str, Any]:
    token_file = str(token_file)
    if not os.path.exists(token_file):
        raise FileNotFoundError(f"❌ Token introuvable : {token_file}")
    with open(token_file, "r", encoding="utf-8") as f:
        return json.load(f)

def _write_token_file(token_file: os.PathLike, data: Dict[str, Any]) -> None:
    token_file = str(token_file)
    with open(token_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def _ensure_expires_at(token_data: Dict[str, Any]) -> Dict[str, Any]:
    if token_data.get("expires_at"):
        return token_data
    expires_in = token_data.get("expires_in")
    if isinstance(expires_in, (int, float)) and expires_in > 0:
        token_data["expires_at"] = int(time.time()) + int(expires_in)
    return token_data

def _is_access_token_expiring(token_data: Dict[str, Any], skew_seconds: int = REFRESH_SKEW_SECONDS) -> bool:
    expires_at = token_data.get("expires_at")
    if not isinstance(expires_at, (int, float)):
        return True
    return time.time() >= (float(expires_at) - skew_seconds)

def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
    if not CLIENT_KEY or not CLIENT_SECRET:
        raise RuntimeError("❌ CLIENT_KEY / CLIENT_SECRET manquants (config_tiktok).")

    data = {
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }

    resp = requests.post(TIKTOK_OAUTH_TOKEN_URL, data=data, timeout=30)
    print("🔄 Refresh token status:", resp.status_code)
    print("🔄 Refresh raw response:", resp.text)
    resp.raise_for_status()

    refreshed = resp.json()
    refreshed = _ensure_expires_at(refreshed)
    return refreshed

def load_access_token_auto_refresh(token_file: os.PathLike) -> str:
    data = _read_token_file(token_file)
    data = _ensure_expires_at(data)

    access_token = data.get("access_token")
    if not access_token:
        raise ValueError(f"❌ access_token manquant dans {token_file}")

    if _is_access_token_expiring(data):
        refresh_token = data.get("refresh_token")
        if not refresh_token:
            raise ValueError(f"❌ refresh_token manquant dans {token_file} (impossible de refresh)")

        new_data = refresh_access_token(refresh_token)

        if not new_data.get("refresh_token"):
            new_data["refresh_token"] = refresh_token

        _write_token_file(token_file, new_data)
        return new_data["access_token"]

    _write_token_file(token_file, data)
    return access_token

# ---------------------------------------------------------------------
# CREATOR INFO (privacy options)
# ---------------------------------------------------------------------

def tiktok_creator_info(access_token: str) -> Dict[str, Any]:
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.post(TIKTOK_CREATOR_INFO_URL, headers=headers, timeout=30)
    print("👤 creator_info status:", resp.status_code)
    print("👤 creator_info raw:", resp.text)
    resp.raise_for_status()
    return resp.json()

def extract_privacy_options(creator_info_payload: Dict[str, Any]) -> List[str]:
    """
    TikTok renvoie généralement:
    {"data": {"privacy_level_options": ["PUBLIC_TO_EVERYONE","SELF_ONLY", ...]}, "error": {"code":"ok"}}
    Mais on reste tolérant à d'autres formes.
    """
    data = creator_info_payload.get("data") or {}
    opts = data.get("privacy_level_options") or data.get("privacy_levels") or []
    if isinstance(opts, list):
        return [str(x) for x in opts]
    return []

def choose_non_public_privacy_level(options: List[str]) -> str:
    """
    Objectif: créer un post non public pour publication manuelle ultérieure.
    Priorité: SELF_ONLY, sinon FRIENDS / FOLLOWERS / autre non-public si présent.
    """
    preferred = ["SELF_ONLY", "FRIENDS", "FOLLOWERS"]  # selon disponibilité compte
    for p in preferred:
        if p in options:
            return p
    # fallback: si rien n'est retourné, on tente SELF_ONLY (c'est le plus standard)
    return "SELF_ONLY"

# ---------------------------------------------------------------------
# TIKTOK API – DIRECT POST via PULL_FROM_URL
# ---------------------------------------------------------------------

def tiktok_direct_post(access_token: str, video_url: str, caption: str, privacy_level: str):
    title = (caption or "").strip() or "WildFacts"
    title = title[:2000]

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8",
    }

    body = {
        "post_info": {
            "title": title,
            "privacy_level": privacy_level,
            "disable_duet": False,
            "disable_comment": False,
            "disable_stitch": False,
        },
        "source_info": {
            "source": "PULL_FROM_URL",
            "video_url": video_url,
        },
    }

    print(f"🚀 Appel TikTok Direct Post… (privacy_level={privacy_level})")
    resp = requests.post(
        TIKTOK_DIRECT_POST_URL,
        headers=headers,
        data=json.dumps(body),
        timeout=60,
    )

    print("🔍 RAW response:", resp.text)

    try:
        data = resp.json()
    except json.JSONDecodeError:
        raise RuntimeError(f"Réponse non-JSON de TikTok: {resp.text}")

    error = data.get("error", {}) or {}
    code = error.get("code")
    if code and code != "ok":
        msg = error.get("message", "")
        logid = error.get("log_id") or error.get("logid")
        raise RuntimeError(f"TikTok error: {code} — {msg} (log_id={logid})")

    return data

# ---------------------------------------------------------------------
# PIPE PRINCIPALE
# ---------------------------------------------------------------------

def post_tiktok(langue: str):
    if langue not in TOKENS_BY_LANG:
        raise ValueError(f"Langue inconnue '{langue}'. Attendu: {list(TOKENS_BY_LANG.keys())}")

    token_file = TOKENS_BY_LANG[langue]
    csv_path = paths.PIPELINE_CSV / f"reels_{langue}_tiktok.csv"

    reels = load_csv(str(csv_path))
    if not reels:
        print("📭 Aucun reel à poster.")
        return

    reel = reels[0]
    reel_id = reel["id"]
    video_url = reel["video_url"]
    caption = reel.get("caption", "") or ""

    print(f"🎬 Upload TikTok : {reel_id}")
    print(f"→ URL vidéo : {video_url}")

    try:
        access_token = load_access_token_auto_refresh(token_file)

        # 1) Récupère les options de privacy autorisées
        creator = tiktok_creator_info(access_token)
        opts = extract_privacy_options(creator)
        print("🔒 privacy options:", opts)

        privacy_level = choose_non_public_privacy_level(opts)

        # 2) Poste en non-public (préparation avant publication manuelle)
        result = tiktok_direct_post(access_token, video_url, caption, privacy_level=privacy_level)
        print("✅ TikTok OK. Résultat parsé :")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        # Succès → on consomme la ligne CSV
        drop_first_line(str(csv_path))
        print("🧹 Première ligne supprimée du CSV.")

        print("📌 Action manuelle: ouvre TikTok et passe la vidéo en Public quand tu es prêt.")

    except Exception as e:
        msg = str(e)

        if "access_token_invalid" in msg:
            print("⚠️ access_token_invalid → refresh forcé + retry…")
            try:
                data = _read_token_file(token_file)
                refresh_token = data.get("refresh_token")
                if not refresh_token:
                    raise RuntimeError("refresh_token absent, impossible de refresh forcé.")

                new_data = refresh_access_token(refresh_token)
                if not new_data.get("refresh_token"):
                    new_data["refresh_token"] = refresh_token
                _write_token_file(token_file, new_data)

                access_token = new_data["access_token"]

                creator = tiktok_creator_info(access_token)
                opts = extract_privacy_options(creator)
                print("🔒 privacy options:", opts)
                privacy_level = choose_non_public_privacy_level(opts)

                result = tiktok_direct_post(access_token, video_url, caption, privacy_level=privacy_level)
                print("✅ TikTok OK après refresh. Résultat parsé :")
                print(json.dumps(result, indent=2, ensure_ascii=False))

                drop_first_line(str(csv_path))
                print("🧹 Première ligne supprimée du CSV.")
                print("📌 Action manuelle: ouvre TikTok et passe la vidéo en Public quand tu es prêt.")
                return

            except Exception as e2:
                print(f"❌ Erreur lors du post TikTok (après refresh) : {e2}")
                return

        if "unaudited_client_can_only_post_to_private_accounts" in msg:
            print("❌ Ton client TikTok n’est pas audité : TikTok autorise uniquement les posts via API vers des COMPTES PRIVÉS.")
            print("➡️ Si tu veux garder le compte public et publier manuellement, l’API ne suffira pas tant que cette restriction est active.")
            print("➡️ Solution: passer l’audit (pour lever la restriction) OU faire un upload manuel (drafts) sans API.")
            return

        print(f"❌ Erreur lors du post TikTok : {e}")

# ---------------------------------------------------------------------
# EXECUTION DIRECTE
# ---------------------------------------------------------------------

if __name__ == "__main__":
    post_tiktok("francais")
