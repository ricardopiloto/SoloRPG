# Fluxo de Sessão — WFRP Solo
**Versão:** 1.0
**Data:** 2026-06-13
**Formato:** Mermaid

---

## 1. Fluxo Geral de Campanha

```mermaid
flowchart TD
    A([Jogador abre o app]) --> B{Tem personagem?}
    B -- Não --> C[Criar personagem\nou escolher pré-gerado]
    C --> D{Tem campanha ativa?}
    B -- Sim --> D
    D -- Não --> E[LLM gera nova campanha\nvia NOVA_CAMPANHA]
    D -- Sim --> F[Carregar estado da campanha]
    E --> F
    F --> G[Início de Sessão]
    G --> H{Campanha encerrada?}
    H -- Sim --> I{Tipo de encerramento}
    H -- Não --> G2[Loop de Sessão]
    I -- Morte --> J[Tela de morte\nCampanha: inacabada]
    I -- Conclusão --> K[Tela de vitória\nCampanha: concluída]
    J --> L{Nova campanha?}
    K --> L
    L -- Sim, mesmo personagem --> E2[LLM gera nova campanha\npersonagem mantido]
    L -- Sim, novo personagem --> C
    L -- Não --> M([Fim])
    E2 --> F
    G2 --> N[Fim de Sessão]
    N --> O[XP + Resumo]
    O --> P{Continuar agora?}
    P -- Sim --> G
    P -- Não --> M
```

---

## 2. Fluxo de Início de Sessão

```mermaid
sequenceDiagram
    actor J as Jogador
    participant FE as Frontend
    participant BE as Backend
    participant DB as Database
    participant LLM as Claude (GM)

    J->>FE: Clica em "Iniciar sessão"
    FE->>BE: GET /session/prepare
    BE->>DB: Carregar estado completo\n(personagem, campanha, memória)
    DB-->>BE: Estado + últimas sessões
    BE->>DB: Buscar memórias relevantes\n(pgvector similarity)
    DB-->>BE: Top 10 memórias semânticas
    BE->>BE: Montar contexto completo\n(montarSystemPrompt)
    BE->>LLM: [System prompt + contexto]\n"Inicie a sessão"
    LLM-->>BE: Duração estimada + abertura de cena
    BE->>FE: { duracao: 45, abertura: "..." }
    FE->>J: "Esta sessão terá ~45 min.\nDeseja começar?"
    J->>FE: Confirma
    FE->>BE: POST /session/start
    BE->>DB: CREATE session
    BE-->>FE: { session_id, texto_abertura }
    FE->>J: Exibe narrativa (streaming)
    FE->>BE: POST /image/generate (async)
    Note over FE,BE: Imagem gera em background\nsem bloquear narrativa
```

---

## 3. Fluxo de Turno — Exploração

```mermaid
sequenceDiagram
    actor J as Jogador
    participant FE as Frontend
    participant BE as Backend
    participant DB as Database
    participant LLM as Claude (GM)
    participant CF as Cloudflare Workers AI

    J->>FE: Digita ação em texto livre
    FE->>BE: POST /turn { input: "..." }
    BE->>BE: Montar mensagens\n(historico + input)
    BE->>LLM: Chamada API (streaming)
    LLM-->>BE: Streaming de resposta
    BE-->>FE: Streaming de texto narrativo
    FE->>J: Texto aparece progressivamente

    alt GM emite [TESTE]
        BE->>BE: Interceptar sinal [TESTE]
        BE-->>FE: { tipo: "TESTE", payload: {...} }
        FE->>J: Componente de dado aparece
        Note over FE,J: Narração pausa\naté jogador decidir
        J->>FE: Clica "Rolar dado"
        FE->>FE: Animação d100 (500ms)
        FE->>BE: POST /dice/roll { teste: {...} }
        BE->>BE: resolverTeste() — server-side
        BE-->>FE: { rolagem: 34, alvo: 35, sucesso: true, sl: 1 }
        FE->>J: Exibe resultado animado
        BE->>LLM: Retorna resultado para narrar
        LLM-->>BE: Narração da consequência
        BE-->>FE: Texto narrativo (streaming)
        FE->>J: Narração aparece
    end

    alt GM emite [IMAGEM]
        BE->>CF: POST workers-ai/flux-1-schnell\n{ prompt: "..." }
        Note over BE,CF: Assíncrono — não bloqueia
        CF-->>BE: { image: "base64..." }
        BE->>DB: Salvar URL da imagem
        BE-->>FE: { imagem_url: "..." }
        FE->>J: Imagem aparece inline na narrativa
    end

    BE->>DB: Salvar turno\n(session_turns)
    BE->>DB: Salvar eventos\n(campaign_events)
```

---

## 4. Fluxo de Teste — Detalhe

```mermaid
stateDiagram-v2
    [*] --> Aguardando: GM emite [TESTE]
    Aguardando --> Animando: Jogador clica "Rolar dado"
    Aguardando --> Alternativa: Jogador escolhe outra opção
    Animando --> Resultado: Backend retorna d100
    Resultado --> Narrando: Backend envia para Claude
    Narrando --> [*]: Claude narra consequência
    Alternativa --> [*]: Jogador digita ação alternativa
```

---

## 5. Fluxo de Combate

