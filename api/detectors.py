"""BadgeIA — signatures de détection des systèmes IA et des mentions de transparence.

Chaque signature est un dictionnaire avec :
- name : nom lisible du système
- category : "chatbot", "generator", "disclosure"
- pattern : expression régulière compilée
"""

import re

IA_WIDGET_SIGNATURES = [
    # Chatbots / assistants conversationnels
    {"name": "Intercom", "category": "chatbot", "pattern": re.compile(r"intercom", re.I)},
    {"name": "Drift", "category": "chatbot", "pattern": re.compile(r"drift\.com|drifttag", re.I)},
    {"name": "Crisp", "category": "chatbot", "pattern": re.compile(r"crisp\.chat|crisp-widget", re.I)},
    {"name": "Tidio", "category": "chatbot", "pattern": re.compile(r"tidio\.co|tidio-chat", re.I)},
    {"name": "Chatbase", "category": "chatbot", "pattern": re.compile(r"chatbase\.co|chatbase-widget", re.I)},
    {"name": "SiteGPT", "category": "chatbot", "pattern": re.compile(r"sitegpt\.ai|sitegpt", re.I)},
    {"name": "Botpress", "category": "chatbot", "pattern": re.compile(r"botpress\.cloud|botpress-webchat", re.I)},
    {"name": "Voiceflow", "category": "chatbot", "pattern": re.compile(r"voiceflow\.com|voiceflow-widget", re.I)},
    {"name": "Zendesk", "category": "chatbot", "pattern": re.compile(r"zendesk\.com|zopim|zendesk-web-widget", re.I)},
    {"name": "HubSpot", "category": "chatbot", "pattern": re.compile(r"hubspot\.com|hs-script-loader|hubspot-messages", re.I)},
    {"name": "LiveChat", "category": "chatbot", "pattern": re.compile(r"livechat\.com|livechatinc", re.I)},
    {"name": "Smartsupp", "category": "chatbot", "pattern": re.compile(r"smartsupp\.com|smartsupp-chat", re.I)},
    {"name": "Landbot", "category": "chatbot", "pattern": re.compile(r"landbot\.io|landbot\.com", re.I)},
    {"name": "Collect.chat", "category": "chatbot", "pattern": re.compile(r"collect\.chat|collectchat", re.I)},
    {"name": "Chatwoot", "category": "chatbot", "pattern": re.compile(r"chatwoot\.com|chatwoot-widget", re.I)},
    {"name": "Freshchat", "category": "chatbot", "pattern": re.compile(r"freshchat\.com|freshchat-widget", re.I)},
    {"name": "Tawk.to", "category": "chatbot", "pattern": re.compile(r"tawk\.to|tawk-widget", re.I)},
    {"name": "CustomGPT", "category": "chatbot", "pattern": re.compile(r"customgpt\.ai", re.I)},
    {"name": "Chatling", "category": "chatbot", "pattern": re.compile(r"chatling\.ai|chatling-app", re.I)},
    {"name": "DocsBot", "category": "chatbot", "pattern": re.compile(r"docsbot\.ai|docsbot-widget", re.I)},
    {"name": "Conversational Forms", "category": "chatbot", "pattern": re.compile(r"conversational[-_]?form|conversationalforms", re.I)},
    {"name": "GPT Trainer", "category": "chatbot", "pattern": re.compile(r"gpt-trainer|gptrainer", re.I)},
    {"name": "OpenAI", "category": "generator", "pattern": re.compile(r"openai\.com|chatgpt|gpt-4|gpt4", re.I)},
    {"name": "Claude", "category": "generator", "pattern": re.compile(r"claude\.ai|anthropic", re.I)},
    {"name": "Midjourney", "category": "generator", "pattern": re.compile(r"midjourney", re.I)},
    {"name": "DALL-E", "category": "generator", "pattern": re.compile(r"dall[- ]?e|dalle", re.I)},
    {"name": "Stable Diffusion", "category": "generator", "pattern": re.compile(r"stable[-_]?diffusion|stability\.ai", re.I)},
]

DISCLOSURE_SIGNATURES = [
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
        if sig["pattern"].search(html):
            evidence = sig["pattern"].search(html).group(0)
            found.append(
                {
                    "name": sig["name"],
                    "category": sig["category"],
                    "evidence": evidence,
                }
            )
            seen.add(sig["name"])
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
