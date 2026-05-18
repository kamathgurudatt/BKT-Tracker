#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "==> Checking for unresolved merge markers"
left_marker="<<<"
right_marker=">>>"
merge_pattern="${left_marker}${left_marker:0:2}|^={7}$|${right_marker}${right_marker:0:2}"
if rg -n "$merge_pattern" . \
  --glob '!**/.git/**' \
  --glob '!**/.gradle/**' \
  --glob '!**/.pytest_cache/**' \
  --glob '!**/.ruff_cache/**'; then
  echo "Unresolved merge markers found." >&2
  exit 1
fi

echo "==> Checking active app surfaces for removed password/JWT auth remnants"
if rg -n "Password must be 72 bytes|hashed_password|bcrypt|passlib|argon2|jwt|JWT|OAuth2|auth/login|auth/signup|auth/token|Bearer|Authorization|SECRET_KEY|ALLOW_INTERNAL|AutofillHints\.password" \
  backend mobile infra postman render.yaml .env.example README.md docs/API.md docs/CLOUD_DEPLOYMENT.md docs/PROJECT_SPEC_PROTOTYPE.md \
  --glob '!mobile/android/.gradle/**'; then
  echo "Removed password/JWT auth remnants found in active app surfaces." >&2
  exit 1
fi

echo "==> Validating Postman collection JSON"
python -m json.tool postman/blinkit-stock-sentinel.postman_collection.json >/dev/null

echo "==> Compiling backend modules"
python -m compileall backend/app >/dev/null

echo "==> Linting backend"
ruff check backend/app

echo "==> Running backend tests"
PYTHONPATH=backend pytest -q backend/tests

echo "Sanity check passed."
