# Propostas OpenSpec — Export

**Projeto:** WFRP Solo  
**Gerado em:** 2026-06-21  
**Changes incluídas:** `session-image-credits-guard` · `skill-row-wfrp-advance-format`

---

# 1. session-image-credits-guard

**Local OpenSpec:** `openspec/changes/session-image-credits-guard/`  
**Status:** Implementado (18/21 tasks — validação manual pendente)

## Proposta

### Por quê

A geração de imagens consome créditos da API Cloudflare Workers AI com quota limitada. Hoje, cada sinal `[IMAGEM]` do GM dispara um job independente — mesmo quando a quota já está esgotada, o sistema continua enfileirando tentativas que falham silenciosamente turno a turno, desperdiçando latência e poluindo logs. Precisamos detectar indisponibilidade de créditos cedo (início da sessão) e cortar novas tentativas assim que a quota acabar no meio do jogo.

### O que muda

- **Probe de créditos no início da sessão:** ao criar uma sessão nova, o backend envia uma requisição real de geração de imagem (prompt mínimo de validação) à Cloudflare. Se falhar, a sessão fica marcada como sem imagens pelo resto da sessão.
- **Flag de sessão `images_enabled`:** novo campo em `GameSession` persiste se a sessão pode gerar imagens. Inicia `true` após probe bem-sucedido; vira `false` em falha no probe ou em falha de quota mid-session.
- **Guard no pipeline de imagens:** `_handle_signal` para `[IMAGEM]` ignora o sinal quando `images_enabled=false` — nenhum `ImageJob` é criado, nenhum spinner aparece.
- **Desligamento mid-session:** quando um job falha por quota/créditos esgotados (HTTP 429, código 10000, ou erro tipado equivalente), `images_enabled` passa a `false` para aquela sessão; jobs subsequentes não são enfileirados.
- **Retomada de sessão pausada:** sessões retomadas reutilizam o flag já persistido — não re-probe (evita consumir crédito extra e respeita estado anterior).
- **Transparência ao jogador:** sem mensagens de erro; narrativa continua normalmente, apenas sem ilustrações.

### Capabilities

| Tipo | Nome | Descrição |
|------|------|-----------|
| Nova | `session-image-credits-guard` | Validação de créditos no início da sessão via probe real e desligamento automático mid-session |

### Impacto

| Área | Alterações |
|------|------------|
| Backend | `GameSession` + migration, `session.py`, `probe_image_credits`, `images.py`, `gm_orchestrator.py`, `cloudflare_workers_ai.py` |
| API | `SessionOut` / `SessionDetailOut` expõem `images_enabled` |
| Frontend | Nenhuma mudança obrigatória |
| Infra | 1 crédito de imagem por sessão nova (custo do probe) |

---

## Design (resumo)

### Fluxo de `images_enabled`

| Evento | `images_enabled` |
|--------|-------------------|
| Sessão nova criada | `False` → probe → `True` se sucesso |
| Probe falha | permanece `False` |
| Sessão pausada retornada | valor existente, sem probe |
| Job falha por quota mid-session | `False` |
| Erro transitório (503, timeout) | inalterado |

### Probe no `start_session`

- Chamada **síncrona** após criar `GameSession` nova
- Prompt fixo: `"minimal dark fantasy landscape, validation probe"` (tipo `"cena"`)
- Bytes gerados são descartados
- Sessão pausada retomada: **sem re-probe**

### Classificação de erro de quota

| Condição | Conta como quota? |
|----------|-------------------|
| `CloudflareNotConfigured` | Sim |
| HTTP 429 / mensagem `"quota/tokens esgotados"` | Sim |
| JSON error code `10000` | Sim |
| Timeout, ConnectError, HTTP 503 | Não (falha pontual) |

**Probe:** qualquer falha → `images_enabled = false`  
**Mid-session:** só erros de quota desligam a sessão inteira

---

## Especificação

### IMG-CRED-01 — Probe no início de sessão nova

- Nova sessão executa geração real de validação na Cloudflare antes do primeiro turno
- Probe ok → `images_enabled = true`
- Probe falha (qualquer motivo) → `images_enabled = false`, zero imagens na sessão
- Credenciais ausentes → falha sem chamar API externa
- Sessão pausada retomada → não re-probe

### IMG-CRED-02 — Ignorar `[IMAGEM]` quando desabilitado

- `images_enabled=false` → sinal ignorado silenciosamente, sem job, sem placeholder
- Narrativa textual continua normalmente
- Cache hit continua funcionando quando `images_enabled=true`

### IMG-CRED-03 — Desligamento mid-session

- Quota esgotada (429 ou code 10000) → `images_enabled=false` imediato
- Erro transitório → job falha, sessão continua tentando
- Jobs já enfileirados podem completar; novos não são criados após desligamento

