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
      .replace(/'/g, "&#39;");
  }

  function renderVerdictClass(verdict) {
    if (verdict === "ok") return "result--ok";
    if (verdict === "warning") return "result--warning";
    return "result--alert";
  }

  function renderVerdictTitle(verdict, systemsCount) {
    if (verdict === "ok") return "✓ Aucun système IA détecté";
    if (verdict === "warning") return "◌ Systèmes IA détectés, mention visible";
    return "✕ Systèmes IA détectés sans mention visible";
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
  // à partir de données provenant de l'API et échappées ci-dessus.
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
      const submitBtn = scanForm.querySelector("button[type='submit']");
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
      const submitBtn = emailForm.querySelector("button[type='submit']");
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

  // Démo du widget : injecte le vrai snippet produit sur la page.
  const demoBtn = document.getElementById("demo-widget");
  if (demoBtn) {
    demoBtn.addEventListener("click", function () {
      if (document.getElementById("badgeia-disclosure-widget")) return;
      const s = document.createElement("script");
      s.src = "widget/badgeia.js";
      s.setAttribute("data-lang", "fr");
      s.setAttribute("data-position", "bottom-right");
      s.setAttribute("data-color", "blue");
      s.async = false;
      document.body.appendChild(s);
      demoBtn.textContent = "Widget affiché en bas à droite ↘ (refermable)";
      demoBtn.disabled = true;
    });
  }
})();
