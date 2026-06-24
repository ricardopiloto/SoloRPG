# Proposal: add-passive-discovery-tests

**Data:** 2026-06-23  
**Status:** Draft  
**Relacionado:** `sync-gm-prompt-v23`, `update-gm-prompt-perception`  
**Arquivo afetado:** `Docs/gm-system-prompt.md` (apenas)

---

## Why

O prompt atual define dois tipos de teste:

- **Tipo 1** — o jogador declara uma ação e o GM avalia se requer teste
- **Tipo 2** — a situação impõe um teste obrigatório (queda, veneno, emboscada)

Esses dois tipos cobrem bem ações declaradas e perigos imediatos, mas **deixam de fora toda uma camada narrativa**: momentos em que a cena naturalmente contém uma oportunidade de descoberta — um som, um cheiro, um detalhe visual — onde o resultado do dado enriquece a cena sem bloquear a história.

**Exemplo concreto:**

> "O formigamento nos seus dedos para completamente.  
> A brisa também para.  
> O silêncio agora é absoluto.  
> E você ouve, vindo de dentro do portal, o som de alguém respirando."

O "ouvir" aqui é narrativo — o GM narrou que o personagem ouve. Mas há uma camada mais profunda: *o que exatamente* ouve? O ritmo de um humano com medo? Uma respiração que não é humana? A distância? Isso é exatamente o que um teste de **Percepção** revelaria. Com sucesso, o personagem detecta urgência/perigo específico. Com falha, continua sabendo apenas que há algo respirando lá dentro. Em ambos os casos, a história avança.

Sem a instrução explícita de um Tipo 3, o GM tende a narrar a cena completa (revelando tudo de graça) ou a não narrar nenhum detalhe sensorial relevante. Nenhum dos dois é o ponto ideal.

---

## What Changes

Adicionar ao `gm-system-prompt.md`, dentro da seção `FLUXO DE TESTES`, um novo **TIPO 3 — TESTE PASSIVO DE DESCOBERTA**:

### Critérios de uso (quando emitir)

O GM deve emitir um [TESTE] de descoberta passiva quando:

1. A narrativa acabou de descrever um estímulo sensorial que o personagem *notou parcialmente* — não completamente
2. Há um detalhe mais profundo que a perícia pode revelar (e que não revelaria sozinha)
3. A história **continua independentemente** do resultado — mas o que o personagem *sabe* difere
4. A perícia relevante é de percepção/exploração: Percepção, Furtividade, Conhecimento (área), Intuição, Rastrear, Avaliar

**Nunca usar para:**
- Confirmar o óbvio narrativo ("você viu a espada — role Percepção para confirmar")
- Substituir narração completa de uma cena
- Gerar um teste a cada parágrafo (máximo 1 por turno, e apenas se organicamente encaixado)

### Formato técnico

`obrigatorio: false` — o resultado não bloqueia o avanço.  
`opcao_alternativa: null` — não há "outra ação"; a descoberta acontece passivamente.  
`consequencia_sucesso`: detalhe específico que o teste revela.  
`consequencia_falha`: personagem mantém o que a narrativa já revelou, sem o detalhe extra.

### Exemplos (a incluir no prompt)

**Exemplo 1 — Percepção auditiva:**
> Narrativa: "E você ouve, vindo de dentro do portal, o som de alguém respirando."
> Teste emitido:
```json
{
  "tipo": "teste_atributo",
  "atributo": "I",
  "pericia": "Percepção",
  "modificador": -10,
  "obrigatorio": false,
  "descricao": "Ouvir detalhes da respiração vinda do portal",
  "consequencia_sucesso": "Você identifica que a respiração tem um ritmo irregular e pesado — algo grande e assustado, não predatório. Há uma única fonte.",
  "consequencia_falha": "Você sabe apenas que algo respira lá dentro. Não consegue dizer mais.",
  "opcao_alternativa": null
}
```

**Exemplo 2 — Percepção visual:**
> Narrativa: "A rua parece vazia, mas você sente que algo está errado."
> Teste emitido:
```json
{
  "tipo": "teste_atributo",
  "atributo": "I",
  "pericia": "Percepção",
  "modificador": 0,
  "obrigatorio": false,
  "descricao": "Identificar o que está errado na rua",
  "consequencia_sucesso": "Uma sombra se move no segundo andar da casa à esquerda. Alguém observa.",
  "consequencia_falha": "Você continua com a sensação de que algo está fora do lugar, mas não consegue identificar o quê.",
  "opcao_alternativa": null
}
```

**Exemplo 3 — Conhecimento contextual:**
> Narrativa: "Os símbolos na parede são antigos."
> Teste emitido:
```json
{
  "tipo": "teste_atributo",
  "atributo": "Int",
  "pericia": "Conhecimento (Magia)",
  "modificador": 0,
  "obrigatorio": false,
  "descricao": "Reconhecer os símbolos na parede",
  "consequencia_sucesso": "São runas de contenção do Séc. XII — alguém aprisionou algo aqui. As runas estão parcialmente apagadas.",
  "consequencia_falha": "São antigos, claramente religiosos, mas você não consegue identificar a tradição específica.",
  "opcao_alternativa": null
}
```

---

## Capabilities

### Modified Capabilities

- **gm-narrative**: GM passa a emitir testes passivos de descoberta em momentos sensoriais/perceptivos organicamente presentes na narrativa

---

## Impact

| Área | Alterações |
|------|------------|
| `Docs/gm-system-prompt.md` | Nova subseção TIPO 3 dentro de FLUXO DE TESTES; 3 exemplos |
| Backend / Frontend | Nenhuma — `obrigatorio: false` já é suportado pelo parser e pelo DiceOverlay |

---

## Non-Goals

- Alterar o parser de sinais (`signals.py`) — já suporta `obrigatorio: false`
- Adicionar lógica de backend para "testes passivos" — é puramente instrução de prompt
- Forçar testes passivos em toda narração — é orgânico e espaçado (máximo 1 por turno)
- Alterar resultado/narração pós-rolagem — já coberto pela seção NARRAÇÃO APÓS RESULTADO

---

## Trade-offs

| Decisão | Alternativa | Motivo |
|---------|-------------|--------|
| Prompt-only (sem mudança de código) | Novo campo no payload JSON | O sistema já suporta `obrigatorio: false`; apenas falta a instrução de quando usar |
| Limite de 1 por turno | Sem limite | Evita que o GM vire um gerador de testes — o teste deve ser especial, não rotineiro |
| `opcao_alternativa: null` para passivos | Fornecer sempre alternativa | Testes passivos não têm "alternativa de ação" — o personagem simplesmente percebe ou não |
