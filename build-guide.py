#!/usr/bin/env python3
"""Génère le guide PDF "AI Act : le guide du dirigeant de PME" depuis le markdown.

Usage:
    python build-guide.py

Le script lit guide-ai-act-pme.md à la racine du dépôt et produit
guide-ai-act-pme.pdf, prêt à être servi par GitHub Pages.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MD_PATH = ROOT / "guide-ai-act-pme.md"
PDF_PATH = ROOT / "guide-ai-act-pme.pdf"
VENV_PATH = ROOT / ".venv-guide"


def log(msg: str) -> None:
    print(f"[build-guide] {msg}")


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    """Extrait un front matter YAML simple du type ---...---."""
    meta: dict[str, str] = {}
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm = parts[1].strip()
            body = parts[2].strip()
            for line in fm.splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    meta[key.strip()] = value.strip().strip('"').strip("'")
            return meta, body
    return meta, text


_APO_LETTERS = "A-Za-zÀ-ÖØ-öø-ÿ0-9*_"


def french_typography(text: str) -> tuple[str, int]:
    """Applique une typographie française systématique au texte.

    Opérations (jamais sur le code, les URLs, les balises HTML ni leurs
    attributs) :
      - apostrophe droite ' -> \u2019 (U+2019) en fin/fin de mot français ;
      - guillemets droits "..." -> « ... » avec espaces insécables ;
      - espace insécable (U+00A0) avant : ; ! ? ;
      - '--' en incise -> tiret cadratin \u2014.

    Retourne (texte traité, nombre d'apostrophes droites corrigées).
    """
    # Contenus à protéger : blocs de code, code inline, URLs, balises HTML.
    tokens: dict[str, str] = {}

    def _stash(m: re.Match) -> str:
        key = f"\x00TYPO{len(tokens)}\x00"
        tokens[key] = m.group(0)
        return key

    text = re.sub(r"```.*?```", _stash, text, flags=re.S)
    text = re.sub(r"`[^`\n]*`", _stash, text)
    text = re.sub(r"https?://[^\s<>'\"]+", _stash, text)
    text = re.sub(r"<[^>]+>", _stash, text)

    # 1. Apostrophe droite -> apostrophe typographique (entre caractères de mot).
    apostrophes = 0
    pattern = re.compile(rf"(?<=[{_APO_LETTERS}])'(?=[{_APO_LETTERS}])")
    text, n = pattern.subn("\u2019", text)
    apostrophes += n

    # 2. Guillemets droits encadrant du texte -> « ... » (espaces insécables).
    text = re.sub(r'"([^"\n]+)"', "\u00ab\u00a0\\1\u00a0\u00bb", text)

    # 3. Espace simple avant : ; ! ? -> espace insécable (jamais de retour ligne).
    text = re.sub(r"[ \t]+([:;!?])", "\u00a0\\1", text)

    # 4. ' -- ' en incise -> tiret cadratin.
    text = re.sub(r"[ \t]+--[ \t]+", " \u2014 ", text)

    # Restauration des contenus protégés.
    for key, value in tokens.items():
        text = text.replace(key, value)

    return text, apostrophes


def ensure_venv() -> Path:
    """Crée un venv local avec weasyprint + markdown si nécessaire."""
    python_bin = VENV_PATH / "bin" / "python"
    if not python_bin.exists():
        log("Création d'un environnement virtuel local pour la génération PDF...")
        subprocess.run([sys.executable, "-m", "venv", str(VENV_PATH)], check=True)
        subprocess.run(
            [str(python_bin), "-m", "pip", "install", "--upgrade", "pip"],
            check=True,
        )
        log("Installation de weasyprint et markdown...")
        subprocess.run(
            [str(python_bin), "-m", "pip", "install", "weasyprint", "markdown"],
            check=True,
        )
    return python_bin


def ensure_dependencies() -> None:
    """Si les dépendances ne sont pas disponibles, bascule vers le venv local."""
    try:
        import markdown  # noqa: F401
        import weasyprint  # noqa: F401
    except ImportError:
        python_bin = ensure_venv()
        log("Relance dans l'environnement virtuel local...")
        os.execv(str(python_bin), [str(python_bin), __file__])


def render_pdf(meta: dict[str, str], body_html: str, output: Path) -> None:
    import weasyprint

    title = meta.get("title", "AI Act : le guide du dirigeant de PME")
    author = meta.get("author", "Brozapi")
    version = meta.get("version", "1.0")
    guide_date = meta.get("date") or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    generated = datetime.now(timezone.utc).strftime("%d/%m/%Y")

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <style>
    @page {{
      size: A4;
      margin: 2.4cm 2.2cm 2.6cm 2.2cm;
      @bottom-center {{
        content: "Brozapi — {title} — page " counter(page);
        font-size: 8.5pt;
        color: #666666;
      }}
    }}

    :root {{
      --blue: #003399;
      --blue-dark: #002266;
      --blue-light: #e6ecf9;
      --gray-900: #1a1a1a;
      --gray-700: #454545;
      --gray-500: #737373;
      --gray-300: #d4d4d4;
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      font-family: "Source Sans 3", "Source Sans Pro", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      font-size: 11pt;
      line-height: 1.55;
      color: var(--gray-900);
    }}

    /* Page de garde */
    .cover {{
      page: cover;
      height: 100vh;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      text-align: center;
      padding: 2cm;
    }}

    .cover__badge {{
      font-size: 14pt;
      font-weight: 800;
      color: var(--blue);
      letter-spacing: -0.02em;
      margin-bottom: 0.5cm;
    }}

    .cover__title {{
      font-size: 28pt;
      font-weight: 800;
      color: var(--blue-dark);
      line-height: 1.15;
      margin: 0 0 0.6cm;
    }}

    .cover__subtitle {{
      font-size: 14pt;
      color: var(--gray-700);
      max-width: 14cm;
      margin: 0 auto 1.5cm;
    }}

    .cover__meta {{
      font-size: 11pt;
      color: var(--gray-500);
      line-height: 1.8;
    }}

    .cover__footer {{
      position: absolute;
      bottom: 2.5cm;
      left: 0;
      right: 0;
      text-align: center;
      font-size: 9pt;
      color: var(--gray-500);
    }}

    @page cover {{
      margin: 0;
      @bottom-center {{
        content: none;
      }}
    }}

    /* Contenu */
    h1 {{
      font-size: 20pt;
      color: var(--blue-dark);
      margin-top: 0;
      margin-bottom: 0.6cm;
      page-break-after: avoid;
    }}

    h2 {{
      font-size: 14pt;
      color: var(--blue);
      margin-top: 0.9cm;
      margin-bottom: 0.4cm;
      page-break-after: avoid;
    }}

    h3 {{
      font-size: 12pt;
      color: var(--gray-900);
      margin-top: 0.6cm;
      margin-bottom: 0.25cm;
      page-break-after: avoid;
    }}

    p {{
      margin: 0 0 0.4cm;
      text-align: justify;
    }}

    ul, ol {{
      margin: 0 0 0.5cm;
      padding-left: 1.1cm;
    }}

    li {{
      margin-bottom: 0.2cm;
    }}

    strong {{
      color: var(--blue-dark);
    }}

    a {{
      color: var(--blue);
      text-decoration: none;
    }}

    blockquote {{
      margin: 0.5cm 0;
      padding: 0.4cm 0.6cm;
      border-left: 3px solid var(--blue);
      background: var(--blue-light);
      color: var(--gray-700);
      font-size: 10.5pt;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 0.5cm 0;
      font-size: 10pt;
      page-break-inside: avoid;
    }}

    th, td {{
      border: 1px solid var(--gray-300);
      padding: 0.25cm 0.35cm;
      text-align: left;
      vertical-align: top;
    }}

    th {{
      background: var(--blue-light);
      color: var(--blue-dark);
      font-weight: 700;
    }}

    hr {{
      border: none;
      border-top: 1px solid var(--gray-300);
      margin: 0.6cm 0;
    }}

    code {{
      font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
      font-size: 9.5pt;
      background: #f4f4f4;
      padding: 0.05cm 0.15cm;
      border-radius: 3px;
    }}

    .page-break {{
      page-break-before: always;
    }}

    .small {{
      font-size: 9.5pt;
      color: var(--gray-500);
    }}
  </style>
</head>
<body>
  <div class="cover">
    <div class="cover__badge">BadgeIA · par Brozapi</div>
    <h1 class="cover__title">{title}</h1>
    <p class="cover__subtitle">Ce qui change, qui est concerné et les actions prioritaires pour les dirigeants de PME.</p>
    <div class="cover__meta">
      Auteur : {author}<br>
      Version : {version}<br>
      Date du guide : {guide_date}<br>
      PDF généré le {generated}
    </div>
    <div class="cover__footer">
      Brozapi — Studio de produits numériques · badgeia.brozapi.com<br>
      Ce guide est fourni à titre indicatif et ne constitue pas un conseil juridique.
    </div>
  </div>

  <div class="page-break"></div>

  {body_html}

  <p class="small" style="margin-top: 1cm;">
    —<br>
    Brozapi, {datetime.now(timezone.utc).year}. Ce document est fourni à titre indicatif. Il ne constitue pas un conseil juridique ni une garantie de conformité.
  </p>
</body>
</html>"""

    weasyprint.HTML(string=html, base_url=str(ROOT)).write_pdf(str(output))


def main() -> int:
    if not MD_PATH.exists():
        log(f"Fichier source introuvable : {MD_PATH}")
        return 1

    ensure_dependencies()

    import markdown

    raw = MD_PATH.read_text(encoding="utf-8")
    meta, body = parse_front_matter(raw)

    # Post-traitement typographique français (apostrophes, guillemets,
    # espaces insécables, tirets cadratins). Ne touche jamais au code, aux
    # URLs, aux balises HTML ni aux attributs.
    body, apostrophes = french_typography(body)
    if apostrophes:
        log(f"Typographie FR : {apostrophes} apostrophes droites corrigées")

    # Conversion markdown -> HTML.
    body_html = markdown.markdown(
        body,
        extensions=["tables", "fenced_code", "toc"],
    )

    # Retire le titre du body HTML (déjà en page de garde).
    body_html = re.sub(r"<h1>.*?</h1>", "", body_html, count=1, flags=re.S)

    log("Génération du PDF...")
    render_pdf(meta, body_html, PDF_PATH)
    log(f"PDF créé : {PDF_PATH} ({PDF_PATH.stat().st_size / 1024:.1f} Ko)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
