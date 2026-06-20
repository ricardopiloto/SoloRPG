# Database Schema — WFRP Solo

**Versão:** 1.0
**Data:** 2026-06-13
**Status:** Documento de referência para implementação

---

## 1. Visão Geral

Stack: **PostgreSQL + pgvector** via Supabase.
Dois domínios de dados: **estruturado** (relacional) e **semântico** (vetorial).

```
┌─────────────────────────────────────────────────────┐
│ DADOS ESTRUTURADOS (PostgreSQL)                     │
│  players → characters → campaigns → sessions        │
│  npcs, factions, events, inventory, journal         │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│ DADOS SEMÂNTICOS (pgvector)                         │
│  memory_embeddings → busca por relevância por turno │
└─────────────────────────────────────────────────────┘
```

---

## 2. Tabelas Relacionais

### 2.1 players
```sql
CREATE TABLE players (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email       TEXT UNIQUE NOT NULL,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
```

### 2.2 characters
```sql
CREATE TABLE characters (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  player_id         UUID REFERENCES players(id) ON DELETE CASCADE,

  -- Identidade
  name              TEXT NOT NULL,
  race              TEXT NOT NULL DEFAULT 'Humano',
  background        TEXT,

  -- Atributos base WFRP4e
  ws                INT NOT NULL DEFAULT 30,  -- Weapon Skill
  bs                INT NOT NULL DEFAULT 30,  -- Ballistic Skill
  s                 INT NOT NULL DEFAULT 30,  -- Strength
  t                 INT NOT NULL DEFAULT 30,  -- Toughness
  i                 INT NOT NULL DEFAULT 30,  -- Initiative
  ag                INT NOT NULL DEFAULT 30,  -- Agility
  dex               INT NOT NULL DEFAULT 30,  -- Dexterity
  int_attr          INT NOT NULL DEFAULT 30,  -- Intelligence
  wp                INT NOT NULL DEFAULT 30,  -- Willpower
  fel               INT NOT NULL DEFAULT 30,  -- Fellowship

  -- Avanços de atributos comprados com XP (soma ao base)
  attr_advances     JSONB NOT NULL DEFAULT '{}',
  -- ex: {"WS": 3, "Ag": 5}

  -- Ferimentos
  wounds_current    INT NOT NULL DEFAULT 10,
  wounds_max        INT NOT NULL DEFAULT 10,

  -- Pontos de Destino
  fate_points       INT NOT NULL DEFAULT 2,
  fate_points_max   INT NOT NULL DEFAULT 2,
  fortune_points    INT NOT NULL DEFAULT 2,
  fortune_points_max INT NOT NULL DEFAULT 2,

  -- Progressão
  xp_current        INT NOT NULL DEFAULT 0,
  xp_total_spent    INT NOT NULL DEFAULT 0,

  -- Carreira atual
  career_name       TEXT,
  career_tier       INT DEFAULT 1,

  -- Camadas internas (nunca exibidas como números)
  karma             INT NOT NULL DEFAULT 0,   -- -100 a 100
  social_perception TEXT,                      -- texto narrativo

  -- Estado
  is_alive          BOOLEAN NOT NULL DEFAULT TRUE,
  death_description TEXT,                      -- preenchido ao morrer

  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW()
);
```

### 2.3 character_skills
```sql
CREATE TABLE character_skills (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  character_id      UUID REFERENCES characters(id) ON DELETE CASCADE,
  name              TEXT NOT NULL,
  linked_attribute  TEXT NOT NULL,  -- ex: 'Ag', 'WS'
  advances          INT NOT NULL DEFAULT 0,
  UNIQUE(character_id, name)
);
```

### 2.4 character_talents
```sql
CREATE TABLE character_talents (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
  name         TEXT NOT NULL,
  times_taken  INT NOT NULL DEFAULT 1,
  UNIQUE(character_id, name)
);
```

