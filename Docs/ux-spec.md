# UI/UX Specification — WFRP Solo
**Versão:** 1.0
**Data:** 2026-06-13
**Método:** BMAD UX Spec (DESIGN.md + EXPERIENCE.md combinados)
**Status:** Referência para implementação do frontend

---

## PARTE 1 — DESIGN.md (Visual)

### 1.1 Identidade Visual

**Conceito:** O Velho Mundo em papel envelhecido. A interface deve parecer um grimório interativo — texto denso, tipografia com peso, tons de tinta sobre pergaminho escuro. Nada que grite "aplicativo moderno".

**Referências visuais:** Manuscritos medievais, mapas de pergaminho, livros de RPG impressos dos anos 80/90, iluminuras góticas.

### 1.2 Paleta de Cores

```
Background principal:    #0D0B08   (preto quase marrom — tinta sobre couro)
Background secundário:   #1A1612   (painéis/sidebars)
Background terciário:    #241E17   (cards, inputs)
Texto primário:          #E8DCC8   (pergaminho claro)
Texto secundário:        #9E8E72   (anotações, labels)
Texto terciário:         #5C5040   (placeholders, desabilitado)
Dourado (destaque):      #C9973A   (bordas especiais, ícones ativos, XP)
Vermelho sangue:         #8B1A1A   (ferimentos, perigo, morte)
Verde musgo:             #3A5C2E   (sucesso, cura)
Azul noite:              #1E2D4A   (modo combate, magia)
Branco osso:             #F0E6D0   (texto em destaque narrativo)
```

### 1.3 Tipografia

```
Narrativa (chat):        "Crimson Text" ou "EB Garamond" — serifada, 17px, line-height 1.8
UI / Labels:             "Inter" ou "Source Sans 3" — sem-serifa, 13px
Títulos de seção:        "Cinzel" — serifada estilo romano, 14px, letter-spacing 0.08em
Código / dados:          "JetBrains Mono" — 12px (para stats)
Dado (animação):         "MedievalSharp" ou similar — display only
```

### 1.4 Layout Geral

```
┌──────────────────────────────────────────────────────────────────────┐
│  SIDEBAR ESQUERDA (280px)  │  CHAT CENTRAL (flex)  │  SIDEBAR DIR. (260px)  │
│  Stats do personagem       │  Narrativa + input    │  Diários               │
│  Minimalista               │  Imersivo             │  Minimalista           │
└──────────────────────────────────────────────────────────────────────┘
```

Breakpoints:
- Desktop: layout de 3 colunas completo
- Tablet (< 1024px): sidebar direita colapsada em drawer
- Mobile: fora do escopo MVP

### 1.5 Sidebar Esquerda — Ficha do Personagem

**Princípio:** Dados puros. Sem decoração excessiva. Como uma ficha de personagem preenchida à mão.

Estrutura (de cima para baixo):
```
┌─────────────────────────────┐
│ [Nome]           [Carreira] │  ← linha de identidade
│ [Raça]           [Tier X]   │
├─────────────────────────────┤
│ FERIMENTOS                  │  ← barra visual simples
│ ████████░░  8/12            │  vermelho quando baixo
├─────────────────────────────┤
│ DESTINO  ◆◆◆◇   FORTUNA ◆◆ │  ← ícones de losango
├─────────────────────────────┤
│ ATRIBUTOS              [▼]  │  ← colapsável
│  WS 35  BS 30  S 30  T 35  │
│  I 35   Ag 30  Dex 25      │
│  Int 30  WP 30  Fel 25     │
├─────────────────────────────┤
│ PERÍCIAS               [▼]  │  ← colapsável
│  Escalar (S) +3            │
│  Furtividade (Ag) +5       │
├─────────────────────────────┤
│ TALENTOS               [▼]  │  ← colapsável
│  Golpe Poderoso            │
├─────────────────────────────┤
│ INVENTÁRIO             [▼]  │  ← colapsável
│  🗡 Espada Longa  (Enc 2)   │
│  🛡 Escudo        (Enc 1)   │
├─────────────────────────────┤
│ XP: 150 disponível          │  ← sempre visível
├─────────────────────────────┤
│ 🗺 EXPLORAÇÃO   ⏱ 32 min    │  ← modo + timer
└─────────────────────────────┘
```

Bordas: linha fina `#2E2820`, sem sombras. Separadores horizontais sutis.

### 1.6 Chat Central — Narrativa

