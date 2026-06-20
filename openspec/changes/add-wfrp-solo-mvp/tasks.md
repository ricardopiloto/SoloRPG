# Tasks: WFRP Solo MVP

## 1. Fundação e Infraestrutura

- [x] 1.1 Inicializar monorepo ou repos: Next.js 14 (frontend) + FastAPI (backend)
- [x] 1.2 Configurar PostgreSQL + pgvector (Supabase) e migrations iniciais
- [x] 1.3 Configurar variáveis de ambiente (LLM API, Flux API, DATABASE_URL)
- [x] 1.4 Implementar adapter model-agnostic para LLM (Claude Sonnet 4 / DeepSeek V4)

## 2. Motor de Regras WFRP4e (`wfrp-rules-engine`)

- [x] 2.1 Implementar rolagem d100 e d10 server-side
- [x] 2.2 Implementar testes de atributo/perícia com níveis de sucesso/falha
- [x] 2.3 Implementar combate corpo a corpo e à distância (WS/BS, dano, redução)
- [x] 2.4 Implementar tabelas de Critical Hit e resolução de wounds
- [x] 2.5 Implementar Fate Points e Fortune Points (gasto e validação)
- [x] 2.6 Implementar morte permanente e transição de estado do personagem
- [x] 2.7 Implementar validação e concessão de XP sugerido pela LLM (30–100 por sessão)
- [x] 2.8 Implementar sistema de careers, avanços de perícias e talentos (WFRP4e)
- [x] 2.9 Escrever testes unitários para motor de regras

## 3. Gestão de Personagem (`character-management`)

- [x] 3.1 Criar schema e API de personagem (atributos, wounds, careers, perícias, talentos, trappings)
- [x] 3.2 Implementar criação customizada de personagem
- [x] 3.3 Implementar seleção de personagem pré-gerado
- [x] 3.4 Implementar ficha WFRP4e na UI (Fate Points visíveis)
- [x] 3.5 Implementar progressão entre sessões (compra de avanços com XP, sem LLM)
- [x] 3.6 Escrever testes de API e fluxo de progressão

## 4. Gestão de Campanha (`campaign-management`)

- [x] 4.1 Criar schema e API de campanhas (tom, objetivos secretos, estado do mundo, status)
- [x] 4.2 Implementar histórico de campanhas (ativas, concluídas, inacabadas por morte)
- [x] 4.3 Implementar fluxo de nova campanha (continuar personagem vs. novo personagem)
- [x] 4.4 Preservar campanhas inacabadas sem deleção
- [x] 4.5 Escrever testes de ciclo de vida de campanha

## 5. Memória Narrativa (`narrative-memory`)

- [x] 5.1 Criar schema relacional (NPCs, facções, eventos, sessões, resumos)
- [x] 5.2 Implementar embeddings e busca semântica com pgvector
- [x] 5.3 Implementar montagem de contexto por turno (4 camadas conforme design.md)
- [x] 5.4 Persistir resumo técnico de `[FIM_SESSAO]` e alimentar próximas sessões
- [x] 5.5 Escrever testes de recuperação semântica e montagem de contexto

## 6. GM Sintético (`synthetic-gm`)

- [x] 6.1 Integrar system prompt de `Docs/gm-system-prompt.md` como template injetável
- [x] 6.2 Implementar parser de sinais: `[TESTE]`, `[IMAGEM]`, `[FIM_SESSAO]`, `[NOVA_CAMPANHA]`, `[ACAO_SISTEMA]`, `[ESTADO_COMBATE]`
- [x] 6.3 Implementar loop de resolução: sinal → regras → resultado → LLM continua narrando
- [x] 6.4 Implementar geração de campanha na primeira sessão via `[NOVA_CAMPANHA]`
- [x] 6.5 Implementar rejeição narrativa para input fora de tom (sem meta-comentário)
- [x] 6.6 Implementar streaming de resposta LLM para o frontend
- [x] 6.7 Escrever testes de parsing de sinais e integração mock LLM

## 7. Orquestração de Sessão (`session-orchestration`)

- [x] 7.1 Implementar início de sessão com duração estimada informada ao jogador
- [x] 7.2 Implementar modo Exploração com timer visível (minutos)
- [x] 7.3 Implementar modo Combate com turnos, iniciativa server-side e contador visível
- [x] 7.4 Implementar encerramento de sessão (tempo esgotado ou sinal do backend) com ponto narrativo natural
- [x] 7.5 Implementar bloqueio de pausa durante sessão ativa
- [x] 7.6 Persistir histórico dos últimos K turnos da sessão ativa
- [x] 7.7 Escrever testes de transição de modos e encerramento

## 8. Camadas de Identidade (`identity-layers`)

- [x] 8.1 Implementar rastreamento interno de karma (-100..100) via deltas de `[FIM_SESSAO]`
- [x] 8.2 Implementar rastreamento de reputação por facção (-100..100)
- [x] 8.3 Implementar percepção social (texto descritivo injetado no contexto LLM)
- [x] 8.4 Implementar diário automático a partir de resumos de sessão (somente leitura)
- [x] 8.5 Garantir que karma/reputação/percepção não apareçam como números na UI
- [x] 8.6 Escrever testes de persistência e efeitos narrativos

## 9. Assets Visuais (`visual-assets`)

- [x] 9.1 Implementar fila assíncrona de geração de imagens via Flux 1.1 Pro
- [x] 9.2 Implementar placeholders temáticos enquanto imagem carrega
- [x] 9.3 Implementar cache de imagens por tipo de cena recorrente
- [x] 9.4 Implementar revelação progressiva de mapa (tipo "mapa" em `[IMAGEM]`)
- [x] 9.5 Implementar inventário visual vinculado aos trappings do personagem
- [x] 9.6 Escrever testes de fila e fallback de placeholder

## 10. Interface Web (`web-interface`)

- [x] 10.1 Implementar layout: chat central + painéis laterais (ficha, inventário, mapa, diário)
- [x] 10.2 Implementar input de texto livre como único meio de ação do jogador
- [x] 10.3 Implementar animação de rolagem de dados + resultado antes da narração LLM
- [x] 10.4 Implementar timer de sessão e contador de turno de combate
- [x] 10.5 Implementar tela de resumo de sessão e XP ao encerrar
- [x] 10.6 Implementar telas de gestão de campanhas e progressão de personagem
- [x] 10.7 Configurar PT-BR nativo com next-intl (i18n-ready)
- [x] 10.8 Testes E2E do loop principal: criar personagem → sessão → XP → progressão

## 11. Validação Final

- [ ] 11.1 Campanha completa de 3–5 sessões jogável sem contradições graves — ver `Docs/mvp-validation-checklist.md`
- [ ] 11.2 Revisar coerência narrativa e aderência ao system prompt
- [x] 11.3 Documentar setup local e deploy (Vercel + Railway/Fly.io + Supabase)
