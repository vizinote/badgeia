"""BadgeIA API — scanner de transparence AI Act et collecte de leads.

Flask + waitress. Aucun secret en dur.
"""

import ipaddress
import os
import re
import smtplib
import socket
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any
from urllib.parse import urlparse, urlunparse

import requests
from flask import Flask, jsonify, request
from waitress import serve

from detectors import detect_disclosure, detect_systems, determine_verdict

app = Flask(__name__)

# Configuration --------------------------------------------------------------------
DATABASE_PATH = os.environ.get("DATABASE_PATH", "/data/leads.db")
METRICS_DATABASE_PATH = os.environ.get("METRICS_DATABASE_PATH", "/data/metrics.db")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
ALLOWED_ORIGINS = {
    "https://badgeia.brozapi.com",
    "https://accessicheck.brozapi.com",
    "https://brozapi.com",
    "https://www.brozapi.com",
    "http://localhost",
}

# Configuration email (lues depuis l'environnement au runtime, jamais en dur).
# Peut aussi provenir d'un fichier .env monté dans /data (badgeia-mail.env),
# avec des clés MAIL_* mappées sur les SMTP_* attendues par le code.
def _load_dotenv(path: str) -> None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip()
                val = val.strip().strip("'").strip('"')
                if key and val and key not in os.environ:
                    os.environ[key] = val
    except OSError:
        pass  # fichier absent : on continue avec les variables existantes


def _email_cfg(name: str) -> str:
    """Récupère une variable SMTP_* avec repli sur son équivalent MAIL_*."""
    val = os.environ.get("SMTP_" + name)
    if val:
        return val
    # Correspondance MAIL_* -> SMTP_*
    mapping = {"HOST": "HOST", "PORT": "PORT", "USER": "USER", "PASSWORD": "PASS"}
    mail_key = mapping.get(name, name)
    return os.environ.get("MAIL_" + mail_key, "")


for _env_path in ("/data/badgeia-mail.env", "/opt/data/badgeia-mail.env", "/app/badgeia-mail.env"):
    _load_dotenv(_env_path)

SMTP_HOST = _email_cfg("HOST")
# Sécurité port : un port 993/995 est un port IMAP/POP (lecture), pas SMTP.
# OVH envoie sur 465 (SSL direct) ou 587 (STARTTLS). On force un port cohérent.
_smtp_port_raw = (_email_cfg("PORT") or "587").strip()
if _smtp_port_raw in ("993", "995"):
    _smtp_port_raw = "587"
SMTP_PORT = int(_smtp_port_raw)
SMTP_USER = _email_cfg("USER")
SMTP_PASSWORD = _email_cfg("PASSWORD")
SMTP_FROM = os.environ.get("SMTP_FROM", "") or SMTP_USER  # par défaut, l'adresse du compte OVH
SMTP_REPLY_TO = os.environ.get("SMTP_REPLY_TO", "")
GUIDE_PDF_PATH = os.environ.get(
    "GUIDE_PDF_PATH", os.path.join(os.path.dirname(__file__), "..", "guide-ai-act-pme.pdf")
)
GUIDE_PDF_URL = "https://badgeia.brozapi.com/guide-ai-act-pme.pdf"

