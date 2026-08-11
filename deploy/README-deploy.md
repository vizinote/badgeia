# Déploiement BadgeIA API

## Prérequis

- Un VPS avec Docker installé.
- Un nom de domaine `api.brozapi.com` pointant vers le VPS.
- Les variables d'environnement dans `api/.env` (jamais commitées).

## Build et lancement du conteneur

```bash
cd /root/badgeia-build/badgeia

docker build -t badgeia-api ./api

docker network create badgeia-net 2>/dev/null || true

docker run -d --name badgeia-api --restart unless-stopped \
  --network badgeia-net \
  -v badgeia-data:/data \
  --env-file /root/badgeia-build/api.env \
  --add-host api.telegram.org:149.154.166.110 \
  -p 127.0.0.1:8080:8080 \
  badgeia-api
```

L'API écoute uniquement sur `127.0.0.1:8080` ; elle n'est pas exposée directement sur Internet. Le conteneur est isolé sur son propre réseau Docker (`badgeia-net`, anti-SSRF) et `--add-host` contourne le DNS IPv6 cassé d'Ionos pour api.telegram.org. Le fichier `.env` réel vit hors du repo dans `/root/badgeia-build/api.env` (chmod 600).

## Installation de Caddy

```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy
```

Copier la configuration :

> **Important** : `deploy/Caddyfile` est la config **canonique complète** du VPS : elle contient
> `api.brozapi.com` ET `brozapi.com, www.brozapi.com`. Ce fichier est recopié sur l'hôte par
> `accessicheck-deploy.sh`. N'y retirez jamais un bloc domaine : le prochain déploiement
> écraserait la config hôte (incident TLS brozapi.com du 2026-08-11).

```bash
sudo cp deploy/Caddyfile /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

## Firewall

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Vérification

```bash
curl -i https://api.brozapi.com/health
```
