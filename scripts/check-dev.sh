#!/usr/bin/env bash
# Verifica pré-requisitos para desenvolvimento local WFRP Solo
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0
FAIL=0

ok() { echo "  ✓ $1"; PASS=$((PASS + 1)); }
bad() { echo "  ✗ $1"; FAIL=$((FAIL + 1)); }

echo "=== WFRP Solo — check-dev ==="
echo

echo "Python"
if command -v python3 >/dev/null 2>&1; then
  ok "python3 $(python3 --version 2>&1)"
else
  bad "python3 não encontrado"
fi

if [[ -d "$ROOT/backend/.venv" ]]; then
  ok "venv em backend/.venv"
else
  bad "venv ausente — rode: cd backend && python -m venv .venv && pip install -r requirements.txt"
fi

echo
echo "Node / Frontend"
if command -v node >/dev/null 2>&1; then
  ok "node $(node --version)"
else
  bad "node não encontrado"
fi
if [[ -d "$ROOT/frontend/node_modules" ]]; then
  ok "frontend/node_modules instalado"
else
  bad "npm install pendente em frontend/"
fi

echo
echo "Banco de dados"
ok "SQLite — arquivo local (sem dependência externa)"
if [[ -f "$ROOT/backend/wfrp_solo.db" ]]; then
  ok "backend/wfrp_solo.db existe"
else
  echo "  · wfrp_solo.db será criado na primeira subida do backend"
fi

echo
echo "LLM (opcional)"
if [[ -f "$ROOT/backend/.env" ]]; then
  if grep -qE '^LLM_PROVIDER=mock' "$ROOT/backend/.env" 2>/dev/null; then
    ok "LLM_PROVIDER=mock (testes locais)"
  elif grep -qE '^DEEPSEEK_API_KEY=.+.' "$ROOT/backend/.env" 2>/dev/null; then
    ok "DEEPSEEK_API_KEY configurada"
  elif grep -qE '^ANTHROPIC_API_KEY=.+.' "$ROOT/backend/.env" 2>/dev/null; then
    ok "ANTHROPIC_API_KEY configurada"
  else
    bad "sem chave LLM — use LLM_PROVIDER=mock ou configure DEEPSEEK_API_KEY"
  fi
else
  bad "backend/.env ausente — copie de .env.example"
fi

echo
echo "Backend health (se rodando)"
if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
  HEALTH=$(curl -s http://localhost:8000/health)
  ok "GET /health → $HEALTH"
else
  echo "  · backend não está em localhost:8000 (ok se ainda não iniciou)"
fi

echo
echo "Resultado: $PASS ok, $FAIL falha(s)"
[[ "$FAIL" -eq 0 ]] && exit 0 || exit 1
