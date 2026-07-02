#!/usr/bin/env bash
# Deploy de laatste (gepushte) versie naar de Mac mini: pull → image bouwen → container
# herstarten, met dezelfde .env/authdata-mounts. Vereist SSH-agent-forwarding (voor de
# GitHub-pull) en dat je eerst hebt gepusht.
#
#   git push        # de nieuwe code naar GitHub
#   ./deploy.sh     # de mini pakt 'm op
set -euo pipefail

HOST="${DEPLOY_HOST:-barts-mac-mini}"
echo "→ deploy naar $HOST …"

ssh -A "$HOST" 'set -e
  D=~/.orbstack/bin/docker
  cd ~/DTax
  git pull -q
  echo "code:  $(git log --oneline -1)"
  echo "build: $($D build -q -t watmagwel ~/DTax)"
  $D rm -f watmagwel >/dev/null 2>&1 || true
  mkdir -p ~/watmagwel-authdata
  $D run -d --name watmagwel --restart unless-stopped \
    -p 127.0.0.1:8010:8000 \
    -v ~/DTax/rekenkern/.env:/app/rekenkern/.env:ro \
    -v ~/watmagwel-authdata:/app/rekenkern/authdata \
    watmagwel >/dev/null
  sleep 2
  echo "lokaal: $(curl -s localhost:8010/health)"
'

echo -n "✓ publiek: "; curl -s -o /dev/null -w 'https://watmagwel.nl → HTTP %{http_code}\n' --max-time 15 https://watmagwel.nl/health
