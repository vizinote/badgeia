"""Tests unitaires pour l'endpoint /lead (formulaire email post-scan).

Objectifs :
- avec consent=true (case RGPD cochée côté front), le guide est envoyé par email ;
- sans consentement, aucun email n'est envoyé mais le lead est stocké ;
- une adresse invalide est rejetée en 400.

Exécution : python -m unittest tests.test_lead
"""

import unittest
from unittest import mock

import app


class LeadTestCase(unittest.TestCase):
    def setUp(self):
        app.app.config["TESTING"] = True
        self.client = app.app.test_client()
        patches = [
            mock.patch.object(app, "is_allowed", return_value=True),
            mock.patch.object(app, "save_lead"),
            mock.patch.object(app, "send_telegram_alert"),
            mock.patch.object(app, "send_guide_email"),
        ]
        self.is_allowed, self.save_lead, self.telegram, self.guide = [
            p.start() for p in patches
        ]
        self.addCleanup(lambda: [p.stop() for p in patches])

    def _post(self, payload):
        return self.client.post("/lead", json=payload)

    def test_consent_true_envoie_le_guide(self):
        resp = self._post(
            {"email": "Test@Example.com", "url": "https://crisp.chat/", "score": "alert", "consent": True}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.get_json()["ok"])
        # Case cochée : la preuve stockée reprend la formulation exacte du formulaire.
        self.save_lead.assert_called_once_with(
            "test@example.com",
            "https://crisp.chat/",
            "alert",
            source="scan",
            consent_text=app.CONSENT_GUIDE_TEXT,
        )
        self.guide.assert_called_once_with("test@example.com")

    def test_consent_text_est_la_formulation_de_la_case(self):
        self._post({"email": "a@b.co", "url": "https://x.y/", "score": "ok", "consent": True})
        _, kwargs = self.save_lead.call_args
        self.assertEqual(
            kwargs["consent_text"],
            "J'accepte la politique de confidentialité et je souhaite recevoir le guide.",
        )

    def test_sans_consent_pas_d_email(self):
        resp = self._post({"email": "a@b.co", "url": "https://x.y/", "score": "ok"})
        self.assertEqual(resp.status_code, 200)
        # Pas de case cochée : intérêt légitime, aucun email.
        self.save_lead.assert_called_once_with(
            "a@b.co",
            "https://x.y/",
            "ok",
            source="scan",
            consent_text=app.CONSENT_SCANNER_TEXT,
        )
        self.guide.assert_not_called()

    def test_consent_false_pas_d_email(self):
        resp = self._post({"email": "a@b.co", "url": "https://x.y/", "score": "ok", "consent": False})
        self.assertEqual(resp.status_code, 200)
        self.guide.assert_not_called()

    def test_echec_envoi_ne_casse_pas_la_requete(self):
        self.guide.side_effect = RuntimeError("smtp down")
        resp = self._post({"email": "a@b.co", "url": "", "score": "", "consent": True})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.get_json()["ok"])

    def test_email_invalide_400(self):
        resp = self._post({"email": "pas-un-email", "consent": True})
        self.assertEqual(resp.status_code, 400)
        self.save_lead.assert_not_called()
        self.guide.assert_not_called()


if __name__ == "__main__":
    unittest.main()
