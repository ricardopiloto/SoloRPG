# gm-narrative Specification

## Purpose
TBD - created by archiving change add-passive-discovery-tests. Update Purpose after archive.
## Requirements
### Requirement: GM MUST emit passive discovery tests for ambient sensory moments

Quando a narrativa do GM contém um estímulo sensorial que o personagem apenas percebeu parcialmente, o GM SHALL emitir um [TESTE] com `obrigatorio: false` e `opcao_alternativa: null` para revelar um detalhe mais profundo condicionado ao resultado.

#### Scenario: Detalhe auditivo embebido na narrativa

- **Dado** que o GM narrou "você ouve, vindo de dentro do portal, o som de alguém respirando"
- **Quando** há uma camada mais específica que uma perícia de Percepção revelaria (ritmo, natureza, origem)
- **Então** o GM emite [TESTE] com `pericia: "Percepção"`, `obrigatorio: false`, `opcao_alternativa: null`
- **E** `consequencia_sucesso` descreve o detalhe específico que o sucesso revela
- **E** `consequencia_falha` mantém o personagem no nível da narração original (sem detalhe extra)
- **E** a história avança após a rolagem independente do resultado

#### Scenario: Sensação vaga de perigo

- **Dado** que o GM narrou "você sente que algo está errado"
- **Quando** há um detalhe concreto que a Percepção revelaria (sombra, som, figura)
- **Então** o GM emite [TESTE] com `obrigatorio: false`
- **E** sucesso: detalhe concreto identificado; falha: sensação permanece vaga

#### Scenario: Estímulo sem camada adicional — sem teste

- **Dado** que o GM narrou "você vê o guarda na entrada — ele está com uma alabarda"
- **Quando** não há nada mais específico que o teste revelaria além do óbvio narrado
- **Então** o GM NÃO emite [TESTE] — a cena é completa como narrada

#### Scenario: Limite de um teste por turno

- **Dado** que o GM já emitiu um [TESTE] passivo no mesmo turno
- **Quando** há outra oportunidade de descoberta passiva na mesma cena
- **Então** o GM incorpora o segundo detalhe diretamente na narrativa ou posterga para o próximo turno

---

### Requirement: Passive discovery test MUST use correct signal structure

O [TESTE] de descoberta passiva SHALL usar `obrigatorio: false` e `opcao_alternativa: null` — indicando que a história continua independente do resultado.

#### Scenario: Campos corretos no payload

- **Dado** que o GM decidiu emitir um teste passivo de Percepção
- **Então** o payload tem `"obrigatorio": false`
- **E** o payload tem `"opcao_alternativa": null`
- **E** `consequencia_sucesso` é uma frase que revela detalhe específico não presente na narrativa
- **E** `consequencia_falha` é uma frase que mantém o personagem no nível narrativo original

#### Scenario: Narração pós-resultado continua a história

- **Dado** que o [RESULTADO DO SISTEMA] retornou sucesso em um teste passivo
- **Então** o GM incorpora o detalhe de `consequencia_sucesso` e avança a cena
- **Dado** que o resultado retornou falha
- **Então** o GM usa `consequencia_falha` e avança a cena igualmente — sem "punição" narrativa

