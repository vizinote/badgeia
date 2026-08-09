# BadgeIA

BadgeIA aide les petits sites web (indépendants, TPE) à respecter l'obligation de transparence de l'AI Act européen (article 50) concernant les chatbots et les contenus générés par IA.

## Statut

MVP en phase de validation. Le produit est volontairement simple : scanner gratuit, widget de disclosure, étiqueteur d'images et dossier de preuve horodaté.

## Structure du dépôt

```
.
├── index.html              # Landing page française
├── merci.html              # Page de confirmation email
├── mentions-legales.html   # Mentions légales, CGV, confidentialité
├── favicon.svg             # Favicon minimaliste
├── CNAME                   # badgeia.brozapi.com
├── .nojekyll               # Désactive Jekyll sur GitHub Pages
├── assets/
│   ├── style.css           # Design responsive sans dépendance externe
│   └── app.js              # Logique du scanner et des formulaires
├── widget/
│   └── badgeia.js          # Widget de disclosure (< 8 Ko, vanilla JS)
├── api/
│   ├── app.py              # API Flask + waitress
│   ├── detectors.py        # Signatures de détection IA + disclosure
│   ├── requirements.txt    # Dépendances Python
│   ├── Dockerfile          # Image Docker de l'API
│   └── .env.example        # Variables d'environnement
├── deploy/
│   ├── Caddyfile           # Configuration reverse proxy
│   └── README-deploy.md    # Commandes de déploiement
└── .gitignore              # Exclusion des secrets et données
```

## Déploiement

### Site statique (GitHub Pages)

1. Pousser la branche `main` vers `github.com/vizinote/badgeia`.
2. Activer GitHub Pages depuis la branche `main` / dossier racine.
3. Le domaine personnalisé `badgeia.brozapi.com` est configuré via le fichier `CNAME`.

### API (VPS + Docker)

Voir `deploy/README-deploy.md` pour les commandes exactes :

```bash
docker build -t badgeia-api ./api
docker run -d --name badgeia-api --restart unless-stopped \
  -v badgeia-data:/data --env-file api/.env \
  -p 127.0.0.1:8080:8080 badgeia-api
```

Le reverse proxy Caddy expose `api.brozapi.com` vers `127.0.0.1:8080`.

## Conformité

- Zéro cookie, zéro tracking côté site statique.
- Les données sont stockées sur un serveur situé en Union européenne.
- Aucun secret n'est commité dans le dépôt.

## Avertissement

BadgeIA est un outil technique d'aide à la transparence. Il ne constitue ni un conseil juridique ni une garantie de conformité.
