# Tasks: fix-dice-production-standalone

## Fase 1 — Fix imediato: `clear()` defensivo

- [x] **T1** Atualizar tipo `DiceBoxInstance.clear()` em `frontend/src/types/dice-box.d.ts` de `Promise<void>` para `void | Promise<void>`
- [x] **T2** Extrair helper `safeClear(box)` em `diceBoxHost.ts` + atualizar tipo local `DiceBoxInstance.clear()` para `void | Promise<void>`
- [x] **T3** Substituir todas as chamadas `box.clear().catch(...)` em `DiceOverlay.tsx` pelo helper `safeClear`
- [ ] **T4** Validar: no ambiente local, rodar 3 sequências de roll → fechar overlay → roll novamente sem TypeError no console *(validação manual)*

## Fase 2 — WASM em produção: headers Caddy

- [x] **T5** Headers COOP/COEP adicionados via `next.config.js` (bloco `headers()` em todas as rotas `/(.*)`); snippet Caddy documentado em `debian-server-install.md`
- [x] **T6** Header `Content-Type: application/wasm` para `*.wasm` documentado em `debian-server-install.md` com snippet Caddy e comando curl de verificação
- [ ] **T7** Recarregar Caddy no servidor e verificar MIME type com `curl -I` *(validação manual no servidor)*
- [ ] **T8** Verificar que COOP/COEP não quebra login, chat ou outras partes da UI *(validação manual após deploy)*

## Fase 3 — Robustez de build e fallback UI

- [x] **T9** `RUN test -f public/assets/dice-box/assets/ammo/ammo.wasm.wasm` adicionado ao `frontend/Dockerfile` com mensagem de erro clara; build falha cedo se assets ausentes
- [x] **T10** Estado `diceUnavailable` adicionado ao `DiceOverlay`; quando `ensureDiceBox` retorna `null`, exibe "Dados físicos indisponíveis — usando resultado numérico" no lugar do spinner
- [x] **T11** Subseção "Dados 3D não aparecem" adicionada à seção 11 de `Docs/debian-server-install.md` cobrindo MIME type, COOP/COEP e assets ausentes

## Fase 4 — Validação em produção

- [ ] **T12** Rebuild e push da imagem frontend: `docker compose build frontend && docker compose up -d frontend`
- [ ] **T13** Abrir `solorpg.1nodado.com.br`, iniciar sessão, disparar roll — verificar que dados 3D aparecem e que console não tem erros `colliderFaceMap` ou `clear().catch`
- [ ] **T14** Verificar fallback: temporariamente bloquear `ammo.wasm.wasm` via DevTools → confirmar que mensagem de fallback aparece e roll numérico é emitido

## Dependências

- T2 antes de T3 ✓
- T9 valida resultado de T12 em CI futuro
- T14 depende de T10 ✓
