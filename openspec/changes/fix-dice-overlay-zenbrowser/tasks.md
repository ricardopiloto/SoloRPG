# Tasks: fix-dice-overlay-zenbrowser

## 1. Assets e setup

- [x] 1.1 Adicionar script `prepare:dice` em `package.json`
- [x] 1.2 Documentar no README

## 2. Módulo diceBoxHost

- [x] 2.1 Criar `lib/dice/diceBoxHost.ts` com `ensureDiceBox`, wait for container size, singleton promise
- [x] 2.2 Config WFRP + `origin` explícito

## 3. DiceOverlay

- [x] 3.1 Refatorar para usar `ensureDiceBox` antes de roll
- [x] 3.2 Loading até init; fallback se falhar

## 4. CSS

- [x] 4.1 `#wfrp-dice-stage` dimensões mínimas estáveis

## 5. Validação

- [ ] 5.1 `npm run prepare:dice` + teste manual Zen Browser macOS
- [ ] 5.2 Primeiro roll após load da página não gera "not ready"
