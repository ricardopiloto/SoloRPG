# Technical Research — WFRP Solo

**Versão:** 1.1
**Data:** 2026-06-11
**Status:** ✓ Completo

---

## 1. Arquitetura Geral

```
[Browser]
   │ texto livre + clique em "Rolar dado"
   ▼
[Frontend — Next.js + Tailwind]
   ├── Chat central (narrativa imersiva)
   ├── Sidebar esquerda (stats do personagem)
   ├── Sidebar direita (diários)
   └── Componente de dado (animação d100)
         │ REST / WebSocket
         ▼
[Backend — FastAPI / Python]  ← implementado (spec original: Node.js)
   ├── Orquestrador de sessão
   ├── Motor de regras WFRP4e (dados, wounds, XP) ✓
   └── Gerenciador de memória narrativa
         │
         ├──► [PostgreSQL / SQLite-dev — Supabase prod]
         │     Personagem, campanha, sessões, XP, inventário
         │
         ├──► [pgvector — Supabase]
         │     Memória semântica: eventos, NPCs, decisões
         │
         └──► [LLM API — DeepSeek / Claude / mock]
               System prompt de GM + contexto comprimido
```

### Princípio de separação de responsabilidades

- **Regras do sistema** (dados, wounds, careers, XP) → código determinístico ✓
- **Narrativa e mundo** → Claude com contexto estruturado
- **Memória de campanha** → banco de dados, não context window

---

## 2. LLM Base

**Spec original:** Claude (único). Sem suporte a outros modelos no MVP.

**Implementação atual:** Adapter model-agnostic com `LLM_PROVIDER` (`mock`, `anthropic`, `deepseek`). Default de desenvolvimento: **DeepSeek** (`deepseek-chat`). Ver `configure-deepseek-llm`.

Justificativa original (Claude): melhor aderência a system prompts complexos. DeepSeek adotado na implementação por custo e disponibilidade, mantendo o adapter para trocar provedor sem refactor.

---

## 3. Memória Persistente — Estratégia em Camadas

O problema central: Claude não tem memória entre chamadas. O histórico completo de campanhas longas não cabe na context window.

### Camada 1 — Fatos Estruturados (PostgreSQL)
```
campaigns      → id, tom, objetivo_secreto, estado_mundo, fase_atual
sessions       → id, campaign_id, resumo, xp_concedido, data
npcs           → id, campaign_id, nome, faccao, relacao, status
events         → id, session_id, tipo, descricao, consequencias
player_characters → atributos, wounds, fate_points, karma, reputacao
```

### Camada 2 — Memória Semântica (pgvector)
Eventos em embeddings, buscados por relevância a cada turno:
- "O jogador traiu a Guilda dos Comerciantes na sessão 3"
- "Aldric, o ferreiro, deve um favor ao personagem"

### Camada 3 — Resumo Comprimido (gerado pela LLM)
Ao fim de cada sessão, Claude gera dois resumos:
1. Narrativo (visível ao jogador — diário)
2. Técnico (invisível — alimenta sessões futuras)

### Camada 4 — Context Window da Sessão Ativa
Injetado a cada turno: `<campanha>` + `<personagem>` + `<memoria>` + `<sessao>` + últimos K turnos.

---

## 4. Fluxo de Teste — Backend

O teste é iniciado pelo jogador (clique em "Rolar dado"), não automaticamente.

```
1. Claude emite sinal [TESTE] com atributo, modificador e consequências
2. Backend intercepta o sinal — NÃO repassa à LLM ainda
3. Frontend exibe componente de teste:
   - Nome do teste, atributo, valor atual, modificador
   - Botão "Rolar dado"
4. Jogador clica → frontend solicita rolagem ao backend
5. Backend rola d100 (server-side)
6. Frontend exibe animação do dado + resultado
7. Backend retorna resultado para Claude narrar consequência
8. Claude narra — nunca antes do resultado
```

**Regra crítica:** Claude nunca inventa resultado de dado. Sempre emite [TESTE], aguarda o backend processar, recebe o resultado, então narra.

---

## 5. Dois Modos de Sessão

```
MODO EXPLORAÇÃO              MODO COMBATE
────────────────────         ──────────────────────
Timer visível                Contador de turno
Texto livre                  Texto livre
LLM calibra ritmo            Backend resolve, LLM narra
Testes aparecem como UI      Testes aparecem como UI
Animação de dado             Animação de dado
```

O backend sinaliza o modo ativo via `<sessao><modo>`. A LLM muda comportamento conforme o modo.

---

## 6. Geração de Imagens

- **Serviço:** Cloudflare Workers AI (FLUX.1 Schnell)
- **Trigger:** sinal `[IMAGEM]` emitido pela LLM
- **Comportamento:** assíncrono — não bloqueia a narrativa
- **Exibição:** inline no chat, carrega em background com placeholder temático
- **Cache:** imagens de cenas recorrentes reutilizadas (taverna, floresta, etc.)
- **Estilo fixo:** sempre inclui "estética Warhammer Fantasy sombria, pintura a óleo detalhada, iluminação dramática"

