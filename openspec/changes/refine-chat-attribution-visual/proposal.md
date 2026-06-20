# Proposal: refine-chat-attribution-visual

**Data:** 2026-06-16  
**Status:** Draft  
**Escopo:** `frontend/src/components/session/ChatLog.tsx` · `frontend/src/app/globals.css`

---

## Problema

O chat da sessão exibe turnos do GM e do jogador sem nenhuma atribuição visual de autoria para o texto do Mestre. O jogador precisa inferir o contexto pela posição e estilo — mas em sessões longas, com alternância rápida, o limite entre "quem está falando" pode se tornar ambíguo.

**Estado atual:**

| Tipo | Classe CSS | Distinção atual |
|---|---|---|
| GM (narrativa) | `.narrative-block` | Nenhuma — texto solto à esquerda, sem label |
| Jogador | `.player-line` | Direita + itálico + borda amber + cor highlight |
| Rolagem | `.roll-system-msg` | Borda amber esquerda + fundo + mono |

O `.player-line` já é bem diferenciado. O gap principal é o `.narrative-block` não ter nenhuma âncora de autoria.

---

## Solução proposta

### Princípio de design

A solução deve ser **literária, não de chat**. O jogo é uma obra narrativa — não queremos balões de mensagem. Queremos algo análogo ao que livros de RPG usam para separar voz do narrador de voz do personagem: um eyebrow de atribuição pequeno, sutil e espaçado acima do bloco.

### Eyebrow de atribuição por grupo de turnos

Em vez de repetir o label a cada parágrafo, o sistema agrupa **turnos consecutivos do mesmo autor** e exibe o label apenas uma vez no início de cada grupo:

```
MESTRE                         ← 10px, uppercase, tracking-wide, accent/40
O vento carrega o cheiro de...
Os dedos do guarda encontram...

VOCÊ                           ← 10px, uppercase, tracking-wide, accent/40, text-right
Aponto para a janela e pergunto...

MESTRE
A estalajadeira ergue uma sobrancelha...
```

### Tratamento visual detalhado

**GM — label "MESTRE":**
- Posição: acima do primeiro bloco de cada sequência GM consecutiva
- Estilo: `text-[10px] uppercase tracking-[0.18em] text-wfrp-accent/40 mb-1 select-none font-sans`
- Resultado: quase invisível num olhar rápido, mas claramente legível ao focar

**Jogador — label "VOCÊ":**
- Posição: acima da linha do jogador, alinhado à direita (acompanhando o `player-line`)
- Estilo: igual ao "MESTRE" mas `text-right`
- O `.player-line` já tem forte diferenciação; o label reforça sem sobrepor

**Agrupamento de turnos consecutivos:**
- Implementado em `ChatLog.tsx` via `reduce` ou iteração sequencial
- Dois blocos de narrativa GM seguidos → um único "MESTRE" antes do primeiro
- Turno do jogador entre dois blocos GM → label "MESTRE" novo após o turno

### Por que não usar pseudo-elementos CSS?

`::before` em `.narrative-block` repetiria "MESTRE" em cada parágrafo (incluindo parágrafos dentro do mesmo turno). O agrupamento por turno exige lógica em `ChatLog.tsx` — mais correto e menos noise.

### Por que não mudar o visual do player-line?

O `.player-line` já tem diferenciação forte. O label "VOCÊ" adicionado é reforço de acessibilidade e consistência de padrão, sem alterar o estilo existente.

---

## Não-escopo

- Nomes de personagem no label (ex: "ELARA" em vez de "VOCÊ") — requereria passar `character.name` para `ChatLog` — pode ser feito em follow-up se bem recebido
- Avatares, fotos ou ícones — foge da estética literária
- Alteração de cores, fontes ou layout de `.player-line` — já funciona bem
- Rolagens e imagens — têm estilo próprio adequado, sem necessidade de label