# Produits supportés par les métriques anonymes.
PRODUCTS = {"badgeia", "accessicheck"}
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
        # Migration : ajout de la colonne source pour distinguer les leads guide-pdf.
        column_exists = conn.execute(
            "SELECT 1 FROM pragma_table_info('leads') WHERE name = 'source'"
        ).fetchone()
        if not column_exists:
            conn.execute("ALTER TABLE leads ADD COLUMN source TEXT DEFAULT ''")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT NOT NULL,
                verdict TEXT NOT NULL,
                systems_count INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def init_metrics_db() -> None:
    os.makedirs(os.path.dirname(METRICS_DATABASE_PATH), exist_ok=True)
    with sqlite3.connect(METRICS_DATABASE_PATH) as conn:
        v2_exists = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='events_v2'"
        ).fetchone()
        old_exists = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='events'"
        ).fetchone()
        if not v2_exists and old_exists:
            # Migration : la v1 n'avait pas de colonne produit.
            conn.execute("ALTER TABLE events RENAME TO events_legacy")
            conn.execute(
                """
                CREATE TABLE events_v2 (
                    product TEXT NOT NULL DEFAULT 'badgeia',
                    event TEXT NOT NULL,
                    path TEXT NOT NULL,
                    day TEXT NOT NULL,
                    count INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (product, event, path, day)
                )
                """
            )
            conn.execute(
                """
                INSERT INTO events_v2 (product, event, path, day, count)
                SELECT 'badgeia', event, path, day, count FROM events_legacy
                """
            )
        else:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS events_v2 (
                    product TEXT NOT NULL DEFAULT 'badgeia',
                    event TEXT NOT NULL,
                    path TEXT NOT NULL,
                    day TEXT NOT NULL,
                    count INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (product, event, path, day)
                )
                """
            )


def track_event(event: str, path: str, product: str = "badgeia") -> None:
    """Incrémente un compteur agrégé par produit, événement, chemin et jour. Aucune donnée personnelle."""
    product = (product or "badgeia").lower()
    if product not in PRODUCTS or not event or not path:
        return
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        with sqlite3.connect(METRICS_DATABASE_PATH) as conn:
            conn.execute(
                """
                INSERT INTO events_v2 (product, event, path, day, count)
                VALUES (?, ?, ?, ?, 1)
                ON CONFLICT(product, event, path, day) DO UPDATE SET count = count + 1
                """,
                (product, event, path, day),
            )
    except sqlite3.Error:
        pass  # les stats ne doivent jamais casser l'application


def save_scan(domain: str, verdict: str, systems_count: int) -> None:
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute(
            "INSERT INTO scans (domain, verdict, systems_count, created_at) VALUES (?, ?, ?, ?)",
            (domain, verdict, systems_count, datetime.now(timezone.utc).isoformat()),
        )


def save_message(name: str, email: str, message: str) -> None:
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute(
            "INSERT INTO messages (name, email, message, created_at) VALUES (?, ?, ?, ?)",
            (name, email, message, datetime.now(timezone.utc).isoformat()),
        )


def save_lead(email: str, url: str, score: str, source: str = "") -> None:
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute(
            "INSERT INTO leads (email, url, score, source, created_at) VALUES (?, ?, ?, ?, ?)",
            (email, url, score, source, datetime.now(timezone.utc).isoformat()),
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


def normalize_url(url: str) -> str:
    """Accepte 'mon-site.fr' ou 'www.mon-site.fr/path' : ajoute https:// si absent."""
    url = url.strip()
    if url and "://" not in url:
        url = "https://" + url
    try:
        p = urlparse(url)
        if p.scheme and p.netloc:
            url = urlunparse((p.scheme.lower(), p.netloc.lower(), p.path or "/", p.params, p.query, ""))
    except Exception:
        pass
    return url


def validate_url(url: str) -> str | None:
    try:
        parsed = urlparse(url)
    except Exception:
        return "URL invalide."
    if parsed.scheme not in {"http", "https"}:
        return "Seuls les protocoles http et https sont autorisés."
    if not parsed.hostname or "." not in parsed.hostname:
        return "URL invalide : indiquez un nom de domaine (ex. mon-site.fr)."
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


