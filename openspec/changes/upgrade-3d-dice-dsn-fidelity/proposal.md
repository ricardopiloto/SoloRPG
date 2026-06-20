# Change: Fidelidade total às animações do Dice So Nice (via @3d-dice/dice-box)

## Why

A implementação atual de dados 3D (`add-3d-dice`) é uma aproximação simplificada construída manualmente com Three.js. Ela difere das animações de referência do Dice So Nice em múltiplos aspectos fundamentais:

| Aspecto | Atual (manual) | @3d-dice/dice-box |
|---|---|---|
| Engine 3D | Three.js (nossa implementação) | BabylonJS (engine profissional) |
| Física | cannon-es com `CANNON.Box` incorreto | AmmoJS (port do Bullet Physics, usado por game engines AAA) |
| Execução | Thread principal (bloqueia UI) | Web workers + offscreenCanvas (thread separada) |
| Geometria d10 | `CylinderGeometry` modificado | Modelos 3D reais com UVs precisos |
| Paredes | Apenas chão | Caixa de contenção completa |
| Física de bounce | Simples, imprecisa | Bullet Physics: restitution, damping, spin, throw force configuráveis |
| Sombras | Sem sombras | Sombras com transparência configurável |
| Temas | Canvas procedural manual | Sistema de temas com diffuse/normal/specular maps |
| Estabilização | Threshold manual de velocidade | `settleTimeout` + detecção de repouso física real |
| Tamanho do dado | Fixo | `scale` configurável (2–9) |

O `@3d-dice/dice-box` ([github.com/3d-dice/dice-box](https://github.com/3d-dice/dice-box)) é a biblioteca de referência que o próprio Dice So Nice recomenda quando não se precisa do ambiente Foundry VTT. Ele usa o mesmo pipeline de física realista que produz as animações que o usuário quer.

## What Changes

- **Substituir implementação própria pelo package `@3d-dice/dice-box`**: remove `dice3d-geometry.ts`, `DicePhysics.ts`, `Dice3DCanvas.tsx` e `DiceSounds.ts`; adiciona wrapper React sobre a API pública do package
- **Assets estáticos em `public/assets/dice-box/`**: os arquivos de física (AmmoJS WASM), workers (`world.offscreen.js`, `world.onscreen.js`) e tema default precisam ser servidos via HTTP; são copiados da pasta `dist/` do package para `public/`
- **Componente `DiceBoxWrapper.tsx`**: inicializa o `DiceBox` com `init()`, chama `roll("2d10")` para a animação decorativa e reporta o resultado via `onRollComplete`; limpa com `clear()` ao desmontar
- **Resultado server-authoritative via texto**: como a versão BabylonJS do `@3d-dice/dice-box` não suporta outcomes pré-determinados, a animação é **puramente decorativa**; o resultado real (do servidor) sempre é exibido no overlay de texto após `onRollComplete` disparar
- **Tema WFRP**: `themeColor: "#1a120b"` (couro escuro) com `theme: "default"` via `updateConfig()`
- **Configuração de física realista**: `gravity: 1`, `mass: 1`, `spinForce: 6`, `throwForce: 5`, `restitution: 0.3`, `angularDamping: 0.4`, `enableShadows: true`
- **Web workers automático**: o package usa `offscreen: true` automaticamente quando disponível no browser; fallback para `onscreen` sem mudança de código
- **Manter fallback `DiceOverlay2D`**: `prefers-reduced-motion` e WebGL ausente continuam usando o overlay 2D existente
- **Next.js config**: nenhuma mudança em `next.config.ts` — os workers são servidos como arquivos estáticos de `public/`, não bundlados pelo webpack

## Nota sobre resultado nos dados

Na versão BabylonJS (`@3d-dice/dice-box`), a animação física determina aleatoriamente os valores visíveis nas faces dos dados. O resultado do jogo (score) vem sempre do servidor (server-authoritative). Após `onRollComplete`, o overlay exibe o resultado do servidor independentemente do que os dados mostram fisicamente — a animação é visual, não determina o resultado.

Isso é comportamento padrão aceitável: o jogador vê a animação satisfatória de dados rolando, e o resultado real do teste é exibido em destaque no overlay.

## Impact

- Affected specs: `dice-ui`
- Affected code:
  - `frontend/package.json` — adicionar `@3d-dice/dice-box`
  - `frontend/public/assets/dice-box/` — assets estáticos (excluídos do git)
  - `frontend/src/components/dice/3d/DiceBoxWrapper.tsx` — novo componente wrapper
  - `frontend/src/components/dice/Dice3DOverlay.tsx` — usar `DiceBoxWrapper`
  - `frontend/src/app/globals.css` — remover/ajustar CSS da implementação manual
  - `.gitignore` — adicionar `frontend/public/assets/dice-box/`
- Removed:
  - `frontend/src/components/dice/3d/dice3d-geometry.ts`
  - `frontend/src/components/dice/3d/DicePhysics.ts`
  - `frontend/src/components/dice/3d/Dice3DCanvas.tsx`
  - `frontend/src/components/dice/3d/DiceSounds.ts`
- Licença: MIT ([@3d-dice/dice-box](https://github.com/3d-dice/dice-box/blob/main/LICENSE))
