# Database Schema — WFRP Solo

**Versão:** 2.0 (SQLite-only)  
**Data:** 2026-06-22

---

## 1. Visão geral

Stack: **SQLite** via `aiosqlite` + SQLAlchemy async. Um arquivo `.db` persiste todos os dados.

```
┌─────────────────────────────────────────────────────┐
│ SQLite (wfrp_solo.db)                               │
│  users → player_characters → campaigns → sessions   │
│  npcs, factions, narrative_events, diary_entries    │
│  embeddings JSON em narrative_events.embedding      │
└─────────────────────────────────────────────────────┘
```

**Configuração:**

```env
DATABASE_URL=sqlite+aiosqlite:///./wfrp_solo.db
```

Produção (VPS): caminho absoluto, ex. `sqlite+aiosqlite:////opt/wfrp-solo/data/wfrp_solo.db`

**Schema em runtime:** `Base.metadata.create_all` + `schema_patch.py` na subida. Alembic mantido como histórico (no-op em SQLite).

---

## 2. Tipos SQLite

| Conceito SQLAlchemy | SQLite |
|---------------------|--------|
| `Uuid` | TEXT (UUID string) |
| `JSON` | TEXT (JSON serializado) |
| `DateTime(timezone=True)` | TEXT ISO8601 |
| `Enum` | TEXT |
| `Boolean` | INTEGER 0/1 |

Embeddings semânticos: coluna **`JSON`** (`list[float]`, 384 dims) — busca por cosine similarity em Python (`PythonSearchAdapter`).

---

## 3. Tabelas principais

### users

Autenticação JWT + verificação por e-mail.

| Coluna | Tipo | Notas |
|--------|------|-------|
| id | UUID | PK |
| email | VARCHAR(320) | UNIQUE |
| password_hash | VARCHAR(255) | bcrypt |
| email_verified_at | DATETIME | NULL até verify |
| created_at | DATETIME | |

### player_characters

Ficha WFRP4e; atributos/perícias/talentos em JSON.

| Coluna | Tipo | Notas |
|--------|------|-------|
| user_id | UUID | FK → users |
| is_starter | BOOLEAN | personagem automático no cadastro |
| attributes | JSON | WS, BS, S, T, … |
| careers, skills, talents, trappings | JSON | |
| karma, social_perception | INT / TEXT | narrativo |

### campaigns / game_sessions

Campanha ativa por personagem; sessões com `turn_history` JSON, timer, modo EXPLORACAO/COMBATE.

### narrative_events

Eventos para memória semântica.

| Coluna | Tipo | Notas |
|--------|------|-------|
| embedding | JSON | vetor 384d; `simple_embedding()` |
| description | TEXT | texto do evento |
| event_type | TEXT | ex. `session_event` |

Busca: últimos `limit * 4` eventos da campanha → cosine similarity → top N.

### npcs, factions, diary_entries, image_jobs

Ver models em `backend/app/db/models.py`.

---

## 4. Backup

```bash
cp wfrp_solo.db wfrp_solo.db.bak
# ou, com backend parado:
sqlite3 wfrp_solo.db ".backup wfrp_solo_backup.db"
```

**Produção:** 1 worker uvicorn (SQLite write lock). WAL mode opcional em follow-up.

---

## 5. Referência de implementação

- Models: `backend/app/db/models.py`
- Patches: `backend/app/db/schema_patch.py`
- Memória: `backend/app/services/memory.py`