def send_guide_email(email: str) -> None:
    """Envoie le guide PDF au lead. Ne fait jamais échouer la requête API."""
    if not all([SMTP_HOST, SMTP_USER, SMTP_PASSWORD, SMTP_FROM]):
        app.logger.warning("SMTP non configuré : email de livraison non envoyé à %s", email)
        return

    subject = "Votre guide AI Act pour dirigeants de PME"
    text_body = (
        f"Bonjour,\n\n"
        f"Merci pour votre intérêt. Votre guide « AI Act : le guide du dirigeant de PME » "
        f"est disponible ici : {GUIDE_PDF_URL}\n\n"
        f"Vous pouvez le télécharger gratuitement et le partager au sein de votre équipe.\n\n"
        f"Ce guide est fourni à titre indicatif. Il ne constitue pas un conseil juridique "
        f"ni une garantie de conformité.\n\n"
        f"Bonne lecture,\n"
        f"L'équipe Brozapi — BadgeIA\n"
        f"https://badgeia.brozapi.com\n"
    )
    html_body = (
        f"<html><body style='font-family: system-ui, sans-serif; color:#1a1a1a;'>"
        f"<p>Bonjour,</p>"
        f"<p>Merci pour votre intérêt. Votre guide <strong>« AI Act : le guide du dirigeant de PME »</strong> "
        f"est disponible ici :</p>"
        f"<p><a href='{GUIDE_PDF_URL}' style='color:#003399;'>Télécharger le guide PDF</a></p>"
        f"<p>Vous pouvez le télécharger gratuitement et le partager au sein de votre équipe.</p>"
        f"<p><small>Ce guide est fourni à titre indicatif. Il ne constitue pas un conseil juridique "
        f"ni une garantie de conformité.</small></p>"
        f"<p>Bonne lecture,<br>"
        f"L'équipe Brozapi — BadgeIA<br>"
        f"<a href='https://badgeia.brozapi.com'>badgeia.brozapi.com</a></p>"
        f"</body></html>"
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM
    msg["To"] = email
    if SMTP_REPLY_TO:
        msg["Reply-To"] = SMTP_REPLY_TO

    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    # Pièce jointe si le fichier PDF est disponible localement.
    pdf_path = os.path.abspath(GUIDE_PDF_PATH)
    try:
        if os.path.isfile(pdf_path):
            with open(pdf_path, "rb") as f:
                part = MIMEBase("application", "pdf")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                'attachment; filename="guide-ai-act-pme.pdf"',
            )
            msg.attach(part)
            app.logger.info("Pièce jointe PDF ajoutée pour %s", email)
        else:
            app.logger.info("PDF local non trouvé (%s) : envoi par lien pour %s", pdf_path, email)
    except Exception as exc:  # noqa: BLE001
        app.logger.warning("Impossible de joindre le PDF : %s", exc)

    try:
        if SMTP_PORT == 465:
            # SSL direct (déprécié mais encore utilisé par certains hôtes dont OVH).
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=15)
        else:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15)
            server.starttls()
        with server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM, [email], msg.as_bytes())
        app.logger.info("Email guide envoyé à %s", email)
    except Exception as exc:  # noqa: BLE001
        app.logger.warning("Échec envoi email guide à %s : %s", email, exc)


def make_cors_response(data: dict, status: int = 200):
    origin = request.headers.get("Origin", "")
    resp = jsonify(data)
    resp.status_code = status
    if origin in ALLOWED_ORIGINS:
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Vary"] = "Origin"
    return resp


@app.after_request
def add_cors_headers(response):
    """Ajoute les en-têtes CORS à toutes les réponses, y compris les pré-vols OPTIONS."""
    origin = request.headers.get("Origin", "")
    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"
        if request.method == "OPTIONS":
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Accept"
            response.headers["Access-Control-Max-Age"] = "86400"
    return response


# Routes ---------------------------------------------------------------------------
@app.route("/scan", methods=["GET"])
def scan():
    client_ip = get_client_ip()
    url = normalize_url(request.args.get("url", ""))
    error = validate_url(url)
    if error:
        return make_cors_response({"ok": False, "error": error}, 400)

    if not is_allowed(client_ip, "scan", limit=30, window_seconds=3600):
        return make_cors_response({"ok": False, "error": "Quota de scans atteint. Réessayez dans une heure."}, 429)

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

    # Statistiques anonymisées : domaine + verdict uniquement (aucune IP ni donnée personnelle).
    try:
        scanned_domain = urlparse(url).hostname or url
        save_scan(scanned_domain, verdict, len(systems))
        track_event("scan", scanned_domain, product="badgeia")
    except sqlite3.Error:
        pass  # les stats ne doivent jamais casser un scan

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


@app.route("/badgeia/lead", methods=["POST"])
def badgeia_lead():
    """Lead magnet : téléchargement du guide AI Act pour dirigeants de PME."""
    client_ip = get_client_ip()

    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    consent = data.get("consent")

    if consent is not True:
        return make_cors_response(
            {"ok": False, "error": "Vous devez accepter la politique de confidentialité."}, 400
        )

    if not EMAIL_RE.match(email):
        return make_cors_response({"ok": False, "error": "Adresse email invalide."}, 400)

    if not is_allowed(client_ip, "lead_guide", limit=3, window_seconds=86400):
        return make_cors_response(
            {"ok": False, "error": "Quota de demandes atteint. Réessayez demain."}, 429
        )

    try:
        save_lead(
            email=email,
            url="/guide-ai-act-pme.pdf",
            score="",
            source="guide-pdf",
        )
    except sqlite3.Error:
        return make_cors_response({"ok": False, "error": "Erreur de stockage. Réessayez plus tard."}, 500)

    # Envoi asynchrone de l'email : ne doit pas faire échouer la requête.
    try:
        send_guide_email(email)
    except Exception as exc:  # noqa: BLE001
        app.logger.warning("Échec envoi email guide après stockage : %s", exc)

    return make_cors_response({"ok": True})


