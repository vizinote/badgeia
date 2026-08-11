# AccessiCheck API

API d'audit accessibilité RGAA/WCAG 2.1 AA pour le produit AccessiCheck.

## Endpoints

- `GET /health` — santé du service
- `POST /scan` — lance un scan asynchrone
  - body: `{ "url": "https://example.com", "offer": "oneshot" }`
  - retourne `{ "ok": true, "id": "...", "status": "pending" }`
- `GET /scan/:id` — statut et résultat du scan
- `GET /result/:id` — alias de `/scan/:id`

## Stack

- Node.js 20 + Express
- Puppeteer + pa11y + axe-core
- SQLite

## Développement local

```bash
cd api
npm install
npm start
```

## Déploiement

```bash
ssh -F /opt/data/.ssh/config kimi-bridge "install-script kanban/boards/brozapi/workspaces/<id>/accessicheck-deploy.sh"
```

Puis exécuter `/root/accessicheck-deploy.sh` sur le VPS.

## Couverture

Ce scan couvre uniquement les critères automatiquement testables (~30-40 % du RGAA). Un audit humain reste nécessaire pour une conformité complète.