**Princípio:** Não parece um chat. Parece um livro interativo. Sem bolhas, sem avatares, sem timestamps.

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  [ILUSTRAÇÃO DE CENA — quando presente]                     │
│  Imagem inline, largura total, altura ~240px                │
│  Fade suave nas bordas                                      │
│                                                             │
│  O cheiro chega antes da luz — peixe podre, alcatrão e     │
│  algo que você já aprendeu a reconhecer como medo de        │
│  multidão.                                                  │
│                                                             │
│  O porto de Marienburg acorda com barulho. Estivadores      │
│  gritam em três idiomas diferentes. [...]                   │
│                                                             │
│  ─────────────────────────────────────────────────────      │
│  [COMPONENTE DE TESTE — quando emitido]                     │
│  ┌─────────────────────────────────────────────────┐        │
│  │ 🎲 TESTE DE AGILIDADE                           │        │
│  │  Valor: 30 + 5 (Escalar) = 35                  │        │
│  │  Modificador: -10 (superfície molhada)          │        │
│  │  Alvo final: 25                                 │        │
│  │                                                 │        │
│  │  Fugir pela escada ou enfrentar o inimigo?      │        │
│  │  ┌──────────────┐  ┌──────────────────────┐    │        │
│  │  │ 🎲 Rolar dado│  │ Enfrentar o inimigo  │    │        │
│  │  └──────────────┘  └──────────────────────┘    │        │
│  └─────────────────────────────────────────────────┘        │
│  ─────────────────────────────────────────────────────      │
│                                                             │
│  [INPUT DO JOGADOR]                                         │
│  ┌─────────────────────────────────────── [Enviar ▶] ─┐    │
│  │ O que você faz?                                     │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

Input:
- Placeholder: "O que você faz?" — nunca muda
- Sem botão de "Send" proeminente — ícone discreto ou Enter
- Sem contador de caracteres
- Sem indicadores de "digitando..."

### 1.7 Componente de Teste (Dado)

Estados sequenciais:

**Estado 1 — Aguardando escolha:**
```
┌─────────────────────────────────────────┐
│ 🎲  TESTE DE AGILIDADE                  │
│     Atributo: 30  Perícia: +5  = 35     │
│     Modificador: -10 (superfície molhada)│
│     ALVO: 25                            │
│                                         │
│  [🎲 Rolar dado]    [Outra opção]       │
└─────────────────────────────────────────┘
```

**Estado 2 — Animação (500ms):**
```
┌─────────────────────────────────────────┐
│ 🎲  TESTE DE AGILIDADE                  │
│                                         │
│         ⚄  →  ⚂  →  ⚅  →  ⚁           │  ← animação CSS
│              rolando...                 │
└─────────────────────────────────────────┘
```

**Estado 3 — Resultado:**
```
┌─────────────────────────────────────────┐
│ ✓  SUCESSO — AGILIDADE                  │  ← verde ou vermelho
│                                         │
│     Rolou: 18    Alvo: 25              │
│     SL: +0  (margem pequena)           │
│                                         │
│  "Você consegue descer a escada com     │
│   os pés molhados, mas chega ao térreo  │
│   no último segundo..."                 │
└─────────────────────────────────────────┘
```

### 1.8 Sidebar Direita — Diários

**Princípio:** Apenas leitura. Como um diário físico aberto ao lado.

```
┌──────────────────────────┐
│  DIÁRIOS          [tabs] │
│  [Campanha] [Personagem] │
├──────────────────────────┤
│                          │
│  Sessão 3                │
│  ──────────────          │
│  Você descobriu que      │
│  Aldric Voss frequenta   │
│  o Ganso Cego às terças. │
│  A Guilda desconfia de   │
│  suas movimentações...   │
│                          │
│  Sessão 2                │
│  ──────────────          │
│  [...]                   │
│                          │
└──────────────────────────┘
```

Sem bordas de "card". Texto fluido, como página de diário.

---

## PARTE 2 — EXPERIENCE.md (Comportamental)

### 2.1 Fluxo de Entrada

```
Usuário abre o app
  → Se não tem personagem: tela de criação / seleção de pré-gerado
  → Se tem campanha ativa: vai direto para o chat
  → Se campanha encerrada: tela de conclusão + opção de nova campanha
```

### 2.2 Início de Sessão

1. LLM calcula duração estimada e exibe antes de começar:
   > *"Esta sessão terá aproximadamente 45 minutos. Uma vez iniciada, não será possível pausar. Deseja começar?"*
2. Jogador confirma → sessão inicia → timer começa
3. LLM narra a abertura de cena (sem introduções meta)
4. Ilustração de cena carrega em background (assíncrona)

