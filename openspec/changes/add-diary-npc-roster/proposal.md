# Proposal: add-diary-npc-roster

**Data:** 2026-06-20  
**Status:** Draft  
**Escopo:** `DiarySidebar` (aba Personagem) · `backend/app/db/models.py` · `memory.py` · `routes.py` · prompt GM (delta mínimo)

---

## Problema

A aba **Personagem** na sidebar direita (`DiarySidebar`) hoje exibe entradas de diário pessoal — mas o frontend **não carrega** esses dados na sessão (`play/[sessionId]/page.tsx` passa só `campaignEntries` e `rollHistory`). A aba fica sempre vazia ("Diário pessoal vazio").

O jogador precisa consultar **NPCs com quem já interagiu**, com:
- **Nome** pelo qual o personagem conhece a pessoa
- **Local** onde a interação / primeiro encontro ocorreu

Exemplo desejado:

```
Greta, a estalajadeira
Estalagem do Corvo
```

---

## Solução proposta

### 1. Aba Personagem → roster de NPCs conhecidos

Substituir o conteúdo principal da aba **Personagem** por uma lista read-only de NPCs que o jogador **já interagiu** na campanha ativa.

Cada card/linha:

| Campo | Fonte | Exemplo |
|---|---|---|
| Nome conhecido | `NPC.known_name` ou fallback `NPC.name` | `Greta, a estalajadeira` |
| Local | `NPC.met_location` | `Estalagem do Corvo` |
| Papel (opcional, muted) | `NPC.role` | `Estalajadeira` |

Layout compacto, scrollável, consistente com aba Rolagens:

```
Greta, a estalajadeira
Estalagem do Corvo · Estalajadeira
─────────────────
Hans Gruber
Praça do Mercado
```

Estado vazio: `"Nenhum NPC registrado ainda."`

### 2. Modelo de dados — estender `NPC`

Adicionar colunas opcionais em `npcs`:

- `known_name: str | null` — nome pelo qual o PJ conhece (default: usar `name`)
- `met_location: str | null` — local do encontro / interação

**Quem entra na lista:** todos os registros `NPC` da campanha — criados em `[NOVA_CAMPANHA]` (NPCs da abertura = já interagidos na cena inicial) ou adicionados/atualizados via `npcs_interagidos` em `[FIM_SESSAO]`.

### 3. Persistência — popular `met_location`

| Origem | Regra |
|---|---|
| `npcs_iniciais` (`apply_nova_campanha`) | `met_location` = `campaign.opening_location` (ou campo `local` se presente no JSON) |
| `npcs_interagidos` (`persist_session_summary`) | Aceitar `local` no payload; atualizar `met_location` se informado |
| `known_name` | Usar `nome_conhecido` se GM enviar; senão `nome` |

Delta mínimo no prompt GM (`Docs/gm-system-prompt.md`): documentar campos opcionais em `npcs_interagidos`:

```json
{"nome": "Greta", "nome_conhecido": "Greta, a estalajadeira", "local": "Estalagem do Corvo", "mudanca": "..."}
```

### 4. API

`GET /campaigns/{campaign_id}/npcs` →

```json
{
  "npcs": [
    {
      "id": "...",
      "name": "Greta",
      "known_name": "Greta, a estalajadeira",
      "met_location": "Estalagem do Corvo",
      "role": "Estalajadeira",
      "relationship_status": "amigavel"
    }
  ]
}
```

Ordenação alfabética por `known_name` / `name`.

### 5. Frontend

- `api.listCampaignNpcs(campaignId)`
- `useSessionPlay`: carregar NPCs junto com diary (ou fetch no `DiarySidebar`)
- `DiarySidebar`: prop `knownNpcs`; aba Personagem renderiza roster
- i18n: empty state PT-BR

---

## Não-escopo

- Editar/remover NPCs manualmente pelo jogador
- Exibir segredos do GM (`NPC.secret`)
- Substituir abas Rolagens / Campanha
- Diário pessoal italic (pode voltar como sub-seção futura abaixo do roster)
- Mapa visual de NPCs

---

## Impacto

- **Backend:** migration/colunas NPC, persistência, endpoint, testes
- **Frontend:** DiarySidebar + hook + api
- **GM prompt:** documentação de campos opcionais (sem mudar comportamento obrigatório do GM)

---

## Nota dev (sqlite)

`create_all` não altera tabelas existentes. Dev sqlite pode precisar recriar `wfrp_solo.db` ou migration manual — documentar no `tasks.md`.
