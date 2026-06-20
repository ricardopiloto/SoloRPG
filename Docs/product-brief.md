# Product Brief — WFRP Solo

**Versão:** 1.1
**Data:** 2026-06-11
**Autor:** Ricardo (facilitado por Mary, PO Virtual)
**Status:** ✓ Completo — todas as questões fechadas

---

## 1. Problema

Jogadores de RPG de mesa frequentemente não conseguem jogar por falta de grupo, agenda incompatível ou ausência de um GM disponível. Os livros-jogo clássicos (Fighting Fantasy, Bandeirantes) resolveram parcialmente esse problema, mas são lineares, estáticos e sem memória — a experiência não cresce com o jogador.

Jogos digitais de RPG existentes ou são videogames com controle/mouse (que quebram a imersão narrativa) ou são chatbots de roleplay sem estrutura de sistema, sem progressão real e sem continuidade entre sessões.

**O gap:** Não existe uma experiência solo que combine a profundidade mecânica de um RPG de mesa, a imersão narrativa dos livros-jogo e a continuidade de uma campanha conduzida por um GM real.

---

## 2. Solução Proposta

Uma aplicação web onde Claude (LLM) atua como GM sintético — com agenda narrativa própria, memória persistente entre sessões e capacidade de conduzir campanhas completas baseadas no sistema WFRP4e (Warhammer Fantasy Roleplay 4ª edição).

O jogador interage exclusivamente via texto livre (como numa mesa de RPG real). A LLM narra, arbitra, reage e evolui a história com base nas decisões do jogador — sem revelar seus planos ou objetivos de campanha.

**LLM base (spec original):** Claude (único). Sem suporte a outros modelos no MVP.

**LLM base (implementação):** DeepSeek (`deepseek-chat`) via adapter model-agnostic. Ver `configure-deepseek-llm` e `Docs/README.md` §Decisões técnicas.

**Princípio central:** Para o jogador, deve ser irrelevante se o mestre é humano ou IA.

---

## 3. Usuário-Alvo

**Perfil primário:**
- Jogadores de RPG de mesa (especialmente WFRP, D&D, Pathfinder) sem grupo disponível
- Faixa etária: 20–40 anos
- Familiarizados com sistemas de RPG — não precisam de tutorial extenso
- Apreciam narrativa densa, mundo com lore rico e consequências reais

**Perfil secundário:**
- Leitores de livros-jogo clássicos que querem uma experiência mais dinâmica
- Curiosos sobre RPG que preferem experimentar solo antes de entrar num grupo

---

## 4. Casos de Uso Primários

1. **Iniciar uma campanha** — jogador cria ou escolhe um personagem, a LLM gera a campanha e conduz a primeira sessão
2. **Continuar uma campanha** — jogador retoma a história de onde parou, com o mesmo personagem e contexto preservado
3. **Encerrar e iniciar nova campanha** — após morte ou conclusão, jogador decide se continua com o mesmo personagem ou recomeça do zero
4. **Progressão entre sessões** — jogador gasta XP para evoluir o personagem fora das sessões ativas

---

## 5. Interface — Decisões de Design

### 5.1 Layout Geral

