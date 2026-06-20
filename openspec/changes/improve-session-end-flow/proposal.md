# Proposal: improve-session-end-flow

**Data:** 2026-06-16  
**Status:** Draft  
**Escopo:** `frontend/src/hooks/useSessionPlay.ts` · `frontend/src/components/session/ChatLog.tsx` · `frontend/messages/pt-BR.json`

---

## Problema

Quando o GM emite `[FIM_SESSAO]`, o backend devolve `result.session_ended = true` no evento `done` do stream. O frontend, ao detectar isso em `applyMeta`, imediatamente executa:

```ts
// useSessionPlay.ts:152-162
if (result.session_ended) {
  sessionStorage.setItem("wfrp-recap", JSON.stringify({ ... }));
  router.push("/session/end");  // ← redireciona antes do jogador ler qualquer coisa
}
```

O jogador é expulso da tela de jogo **antes de ver a última mensagem do Mestre** — exatamente o desfecho narrativo da sessão, o texto mais importante do turno. O resumo em `/session/end` é textual e descontextualizado; o impacto da cena final se perde completamente.

---

## Solução proposta

### Princípio

Remover o redirect automático. Em vez disso, o fim de sessão é **sinalizado dentro do próprio chat** com um banner inline. O jogador:

1. Lê a última mensagem do Mestre normalmente no chat
2. Vê um banner de encerramento abaixo da narrativa com duas opções
3. Escolhe quando e como sair

### Novo tipo de entrada no ChatLog: `session-end`

```ts
| {
    kind: "session-end";
    xp: number;
    playerSummary?: string;
    campaignId?: string;
    characterId?: string;
  }
```

### Fluxo atualizado

**Antes (atual):**
```
stream narrative → done event → session_ended=true → router.push("/session/end")
```

**Depois:**
```
stream narrative → done event → session_ended=true
  → adiciona entry { kind: "session-end", xp, ... } ao chat
  → desabilita input (sessão encerrada)
  → banner inline aguarda ação do jogador
     ├─ "Encerrar por hoje" → router.push("/session/end")  (resumo + progressão)
     └─ "Continuar campanha" → router.push("/campaigns")   (iniciar nova sessão)
```

### Banner `session-end` no ChatLog

Estilo: separador visual sutil (linha + ícone) com dois botões. Integrado ao scroll do chat — o jogador rola naturalmente até ele depois de ler a narrativa.

```
─────────────── ✦ ───────────────
    Sessão encerrada · +{xp} XP

  [ Continuar campanha ]  [ Encerrar por hoje ]
```

- Fundo: `bg-wfrp-surface/60 border border-wfrp-border/60`
- Texto central: `font-display text-sm text-wfrp-muted`
- XP: destaque em `text-wfrp-accent`
- Dois botões: `btn-primary` (continuar) + `btn-secondary` (encerrar)

### Input desabilitado após fim de sessão

Quando há uma entry `session-end` no chat, o campo de input e o botão de envio devem ser desabilitados e exibir hint diferente — a sessão está encerrada, não pausada.

### Estado `sessionStorage` preservado

O `wfrp-recap` ainda é escrito em `sessionStorage` ao detectar `session_ended`, mas o redirect só ocorre quando o jogador clica "Encerrar por hoje". Isso garante que `/session/end` receba os dados corretos.

---

## Não-escopo

- Alterar a página `/session/end` (resumo já funciona bem)
- Alterar o backend (o `[FIM_SESSAO]` e `end_session` já funcionam corretamente)
- Adicionar novo endpoint de API
- Permitir que o jogador continue digitando após o fim de sessão
