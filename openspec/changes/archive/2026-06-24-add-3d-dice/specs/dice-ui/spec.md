## ADDED Requirements

### Requirement: Simulação 3D de dois d10 para rolagens d100
Quando uma rolagem d100 for executada, o sistema SHALL exibir uma animação 3D de dois dados d10 (dezenas e unidades) com física de colisão realista. O resultado final exibido nos dados DEVE corresponder exatamente ao valor retornado pelo backend.

#### Scenario: Dados rolam e exibem resultado correto
- **WHEN** o backend retorna `roll_results[0].roll = 47`
- **THEN** o d10 de dezenas para na face `4` (representando 40) e o d10 de unidades para na face `7`, e o overlay exibe o resultado total `47`

#### Scenario: Animação tem duração não-bloqueante
- **WHEN** a animação 3D inicia
- **THEN** ela completa em no máximo 2,5 segundos e então chama `onDone` para prosseguir com a narração

#### Scenario: Resultado legível após animação
- **WHEN** os dados param
- **THEN** o número total é exibido em tipografia `font-display` com badge de sucesso (verde) ou falha (vermelho) baseado em `roll_results[0].success`

---

### Requirement: Estética temática WFRP
Os dados 3D SHALL adotar a paleta visual do grimório WFRP: fundo escuro (`#1a1510`), textura dos dados em couro/pedra escura, numeração em dourado envelhecido (`#c8a84b`). A iluminação deve evidenciar a face ativa do dado.

#### Scenario: Paleta consistente com o resto da UI
- **WHEN** o overlay de dados aparece sobre a tela de jogo
- **THEN** as cores e fontes são visualmente consistentes com a paleta `wfrp-*` do design system

---

### Requirement: Fallback para preferência de movimento reduzido
Quando o sistema operacional ou navegador sinalizar `prefers-reduced-motion: reduce`, o sistema SHALL exibir o overlay 2D plano em vez da animação 3D.

#### Scenario: Acessibilidade respeitada
- **WHEN** o usuário tem `prefers-reduced-motion: reduce` ativo
- **THEN** o dado 2D flat é exibido normalmente, sem nenhuma física ou animação pesada

#### Scenario: WebGL indisponível
- **WHEN** o navegador não suporta WebGL (hardware antigo, servidor de renderização)
- **THEN** o sistema detecta e usa automaticamente o overlay 2D como fallback

---

### Requirement: Som de impacto dos dados (opcional)
O sistema SHALL reproduzir um som curto de impacto quando os dados tocam a superfície. O som DEVE ser desabilitável pelo jogador e DEVE respeitar a política de autoplay (apenas após gesto do usuário).

#### Scenario: Som habilitado após gesto
- **WHEN** o jogador interage com a página e o som está habilitado em `localStorage`
- **THEN** o som de impacto é reproduzido quando o dado toca a superfície virtual

#### Scenario: Som desabilitado por padrão
- **WHEN** é a primeira sessão do jogador (sem preferência salva)
- **THEN** o som está desabilitado; o jogador pode habilitá-lo via controle na interface

#### Scenario: Silêncio quando desabilitado
- **WHEN** o som está desabilitado
- **THEN** nenhum audio é reproduzido durante a animação 3D