### 2.5 character_careers
```sql
CREATE TABLE character_careers (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
  name         TEXT NOT NULL,
  tier         INT NOT NULL DEFAULT 1,
  xp_spent     INT NOT NULL DEFAULT 0,
  started_at   TIMESTAMPTZ DEFAULT NOW(),
  ended_at     TIMESTAMPTZ
);
```

### 2.6 inventory_items
```sql
CREATE TABLE inventory_items (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
  name         TEXT NOT NULL,
  description  TEXT,
  encumbrance  INT DEFAULT 0,
  quantity     INT DEFAULT 1,
  item_type    TEXT,  -- 'weapon', 'armor', 'gear', 'consumable'
  properties   JSONB DEFAULT '{}'
  -- ex: {"damage": 4, "qualities": ["Precise"]}
);
```

### 2.7 campaigns
```sql
CREATE TABLE campaigns (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  character_id      UUID REFERENCES characters(id) ON DELETE CASCADE,
  player_id         UUID REFERENCES players(id) ON DELETE CASCADE,

  -- Dados do GM (nunca exibidos ao jogador)
  tone              TEXT NOT NULL,
  -- ex: 'sombrio/político', 'horror/sobrenatural'
  secret_objective  TEXT NOT NULL,
  antagonist        JSONB,
  -- ex: {"nome": "Aldric Voss", "motivacao": "..."}

  -- Estado narrativo
  opening_location  TEXT NOT NULL,
  current_phase     TEXT NOT NULL DEFAULT 'inicio',
  world_state       TEXT,  -- resumo comprimido do estado do mundo

  -- Status
  status            TEXT NOT NULL DEFAULT 'ativa',
  -- 'ativa', 'concluida', 'inacabada'
  conclusion_type   TEXT,
  -- 'vitoria', 'morte', 'abandono'
  conclusion_desc   TEXT,

  -- Sessão estimada e duração
  estimated_session_minutes INT DEFAULT 45,

  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW()
);
```

