# Design: WFRP Solo MVP

## Context

WFRP Solo é uma aplicação web de RPG solo onde uma LLM atua como GM com agenda narrativa própria, memória persistente e campanhas completas baseadas em WFRP4e. O jogador interage exclusivamente via texto livre. O princípio central é que, para o jogador, deve ser irrelevante se o mestre é humano ou IA.

Restrições do MVP:
- Idioma nativo PT-BR, arquitetura preparada para i18n futuro
- Sessões não pausáveis; duração estimada informada antes de cada sessão
- Morte permanente quando Fate Points se esgotam
- Insanidade/corrupção WFRP4e fora do escopo
- Projeto pessoal — métricas qualitativas, não escala comercial

## Goals / Non-Goals

**Goals:**
- Loop completo: criar personagem → iniciar campanha → jogar sessões → ganhar XP → progredir → continuar ou encerrar campanha
- Regras WFRP4e determinísticas no backend; LLM nunca rola dados nem calcula wounds
- Memória em camadas (relacional + vetorial + resumos comprimidos + histórico da sessão ativa)
- Protocolo de sinais estruturados entre LLM e backend
- Interface imersiva sem controles de videogame; elementos visuais como apoio

**Non-Goals:**
- Multiplayer ou co-op
- Controles de ação via mouse/teclado (além de digitar texto)
- Sistema de insanidade/corrupção
- Monetização
- App mobile nativo
- Modos de dificuldade configuráveis pelo jogador

## Decisions

### 1. Separação LLM vs Backend

- **Decision:** A LLM narra, arbitra narrativamente e emite sinais JSON; o backend executa rolagens, aplica regras, persiste estado e monta contexto.
- **Rationale:** Evita alucinação mecânica e manipulação de dados pelo jogador.
- **Alternatives:** Delegar regras à LLM — rejeitado por inconsistência e falta de auditabilidade.

### 2. Protocolo de Sinais

- **Decision:** Tags delimitadas (`[TESTE]`, `[IMAGEM]`, `[FIM_SESSAO]`, `[NOVA_CAMPANHA]`, `[ACAO_SISTEMA]`, `[ESTADO_COMBATE]`) com payload JSON conforme `Docs/gm-system-prompt.md`.
- **Rationale:** Parsing determinístico; contrato testável entre prompt e código.

### 3. Memória em Quatro Camadas

| Camada | Armazenamento | Conteúdo |
|--------|---------------|----------|
| 1 — Fatos estruturados | PostgreSQL | Campanha, personagem, NPCs, facções, eventos, sessões |
| 2 — Memória semântica | pgvector | Embeddings de eventos/decisões; busca por relevância + filtros (campaign_id, recência) |
| 3 — Resumo comprimido | PostgreSQL (campo texto) | Resumo técnico de sessão gerado pela LLM em `[FIM_SESSAO]` |
| 4 — Context window ativa | Montagem em runtime | System prompt + resumos + eventos recuperados + estado personagem + últimos K turnos |

### 4. Stack

- **Frontend:** Next.js 14 (App Router), TailwindCSS, shadcn/ui, next-intl (i18n-ready)
- **Backend:** Python + FastAPI (preferido para ecossistema de embeddings) ou Node + Fastify
- **Banco:** PostgreSQL + pgvector (Supabase no MVP)
- **LLM:** Claude Sonnet 4 (dev); DeepSeek V4 Pro/Flash (produção); adapter model-agnostic
- **Imagens:** Flux 1.1 Pro, geração assíncrona em background; placeholder temático enquanto carrega

### 5. Modos de Sessão

- **Exploração (padrão):** timer em minutos visível; texto livre; LLM calibra ritmo ao tempo restante
- **Combate:** backend controla iniciativa e turnos; contador de turno visível; `[ESTADO_COMBATE]` a cada turno

### 6. Sequência de Resolução de Teste

```
Jogador envia ação → LLM emite [TESTE] → Backend rola d100 → UI anima resultado → Backend envia resultado à LLM → LLM narra consequência
```

### 7. Camadas de Identidade

- Karma, reputação e percepção social: valores internos (-100..100); **nunca** exibidos como números na UI
- Diário: gerado automaticamente a partir de resumos de sessão; somente leitura
- Fate Points: visíveis na ficha como recurso finito

### 8. Campanhas e Morte

- Campanhas inacabadas por morte são preservadas (não deletadas)
- Fate Points **não** recarregam entre campanhas no MVP
- Nova campanha: continuar personagem existente ou criar novo

## Risks / Trade-offs

| Risco | Mitigação |
|-------|-----------|
| LLM perde contexto em campanhas longas | Memória em camadas; busca semântica; resumos comprimidos |
| LLM quebra persona de GM | System prompt rígido; rejeição narrativa (nunca meta-comentário) para input fora de tom |
| Latência 5–15s/turno | Streaming de resposta LLM; imagens assíncronas |
| Custo de tokens | Compressão agressiva; modelo mais barato em produção |
| Sessão não pausável frustra jogador | Aviso preciso de duração; encerramento em ponto narrativo natural |

## Migration Plan

Greenfield — sem migração de dados existentes. Implementação em 4 fases (ver `tasks.md`).

## Open Questions

- Nenhuma questão bloqueante para o MVP — todas as decisões relevantes estão fechadas em `Docs/product-brief.md` seção 9.
