#!/bin/bash
set -e
echo "=== Force redeploy AccessiCheck ==="
cd /opt/badgeia/accessicheck
docker compose down --remove-orphans || true
docker compose pull 2>/dev/null || true
docker compose up --build -d --remove-orphans
for i in {1..30}; do
  if curl -fsS http://127.0.0.1:8081/health >/dev/null 2>&1; then
    echo "Healthcheck OK"
    exit 0
  fi
  sleep 2
done
echo "ERREUR: healthcheck timeout"
docker compose logs --tail=50
exit 1
