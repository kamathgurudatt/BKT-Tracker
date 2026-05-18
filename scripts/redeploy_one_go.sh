#!/usr/bin/env bash
set -euo pipefail

# One-go release gate for Blinkit Stock Sentinel
# Usage:
#   bash scripts/redeploy_one_go.sh https://<backend-domain>/api/v1

BASE_URL="${1:-}"

printf '\n==> 1) Backend sanity checks\n'
./scripts/sanity_check.sh

printf '\n==> 2) Mobile checks (best effort in current environment)\n'
if command -v flutter >/dev/null 2>&1; then
  (cd mobile && flutter pub get && flutter analyze)
else
  echo "[warn] flutter not installed; skipping mobile analyze/build in this environment"
fi

printf '\n==> 3) Release smoke checks against deployed backend (optional)\n'
if [[ -n "$BASE_URL" ]]; then
  echo "GET $BASE_URL/auth/me"
  curl -fsS "$BASE_URL/auth/me" >/tmp/auth_me.json
  echo "OK: /auth/me reachable"

  code_login=$(curl -s -o /tmp/login_resp.txt -w "%{http_code}" -X POST "$BASE_URL/auth/login")
  code_token=$(curl -s -o /tmp/token_resp.txt -w "%{http_code}" -X POST "$BASE_URL/auth/token")
  echo "POST /auth/login -> HTTP $code_login"
  echo "POST /auth/token -> HTTP $code_token"
  if [[ "$code_login" != "410" || "$code_token" != "410" ]]; then
    echo "[warn] expected HTTP 410 on legacy password auth endpoints"
  fi
else
  echo "No BASE_URL provided; skipping live smoke checks."
fi

printf '\nRelease gate completed.\n'
