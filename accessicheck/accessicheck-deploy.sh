#!/usr/bin/env bash
set -euo pipefail

# Déploiement AccessiCheck API sur le VPS Brozapi
# Ce script est exécuté sur l'hôte VPS (root) via la porte SSH blindée.

REPO_DIR="/opt/badgeia"
REPO_URL="https://github.com/vizinote/badgeia.git"
BRANCH="main"
NETWORK="badgeia-net"

echo "=== AccessiCheck deploy ==="

# Vérifie que le réseau Docker existe
if ! docker network ls --format '{{.Name}}' | grep -qx "$NETWORK"; then
  echo "ERREUR: réseau Docker $NETWORK introuvable"
  exit 1
fi

# Clone ou met à jour le repo
if [ -d "$REPO_DIR/.git" ]; then
  echo "Pull $BRANCH dans $REPO_DIR"
  cd "$REPO_DIR"
  TOKEN=$(python3 /opt/data/bin/github-token 2>/dev/null | tr -d '\n')
  if [ -n "$TOKEN" ]; then
    git remote set-url origin "https://x-access-token:${TOKEN}@github.com/vizinote/badgeia.git"
  fi
  git fetch origin
  git reset --hard "origin/$BRANCH"
  git remote set-url origin "$REPO_URL"
else
  echo "Clone $REPO_URL dans $REPO_DIR"
  git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "$REPO_DIR"
  cd "$REPO_DIR"
fi

GIT_SHA=$(git rev-parse --short HEAD)
echo "Git SHA: $GIT_SHA"

# Build et démarrage
echo "Docker compose up --build"
cd "$REPO_DIR/accessicheck"
docker compose pull 2>/dev/null || true
docker compose up --build -d --remove-orphans

# Attente healthcheck
echo "Attente healthcheck..."
for i in {1..30}; do
  if curl -fsS http://127.0.0.1:8081/health >/dev/null 2>&1; then
    echo "Healthcheck OK"
    break
  fi
  if [ "$i" -eq 30 ]; then
    echo "ERREUR: healthcheck timeout"
    docker compose logs --tail=50
    exit 1
  fi
  sleep 2
done

# Met à jour la config Caddy
CADDYFILE_SRC="$REPO_DIR/deploy/Caddyfile"
CADDYFILE_DST="/etc/caddy/Caddyfile"
if [ -f "$CADDYFILE_SRC" ]; then
  echo "Mise à jour Caddyfile"
  cp "$CADDYFILE_SRC" "$CADDYFILE_DST"
fi

if systemctl is-active --quiet caddy 2>/dev/null; then
  echo "Reload Caddy"
  caddy reload --config "$CADDYFILE_DST" --adapter caddyfile || true
fi

echo "=== Deploy OK — $GIT_SHA ==="
