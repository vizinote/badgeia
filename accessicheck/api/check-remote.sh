#!/bin/bash
echo "=== /opt/badgeia git status ==="
cd /opt/badgeia && git log --oneline -3 && echo "" && git status --short && echo "" && echo "server.js md5sum:" && md5sum accessicheck/api/server.js && echo "" && echo "reports dir:" && ls -la accessicheck/api/reports/
