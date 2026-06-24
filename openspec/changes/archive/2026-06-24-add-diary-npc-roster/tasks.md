# Tasks: add-diary-npc-roster

## 1. Backend — modelo e persistência

- [x] 1.1 Adicionar `known_name` e `met_location` ao model `NPC`
- [x] 1.2 `apply_nova_campanha`: set `met_location` = `opening_location` nos NPCs iniciais
- [x] 1.3 `persist_session_summary`: processar `nome_conhecido` e `local` em `npcs_interagidos`
- [x] 1.4 Documentar campos opcionais em `Docs/gm-system-prompt.md` (exemplo JSON)

## 2. Backend — API e testes

- [x] 2.1 `GET /campaigns/{campaign_id}/npcs` com schema Pydantic
- [x] 2.2 Teste: NPC inicial tem `met_location`; NPC de fim de sessão atualiza local/nome

## 3. Frontend — API e hook

- [x] 3.1 Tipo `CampaignNpc` + `api.listCampaignNpcs()`
- [x] 3.2 `useSessionPlay`: state `knownNpcs`, fetch junto com diary

## 4. Frontend — DiarySidebar

- [x] 4.1 Prop `knownNpcs` em `DiarySidebar`
- [x] 4.2 Aba Personagem: roster com nome conhecido + local (+ papel muted)
- [x] 4.3 Empty state i18n PT-BR
- [x] 4.4 `play/[sessionId]/page.tsx`: passar `knownNpcs`

## 5. Validação

- [x] 5.1 `npm run build` + `pytest` relevantes
- [ ] 5.2 Manual: campanha nova → aba Personagem lista NPCs da abertura com local
- [ ] 5.3 Manual: após sessão com novo NPC, roster atualiza nome/local

## 6. Dev sqlite

- [x] 6.1 Documentar no README ou task note: recriar DB se colunas não aparecerem