```
┌─────────────────────────────────────────────────────────────┐
│  SIDEBAR ESQUERDA     │     CHAT CENTRAL     │ SIDEBAR DIR. │
│  (stats personagem)   │   (narrativa + input)│  (diários)   │
│  Minimalista          │   Imersivo           │  Minimalista │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Chat Central — Princípios de Imersão

O chat é o coração da experiência. Deve parecer pessoal — o jogador sente que o que acontece ali está acontecendo *com ele* e com o personagem dele.

- Narrativa em segunda pessoa, tempo presente — sem distanciamento
- Sem elementos que "quebrem" o contexto do jogo (sem bordas de chat estilo aplicativo de mensagens, sem avatares de usuário, sem timestamps visíveis)
- Tipografia e espaçamento cuidadosos — leitura densa mas confortável
- Ilustrações de cena aparecem inline na narrativa, de forma orgânica
- O input do jogador é discreto — não compete visualmente com a narrativa

### 5.3 Sidebar Esquerda — Informações do Personagem

Exclusiva para dados do personagem. Estilo minimalista — sem decoração excessiva.

Conteúdo:
- Nome, raça, carreira e tier
- Atributos (WS, BS, S, T, I, Ag, Dex, Int, WP, Fel)
- Wounds (barra visual simples)
- Fate Points e Fortune Points
- Perícias e talentos (colapsável)
- Inventário visual (colapsável)
- Modo da sessão (EXPLORAÇÃO / COMBATE) + tempo restante

Princípio: números e estado. Sem narrativa aqui.

### 5.4 Sidebar Direita — Diários (Notas)

Exclusiva para registros narrativos automáticos. Estilo minimalista.

Conteúdo:
- Diário da campanha (log de eventos por sessão)
- Diário do personagem (perspectiva pessoal, gerado automaticamente)
- Outras notas futuras (mapa, reputação com facções — a definir)

Princípio: leitura e consulta. Sem interação mecânica aqui. Tudo gerado automaticamente pelo sistema — o jogador lê, não escreve.

---

## 6. Sistema de Testes — Fluxo de Interação

### 6.1 Princípio

Quando um teste é necessário, o jogador deve *escolher* fazê-lo e *executá-lo* ativamente. Não é algo que acontece automaticamente — é um momento de agência e tensão.

### 6.2 Fluxo

1. **GM apresenta a situação** com duas ou mais opções claras (ex: "Você pode enfrentar o inimigo ou fugir pela escada — mas a descida será arriscada.")
2. **O sistema apresenta o teste** como um elemento de UI destacado no chat:
   - Nome do teste (ex: "Teste de Agilidade")
   - Atributo e valor atual do personagem
   - Modificador situacional e dificuldade
   - Botão: **"Rolar dado"**
3. **O jogador clica em "Rolar dado"** — a animação do d100 acontece na tela
4. **O resultado aparece** — valor rolado, valor alvo, sucesso/falha e SL
5. **O GM narra a consequência** com base no resultado recebido do backend

### 6.3 Princípios do Momento do Teste

- O jogador nunca é forçado a rolar sem escolha — ele pode optar pelo caminho alternativo
- A animação do dado é visível e satisfatória — é um momento de tensão real
- O resultado é transparente: o jogador vê o que rolou, o alvo, e se passou ou falou
- O GM narra *depois* do resultado — nunca antes

---

## 7. Funcionalidades do MVP

### 7.1 GM Sintético (Claude)
- Geração de campanha na primeira sessão (cenário, tom, objetivos secretos, NPCs iniciais)
- Condução de sessões via texto livre — sem opções pré-definidas
- Aviso de duração estimada antes de cada sessão; sessões pausáveis (pausa e retomada a qualquer momento)
- Geração de resumo narrativo e XP ao fim de cada sessão
- Memória persistente: banco de dados com eventos, decisões, NPCs, estado do mundo

### 7.2 Personagem
- Criação customizada (atributos, career inicial, background) OU seleção de personagem pré-gerado
- Ficha baseada em WFRP4e: atributos, wounds, careers, perícias, talentos, Fate Points
- Progressão: compra de perícias e talentos com XP entre sessões
- Morte permanente quando Fate Points se esgotam

### 7.3 Camadas de Identidade (internas — nunca exibidas como números)
- Karma: eixo moral que influencia o comportamento do mundo
- Reputação com facções: rastreada silenciosamente, revelada via reações narrativas
- Percepção social: como NPCs enxergam o personagem — expresso apenas em comportamento

### 7.4 Elementos Visuais
- Ilustrações de cenas geradas on-demand via Cloudflare Workers AI / FLUX.1 Schnell (assíncrono)
- Mapa revelável gerado pela LLM
- Inventário visual
- Diário automático (campanha + personagem)
- Animação de dado (d100) no momento dos testes

### 7.5 Gestão de Campanhas
- Histórico de campanhas (ativas, concluídas, inacabadas por morte)
- Campanhas inacabadas preservadas — não deletadas
- Ao iniciar nova campanha: manter personagem ou gerar novo

---

## 8. Fora do Escopo (MVP)

- Multiplayer ou co-op
- Controles de videogame (mouse/teclado como input de ação)
- Sistema de insanidade/corrupção do WFRP4e
- Monetização
- App mobile nativo
- Modos de dificuldade configuráveis pelo jogador
- Fate Points não se regeneram entre campanhas no MVP

---

## 9. Questões — Todas Fechadas ✓

- [x] O jogador vê os dados sendo rolados? → Sim. Animação de d100 visível, resultado transparente.
- [x] O jogador escolhe quando rolar? → Sim. Teste aparece como elemento de UI com botão "Rolar dado".
- [x] LLM base? → Claude (único no MVP).
- [x] Imagens? → Geração on-demand assíncrona via Cloudflare Workers AI (FLUX.1 Schnell).
- [x] Fate Points visíveis? → Sim, na sidebar esquerda.
- [x] Limite de sessão? → Tempo (exploração) + turnos (combate).
- [x] Idioma? → PT-BR nativo, arquitetura i18n preparada.
- [x] Layout? → Sidebar esquerda (stats) + chat central (imersivo) + sidebar direita (diários).
- [x] Diário? → Automático, gerado pelo sistema. Jogador lê, não escreve.
- [x] Karma e reputação visíveis? → Não. Apenas efeitos narrativos.
- [x] Como tratar input disruptivo? → Rejeição narrativa pelo GM — sem meta-comentário.
- [x] Fate Points entre campanhas? → Não se regeneram no MVP.
- [x] Mapa? → Gerado pela LLM, revelado progressivamente.

---

## 10. Próximos Passos

Ver [Ordem de desenvolvimento](development-order.md) para a sequência completa e [Frontend vs Backend](frontend-backend-split.md) para divisão de responsabilidades.

| # | Entrega | Status |
|---|---------|--------|
| 1 | System prompt do GM | ✓ Concluído — [`gm-system-prompt.md`](gm-system-prompt.md) |
| 2 | Motor de regras WFRP4e | ✓ Core — `backend/app/rules/` + testes unitários |
| 3 | Esquema do banco + memória | ✓ sqlite-dev/postgres; memória semântica + diário/karma |
| 4 | Loop de sessão + DeepSeek | ✓ Adapter DeepSeek; test-block; combate; mock para testes |
| 5 | Frontend imersivo | ✓ Protótipo OD; quick-roll; Workers AI para imagens |
| 6 | Qualidade MVP | ✓ pytest API + Playwright E2E + README; checklist manual em [`mvp-validation-checklist.md`](mvp-validation-checklist.md) |

**Fase atual:** Fase 6 concluída em [development-order.md](development-order.md). Próximo passo opcional: arquivar changes OpenSpec e validar campanha real com DeepSeek (checklist acima).
