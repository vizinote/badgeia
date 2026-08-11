"""Tests unitaires pour les détecteurs BadgeIA.

Objectifs :
- un outil IA n'est détecté que sur une intégration réelle (script/iframe/objet JS),
  pas sur une simple mention textuelle ;
- le widget BadgeIA est reconnu comme une mention de transparence ;
- les verdicts sont cohérents.

Exécution : python -m unittest tests.test_detectors
"""

import unittest

from detectors import detect_disclosure, detect_systems, determine_verdict


class DetectorTestCase(unittest.TestCase):
    def _names(self, systems):
        return [s["name"] for s in systems]

    def test_badgeia_landing_no_false_positives(self):
        """La page badgeia.brozapi.com ne doit plus voir Intercom/Crisp dans ses exemples cliquables."""
        html = """
        <html><body>
          <h1>BadgeIA</h1>
          <p>Essayer avec un site connu :
            <button class="chip" data-url="crisp.chat">crisp.chat</button>
            <button class="chip" data-url="intercom.com">intercom.com</button>
          </p>
          <script src="https://badgeia.brozapi.com/widget/badgeia.js" defer></script>
        </body></html>
        """
        systems = detect_systems(html)
        disclosure_found, evidence = detect_disclosure(html)

        self.assertEqual(self._names(systems), [])
        self.assertTrue(disclosure_found)
        self.assertIn("badgeia", evidence.lower())
        self.assertEqual(determine_verdict(systems, disclosure_found), "ok")

    def test_crisp_real_integration_detected(self):
        """Un vrai script Crisp doit être détecté."""
        html = '<script src="https://client.crisp.chat/l.js" async></script>'
        systems = detect_systems(html)

        self.assertEqual(self._names(systems), ["Crisp"])
        self.assertEqual(systems[0]["category"], "chatbot")
        self.assertEqual(determine_verdict(systems, False), "alert")

    def test_crisp_website_id_detected(self):
        """La présence de CRISP_WEBSITE_ID (snippet inline) doit être détectée."""
        html = """
        <script type="text/javascript">window.CRISP_WEBSITE_ID = "a1b2c3d4";</script>
        """
        systems = detect_systems(html)
        self.assertEqual(self._names(systems), ["Crisp"])

    def test_text_mentions_only_are_not_detected(self):
        """Des mentions textuelles de domaines/outils ne doivent rien déclencher."""
        html = """
        <p>We use intercom.com, crisp.chat, tidio.co, zendesk.com and hubspot.com
        for customer support. ChatGPT and GPT-4 are cool.</p>
        """
        systems = detect_systems(html)
        self.assertEqual(self._names(systems), [])

    def test_intercom_real_widget_detected(self):
        html = '<script src="https://widget.intercom.io/widget/abc123" async></script>'
        systems = detect_systems(html)
        self.assertEqual(self._names(systems), ["Intercom"])

    def test_intercom_settings_object_detected(self):
        html = """
        <script>window.intercomSettings = { app_id: "abc123" };</script>
        """
        systems = detect_systems(html)
        self.assertEqual(self._names(systems), ["Intercom"])

    def test_tidio_real_widget_detected(self):
        html = '<script src="https://code.tidio.co/abc123.js" async></script>'
        systems = detect_systems(html)
        self.assertEqual(self._names(systems), ["Tidio"])

    def test_zendesk_real_widget_detected(self):
        html = '<script src="https://static.zdassets.com/ekr/snippet.js" async></script>'
        systems = detect_systems(html)
        self.assertEqual(self._names(systems), ["Zendesk"])

    def test_hubspot_real_widget_detected(self):
        html = '<script src="https://js.hs-scripts.com/123456.js" async></script>'
        systems = detect_systems(html)
        self.assertEqual(self._names(systems), ["HubSpot"])

    def test_openai_text_not_detected(self):
        html = "<p>Our product uses ChatGPT and GPT-4.</p>"
        systems = detect_systems(html)
        self.assertEqual(self._names(systems), [])

    def test_openai_script_detected(self):
        html = '<script src="https://cdn.openai.com/v1/embedding.js"></script>'
        systems = detect_systems(html)
        self.assertEqual(self._names(systems), ["OpenAI"])

    def test_badgeia_widget_id_detected_as_disclosure(self):
        html = '<div id="badgeia-disclosure-widget">Vous échangez avec un assistant IA</div>'
        disclosure_found, evidence = detect_disclosure(html)
        self.assertTrue(disclosure_found)
        self.assertIn("badgeia-disclosure-widget", evidence.lower())

    def test_real_system_with_disclosure_is_warning(self):
        html = """
        <script src="https://client.crisp.chat/l.js" async></script>
        <p>Vous échangez avec un assistant IA.</p>
        """
        systems = detect_systems(html)
        disclosure_found, _ = detect_disclosure(html)
        self.assertEqual(self._names(systems), ["Crisp"])
        self.assertTrue(disclosure_found)
        self.assertEqual(determine_verdict(systems, disclosure_found), "warning")


if __name__ == "__main__":
    unittest.main()
