/**
 * BadgeIA — application frontale
 * Zéro dépendance externe. Zéro cookie. Zéro tracking.
 */

// TODO(D16): renseigner les liens Stripe avant le lancement.
const STRIPE_LINKS = {
  kit39: "https://buy.stripe.com/bJeeV7cRb5OtaFZbzLcZa04",
  suivi6: "https://buy.stripe.com/aFabIVaJ31yd01lbzLcZa05",
};

const API_BASE = "https://api.brozapi.com";

/**
 * Envoie un événement de mesure d’audience anonyme.
 * Aucun cookie, aucune IP, aucun identifiant n’est transmis.
 */
function trackEvent(event, path) {
  try {
    var payload = JSON.stringify({ event: event, path: path });
    navigator.sendBeacon
      ? navigator.sendBeacon(API_BASE + "/track", new Blob([payload], { type: "application/json" }))
      : fetch(API_BASE + "/track", {
          method: "POST",
          keepalive: true,
          headers: { "Content-Type": "application/json" },
          body: payload,
        }).catch(function () {});
  } catch (e) {
    // silencieux : la mesure ne doit jamais bloquer le site
  }
}

(function () {
  "use strict";

  const scanForm = document.getElementById("scan-form");
  const scanResult = document.getElementById("scan-result");
  const emailGate = document.getElementById("email-gate");
  const emailForm = document.getElementById("email-form");
  const buyKitBtn = document.getElementById("buy-kit");
  const buySuiviBtn = document.getElementById("buy-suivi");

  let lastScan = { url: "", score: "" };

  function setStatus(el, message, type) {
    el.textContent = message;
    el.className = "status-msg status-msg--" + type;
  }

  function clearChildren(el) {
    while (el.firstChild) {
      el.removeChild(el.firstChild);
    }
  }

  function createSpinner() {
    const span = document.createElement("span");
    span.className = "spinner";
    span.setAttribute("aria-hidden", "true");
    return span;
  }

  function escapeHtml(str) {
    if (str == null) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/\u0027/g, "&#39;");
  }

  function renderVerdictClass(verdict) {
    if (verdict === "ok") return "result--ok";
    if (verdict === "warning") return "result--warning";
    return "result--alert";
  }

  function renderVerdictTitle(verdict, systemsCount) {
    if (verdict === "ok") return "✓ Aucun système IA détecté";
    if (verdict === "warning") return "◌ Chatbot IA détecté — mention de transparence présente";
    const count = systemsCount || 1;
    const mention = count > 1 ? "mentions" : "mention";
    const manquante = count > 1 ? "manquantes" : "manquante";
    if (count === 1) return "Chatbot IA détecté — 1 " + mention + " de transparence " + manquante;
    return "Chatbots IA détectés — " + count + " " + mention + " de transparence " + manquante;
  }

  function renderSystems(systems) {
    if (!Array.isArray(systems) || systems.length === 0) {
      return "<p>Aucun widget ou service IA détecté sur cette page.</p>";
    }
    let html = "<ul>";
    for (const s of systems) {
      html +=
        "<li>" +
        escapeHtml(s.name) +
        (s.category ? " <em>(" + escapeHtml(s.category) + ")</em>" : "") +
        "</li>";
    }
    html += "</ul>";
    return html;
  }

  // Note : le résultat est injecté via innerHTML mais construit exclusivement
  // à partir de données provenant de l’API et échappées ci-dessus.
  function renderScanResult(data) {
    clearChildren(scanResult);
    scanResult.className = "result " + renderVerdictClass(data.verdict);

    const title = document.createElement("h3");
    title.textContent = renderVerdictTitle(
      data.verdict,
      Array.isArray(data.systems) ? data.systems.length : 0
    );
    scanResult.appendChild(title);

    const listContainer = document.createElement("div");
    listContainer.innerHTML = renderSystems(data.systems);
    scanResult.appendChild(listContainer);

    const disclosure = document.createElement("p");
    if (data.disclosure_found) {
      disclosure.textContent = "Mention de transparence repérée.";
    } else {
      disclosure.textContent = "Aucune mention de transparence visible repérée.";
    }
    scanResult.appendChild(disclosure);

    const small = document.createElement("p");
    small.innerHTML =
      "<small>Scan réalisé le " +
      escapeHtml(new Date(data.scanned_at || Date.now()).toLocaleString("fr-FR")) +
      "</small>";
    scanResult.appendChild(small);

    emailGate.hidden = false;
    scanResult.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  if (scanForm) {
    scanForm.addEventListener("submit", async function (event) {
      event.preventDefault();
      const input = document.getElementById("scan-url");
      let url = input.value.trim();
      // Accepte "mon-site.fr" sans schéma : on ajoute https:// automatiquement.
      if (url && !url.includes("://")) {
        url = "https://" + url;
        input.value = url;
      }
      const submitBtn = scanForm.querySelector("button[type=\"submit\"]");
      const originalBtnText = submitBtn.innerHTML;

      if (!url) {
        setStatus(scanResult, "Veuillez saisir une URL.", "error");
        return;
      }

      try {
        const parsed = new URL(url);
        if (!parsed.hostname.includes(".")) throw new Error("no dot");
      } catch (e) {
        setStatus(scanResult, "Veuillez saisir une adresse valide (ex. mon-site.fr).", "error");
        return;
      }

      submitBtn.disabled = true;
      submitBtn.innerHTML = "";
      submitBtn.appendChild(createSpinner());
      submitBtn.appendChild(document.createTextNode(" Analyse en cours…"));
      clearChildren(scanResult);
      scanResult.className = "result";
      emailGate.hidden = true;

      try {
        const response = await fetch(API_BASE + "/scan?url=" + encodeURIComponent(url), {
          method: "GET",
          headers: { Accept: "application/json" },
        });
        const data = await response.json();

        if (!response.ok || !data.ok) {
          setStatus(scanResult, data.error || "Réessayez dans quelques instants.", "error");
          return;
        }

        lastScan = {
          url: data.url || url,
          score: data.verdict || "unknown",
        };
        renderScanResult(data);
      } catch (err) {
        setStatus(scanResult, "Réessayez dans quelques instants.", "error");
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnText;
      }
    });
  }

  if (emailForm) {
    emailForm.addEventListener("submit", async function (event) {
      event.preventDefault();
      const input = document.getElementById("lead-email");
      const email = input.value.trim();
      const statusEl = document.getElementById("email-status");
      const submitBtn = emailForm.querySelector("button[type=\"submit\"]");
      const originalText = submitBtn.textContent;

      if (!email || !email.includes("@") || !email.includes(".")) {
        setStatus(statusEl, "Veuillez saisir une adresse email valide.", "error");
        return;
      }

      submitBtn.disabled = true;
      submitBtn.textContent = "Envoi en cours…";

      try {
        const response = await fetch(API_BASE + "/lead", {
          method: "POST",
          headers: { "Content-Type": "application/json", Accept: "application/json" },
          body: JSON.stringify({
            email: email,
            url: lastScan.url,
            score: lastScan.score,
          }),
        });
        const data = await response.json();

        if (!response.ok || !data.ok) {
          setStatus(statusEl, data.error || "Réessayez dans quelques instants.", "error");
          return;
        }

        setStatus(statusEl, "Merci ! Vous recevrez le rapport et le guide sous peu.", "success");
        input.value = "";
      } catch (err) {
        setStatus(statusEl, "Réessayez dans quelques instants.", "error");
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
      }
    });
  }

  const guideForm = document.getElementById("guide-form");
  if (guideForm) {
    guideForm.addEventListener("submit", async function (event) {
      event.preventDefault();
      const emailInput = document.getElementById("guide-email");
      const consentInput = document.getElementById("guide-consent");
      const statusEl = document.getElementById("guide-status");
      const submitBtn = guideForm.querySelector("button[type=\"submit\"]");
      const originalText = submitBtn.textContent;

      const email = emailInput.value.trim();
      const consent = consentInput.checked;

      if (!email || !email.includes("@") || !email.includes(".")) {
        setStatus(statusEl, "Veuillez saisir une adresse email valide.", "error");
        return;
      }
      if (!consent) {
        setStatus(statusEl, "Vous devez accepter la politique de confidentialité.", "error");
        return;
      }

      submitBtn.disabled = true;
      submitBtn.textContent = "Envoi en cours…";

      try {
        const response = await fetch(API_BASE + "/badgeia/lead", {
          method: "POST",
          headers: { "Content-Type": "application/json", Accept: "application/json" },
          body: JSON.stringify({ email: email, consent: true }),
        });
        const data = await response.json();

        if (!response.ok || !data.ok) {
          setStatus(statusEl, data.error || "Réessayez dans quelques instants.", "error");
          return;
        }

        setStatus(statusEl, "Merci ! Le guide vous a été envoyé par email.", "success");
        trackEvent("download_guide", location.pathname || "/");
        emailInput.value = "";
        consentInput.checked = false;
      } catch (err) {
        setStatus(statusEl, "Réessayez dans quelques instants.", "error");
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
      }
    });
  }

  function setupBuyButton(btn, key) {
    if (!btn) return;
    if (STRIPE_LINKS[key]) {
      btn.href = STRIPE_LINKS[key];
      btn.target = "_blank";
      btn.rel = "noopener";
      btn.textContent = key === "kit39" ? "Commander le Kit — 39 €" : "Souscrire — 6 €/mois";
    } else {
      btn.addEventListener("click", function (event) {
        event.preventDefault();
        document.getElementById("scanner").scrollIntoView({ behavior: "smooth" });
      });
      btn.textContent = "Être prévenu du lancement";
    }
  }

  setupBuyButton(buyKitBtn, "kit39");
  setupBuyButton(buySuiviBtn, "suivi6");

  // Mesures d’audience anonymes (aucun cookie, aucune IP).
  document.addEventListener("DOMContentLoaded", function () {
    trackEvent("pageview", location.pathname || "/");
  });

  if (buyKitBtn) {
    buyKitBtn.addEventListener("click", function () {
      trackEvent("click_buy_kit", location.pathname || "/");
    });
  }

  if (buySuiviBtn) {
    buySuiviBtn.addEventListener("click", function () {
      trackEvent("click_buy_suivi", location.pathname || "/");
    });
  }

  // Exemples cliquables : remplissent le champ et lancent le scan.
  document.querySelectorAll(".chip[data-url]").forEach(function (chip) {
    chip.addEventListener("click", function () {
      const input = document.getElementById("scan-url");
      input.value = chip.getAttribute("data-url");
      if (typeof scanForm.requestSubmit === "function") {
        scanForm.requestSubmit();
      } else {
        scanForm.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
      }
    });
  });

  // Démo du widget : le badge est déjà affiché (chargé en bas de page) ;
  // au clic, on scrolle en bas, on fait pulser le widget et on donne un feedback texte.
  const demoBtn = document.getElementById("demo-widget");
  if (demoBtn) {
    const initialLabel = demoBtn.textContent;
    demoBtn.addEventListener("click", function () {
      const widget = document.getElementById("badgeia-disclosure-widget");
      window.scrollTo({ top: document.documentElement.scrollHeight, behavior: "smooth" });
      if (widget) {
        widget.classList.remove("badgeia-pulse");
        // Forcer le reflow pour relancer l'animation à chaque clic.
        void widget.offsetWidth;
        widget.classList.add("badgeia-pulse");
        setTimeout(function () {
          widget.classList.remove("badgeia-pulse");
        }, 2000);
      }
      demoBtn.textContent = "Widget affiché en bas à droite ↘";
      setTimeout(function () {
        demoBtn.textContent = initialLabel;
      }, 3000);
    });
  }
})();