### 2.3 Fluxo de Turno Normal (Exploração)

```
Jogador digita ação
→ Backend envia para Claude (streaming)
→ Texto narrativo aparece progressivamente (streaming)
→ Se [IMAGEM]: Cloudflare Workers AI gera em background (não bloqueia)
→ Se [TESTE]: componente de dado aparece inline (bloqueia narração)
→ Jogador lê e digita próxima ação
```

### 2.4 Fluxo de Teste

```
Claude emite [TESTE] → backend intercepta
→ Componente aparece no chat
→ Jogador vê as opções (rolar ou alternativa)
→ Se rolar: animação do d100 (500ms)
→ Resultado aparece: rolagem, alvo, SL, sucesso/falha
→ Backend retorna resultado para Claude
→ Claude narra consequência (streaming)
→ Componente fecha (resultado fica visível no histórico)
```

### 2.5 Fluxo de Combate

```
Claude sinaliza início de combate → backend muda modo para COMBATE
→ Sidebar esquerda: modo muda para "⚔ COMBATE | Turno 1"
→ Timer pausa (combate é por turnos)
→ Iniciativa calculada pelo backend
→ Claude narra abertura do combate
→ A cada turno: [ESTADO_COMBATE] atualiza sidebar em tempo real
→ Fim do combate → modo volta para EXPLORAÇÃO → timer retoma
```

### 2.6 Fim de Sessão

```
Timer chega a zero (ou Claude decide encerrar)
→ Claude conduz narrativa a ponto de pausa natural
→ Claude emite [FIM_SESSAO]
→ Backend processa: XP, karma, reputação
→ Tela de resumo:
  - Resumo narrativo (diário desta sessão)
  - XP ganho + XP disponível
  - Botão "Gastar XP" → tela de progressão
  - Botão "Continuar depois"
→ Diário atualizado automaticamente
```

### 2.7 Morte do Personagem

```
Critical Hit letal → Claude emite [ACAO_SISTEMA] tipo usar_ponto_destino
→ Se tem Fate Points: interface pergunta "Gastar Ponto de Destino?"
  → Sim: continua com 1 wound, Fate Points - 1
  → Não: morte processada
→ Se não tem Fate Points: morte automática
→ Tela de morte:
  - Narração final da morte
  - Campanha marcada como "inacabada"
  - "A história de [Nome] ficou sem conclusão."
  - Opção: nova campanha (manter ou novo personagem)
```

### 2.8 Estados da Interface

| Estado | Sidebar Esq | Chat | Sidebar Dir | Timer |
|--------|------------|------|------------|-------|
| Exploração | Stats normais | Narrativa fluindo | Diários | Contando |
| Aguardando input | Stats normais | Input ativo | Diários | Contando |
| Teste pendente | Stats normais | Componente bloqueando | Diários | Pausado |
| Combate | Modo COMBATE + Turno | Narração de turno | Diários | Pausado |
| Carregando LLM | Stats normais | Cursor piscando | Diários | Contando |
| Fim de sessão | Stats atualizados | Resumo | Diário novo | Encerrado |
| Morte | Stats (morto) | Narração final | — | Encerrado |

### 2.9 Acessibilidade Mínima

- Contraste mínimo 4.5:1 para texto narrativo
- Animação do dado: respeita `prefers-reduced-motion`
- Focus visible em todos os elementos interativos
- Sem autoplay de mídia

---

## 3. Decisão Log

| Decisão | Escolha | Justificativa |
|---------|---------|--------------|
| Chat sem bolhas | Sim | Imersão — parece livro, não messenger |
| Timestamps visíveis | Não | Quebra o fluxo narrativo |
| Avatar do GM | Não | Não deve existir representação visual da IA |
| Fonte serifada para narrativa | Sim | Remete a texto impresso/livro |
| Animação do dado | CSS puro, 500ms | Rápido e satisfatório sem ser excessivo |
| Ilustrações inline | Sim, fade nas bordas | Parte da narrativa, não elemento UI separado |
| Stat numbers always visible | Não | Colapsáveis — imersão primeiro |
| Input placeholder fixo | "O que você faz?" | Reforça o contexto de RPG continuamente |


---

## 4. Componente de Dado — Especificação Detalhada

### 4.1 Conceito

Inspirado no **Dice So Nice** (Foundry VTT): dados 3D aparecem **sobrepostos sobre o chat**, rolam com física simulada, mostram o resultado com clareza e **desaparecem em ~3 segundos**. A sensação é de jogar dados físicos sobre a mesa de jogo — não de clicar um botão numa interface.