def send_contact_alert(name: str, email: str, message: str) -> None:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    text = f"✉️ Message contact BadgeIA — {name or 'Anonyme'} ({email}) :\n{message[:500]}"
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": text},
            timeout=15,
        )
    except Exception as exc:  # noqa: BLE001
        app.logger.warning("Échec envoi Telegram : %s", exc)


@app.route("/contact", methods=["POST"])
def contact():
    client_ip = get_client_ip()
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()[:100]
    email = (data.get("email") or "").strip().lower()
    message = (data.get("message") or "").strip()[:2000]

    # Pot de miel : les robots remplissent ce champ invisible, pas les humains.
    if (data.get("website") or "").strip():
        return make_cors_response({"ok": True})  # rejet silencieux

    # Validation AVANT consommation du quota (une erreur 400 ne coûte rien).
    if not EMAIL_RE.match(email):
        return make_cors_response({"ok": False, "error": "Adresse email invalide."}, 400)
    if len(message) < 10:
        return make_cors_response({"ok": False, "error": "Message trop court (10 caractères minimum)."}, 400)

    if not is_allowed(client_ip, "contact", limit=3, window_seconds=86400):
        return make_cors_response({"ok": False, "error": "Quota de messages atteint. Réessayez demain."}, 429)

    try:
        save_message(name, email, message)
    except sqlite3.Error:
        return make_cors_response({"ok": False, "error": "Erreur de stockage. Réessayez plus tard."}, 500)

    send_contact_alert(name, email, message)
    return make_cors_response({"ok": True})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})


ALLOWED_EVENTS = {
    "pageview",
    "scan",
    "download_guide",
    "click_buy_kit",
    "click_buy_suivi",
    "click_buy_oneshot",
    "click_buy_pro",
    "click_buy_monitoring",
    "scan_triggered",
    "payment_confirmed",
}


@app.route("/track", methods=["POST", "OPTIONS"])
def track():
    """Incrémente un compteur agrégé anonyme. Aucune donnée personnelle n'est stockée."""
    if request.method == "OPTIONS":
        return "", 204

    data = request.get_json(silent=True) or {}
    event = (data.get("event") or "").strip().lower()
    path = (data.get("path") or "").strip()
    product = (data.get("product") or "badgeia").strip().lower()

    if product not in PRODUCTS:
        return "", 400
    if event not in ALLOWED_EVENTS:
        return "", 400
    if not path or len(path) > 2048:
        return "", 400

    track_event(event, path, product=product)
    return "", 204


@app.route("/stats", methods=["GET"])
def stats():
    """Retourne les compteurs agrégés des 90 derniers jours, filtrables par produit. Données publiques et anonymes."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=90)).strftime("%Y-%m-%d")
    product_filter = (request.args.get("product") or "").strip().lower()

    query = "SELECT product, event, day, SUM(count) FROM events_v2 WHERE day >= ?"
    params: list[Any] = [cutoff]
    if product_filter in PRODUCTS:
        query += " AND product = ?"
        params.append(product_filter)
    query += " GROUP BY product, event, day"

    totals_by_event: dict[str, int] = {}
    by_day: dict[str, dict[str, int]] = {}
    by_product: dict[str, dict[str, Any]] = {}

    try:
        with sqlite3.connect(METRICS_DATABASE_PATH) as conn:
            cursor = conn.execute(query, params)
            for product, event, day, count in cursor.fetchall():
                totals_by_event[event] = totals_by_event.get(event, 0) + count

                day_block = by_day.setdefault(day, {})
                day_block[event] = day_block.get(event, 0) + count

                product_block = by_product.setdefault(
                    product, {"totals_by_event": {}, "by_day": {}}
                )
                product_block["totals_by_event"][event] = (
                    product_block["totals_by_event"].get(event, 0) + count
                )
                product_day_block = product_block["by_day"].setdefault(day, {})
                product_day_block[event] = product_day_block.get(event, 0) + count
    except sqlite3.Error:
        pass

    result: dict[str, Any] = {
        "since": cutoff,
        "totals_by_event": totals_by_event,
        "by_day": by_day,
    }
    if product_filter in PRODUCTS:
        result["product"] = product_filter
    else:
        result["by_product"] = by_product

    return jsonify(result)


# Point d'entrée --------------------------------------------------------------------
if __name__ == "__main__":
    init_db()
    init_metrics_db()
    serve(app, host="0.0.0.0", port=8080)