### IMG-CRED-04 — API

- `images_enabled: boolean` em `SessionOut` e `SessionDetailOut`

---

## Tasks

### Concluídas

- [x] Coluna `images_enabled` em `GameSession` + migration Alembic
- [x] `is_quota_or_credit_error()` e `probe_image_credits()` em Cloudflare
- [x] Probe em `start_session()` (skip em sessão pausada)
- [x] Guard em `_handle_signal` para `[IMAGEM]`
- [x] Desligamento mid-session em `process_image_job`
- [x] Campo `images_enabled` na API
- [x] 6 testes automatizados (unit + integração)

### Pendentes (validação manual)

- [ ] Sessão com CF válido → probe ok e imagens no turno
- [ ] CF inválido → zero spinners/imagens na sessão
- [ ] Quota esgotada mid-session → imagens param após primeira falha

---

# 2. skill-row-wfrp-advance-format

**Local OpenSpec:** `openspec/changes/skill-row-wfrp-advance-format/`  
**Status:** Implementado (4/6 tasks — validação visual pendente)

## Proposta

### Por quê

Na sidebar de perícias, o jogador precisa ver de forma imediata **quantos avanços possui** em cada perícia e **qual atributo** a compõe — no padrão WFRP de ficha: avanços primeiro, atributo entre colchetes (ex.: `4+[Fel]`). A implementação anterior (`refine-skill-row-target-display`) exibia `[Fel] +4`, que inverte a ordem.

### O que muda

- **Formato WFRP na meta da linha:** `{N}+[{Attr}]` quando `N > 0`; apenas `[{Attr}]` quando `N === 0`
- **Atualizar `formatSkillRowMeta`:** de `[Fel] +4` para `4+[Fel]`

### Exemplos visuais

| Perícia | Avanços | Atributo | Exibição |
|---------|---------|----------|----------|
| Seduzir | 4 | Fel | `4+[Fel]` |
| Furtividade | 0 | Ag | `[Ag]` |
| Atirar (Arco) | 5 | BS | `5+[BS]` |

- **Cálculo de alvo inalterado:** `atributo + avanços + modificador` (quick roll)
- **Acessibilidade:** `aria-label` informa avanços, atributo e alvo calculado

### Capabilities

| Tipo | Nome | Descrição |
|------|------|-----------|
| Nova | `skill-row-display` | Formato WFRP de avanços + atributo na sidebar |

### Impacto

| Área | Alterações |
|------|------------|
| Frontend | `wfrp-attributes.ts` (`formatSkillRowMeta`), `CharacterSidebar.tsx`, testes |
| Backend | Nenhum |

---

## Design (resumo)

### Formato

```
// Antes                    // Depois
Seduzir      [Fel] +4   →   Seduzir      4+[Fel]
Furtividade  [Ag]       →   Furtividade  [Ag]
```

### Regra em código

```typescript
export function formatSkillRowMeta(linkedAttribute: string, advances: number): string {
  const tag = `[${linkedAttribute}]`;
  return advances > 0 ? `${advances}+${tag}` : tag;
}
```

- Fonte de avanços: `character.skills[].advances` cruzado com catálogo `GET /rules/skills`
- Perícia ausente na ficha → 0 avanços → só `[Attr]`

---

## Especificação

### SKILL-ROW-01 — Meta WFRP com avanços e atributo

- Com avanços: exibir `{N}+[{Attr}]` (ex.: `4+[Fel]`)
- Sem avanços: exibir só `[{Attr}]` — sem `0+` ou `+0`
- Perícia do catálogo não possuída: `[{linked_attribute}]`, alvo = atributo + 0
- Layout: nome à esquerda, meta à direita; `aria-label` completo

---

## Tasks

### Concluídas

- [x] Atualizar `formatSkillRowMeta` para `{N}+[{Attr}]`
- [x] JSDoc com exemplos `4+[Fel]` e `[Ag]`
- [x] Testes unitários (3 casos)
- [x] `npm run build` sem erros

### Pendentes (validação visual)

- [ ] Pregen Helena: `Armas Corpo a Corpo (Básicas)` → `1+[WS]`
- [ ] Pregen Tobias: `Conhecimento (Magia)` → `2+[Int]`
- [ ] Perícias sem avanços → só `[Attr]`, quick roll alvo = atributo

---

## Referências

| Change | Caminho |
|--------|---------|
| session-image-credits-guard | `openspec/changes/session-image-credits-guard/` |
| skill-row-wfrp-advance-format | `openspec/changes/skill-row-wfrp-advance-format/` |
| Relacionada (supersedida visualmente) | `openspec/changes/refine-skill-row-target-display/` |
| Relacionada (falha silenciosa de imagens) | `openspec/changes/handle-image-api-failure/` |
