# Design: add-diary-npc-roster

## Aba Personagem vs. diário pessoal

**Decisão:** A aba **Personagem** passa a exibir o **roster de NPCs conhecidos** como conteúdo principal.

**Motivo:** Pedido explícito do usuário; diário pessoal nunca foi wired na sessão. Spec arquivada `identity-layers` previa reflexões pessoais — adiar para follow-up se necessário.

**Alternativa rejeitada:** Nova aba "NPCs" — evita 4ª tab estreita na sidebar direita (~259px).

## Campos NPC

```python
known_name: str | None   # display; fallback → name
met_location: str | None # "Estalagem do Corvo"
```

NPCs iniciais recebem `met_location = campaign.opening_location` automaticamente no backend — não depende do GM lembrar de enviar `local` na abertura.

## Critério "interagiu"

**Decisão:** Todo registro em `npcs` para a campanha conta como interagido.

**Motivo:** Registros só entram via abertura (cena inicial) ou `npcs_interagidos` pós-sessão. NPCs não revelados não existem na tabela.

## UI — componente

```tsx
<article className="border-b border-wfrp-border/50 pb-2">
  <div className="font-medium text-wfrp-fg">{displayName}</div>
  {metLocation && <div className="text-xs text-wfrp-muted">{metLocation}</div>}
  {role && <div className="text-[10px] text-wfrp-muted/80">{role}</div>}
</article>
```

`displayName = npc.known_name || npc.name`

## Refresh de dados

Carregar NPCs:
1. No mount/resume da sessão (`useSessionPlay`)
2. Após `session_ended` / fim de turno que persiste `npcs_interagidos` (reload da lista)

MVP: refetch após cada turno `done` que altera campanha — ou só no mount + após fim de sessão (mais simples; aceitar lag de 1 sessão para NPCs novos até FIM_SESSAO).

**Decisão MVP:** refetch no mount e quando `useSessionPlay` recarrega diary (já ocorre pós-turno em alguns fluxos). Se gap, follow-up com refetch explícito pós-stream.

## Relacionamento com specs existentes

Modifica expectativa da aba Personagem em `identity-layers` (arquivada) — delta explícito em `web-interface`.