---

## 7. Interface — Decisões Técnicas

### Chat Central
- Sem estilo de "aplicativo de mensagens" (sem avatares, sem timestamps visíveis, sem bolhas)
- Tipografia imersiva — fonte serifada para narrativa, sem-serifa para UI
- Ilustrações aparecem inline entre parágrafos
- Input discreto na base da tela

### Sidebar Esquerda (stats)
- Minimalista — dados puros, sem decoração
- Wounds como barra visual simples
- Fate/Fortune Points como ícones contáveis
- Seções colapsáveis: perícias, talentos, inventário
- Indicador de modo (EXPLORAÇÃO/COMBATE) + timer

### Sidebar Direita (diários)
- Minimalista — leitura limpa
- Diário da campanha: log por sessão
- Diário do personagem: perspectiva narrativa gerada automaticamente
- Somente leitura — jogador consulta, não edita

### Componente de Dado
- Aparece inline no chat quando [TESTE] é emitido
- Mostra: nome do teste, atributo + valor, modificador, dificuldade
- Botão "Rolar dado" — clique do jogador dispara a rolagem
- Animação do d100 rolando (CSS/JS)
- Resultado: valor rolado, alvo final, SL, sucesso/falha
- Após resultado: Claude narra a consequência

---

## 8. Stack

| Camada | Tecnologia | Justificativa |
|--------|-----------|--------------|
| Frontend | Next.js 14 + Tailwind | SSR + API routes integradas |
| Backend | Node.js | Motor de regras já em JS ✓ |
| Banco principal | PostgreSQL (Supabase) | Gerenciado, gratuito no MVP |
| Banco vetorial | pgvector (Supabase) | Memória semântica no mesmo banco |
| LLM | Claude (Anthropic API) | Base única no MVP |
| Imagens | Cloudflare Workers AI (FLUX.1 Schnell) | Qualidade/custo para fantasy sombrio |
| Deploy frontend | Vercel | Integração nativa com Next.js |
| Deploy backend | Railway ou Fly.io | Custo baixo para MVP |

**Custo estimado de infraestrutura:** ~$0–20/mês (tokens Claude à parte, ~$0.05–0.15/sessão)

---

## 9. Riscos e Mitigações

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Claude perde coerência em campanhas longas | Alto | Memória em camadas — não depende da context window |
| Claude quebra persona de GM | Alto | System prompt rígido ✓ + rejeição narrativa (sem meta-comentário) |
| Latência alta por turno | Médio | Streaming de resposta — jogador vê texto sendo gerado |
| Custo de tokens escala mal | Médio | Compressão agressiva de contexto entre sessões |
| Animação de dado parece trivial | Baixo | Componente com peso visual — momento de tensão real |

---

## 10. Sequência de Desenvolvimento

| Fase | Entregas | Status |
|------|---------|--------|
| 1 — Fundação | System prompt do GM | ✓ Concluído |
| 1 — Fundação | Motor de regras WFRP4e (28/28 testes) | ✓ Concluído |
| 2 — Persistência | Esquema do banco de dados | ⬜ Próximo |
| 3 — Loop de sessão | Backend + integração Claude | ⬜ A fazer |
| 4 — Frontend | Chat imersivo, sidebars, dado animado | ⬜ A fazer |
| 5 — Imersão | Cloudflare Workers AI (FLUX.1 Schnell) assíncrono, mapa, diários | ✓ |

---

## 11. Dados 3D — Stack Técnica

### Biblioteca

**`@3d-dice/dice-box`** — Three.js + cannon-es + física real.
Mesma base do Dice So Nice (Foundry VTT). Suporte oficial a React/Next.js.

```bash
npm install @3d-dice/dice-box
# Copiar assets para /public/assets/dice-box/
```

### Princípio de integridade

O resultado do dado vem SEMPRE do backend (server-side). A animação 3D recebe o número real via `roll('1d100', { value: resultado })` — nunca gera o número visualmente.

### Integração Next.js

- `useDiceBox.ts`: hook que inicializa o DiceBox com `'use client'`, guarda instância em ref
- `DiceOverlay.tsx`: canvas fixo sobre o chat, `pointer-events: none` durante animação
- Resultado: backend → animação → chat → Claude

### Configuração tema Warhammer

```javascript
themeColor: '#C9973A'  // dourado
scale: 8               // dado grande
gravity: 2
throwForce: 6
```

### Quick Roll — Itens clicáveis da sidebar

Perícias, atributos e armas/escudos são clicáveis. Ao clicar:
1. Popover de modificador (2s timeout → rola com 0)
2. POST /dice/roll ao backend
3. Animação 3D com resultado real
4. Resultado injetado no chat como mensagem de sistema
5. Claude pode incorporar narrativamente

**Não clicáveis:** itens de inventário sem rolagem (consumíveis, equipamento geral)
