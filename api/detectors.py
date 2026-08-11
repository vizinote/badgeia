"""BadgeIA — signatures de détection des systèmes IA et des mentions de transparence.

Chaque signature de système IA est un dictionnaire avec :
- name : nom lisible du système
- category : "chatbot", "generator"
- patterns : liste d'expressions régulières ; une seule correspondance suffit
  à considérer l'intégration comme présente.

Règle d'or : on ne détecte PAS un outil sur une simple mention textuelle
(ex. « intercom.com » dans un paragraphe ou un bouton). Il faut un pattern
d'intégration réel : balise <script src=...> / <iframe src=...> sur un
domaine connu, ou un objet/fonction JavaScript caractéristique.

Les signatures de transparence (DISCLOSURE_SIGNATURES) matchent elles du
texte/HTML, car une mention de transparence est par nature textuelle.
"""

import re


def _script_src(domain_pattern: str) -> re.Pattern:
    """Regex pour une balise <script src="https://<domain_pattern>/...">."""
    return re.compile(r'<script[^>]+src=["\']https?://' + domain_pattern + r'[^"\']*["\']', re.I)


def _iframe_src(domain_pattern: str) -> re.Pattern:
    """Regex pour une balise <iframe src="https://<domain_pattern>/...">."""
    return re.compile(r'<iframe[^>]+src=["\']https?://' + domain_pattern + r'[^"\']*["\']', re.I)


