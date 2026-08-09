"""BadgeIA API — scanner de transparence AI Act et collecte de leads.

Flask + waitress. Aucun secret en dur.
"""

import ipaddress
import os
import re
import socket
import sqlite3
import time
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

import requests
from flask import Flask, jsonify, request
from waitress import serve

from detectors import detect_disclosure, detect_systems, determine_verdict

app = Flask(__name__)

# Configuration --------------------------------------------------------------------
DATABASE_PATH = os.environ.get("DATABASE_PATH", "/data/leads.db")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
ALLOWED_ORIGINS = {"https://badgeia.brozapi.com", "http://localhost"}
MAX_BODY_SIZE = 2 * 1024 * 1024  # 2 Mo
SCAN_TIMEOUT = 10
USER_AGENT = "BadgeIA-Scanner/0.1 (+https://badgeia.brozapi.com)"

# Rate limiting en mémoire --------------------------------------------------------
rate_limits: dict[str, dict[str, Any]] = {}


def _now() -> int:
    return int(time.time())


def _ip_key(ip: str, action: str) -> str:
    return f"{ip}:{action}"


def is_allowed(ip: str, action: str, limit: int, window_seconds: int) -> bool:
    key = _ip_key(ip, action)
    now = _now()
    bucket = rate_limits.setdefault(key, {"start": now, "count": 0})
    if now - bucket["start"] > window_seconds:
        bucket["start"] = now
        bucket["count"] = 0
    if bucket["count"] >= limit:
        return False
    bucket["count"] += 1
    return True


