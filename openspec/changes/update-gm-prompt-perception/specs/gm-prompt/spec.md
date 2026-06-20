## ADDED Requirements

### Requirement: Testes passivos de Percepção e Intuição
O GM SHALL emitir automaticamente um sinal `[TESTE]` de Percepção ou Intuição nos seguintes cenários, sem necessidade de declaração explícita do jogador:

- Uma figura está seguindo o personagem por mais de uma cena
- Existe um detalhe visual, auditivo ou olfativo fora do padrão em uma cena
- Um NPC está mentindo ou ocultando informação relevante para o personagem
- Uma emboscada ou perigo iminente existe mas não foi declarado
- O personagem examina um objeto ou área que contém algo escondido

O sucesso no teste DEVE revelar o detalhe através da narração. A falha NÃO deve revelar o detalhe e o GM NÃO deve indicar que havia algo a observar.

#### Scenario: Seguidor não percebido
- **WHEN** um NPC está seguindo o personagem há mais de uma cena
- **THEN** o GM emite `[TESTE]` de Percepção sem que o jogador peça, e narra a situação criando a oportunidade de rolagem

#### Scenario: NPC mentindo
- **WHEN** um NPC está mentindo e a informação é relevante para o personagem
- **THEN** o GM emite `[TESTE]` de Intuição com modificador contextual apropriado

#### Scenario: Falha em percepção passiva
- **WHEN** o jogador falha em um teste passivo de Percepção
- **THEN** o GM continua a narração sem revelar o detalhe e sem indicar que havia algo a notar

---

### Requirement: Tratativa de rolagens não solicitadas
Quando o resultado de uma rolagem aparecer no contexto sem que nenhum `[TESTE]` tenha sido emitido pelo GM previamente, o GM SHALL reconhecer narrativamente a ação física do personagem sem inventar uma situação retroativa para justificar o dado.

#### Scenario: Quick-roll sem teste pendente
- **WHEN** o jogador usa o painel de quick-roll fora de qualquer teste solicitado
- **THEN** o GM narra o gesto físico do personagem ("Você flexiona os dedos, testando os próprios reflexos") sem tratar o resultado como resolução de um desafio narrativo

#### Scenario: Nota de quick-roll no histórico
- **WHEN** o jogador executa um quick-roll
- **THEN** o sistema persiste no histórico da sessão a nota "Jogador verificou [atributo/perícia] espontaneamente — resultado: [sucesso/falha]" para contexto do GM no próximo turno
