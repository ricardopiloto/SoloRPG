#!/usr/bin/env bash
# Suite local: pytest + build frontend (+ E2E opcional)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUN_E2E="${RUN_E2E:-0}"

echo "=== WFRP Solo — run-tests ==="
echo

echo "→ Backend (pytest)"
cd "$ROOT/backend"
if [[ ! -x .venv/bin/pytest ]]; then
  echo "Erro: backend/.venv ausente. Rode: cd backend && python -m venv .venv && pip install -r requirements.txt"
  exit 1
fi
DATABASE_PROFILE=sqlite-dev DATABASE_URL= LLM_PROVIDER=mock .venv/bin/pytest tests/ -q
echo

echo "→ Frontend (build)"
cd "$ROOT/frontend"
npm run build
echo

if [[ "$RUN_E2E" == "1" ]]; then
  echo "→ E2E (Playwright)"
  if [[ ! -d node_modules/@playwright/test ]]; then
    echo "Instale Playwright: cd frontend && npm install && npx playwright install chromium"
    exit 1
  fi
  npm run test:e2e
  echo
fi

echo "✓ Suite concluída"
if [[ "$RUN_E2E" != "1" ]]; then
  echo "  Dica: RUN_E2E=1 ./scripts/run-tests.sh para incluir Playwright"
fi