# Base de données ------------------------------------------------------------------
def init_db() -> None:
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                url TEXT,
                score TEXT,
                created_at TEXT NOT NULL
            )
            """
        )


def save_lead(email: str, url: str, score: str) -> None:
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute(
            "INSERT INTO leads (email, url, score, created_at) VALUES (?, ?, ?, ?)",
            (email, url, score, datetime.now(timezone.utc).isoformat()),
        )


# Utilitaires ----------------------------------------------------------------------
def get_client_ip() -> str:
    xff = request.headers.get("X-Forwarded-For")
    if xff:
        # Caddy ajoute l'IP réelle du client en FIN de chaîne ; le début est falsifiable.
        return xff.split(",")[-1].strip()
    if request.headers.get("X-Real-Ip"):
        return request.headers.get("X-Real-Ip").strip()
    return request.remote_addr or "unknown"


def is_private_url(parsed: urlparse) -> bool:
    if parsed.hostname is None:
        return True
    hostname = parsed.hostname.lower()
    if hostname in {"localhost", "127.0.0.1", "0.0.0.0", "::1"}:
        return True
    try:
        ip = ipaddress.ip_address(hostname)
        return ip.is_private or ip.is_loopback or ip.is_reserved
    except ValueError:
        pass
    return False


def validate_url(url: str) -> str | None:
    try:
        parsed = urlparse(url)
    except Exception:
        return "URL invalide."
    if parsed.scheme not in {"http", "https"}:
        return "Seuls les protocoles http et https sont autorisés."
    if is_private_url(parsed):
        return "Les adresses locales ou privées ne sont pas autorisées."
    return None


# --- Réseau : IPv4 uniquement (le DNS Ionos renvoie des IPv6 cassées pour certains domaines) ---
_orig_getaddrinfo = socket.getaddrinfo


def _ipv4_getaddrinfo(host, port, family=0, *args, **kwargs):
    return _orig_getaddrinfo(host, port, socket.AF_INET, *args, **kwargs)


socket.getaddrinfo = _ipv4_getaddrinfo


def _is_public_ip(ip_str: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False
    return not (
        ip.is_private or ip.is_loopback or ip.is_reserved
        or ip.is_link_local or ip.is_multicast or ip.is_unspecified
    )


def assert_public_hostname(hostname: str) -> None:
    """Anti-SSRF : toutes les adresses IPv4 résolues doivent être publiques."""
    infos = _orig_getaddrinfo(hostname, None, socket.AF_INET)
    ips = {info[4][0] for info in infos}
    if not ips:
        raise ValueError("Résolution DNS impossible.")
    if any(not _is_public_ip(ip) for ip in ips):
        raise ValueError("La cible résout vers une adresse non publique.")


def fetch_page(url: str, timeout: int = SCAN_TIMEOUT) -> requests.Response:
    """GET avec IPv4 forcé, vérification anti-SSRF et max 3 redirections.

    Note : la re-résolution au moment de la connexion laisse une fenêtre
    DNS-rebinding (TOCTOU) résiduelle — acceptée pour le MVP : le conteneur
    est isolé sur son propre réseau Docker et ne retourne qu'une
    classification du HTML, jamais le contenu brut.
    """
    parsed = urlparse(url)
    assert_public_hostname(parsed.hostname)
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "fr,en;q=0.5",
    }
    session = requests.Session()
    session.max_redirects = 3
    return session.get(url, headers=headers, timeout=timeout, stream=True)


def send_telegram_alert(email: str, url: str, score: str) -> None:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    text = f"🎯 Nouveau lead BadgeIA : {email} — {url} ({score})"
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": text},
            timeout=15,
        )
    except Exception as exc:  # noqa: BLE001
        app.logger.warning("Échec envoi Telegram : %s", exc)


def make_cors_response(data: dict, status: int = 200):
    origin = request.headers.get("Origin", "")
    resp = jsonify(data)
    resp.status_code = status
    if origin in ALLOWED_ORIGINS:
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Vary"] = "Origin"
    return resp


# Routes ---------------------------------------------------------------------------
@app.route("/scan", methods=["GET"])
def scan():
    client_ip = get_client_ip()
    if not is_allowed(client_ip, "scan", limit=10, window_seconds=3600):
        return make_cors_response({"ok": False, "error": "Quota de scans atteint. Réessayez dans une heure."}, 429)

    url = request.args.get("url", "").strip()
    error = validate_url(url)
    if error:
        return make_cors_response({"ok": False, "error": error}, 400)

    try:
        with fetch_page(url, timeout=SCAN_TIMEOUT) as resp:
            resp.raise_for_status()
            content = b""
            for chunk in resp.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > MAX_BODY_SIZE:
                    break
            html = content.decode("utf-8", errors="ignore")
    except ValueError as exc:
        return make_cors_response({"ok": False, "error": str(exc)}, 400)
    except requests.exceptions.Timeout:
        return make_cors_response({"ok": False, "error": "Le site a mis trop de temps à répondre."}, 504)
    except requests.exceptions.RequestException as exc:
        return make_cors_response({"ok": False, "error": f"Impossible d'accéder au site : {exc}"}, 502)

    systems = detect_systems(html)
    disclosure_found, disclosure_evidence = detect_disclosure(html)
    verdict = determine_verdict(systems, disclosure_found)

    return make_cors_response(
        {
            "ok": True,
            "url": url,
            "systems": systems,
            "disclosure_found": disclosure_found,
            "disclosure_evidence": disclosure_evidence,
            "verdict": verdict,
            "scanned_at": datetime.now(timezone.utc).isoformat(),
        }
    )


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@app.route("/lead", methods=["POST"])
def lead():
    client_ip = get_client_ip()
    if not is_allowed(client_ip, "lead", limit=3, window_seconds=86400):
        return make_cors_response({"ok": False, "error": "Quota de demandes atteint. Réessayez demain."}, 429)

    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    url = (data.get("url") or "").strip()
    score = (data.get("score") or "").strip()

    if not EMAIL_RE.match(email):
        return make_cors_response({"ok": False, "error": "Adresse email invalide."}, 400)

    try:
        save_lead(email, url, score)
    except sqlite3.Error as exc:
        return make_cors_response({"ok": False, "error": "Erreur de stockage. Réessayez plus tard."}, 500)

    send_telegram_alert(email, url, score)
    return make_cors_response({"ok": True})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})


# Point d'entrée --------------------------------------------------------------------
if __name__ == "__main__":
    init_db()
    serve(app, host="0.0.0.0", port=8080)
