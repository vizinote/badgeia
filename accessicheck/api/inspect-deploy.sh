#!/bin/bash
set -e
echo "=== Docker containers ==="
docker ps --filter name=accessicheck --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"
echo ""
echo "=== Last 20 lines of accessicheck logs ==="
docker logs --tail 20 accessicheck-api 2>&1 || true
echo ""
echo "=== Server.js checksum ==="
docker exec accessicheck-api md5sum /app/server.js 2>/dev/null || true
echo ""
echo "=== API health ==="
curl -s https://api.brozapi.com/accessicheck/health || true
echo ""