IA_WIDGET_SIGNATURES = [
    # Chatbots / assistants conversationnels
    {
        "name": "Intercom",
        "category": "chatbot",
        "patterns": [
            _script_src(r'(?:[a-z0-9-]+\.)?intercom\.(?:io|com)'),
            _script_src(r'js\.intercomcdn\.com'),
            re.compile(r'window\.intercomSettings', re.I),
            re.compile(r'\bIntercom\s*\(', re.I),
        ],
    },
    {
        "name": "Drift",
        "category": "chatbot",
        "patterns": [
            _script_src(r'(?:[a-z0-9-]+\.)?drift\.com'),
            _script_src(r'js\.driftt\.com'),
            re.compile(r'\bdrifttag\b', re.I),
            re.compile(r'\bdrift\.load\b', re.I),
            re.compile(r'\bDrift\s*\(', re.I),
        ],
    },
    {
        "name": "Crisp",
        "category": "chatbot",
        "patterns": [
            _script_src(r'(?:client|game|api|image|settings)\.crisp\.chat'),
            re.compile(r'\bCRISP_WEBSITE_ID\b', re.I),
            re.compile(r'\$crisp\b', re.I),
            re.compile(r'crisp\s*[-=:]\s*["\']?[a-f0-9-]{20,}', re.I),
        ],
    },
    {
        "name": "Tidio",
        "category": "chatbot",
        "patterns": [
            _script_src(r'code\.tidio\.co'),
            _script_src(r'(?:[a-z0-9-]+\.)?tidio\.chat'),
            re.compile(r'\btidioChat\b', re.I),
            re.compile(r'tidio-chat', re.I),
        ],
    },
    {
        "name": "Chatbase",
        "category": "chatbot",
        "patterns": [
            _script_src(r'(?:[a-z0-9-]+\.)?chatbase\.co'),
            re.compile(r'chatbase-widget', re.I),
            re.compile(r'\bChatbase\s*\(', re.I),
        ],
    },
    {
        "name": "SiteGPT",
        "category": "chatbot",
        "patterns": [
            _script_src(r'(?:[a-z0-9-]+\.)?sitegpt\.ai'),
            re.compile(r'sitegpt-widget', re.I),
            re.compile(r'\bSiteGPT\s*\(', re.I),
        ],
    },
    {
        "name": "Botpress",
        "category": "chatbot",
        "patterns": [
            _script_src(r'(?:[a-z0-9-]+\.)?botpress\.cloud'),
            _script_src(r'cdn\.botpress\.dev'),
            re.compile(r'botpress-webchat', re.I),
            re.compile(r'\bbotpressWebChat\b', re.I),
            re.compile(r'\bBotpress\s*\(', re.I),
        ],
    },
    {
        "name": "Voiceflow",
        "category": "chatbot",
        "patterns": [
            _script_src(r'(?:[a-z0-9-]+\.)?voiceflow\.com'),
            _script_src(r'cdn\.voiceflow\.com'),
            re.compile(r'voiceflow-widget', re.I),
            re.compile(r'\bVoiceflow\s*\(', re.I),
        ],
    },
    {
        "name": "Zendesk",
        "category": "chatbot",
        "patterns": [
            _script_src(r'(?:[a-z0-9-]+\.)?zendesk\.com'),
            _script_src(r'(?:[a-z0-9-]+\.)?zopim\.com'),
            _script_src(r'(?:[a-z0-9-]+\.)?zdassets\.com'),
            re.compile(r'zendesk-web-widget', re.I),
            re.compile(r'\bzE\s*\(', re.I),
            re.compile(r'\b$zopim\b', re.I),
        ],
    },
    {
        "name": "HubSpot",
        "category": "chatbot",
        "patterns": [
            _script_src(r'(?:[a-z0-9-]+\.)?hubspot\.com'),
            _script_src(r'js\.hs-scripts\.com'),
            re.compile(r'hs-script-loader', re.I),
            re.compile(r'hubspot-messages', re.I),
            re.compile(r'\bHubSpot\s*\(', re.I),
        ],
    },
    {
        "name": "LiveChat",
        "category": "chatbot",
        "patterns": [
            _script_src(r'(?:[a-z0-9-]+\.)?livechat(?:inc)?\.com'),
            re.compile(r'\bLC_API\b', re.I),
            re.compile(r'window\.__lc\b', re.I),
        ],
    },
    {
        "name": "Smartsupp",
        "category": "chatbot",
        "patterns": [
            _script_src(r'(?:[a-z0-9-]+\.)?smartsupp\.com'),
            re.compile(r'smartsupp-chat', re.I),
            re.compile(r'\b_smartsupp\b', re.I),
        ],
    },
    {
        "name": "Landbot",
        "category": "chatbot",
        "patterns": [
            _script_src(r'(?:[a-z0-9-]+\.)?landbot\.(?:io|com)'),
            re.compile(r'\bLandbot\s*\(', re.I),
            re.compile(r'landbot-widget', re.I),
        ],
    },
    {
        "name": "Collect.chat",
        "category": "chatbot",
        "patterns": [
            _script_src(r'(?:[a-z0-9-]+\.)?collect\.chat'),
            re.compile(r'collectchat', re.I),
            re.compile(r'\bCollectChat\s*\(', re.I),
        ],
    },
    {
        "name": "Chatwoot",
        "category": "chatbot",
        "patterns": [
            _script_src(r'(?:[a-z0-9-]+\.)?chatwoot\.com'),
            re.compile(r'chatwoot-widget', re.I),
            re.compile(r'\bchatwoot\b', re.I),
            re.compile(r'window\.__chatwoot', re.I),
        ],
    },
    {
        "name": "Freshchat",
        "category": "chatbot",
        "patterns": [
            _script_src(r'(?:[a-z0-9-]+\.)?freshchat\.com'),
            re.compile(r'freshchat-widget', re.I),
            re.compile(r'\bfcWidget\b', re.I),
        ],
    },
    {
        "name": "Tawk.to",
        "category": "chatbot",
        "patterns": [
            _script_src(r'(?:[a-z0-9-]+\.)?tawk\.to'),
            re.compile(r'tawk-widget', re.I),
            re.compile(r'\bTawk_API\b', re.I),
        ],
    },
    {
        "name": "CustomGPT",
        "category": "chatbot",
        "patterns": [
            _script_src(r'(?:[a-z0-9-]+\.)?customgpt\.ai'),
            re.compile(r'customgpt-widget', re.I),
            re.compile(r'\bCustomGPT\s*\(', re.I),
        ],
    },
    {
        "name": "Chatling",
        "category": "chatbot",
        "patterns": [
            _script_src(r'(?:[a-z0-9-]+\.)?chatling\.ai'),
            re.compile(r'chatling-app', re.I),
            re.compile(r'\bChatling\s*\(', re.I),
        ],
    },
    {
        "name": "DocsBot",
        "category": "chatbot",
        "patterns": [
            _script_src(r'(?:[a-z0-9-]+\.)?docsbot\.ai'),
            re.compile(r'docsbot-widget', re.I),
            re.compile(r'\bDocsBot\s*\(', re.I),
        ],
    },
    {
        "name": "Conversational Forms",
        "category": "chatbot",
        "patterns": [
            _script_src(r'(?:[a-z0-9-]+\.)?typeform\.com'),
            re.compile(r'conversational[-_]form', re.I),
            re.compile(r'\bConversationalForm\b', re.I),
        ],
    },
    {
        "name": "GPT Trainer",
        "category": "chatbot",
        "patterns": [
            _script_src(r'(?:[a-z0-9-]+\.)?gpt-trainer\.com'),
            _script_src(r'(?:[a-z0-9-]+\.)?gptrainer\.ai'),
            re.compile(r'gpt-trainer', re.I),
            re.compile(r'\bGPTrainer\s*\(', re.I),
        ],
    },
    # Générateurs de contenu IA (seules les intégrations réelles comptent)
    {
        "name": "OpenAI",
        "category": "generator",
        "patterns": [
            _script_src(r'(?:[a-z0-9-]+\.)?openai\.com'),
            _script_src(r'cdn\.openai\.com'),
            re.compile(r'\bOpenAI\s*\(', re.I),
            re.compile(r'\bwindow\.openai\b', re.I),
        ],
    },
    {
        "name": "Claude",
        "category": "generator",
        "patterns": [
            _script_src(r'(?:[a-z0-9-]+\.)?anthropic\.com'),
            _script_src(r'(?:[a-z0-9-]+\.)?claude\.ai'),
            re.compile(r'\bAnthropic\s*\(', re.I),
            re.compile(r'\bwindow\.anthropic\b', re.I),
        ],
    },
    {
        "name": "Midjourney",
        "category": "generator",
        "patterns": [
            _script_src(r'(?:[a-z0-9-]+\.)?midjourney\.com'),
            re.compile(r'\bMidjourney\s*\(', re.I),
        ],
    },
    {
        "name": "DALL-E",
        "category": "generator",
        "patterns": [
            _script_src(r'[^"\']*dall[-_]?e[^"\']*'),
            re.compile(r'\bDALL[- ]?E\s*\(', re.I),
            re.compile(r'\bdall[-_]?e[-_]?api\b', re.I),
        ],
    },
    {
        "name": "Stable Diffusion",
        "category": "generator",
        "patterns": [
            _script_src(r'(?:[a-z0-9-]+\.)?stability\.ai'),
            re.compile(r'\bStableDiffusion\b', re.I),
        ],
    },
]