### 2.8 sessions
```sql
CREATE TABLE sessions (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_id     UUID REFERENCES campaigns(id) ON DELETE CASCADE,
  session_number  INT NOT NULL,

  -- Controle de tempo
  started_at      TIMESTAMPTZ DEFAULT NOW(),
  ended_at        TIMESTAMPTZ,
  duration_minutes INT,

  -- Modo e estado
  mode            TEXT NOT NULL DEFAULT 'EXPLORACAO',
  -- 'EXPLORACAO', 'COMBATE'
  combat_turn     INT DEFAULT 0,

  -- Resumos gerados pela LLM ao fim da sessão
  summary_player  TEXT,  -- visível ao jogador (diário)
  summary_system  JSONB, -- invisível, para alimentar próximas sessões
  -- ex: {"eventos": [...], "npcs_interagidos": [...]}

  -- XP
  xp_awarded      INT DEFAULT 0,
  xp_justification TEXT,

  -- Deltas aplicados
  karma_delta     INT DEFAULT 0,
  reputation_deltas JSONB DEFAULT '{}',

  created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### 2.9 session_turns
```sql
CREATE TABLE session_turns (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id   UUID REFERENCES sessions(id) ON DELETE CASCADE,
  turn_number  INT NOT NULL,
  role         TEXT NOT NULL,  -- 'player', 'gm'
  content      TEXT NOT NULL,  -- texto visível
  raw_llm      TEXT,           -- resposta bruta da LLM (com sinais)
  signals      JSONB,          -- sinais extraídos e processados
  created_at   TIMESTAMPTZ DEFAULT NOW()
);
```

### 2.10 npcs
```sql
CREATE TABLE npcs (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_id  UUID REFERENCES campaigns(id) ON DELETE CASCADE,
  name         TEXT NOT NULL,
  role         TEXT,           -- 'aliado', 'neutro', 'antagonista', 'desconhecido'
  faction      TEXT,
  description  TEXT,
  secret       TEXT,           -- informação que o jogador não sabe
  relationship TEXT,           -- relação atual com o personagem
  status       TEXT DEFAULT 'vivo',  -- 'vivo', 'morto', 'desaparecido'
  first_seen_session INT,
  last_seen_session  INT,
  created_at   TIMESTAMPTZ DEFAULT NOW(),
  updated_at   TIMESTAMPTZ DEFAULT NOW()
);
```

### 2.11 factions
```sql
CREATE TABLE factions (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_id  UUID REFERENCES campaigns(id) ON DELETE CASCADE,
  name         TEXT NOT NULL,
  description  TEXT,
  UNIQUE(campaign_id, name)
);
```

### 2.12 faction_reputation
```sql
CREATE TABLE faction_reputation (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
  faction_id   UUID REFERENCES factions(id) ON DELETE CASCADE,
  score        INT NOT NULL DEFAULT 0,  -- -100 a 100
  updated_at   TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(character_id, faction_id)
);
```

### 2.13 campaign_events
```sql
CREATE TABLE campaign_events (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_id  UUID REFERENCES campaigns(id) ON DELETE CASCADE,
  session_id   UUID REFERENCES sessions(id),
  event_type   TEXT NOT NULL,
  -- 'decisao', 'combate', 'morte_npc', 'revelacao', 'marco', 'morte_personagem'
  description  TEXT NOT NULL,
  consequences TEXT,
  importance   INT DEFAULT 1,  -- 1=normal, 2=importante, 3=marco
  created_at   TIMESTAMPTZ DEFAULT NOW()
);
```

### 2.14 journal_entries
```sql
CREATE TABLE journal_entries (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_id  UUID REFERENCES campaigns(id) ON DELETE CASCADE,
  session_id   UUID REFERENCES sessions(id),
  entry_type   TEXT NOT NULL,
  -- 'campanha', 'personagem'
  content      TEXT NOT NULL,  -- gerado automaticamente pela LLM
  created_at   TIMESTAMPTZ DEFAULT NOW()
);
```

### 2.15 generated_images
```sql
CREATE TABLE generated_images (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id   UUID REFERENCES sessions(id),
  campaign_id  UUID REFERENCES campaigns(id),
  prompt       TEXT NOT NULL,
  image_type   TEXT NOT NULL,  -- 'cena', 'personagem', 'mapa', 'item'
  image_url    TEXT,           -- URL após upload
  priority     TEXT DEFAULT 'normal',  -- 'normal', 'marco'
  status       TEXT DEFAULT 'pending', -- 'pending', 'generated', 'failed'
  created_at   TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 3. Memória Semântica (pgvector)

```sql
-- Habilitar extensão
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE memory_embeddings (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_id  UUID REFERENCES campaigns(id) ON DELETE CASCADE,
  session_id   UUID REFERENCES sessions(id),

  -- Conteúdo
  content      TEXT NOT NULL,      -- texto do evento/memória
  summary      TEXT,               -- versão comprimida para contexto
  memory_type  TEXT NOT NULL,
  -- 'evento', 'decisao', 'npc', 'localizacao', 'segredo', 'gancho'

  -- Metadados para filtragem
  importance   INT DEFAULT 1,      -- 1=normal, 2=importante, 3=crítico
  session_number INT,
  tags         TEXT[],

  -- Vetor semântico (text-embedding-3-small = 1536 dims)
  embedding    vector(1536),

  created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- Índice para busca por similaridade (IVFFlat)
CREATE INDEX ON memory_embeddings
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

-- Índice para filtragem por campanha
CREATE INDEX ON memory_embeddings (campaign_id, importance DESC);
```

### Função de busca semântica
```sql
CREATE OR REPLACE FUNCTION buscar_memorias_relevantes(
  p_campaign_id UUID,
  p_embedding   vector(1536),
  p_limit       INT DEFAULT 10,
  p_min_importance INT DEFAULT 1
)
RETURNS TABLE (
  content      TEXT,
  summary      TEXT,
  memory_type  TEXT,
  importance   INT,
  similarity   FLOAT
) AS $$
  SELECT
    content,
    summary,
    memory_type,
    importance,
    1 - (embedding <=> p_embedding) AS similarity
  FROM memory_embeddings
  WHERE
    campaign_id = p_campaign_id
    AND importance >= p_min_importance
  ORDER BY embedding <=> p_embedding
  LIMIT p_limit;
$$ LANGUAGE sql;
```

---

## 4. Índices Adicionais

```sql
-- Personagem por jogador
CREATE INDEX ON characters (player_id, is_alive);

-- Campanhas ativas por personagem
CREATE INDEX ON campaigns (character_id, status);

-- Sessões por campanha
CREATE INDEX ON sessions (campaign_id, session_number DESC);

-- Turnos por sessão
CREATE INDEX ON session_turns (session_id, turn_number);

-- NPCs por campanha
CREATE INDEX ON npcs (campaign_id, status);

-- Eventos por importância
CREATE INDEX ON campaign_events (campaign_id, importance DESC, created_at DESC);

-- Imagens pendentes
CREATE INDEX ON generated_images (status, created_at)
  WHERE status = 'pending';
```

---

## 5. Views Úteis

```sql
-- Estado completo do personagem para injeção no prompt
CREATE VIEW v_character_state AS
SELECT
  c.*,
  json_agg(DISTINCT jsonb_build_object(
    'nome', cs.name, 'avancos', cs.advances, 'atributo', cs.linked_attribute
  )) AS skills,
  json_agg(DISTINCT jsonb_build_object(
    'nome', ct.name, 'vezes', ct.times_taken
  )) AS talents,
  json_agg(DISTINCT jsonb_build_object(
    'nome', ii.name, 'enc', ii.encumbrance, 'tipo', ii.item_type
  )) AS inventory
FROM characters c
LEFT JOIN character_skills cs ON cs.character_id = c.id
LEFT JOIN character_talents ct ON ct.character_id = c.id
LEFT JOIN inventory_items ii ON ii.character_id = c.id
GROUP BY c.id;

-- Resumo de campanha para contexto
CREATE VIEW v_campaign_context AS
SELECT
  camp.*,
  COUNT(DISTINCT s.id) AS total_sessions,
  COUNT(DISTINCT n.id) AS total_npcs,
  COUNT(DISTINCT e.id) FILTER (WHERE e.importance >= 2) AS major_events
FROM campaigns camp
LEFT JOIN sessions s ON s.campaign_id = camp.id
LEFT JOIN npcs n ON n.campaign_id = camp.id
LEFT JOIN campaign_events e ON e.campaign_id = camp.id
GROUP BY camp.id;
```

---

## 6. Estratégia de Compressão de Memória

A cada fim de sessão, o sistema executa:

1. **Gerar embedding** do resumo técnico da sessão → salvar em `memory_embeddings`
2. **Comprimir sessões antigas**: sessões com mais de 5 sessões atrás têm `summary_system` comprimido
3. **Promover eventos críticos**: eventos com `importance = 3` nunca são descartados
4. **Limite de contexto**: máximo de 10 memórias semânticas por turno (busca pgvector)

```
Camadas de contexto por turno (ordem de prioridade):
1. Estado atual do personagem         → v_character_state
2. Resumo da campanha                  → v_campaign_context
3. Resumos das últimas 3 sessões       → sessions.summary_system
4. Top 10 memórias por relevância      → buscar_memorias_relevantes()
5. NPCs ativos na sessão atual         → npcs WHERE status = 'vivo'
6. Histórico recente (últimos 8 turnos) → session_turns
```

---

## 7. Retenção e Limpeza

```sql
-- Limpar turnos muito antigos (manter apenas últimos 50 por sessão encerrada)
-- Executado semanalmente via job

-- Imagens falhas após 24h
DELETE FROM generated_images
WHERE status = 'failed'
AND created_at < NOW() - INTERVAL '24 hours';
```

