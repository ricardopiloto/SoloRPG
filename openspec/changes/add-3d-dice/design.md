## Context

O WFRP Solo precisa de um momento de rolagem dramático. O dado 3D deve ser fisicamente plausível (não só uma animação pré-determinada), ter estética temática WFRP e ser não-bloqueante para o loop de jogo.

A referência principal é **Dice So Nice** (FoundryVTT), que usa Three.js + cannon-es + Proton. Nosso escopo é menor: apenas d10 × 2, sem multiplayer, sem sistema de temas complexo.

## Goals / Non-Goals

- **Goals:**
  - Substituir o d100 flat por dois d10 3D com física real
  - Estética temática: couro escuro, numeração dourada, tema Empire
  - Server-authoritative: resultado definido pelo backend, física é só visual
  - Fallback gracioso para `prefers-reduced-motion` e WebGL indisponível
  - Som de impacto leve e desligável

- **Non-Goals:**
  - Suporte a outros tipos de dado (d6, d8, d20) — fora do MVP WFRP4e
  - Sistema de skins/temas configurável pelo usuário
  - Sincronização de dados entre jogadores (não há multiplayer)
  - AR/VR

## Decisions

### Three.js + cannon-es (não CSS 3D)
CSS 3D transforms podem simular rotação mas não colisão realista entre objetos. A imprevisibilidade de física de verdade (os dados ricocheteiam de forma diferente a cada lançamento) é o que faz a rolagem se sentir "real". Three.js é a lib 3D mais madura do ecossistema web; cannon-es é um fork mantido de cannon.js com suporte a ESM.

**Alternativas:**
- `rapier.js` (WASM, mais preciso) — descartado: binário WASM adiciona 500 KB; cannon-es é suficiente para física simples de dados.
- Three.js + Ammo.js — descartado: Ammo.js é maior e mais complexo que cannon-es.
- react-three-fiber — descartado: adiciona abstração React sobre Three.js sem benefício claro para um componente de curta duração.

### Server-authoritative com fixação de face
O backend gera o número real (d100 = d10×10 + d10). A física é executada com velocidade angular aleatória. Quando os dados param, o sistema força o quaternion da face correta via lookup table. Isso garante que o número exibido bata com o resultado do servidor sem depender de física determinística.

### Canvas isolado, não cena global
O canvas de dados é criado e destruído por montagem/desmontagem do componente React. Não há cena persistente. Isso evita memory leaks e mantém o componente self-contained.

## Risks / Trade-offs

- **Performance em hardware fraco** → canvas pequeno (400×300), single light, textura gerada proceduralmente (sem fetch de imagem externa). Fallback 2D para prefers-reduced-motion.
- **WebGL não disponível** → `try/catch` no renderer; fallback para `DiceOverlay2D`.
- **Bundle size** → Three.js ~600 KB minificado, cannon-es ~80 KB. Tree-shaking via imports seletivos reduz para ~350 KB para o subconjunto usado. Apenas carregado na rota `/play/[sessionId]` via dynamic import.

## Migration Plan

1. Instalar dependências
2. Implementar `Dice3DOverlay` em paralelo com `DiceOverlay2D` (antigo)
3. Substituir em `page.tsx` com feature flag (env `NEXT_PUBLIC_DICE_3D=true`) para teste gradual
4. Remover flag e `DiceOverlay2D` após validação visual

## Open Questions

- Usar um d10 com faces numeradas 0–9 (como dados físicos WFRP) ou exibir dezenas/unidades como `30` e `7`? Recomendação: exibir valores decimais reais (0, 10, 20... para dezenas; 0–9 para unidades).
- Som deve ser habilitado por padrão? Proposta: desabilitado por padrão, com aviso "Clique para ativar som dos dados" na primeira sessão.
