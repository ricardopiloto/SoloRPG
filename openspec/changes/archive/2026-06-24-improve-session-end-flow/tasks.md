# Tasks: improve-session-end-flow

## 1. Frontend — `ChatLog.tsx`

- [x] 1.1 Adicionar novo kind ao tipo `ChatEntry`:
  ```ts
  | { kind: "session-end"; xp: number; playerSummary?: string; campaignId?: string; characterId?: string }
  ```
- [x] 1.2 No render do `ChatLog`, adicionar case para `entry.kind === "session-end"`:
  - Renderizado como banner com título "Sessão encerrada", XP ganho, dois botões via `Link`
  - Botão primário "Continuar campanha" → `/campaigns`
  - Botão secundário "Encerrar por hoje" → `/session/end`
  - Estilo: `max-w-prose my-8 mx-auto text-center border border-wfrp-border/60 rounded p-6 bg-wfrp-surface/60`
- [x] 1.3 Botões usam `Link` de `next/link` — sem dependência de props do pai

## 2. Frontend — `useSessionPlay.ts`

- [x] 2.1 Em `applyMeta`, quando `result.session_ended === true`:
  - **Removido** `router.push("/session/end")`
  - **Mantido** `sessionStorage.setItem("wfrp-recap", ...)` para que `/session/end` funcione quando o jogador navegar lá
  - **Adicionado** ao `setEntries`: `{ kind: "session-end", xp, playerSummary, campaignId, characterId }`
- [x] 2.2 `sessionEnded` derivado de `entries.some(e => e.kind === "session-end")` — exportado no retorno do hook
- [x] 2.3 `sessionEnded` exportado e usado para desabilitar o input

## 3. Frontend — `page.tsx`

- [x] 3.1 `sessionEnded` recebido do hook `useSessionPlay`
- [x] 3.2 Input e botão de submit: `disabled={loading || !!awaitingRoll || diceRolling || sessionEnded}`
- [x] 3.3 Hint: quando `sessionEnded` → `t("session.ended")`, caso contrário segue lógica anterior

## 4. Frontend — `pt-BR.json`

- [x] 4.1 `session.ended`: `"Sessão encerrada."`
- [x] 4.2 `session.endContinue`: `"Continuar campanha"`
- [x] 4.3 `session.endClose`: `"Encerrar por hoje"`
- [x] 4.4 `session.endBanner`: `"Sessão encerrada"`

## 5. Validação

- [x] 5.1 `npm run build` — zero erros TypeScript ✓
- [ ] 5.2 Teste manual: jogar até o GM emitir `[FIM_SESSAO]` — verificar que a última narrativa é lida normalmente antes do banner aparecer
- [ ] 5.3 Verificar que o input fica desabilitado após o banner aparecer
- [ ] 5.4 Clicar "Encerrar por hoje" — verificar que `/session/end` abre com resumo e XP corretos
- [ ] 5.5 Clicar "Continuar campanha" — verificar que redireciona para `/campaigns`
- [ ] 5.6 Verificar que o banner rola naturalmente com o chat (não flutua, não bloqueia conteúdo)