### 4.2 Comportamento

```
1. Jogador clica "Rolar dado"
2. O dado d100 aparece overlay SOBRE o chat (não abaixo, não ao lado)
3. Animação de rotação 3D + leve salto físico (~600ms)
4. Dado para no resultado — face com o número bem legível
5. Permanece visível por 3 segundos
6. Fade out suave (~300ms)
7. Resultado persiste no histórico do chat (texto estático)
```

### 4.3 Posicionamento

```
┌─────────────────────────────────────────────┐
│  Chat — Narrativa                           │
│                                             │
│  O cheiro chega antes da luz...             │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │ 🎲 TESTE DE AGILIDADE — Alvo: 25   │    │  ← card de teste
│  │ [Rolar dado]  [Enfrentar inimigo]  │    │
│  └─────────────────────────────────────┘    │
│                                             │
│         ╔═══════════╗                       │  ← dado aparece
│         ║    34     ║   ← overlay           │    aqui, centralizado
│         ║   d100    ║     sobre o chat      │    sobre o card de teste
│         ╚═══════════╝                       │
│                                             │
│  [input do jogador___________________]      │
└─────────────────────────────────────────────┘
```

### 4.4 Especificação Visual do Dado

- **Tamanho:** 120×120px — grande o suficiente para ler sem esforço
- **Forma:** cubo d100 estilizado (face mostrando dois dígitos)
- **Estética:** pedra escura gravada com dourado — consistente com o tema Warhammer
- **Face resultado:** número em fonte grande (~40px), dourado `#C9973A` sobre fundo escuro
- **Sombra:** drop shadow sutil para dar profundidade sobre o conteúdo
- **Fundo:** sem backdrop — dado flutua sobre o chat com `box-shadow` e leve `backdrop-filter: blur(2px)` ao redor

### 4.5 Animação CSS

```
Fase 1 — Entrada (0–200ms):
  scale: 0.3 → 1.0
  opacity: 0 → 1
  rotateX: 180deg → 0deg (chega "caindo")

Fase 2 — Rolando (200–800ms):
  rotateX e rotateY: valores aleatórios rápidos
  translateY: leve bounce (−8px → 0px)
  easing: cubic-bezier(0.34, 1.56, 0.64, 1)

Fase 3 — Parado (800ms–3800ms):
  estático, resultado visível
  leve pulse de brilho na borda (0.5s, 1 vez)

Fase 4 — Saída (3800–4100ms):
  opacity: 1 → 0
  scale: 1.0 → 0.8
  translateY: 0 → 10px
```

### 4.6 Som (opcional, fase futura)

Som de dados físicos rolando sobre mesa de madeira — curto (~500ms), volume baixo. Controlável nas configurações.

### 4.7 Resultado no Histórico

Após o dado desaparecer, o resultado fica registrado no chat como texto inline:

```
┌────────────────────────────────────────┐
│ 🎲 Agilidade — Rolou 34 / Alvo 25     │
│    ✓ SUCESSO  SL +0                    │
│                                        │
│  Você desce a escada no último segundo │
│  antes da guarda dobrar a esquina...   │
└────────────────────────────────────────┘
```

### 4.8 Acessibilidade

- `prefers-reduced-motion`: animação reduzida para simples fade in/out sem rotação
- ARIA live region anuncia resultado ao screen reader
- Resultado sempre persiste em texto — não depende de ver a animação

---

## 5. Dados 3D — Implementação com @3d-dice/dice-box

### 5.1 Biblioteca escolhida

**`@3d-dice/dice-box`** — equivalente web do Dice So Nice para Next.js.

Mesma base técnica do Dice So Nice (Foundry VTT): Three.js + cannon-es para física real.
Dados 3D com colisão, gravidade, bounce — o dado é jogado e rola de verdade.

```bash
npm install @3d-dice/dice-box
```

Assets estáticos (modelos 3D, texturas) precisam ser copiados para `/public/assets/dice-box/`.

### 5.2 Comportamento esperado (inspirado no Dice So Nice)

```
1. Jogador clica em "Rolar dado" (ou clica num item clicável da sidebar)
2. Bloco `.chat-roll-entry` aparece inline dentro de `.chat-log` (ChatLog)
3. Canvas WebGL 3D (~280px) rola o d100 com física — quica, rola, para
4. Resultado fica visível por ~2 segundos com veredito sucesso/falha
5. Bloco faz fade-out e é removido do chat
6. Backend recebe o valor e GM narra o resultado
```

### 5.3 Arquitetura no Next.js

