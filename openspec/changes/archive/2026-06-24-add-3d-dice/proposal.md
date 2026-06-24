# Change: Dado 3D animado para rolagens de sessão

## Why

O overlay atual de dado é um cubo plano 2D com um número que gira. A experiência de rolar dados é o momento mais tátil e dramático do RPG — e o WFRP4e usa d100 (dois d10). Dice So Nice (referência do FoundryVTT) mostra que dados 3D realistas com física de colisão, sons e skins temáticas elevam significativamente a imersão. Queremos trazer isso para o WFRP Solo.

## What Changes

- **Substituir `DiceOverlay`** por uma cena 3D (Three.js + cannon-es para física) que simula um d10 de dezenas e um d10 de unidades rolando sobre uma superfície.
- **Estética gótica WFRP:** textura de couro/pedra, numeração em dourado envelhecido, coroas de ferro no topo dos dados (tema Empire). Paleta alinhada ao grimório: `#1a1510` (fundo), `#c8a84b` (dourado), `#2d2417` (dados).
- **Sons opcionais:** som de dados rolando no final da animação (Web Audio API, arquivo local, desligável nas configurações).
- **Resultado do d100:** exibição dos dois d10 separados (dezenas + unidades), depois o número final em destaque. Ex.: d10 mostra `3` e `7` → resultado `37`.
- **Duração calibrada:** animação entre 1,5 s e 2,5 s; não pode travar o loop de narração.
- **Modo reduzido:** preferência de acessibilidade — se o usuário ativa "reduzir movimento" (prefers-reduced-motion), exibe o overlay 2D atual.

## Referência técnica

- **Dice So Nice** (GitLab: `riccisi/foundryvtt-dice-so-nice`): usa Three.js + cannon-es (physics) + Proton (efeitos de partículas). Os modelos 3D dos d10 estão no repositório sob `/models/`. A geometria do d10 é um "Pentagonal Trapezohedron" customizado.
- **Abordagem para este projeto:** Three.js já está disponível via CDN/npm sem Foundry VTT. Cannon-es é leve (~60 KB gzip). Usamos apenas o subconjunto: dois d10, uma superfície plana, colisão e gravidade. Sem multiplayer sync, sem sistema de temas complexo.
- **Alternativa considerada:** CSS 3D transform puro (sem physics). Mais simples mas sem a imprevisibilidade de física real que torna cada rolagem única. Descartada em favor de Three.js para a experiência correta.

## Impact

- Affected specs: `dice-ui`
- Affected code:
  - `frontend/src/components/dice/DiceOverlay.tsx` — substituído por `Dice3DOverlay.tsx`
  - `frontend/src/app/play/[sessionId]/page.tsx` — trocar componente
  - `frontend/src/app/globals.css` — remover estilos `.d100-cube`, adicionar estilos canvas 3D
- New dependencies: `three`, `cannon-es` (frontend npm)
- **Risco:** performance em hardware fraco. Mitigado por: canvas pequeno (~400 px), física simples, `prefers-reduced-motion` como fallback.
