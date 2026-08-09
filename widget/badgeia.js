/**
 * BadgeIA Widget v0 — Disclosure AI Act
 * Usage : <script src="https://badgeia.brozapi.com/widget/badgeia.js"
 *               data-lang="fr"
 *               data-position="bottom-right"
 *               data-color="blue"
 *               data-text=""
 *               defer></script>
 *
 * Positions : bottom-right, bottom-left, top-right, top-left
 * Couleurs  : blue, dark, green, red
 * Langues   : fr, en
 *
 * Zéro dépendance, < 8 Ko, accessible (ARIA, contraste, focus clavier).
 */

(function () {
  "use strict";

  const SCRIPT = document.currentScript || (function () {
    const scripts = document.getElementsByTagName("script");
    return scripts[scripts.length - 1];
  })();

  const lang = (SCRIPT.getAttribute("data-lang") || "fr").toLowerCase();
  const position = (SCRIPT.getAttribute("data-position") || "bottom-right").toLowerCase();
  const color = (SCRIPT.getAttribute("data-color") || "blue").toLowerCase();
  const customText = SCRIPT.getAttribute("data-text") || "";

  const texts = {
    fr: {
      label: customText || "Vous échangez avec un assistant IA",
      close: "Masquer l'information",
      hidden: "Afficher l'information IA",
    },
    en: {
      label: customText || "You are chatting with an AI assistant",
      close: "Hide notice",
      hidden: "Show AI notice",
    },
  };

  const t = texts[lang] || texts.fr;

  const palettes = {
    blue:  { bg: "#003399", fg: "#ffffff", border: "#002266" },
    dark:  { bg: "#1a1a1a", fg: "#ffffff", border: "#000000" },
    green: { bg: "#0b6e47", fg: "#ffffff", border: "#084d31" },
    red:   { bg: "#a61b1b", fg: "#ffffff", border: "#7a1313" },
  };

  const palette = palettes[color] || palettes.blue;

  const positions = {
    "bottom-right": { bottom: "1rem", right: "1rem", top: "auto", left: "auto" },
    "bottom-left":  { bottom: "1rem", left: "1rem", top: "auto", right: "auto" },
    "top-right":    { top: "1rem", right: "1rem", bottom: "auto", left: "auto" },
    "top-left":     { top: "1rem", left: "1rem", bottom: "auto", right: "auto" },
  };

  const pos = positions[position] || positions["bottom-right"];

  const widgetId = "badgeia-disclosure-widget";
  if (document.getElementById(widgetId)) return;

  const widget = document.createElement("div");
  widget.id = widgetId;
  widget.setAttribute("role", "status");
  widget.setAttribute("aria-live", "polite");
  widget.setAttribute("aria-label", t.label);

  Object.assign(widget.style, {
    position: "fixed",
    zIndex: "9999",
    maxWidth: "320px",
    padding: "0.75rem 1rem",
    borderRadius: "0.75rem",
    backgroundColor: palette.bg,
    color: palette.fg,
    border: "1px solid " + palette.border,
    boxShadow: "0 4px 20px rgba(0,0,0,0.15)",
    fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    fontSize: "0.95rem",
    lineHeight: "1.4",
    display: "flex",
    alignItems: "center",
    gap: "0.75rem",
    transition: "transform 0.2s ease, opacity 0.2s ease",
  });

  widget.style.top = pos.top;
  widget.style.bottom = pos.bottom;
  widget.style.left = pos.left;
  widget.style.right = pos.right;

  const icon = document.createElement("span");
  icon.setAttribute("aria-hidden", "true");
  icon.textContent = "🤖";
  icon.style.fontSize = "1.1rem";

  const text = document.createElement("span");
  text.textContent = t.label;
  text.style.flex = "1";

  const closeBtn = document.createElement("button");
  closeBtn.type = "button";
  closeBtn.setAttribute("aria-label", t.close);
  closeBtn.title = t.close;
  closeBtn.textContent = "×";
  Object.assign(closeBtn.style, {
    background: "transparent",
    border: "none",
    color: "inherit",
    fontSize: "1.4rem",
    lineHeight: "1",
    cursor: "pointer",
    padding: "0 0.25rem",
    margin: "-0.25rem -0.25rem -0.25rem 0",
    borderRadius: "0.25rem",
  });

  closeBtn.addEventListener("mouseover", function () {
    closeBtn.style.backgroundColor = "rgba(255,255,255,0.15)";
  });
  closeBtn.addEventListener("mouseout", function () {
    closeBtn.style.backgroundColor = "transparent";
  });

  let hidden = false;
  closeBtn.addEventListener("click", function () {
    if (!hidden) {
      widget.style.opacity = "0.7";
      widget.style.transform = "scale(0.92)";
      text.textContent = "";
      icon.textContent = "👁";
      closeBtn.setAttribute("aria-label", t.hidden);
      closeBtn.title = t.hidden;
      widget.setAttribute("aria-label", t.hidden);
      hidden = true;
    } else {
      widget.style.opacity = "1";
      widget.style.transform = "scale(1)";
      text.textContent = t.label;
      icon.textContent = "🤖";
      closeBtn.setAttribute("aria-label", t.close);
      closeBtn.title = t.close;
      widget.setAttribute("aria-label", t.label);
      hidden = false;
    }
  });

  closeBtn.addEventListener("focus", function () {
    closeBtn.style.outline = "2px solid currentColor";
    closeBtn.style.outlineOffset = "2px";
  });
  closeBtn.addEventListener("blur", function () {
    closeBtn.style.outline = "none";
  });

  widget.appendChild(icon);
  widget.appendChild(text);
  widget.appendChild(closeBtn);

  function insert() {
    document.body.appendChild(widget);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", insert);
  } else {
    insert();
  }
})();
