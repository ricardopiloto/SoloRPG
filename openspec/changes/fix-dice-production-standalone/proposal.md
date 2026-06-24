# Proposal: fix-dice-production-standalone

**Data:** 2026-06-23  
**Status:** Draft  
**Supersede parcial:** `fix-dice-overlay-zenbrowser` (7/9 tasks — esse change cobre os 2 restantes e adiciona causa de produção)  
**Relacionado:** `add-3d-dice`, `fix-dice-box-v11-api`, `fix-dice-overlay-zenbrowser`

---

## Why

Em ambiente de desenvolvimento (`npm run dev`), os dados 3D funcionam. No deploy Docker com Next.js standalone + Caddy + Cloudflare Tunnel, **os dados não aparecem** com os seguintes erros no console:

```
colliderFaceMap Error: No value found for d100 mesh face -1
colliderFaceMap Error: No value found for d10 mesh face -1
Uncaught (in promise) TypeError: e.clear().catch is not a function
```

Causa raiz identificada em três camadas:

### Causa 1 — `clear().catch` inválido (API mismatch)

Em `DiceOverlay.tsx` linha 75:
```ts
if (box) void box.clear().catch(() => undefined);
```

No build de produção do `@3d-dice/dice-box`, `clear()` **não retorna uma Promise** em determinados estados do ciclo de vida — retorna `void` ou `undefined`. Chamar `.catch()` sobre isso lança `TypeError: e.clear().catch is not a function`. Como está dentro de um path de cleanup (`!visible && was`), esse erro não impede o roll atual, mas corrompe o estado do singleton para a próxima rolagem.

### Causa 2 — Ammo.js WASM não carrega em produção

Os erros `colliderFaceMap face -1` indicam que o motor de física (Ammo.js, servido via `assets/ammo/ammo.wasm`) **não inicializou**. Quando Ammo.js falha, o DiceBox inicializa parcialmente sem física — os dados não aparecem visualmente e a detecção de face retorna `-1` (sem colisão detectada).

O WASM falha em produção por uma combinação de:

1. **MIME type incorreto**: Para que um Worker ou módulo carregue um `.wasm` via `fetch()`, o servidor deve responder com `Content-Type: application/wasm`. O Next.js standalone (`server.js`) serve arquivos de `public/` mas pode não definir o MIME correto para `.wasm` sem configuração explícita.

2. **Headers de segurança bloqueando SharedArrayBuffer/COOP**: DiceBox usa workers. Alguns ambientes exigem `Cross-Origin-Opener-Policy: same-origin` e `Cross-Origin-Embedder-Policy: require-corp` para SharedArrayBuffer. Sem eles, o Worker pode ser bloqueado silenciosamente.

3. **Caddy não propaga headers para arquivos estáticos do container**: O Caddy faz reverse proxy para o container, mas pode não repassar ou adicionar os headers necessários para os assets WASM.

### Causa 3 — Fallback silencioso mascarando a falha

O `diceBoxHost.ts` captura exceções de init e retorna `null`, mas o `DiceOverlay.tsx` tem fallback para RNG do browser quando DiceBox é `null`. Isso significa que o dado "funciona" numericamente mas **sem animação 3D** — o usuário vê o resultado mas não os dados na tela. Os erros aparecem no console mas não são surfaceados na UI.

---

## What Changes

### Fix 1 — `clear()` defensivo (sem assumir Promise)

Em `DiceOverlay.tsx` e `diceBoxHost.ts`, substituir chamadas `box.clear().catch(...)` por padrão seguro:

```ts
// Antes:
void box.clear().catch(() => undefined);

// Depois:
const r = box.clear() as unknown;
if (r && typeof (r as Promise<void>).catch === 'function') {
  void (r as Promise<void>).catch(() => undefined);
}
```

Alternativamente, atualizar o tipo `DiceBoxInstance.clear()` para `clear(): void | Promise<void>` e usar a versão defensiva em todos os callsites.

### Fix 2 — Headers MIME e COOP/COEP via Caddy

Adicionar ao bloco `@solorpg` do Caddyfile headers necessários para WASM e Workers:

```caddyfile
@solorpg host solorpg.1nodado.com.br
handle @solorpg {
    header Cross-Origin-Opener-Policy "same-origin"
    header Cross-Origin-Embedder-Policy "require-corp"
    reverse_proxy localhost:3000
}
```

E adicionar tipo MIME explícito para `.wasm` quando servido via Caddy (para requests que chegam diretamente ao Caddy antes do Next.js):

```caddyfile
@wasm {
    path *.wasm
}
header @wasm Content-Type "application/wasm"
```

### Fix 3 — Verificação de carregamento de assets no Dockerfile

Garantir que o script `prepare:dice` rode **e** que os assets gerados sejam copiados para o runner no Dockerfile. O Dockerfile atual já faz `COPY --from=builder /app/public ./public`, mas adicionar um `RUN ls public/assets/dice-box/assets/ammo/` como smoke check de build para falhar cedo se os assets estiverem ausentes.

### Fix 4 — Surfacear falha de DiceBox na UI

Quando `ensureDiceBox` retorna `null` (init falhou), o `DiceOverlay` cai no fallback silencioso. Adicionar um indicador visual mínimo: mensagem "Dados físicos indisponíveis — usando resultado numérico" para que o usuário saiba que a animação 3D não está funcionando e não confunda com ausência de rolagem.

---

## Capabilities

### Modified Capabilities

- **dice-ui**: `clear()` defensivo; indicador de fallback quando 3D indisponível
- **dice-wasm-load**: MIME type e headers de segurança corretos para WASM em produção

---

## Impact

| Área | Alterações |
|------|------------|
| `frontend/src/components/dice/DiceOverlay.tsx` | `clear()` defensivo; mensagem de fallback |
| `frontend/src/types/dice-box.d.ts` | Tipo `clear()` atualizado para `void \| Promise<void>` |
| `frontend/Dockerfile` | Smoke check de assets pós-`prepare:dice` |
| `Caddyfile` (servidor) | Headers COOP/COEP e MIME `.wasm` |
| `Docs/debian-server-install.md` | Seção sobre headers necessários para dados 3D |

---

## Non-Goals

- Trocar `@3d-dice/dice-box` por outra biblioteca
- Dados 3D em modo `offscreen: true` (Workers separados — escopo diferente)
- Corrigir dados 3D em navegadores sem WebAssembly (Safari antigo, etc.) — fallback numérico é suficiente

---

## Trade-offs

| Decisão | Alternativa descartada | Motivo |
|---------|------------------------|--------|
| Headers COOP/COEP no Caddy | Injetar via next.config.js headers | Caddy é o ponto de entrada HTTP — mais simples e cobre todos os assets incluindo os servidos diretamente |
| Tipo `clear()` como `void \| Promise<void>` | Fixar versão do dice-box com `clear()` sempre async | Versão de patch pode não existir; a defesa no callsite é mais resiliente a atualizações futuras |
| Smoke check no Dockerfile | CI test | Falha de build é mais visível e imediata |

---

## Open Questions

| Questão | Decisão assumida |
|---------|-----------------|
| COOP/COEP quebra outros recursos do site (iframes, embeds)? | Improvável no escopo atual (sem iframes de terceiros) — verificar após deploy |
| O `clear()` do dice-box retorna Promise em todas as versões ≥1.1.4? | Não confirmado — por isso o fix é defensivo |