DISCLOSURE_SIGNATURES = [
    # Widget BadgeIA lui-même = mention de transparence présente
    {"name": "BadgeIA", "category": "disclosure", "pattern": re.compile(r'<script[^>]+src=["\'][^"\']*badgeia[^"\']*\.js["\']', re.I)},
    {"name": "BadgeIA", "category": "disclosure", "pattern": re.compile(r'id=["\']badgeia-disclosure-widget["\']', re.I)},
    # Français
    {"name": "Mention IA", "category": "disclosure", "pattern": re.compile(r"assistant\s+(?:artificiel|ia|intelligence artificielle)", re.I)},
    {"name": "Mention IA", "category": "disclosure", "pattern": re.compile(r"vous\s+échangez\s+avec\s+(?:une\s+)?(?:ia|intelligence artificielle|assistant)", re.I)},
    {"name": "Mention IA", "category": "disclosure", "pattern": re.compile(r"contenu\s+généré\s+(?:par\s+)?(?:une\s+)?(?:ia|intelligence artificielle)", re.I)},
    {"name": "Mention chatbot", "category": "disclosure", "pattern": re.compile(r"chatbot\s+(?:ia|intelligence artificielle)", re.I)},
    {"name": "Mention virtuel", "category": "disclosure", "pattern": re.compile(r"assistant\s+virtuel", re.I)},
    # Anglais
    {"name": "AI-generated mention", "category": "disclosure", "pattern": re.compile(r"ai[- ]?generated|generated\s+by\s+(?:an\s+)?ai", re.I)},
    {"name": "AI assistant mention", "category": "disclosure", "pattern": re.compile(r"ai\s+assistant|artificial\s+intelligence\s+assistant", re.I)},
    {"name": "Chatbot mention", "category": "disclosure", "pattern": re.compile(r"chatbot\s+(?:ai|powered\s+by\s+ai)", re.I)},
    {"name": "Virtual assistant mention", "category": "disclosure", "pattern": re.compile(r"virtual\s+assistant", re.I)},
    {"name": "AI content mention", "category": "disclosure", "pattern": re.compile(r"content\s+(?:was\s+)?generated\s+by\s+(?:an\s+)?ai", re.I)},
]


def detect_systems(html: str) -> list[dict]:
    """Retourne la liste des systèmes IA détectés dans le HTML."""
    found = []
    seen = set()
    for sig in IA_WIDGET_SIGNATURES:
        if sig["name"] in seen:
            continue
        for pattern in sig["patterns"]:
            match = pattern.search(html)
            if match:
                found.append(
                    {
                        "name": sig["name"],
                        "category": sig["category"],
                        "evidence": match.group(0),
                    }
                )
                seen.add(sig["name"])
                break
    return found


def detect_disclosure(html: str) -> tuple[bool, str]:
    """Indique si une mention de transparence est présente et retourne l'extrait trouvé."""
    for sig in DISCLOSURE_SIGNATURES:
        match = sig["pattern"].search(html)
        if match:
            return True, match.group(0)
    return False, ""


def determine_verdict(systems: list[dict], disclosure_found: bool) -> str:
    """Détermine le verdict entre ok, warning et alert."""
    if not systems:
        return "ok"
    if disclosure_found:
        return "warning"
    return "alert"