```mermaid
sequenceDiagram
    actor J as Jogador
    participant FE as Frontend
    participant BE as Backend
    participant LLM as Claude (GM)

    Note over FE: Modo muda para COMBATE
    BE->>BE: Calcular iniciativa\n(Agilidade + d10 por combatente)
    BE->>LLM: Resultado de iniciativa + contexto
    LLM-->>BE: Narração abertura de combate
    BE-->>FE: Texto + ordem de iniciativa

    loop Cada turno de combate
        BE-->>FE: [ESTADO_COMBATE] atualiza sidebar
        FE->>J: Turno atual visível

        alt Turno do Personagem
            J->>FE: Descreve ação em texto
            FE->>BE: POST /turn { input: "Ataco o salteador" }
            BE->>LLM: Input do jogador
            LLM-->>BE: Emite [TESTE] tipo ataque_cc
            BE->>BE: resolverAtaqueCC()
            BE-->>FE: Resultado do ataque
            FE->>J: Animação de dado + resultado
            BE->>LLM: Resultado para narrar
            LLM-->>BE: Narração do ataque
        else Turno do Inimigo
            BE->>LLM: "Turno do inimigo"
            LLM-->>BE: Emite [TESTE] tipo ataque_cc (inimigo)
            BE->>BE: resolverAtaqueCC()
            BE->>BE: Aplica dano ao personagem
            BE-->>FE: Wounds atualizados na sidebar
            BE->>LLM: Resultado
            LLM-->>BE: Narração do ataque inimigo
        end

        alt Wounds chegam a 0
            BE->>BE: Critical Hit table (d10)
            alt Efeito mortal E tem Fate Points
                BE-->>FE: "Gastar Ponto de Destino?"
                J->>FE: Decide
            else Sem Fate Points OU morte instantânea
                BE->>LLM: [ACAO_SISTEMA] morte_personagem
                LLM-->>BE: Narração da morte
                BE->>DB: Marcar personagem morto\ncampanha inacabada
                BE-->>FE: Tela de morte
            end
        end
    end

    Note over FE: Modo volta para EXPLORAÇÃO
```

---

## 6. Fluxo de Fim de Sessão

```mermaid
sequenceDiagram
    actor J as Jogador
    participant FE as Frontend
    participant BE as Backend
    participant DB as Database
    participant LLM as Claude (GM)

    BE->>BE: Timer chega a zero
    BE->>LLM: "Encerrar sessão"
    LLM-->>BE: Conduz narrativa a pausa natural
    LLM-->>BE: Emite [FIM_SESSAO] com resumos
    BE->>BE: processarFimSessao()\nValidar XP (30-100)\nCalcular karma delta\nCalcular reputação delta
    BE->>DB: Salvar session.summary_player
    BE->>DB: Salvar session.summary_system
    BE->>DB: Aplicar XP ao personagem
    BE->>DB: Aplicar karma + reputação
    BE->>DB: Salvar journal_entry (campanha + personagem)
    BE->>DB: Gerar embedding do resumo\n→ memory_embeddings (pgvector)
    BE-->>FE: { resumo, xp_ganho, xp_disponivel }
    FE->>J: Tela de fim de sessão:\n- Resumo narrativo\n- XP ganho\n- Botão "Gastar XP"\n- Botão "Continuar depois"

    opt Jogador quer gastar XP
        J->>FE: Clica "Gastar XP"
        FE->>J: Tela de progressão\n(perícias, talentos, atributos)
        J->>FE: Seleciona avanços
        FE->>BE: POST /character/advance { advances: [...] }
        BE->>BE: comprarAvancPericia()\ncomprarAvancAtributo()
        BE->>DB: Salvar avanços
        BE-->>FE: Personagem atualizado
    end
```

---

## 7. Fluxo de Geração de Imagem (Assíncrono)

```mermaid
flowchart LR
    A[LLM emite IMAGEM] --> B[Backend extrai sinal]
    B --> C[Montar prompt\n+ estilo Warhammer]
    C --> D[POST Cloudflare Workers AI\nflux-1-schnell]
    D --> E{Resposta}
    E -- Sucesso --> F[Salvar base64\ncomo URL]
    F --> G[Notificar Frontend\nvia WebSocket]
    G --> H[Imagem aparece\ninline no chat]
    E -- Falha --> I[Log erro\nPlaceholder mantido]
    E -- Timeout 15s --> I
```


---

## 8. Fluxo de Quick Roll (Clique na Sidebar)

```mermaid
sequenceDiagram
    actor J as Jogador
    participant SB as Sidebar Esquerda
    participant PO as Popover
    participant FE as Frontend
    participant BE as Backend
    participant DX as DiceBox 3D
    participant LLM as Claude (GM)

    J->>SB: Clica em "Escalar (S) +3"
    SB->>PO: Exibe popover com alvo e campo de modificador
    Note over PO: Timeout 2s — rola automaticamente se não interagir
    J->>PO: Ajusta modificador (opcional) e confirma
    PO->>FE: { pericia: 'Escalar', atributo: 'S', valor: 35, mod: 0 }
    FE->>BE: POST /dice/roll { tipo: 'teste_atributo', ... }
    BE->>BE: resolverTeste() — server-side
    BE-->>FE: { resultado: 18, alvo: 35, sl: 1, sucesso: true }
    FE->>DX: diceBox.roll('1d100', { value: 18 })
    DX-->>J: Animação 3D — dado rola e para no 18
    Note over DX: Visível por ~3 segundos
    DX-->>FE: onRollComplete()
    FE-->>J: Resultado no chat como mensagem de sistema:\n"[Rolagem] Escalar — 18/35 — ✓ SUCESSO SL +1"
    FE->>LLM: Resultado disponível para narração (opcional)
```
