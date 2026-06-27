# Tasks: expand-audio-mood-vocabulary

## Fase 1 — Frontend: audioManager

- [x] **T1** Estender `AudioCategory` e `TRACKS` com paths exatos dos 14 MP3 in-game (validados em `audio/`)
- [x] **T2** `horror`: `Horror.mp3` + `Horror 2.mp3` (pool sobrenatural); `horror_caos`: `Horror Chaos.mp3` + `Horror Chaos 2.mp3` (pool Caos; sem sorteio cruzado)
- [x] **T3** Adicionar `VOLUME` por categoria (menu 0.12, tensao 0.08, combate 0.09, demais 0.06–0.07)
- [x] **T4** Garantir que `play()` in-game categories respeitam `isInGameRoute` (mesma regra que `tensao` se aplicável) ou delegação só via `useAudioPlayer`

## Fase 2 — Frontend: useAudioPlayer + testes

- [x] **T5** Criar `MOOD_TO_CATEGORY` em `audioMoods.ts` mapeando os 8 moods in-game + `normal` → `stop()`
- [x] **T6** `setMood`: ignorar moods desconhecidos; bloquear in-game fora de `/play/` via `resolveMoodAction`
- [x] **T7** Testes: `horror` vs `horror_caos` carregam arquivos distintos
- [x] **T8** Testes: troca `combate` → `exploração`, idempotência, mood inválido, fora de `/play/`

## Fase 3 — Backend

- [x] **T9** Extrair `IN_GAME_MOODS` (constante) e expandir whitelist em `gm_orchestrator._handle_signal` MUSICA
- [x] **T10** Teste backend: sinais `horror`, `horror_caos`, `combate` propagam `scene_mood`; mood inválido ignorado

## Fase 4 — Prompt e documentação

- [x] **T11** Atualizar `Docs/gm-system-prompt.md` § Trilha Sonora: 9 moods, critérios, distinção `horror` / `horror_caos`, exemplos
- [x] **T12** Atualizar `Docs/audio-engine.md`: assets completos, tabela moods, remover §11 “planejado”
- [x] **T13** Atualizar `CHANGELOG.md` (Unreleased) e bullet no `README.md`

## Fase 5 — Build e validação manual

- [x] **T14** Rodar `npm run prepare:audio` + `npm run test:unit`; smoke `SoloRPG - Combat.mp3` no Dockerfile
- [ ] **T15** Validação manual em `/play/`: GM emite `combate`, `horror`, `horror_caos`, `normal`; mute; sticky entre turnos

## Dependências

- T1–T3 antes de T5–T8
- T9 antes de T10
- T5–T6 antes de T15
- T11–T12 podem paralelizar com T1–T10 após design aprovado