```
components/
  dice/
    ChatRollEntry.tsx    ← bloco inline no chat-log (label, meta, stage 3D, resultado)
  session/
    ChatLog.tsx          ← renderiza entradas kind: "dice-roll"

lib/
  dice/
    diceRoller.ts        ← singleton DiceBox, rollPhysics, preload (port de dice.mjs)

hooks/
  useDiceRoller.ts       ← preload no mount da sessão
```

A animação 3D é decorativa; o valor enviado ao backend vem da simulação física do cliente.

### 5.4 Posicionamento

```css
.chat-roll-entry {
  max-width: 65ch;
  margin: 28px auto;       /* centralizado no chat-log */
}
.dice-inline-stage {
  min-height: 280px;       /* dimensões explícitas para canvas onscreen */
}
.dice-canvas-host {
  width: 100%;
  height: 280px;
}
```

Os dados aparecem **dentro** da área scrollável do chat (`section.chat-column > div.chat-log`), não como overlay `position: fixed` sobre a viewport.

### 5.5 Tema visual Warhammer

```javascript
const diceBox = new DiceBox('#dice-canvas', {
  assetPath: '/assets/dice-box/',
  theme: 'default',
  themeColor: '#C9973A',     // dourado Warhammer
  scale: 8,                  // dado grande, visível
  gravity: 2,
  throwForce: 6,
  spinForce: 4,
  lightIntensity: 1.2,
  onRollComplete: (result) => handleResult(result)
})
```

### 5.6 Fluxo técnico completo

```
[Jogador clica "Rolar"] 
  → Frontend solicita resultado ao backend (POST /dice/roll)
  → Backend rola d100 server-side, retorna { resultado: 34, alvo: 25, sl: 1, sucesso: true }
  → Frontend chama diceBox.roll('1d100', { value: 34 })  ← força o resultado visual
  → Animação 3D mostra o dado parando no número 34
  → Após 3s: canvas faz fade out
  → Chat exibe resultado em texto
  → Frontend envia resultado para Claude narrar
```

**Crítico:** o `value` passado para `diceBox.roll()` vem do backend — a animação mostra o resultado real, não um número aleatório visual.

---

## 6. Itens Clicáveis na Sidebar — Quick Roll

### 6.1 Conceito

Perícias, atributos e itens de combate na sidebar esquerda são clicáveis. Ao clicar, disparam automaticamente a rolagem correspondente — sem precisar que o GM emita um [TESTE] primeiro.

Simula o gesto físico de pegar o dado e rolar quando você quer testar algo.

### 6.2 O que é clicável

**Perícias** (todas):
- Clique → rola o teste usando o atributo vinculado + avanços
- Ex: clicar em "Escalar (S +3)" → teste de S com +3

**Atributos** (todos):
- Clique → rola teste puro do atributo sem modificador
- Ex: clicar em "Ag 30" → teste de Agilidade com alvo 30

**Itens de combate** (apenas armas e escudos):
- Clique → rola ataque com aquela arma (WS para CC, BS para distância)
- Ex: clicar em "🗡 Espada Longa" → ataque corpo a corpo com Espada Longa

**Não clicáveis:** itens comuns de inventário (tocha, corda, poção) — não têm rolagem associada.

### 6.3 Visual dos itens clicáveis

```
Estado padrão:
  Escalar (S) +3        ← texto normal, cor #9E8E72

Estado hover:
  🎲 Escalar (S) +3     ← ícone de dado aparece, cor #C9973A, cursor pointer
  sublinhado pontilhado dourado

Estado ativo (rolando):
  🎲 Escalar (S) +3     ← ícone gira levemente, dado aparece na tela
```

### 6.4 Contexto enviado ao GM após quick roll

Quando o jogador usa um quick roll (clique na sidebar), o backend:
1. Rola o dado server-side
2. Exibe a animação 3D
3. Injeta o resultado no chat como mensagem de sistema:

```
[Rolagem livre] Escalar — Rolou 18 / Alvo 35 — ✓ SUCESSO SL +1
```

4. Claude recebe o resultado e pode incorporar narrativamente se quiser, ou ignorar se não for relevante no momento.

### 6.5 Modificador opcional no quick roll

Ao clicar, um pequeno popover aparece por 2 segundos antes de rolar:

```
┌────────────────────────────┐
│ 🎲 Escalar (S) — Alvo: 35  │
│ Modificador: [  0  ] ±     │
│ [Rolar agora]  [Cancelar]  │
└────────────────────────────┘
```

Se o jogador não interagir em 2 segundos, rola automaticamente com modificador 0.

