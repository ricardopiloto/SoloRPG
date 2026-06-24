# Tasks: Dado 3D animado

## 1. Setup e dependências

- [x] 1.1 Instalar `three`, `@types/three` e `cannon-es` em `frontend/` via npm
- [x] 1.2 Criar diretório `frontend/src/components/dice/3d/` para isolar a lógica
- [x] 1.3 Criar utilitário `dice3d-geometry.ts` que define geometria d10, quaternions de face, e textura de couro procedural
- [x] 1.4 Geometria d10 via `THREE.CylinderGeometry(0, 1, 1.6, 5)` modificado em double-pyramid

## 2. Motor de física dos dados

- [x] 2.1 Criar `DicePhysics.ts`: classe que gerencia dois corpos rígidos (tens, units) no cannon-es world
- [x] 2.2 Implementar superfície plana (plano com restitution 0.35, friction 0.7)
- [x] 2.3 Implementar lançamento inicial: velocidade angular e linear aleatórias, gravidade `(0, -40, 0)`
- [x] 2.4 Implementar fixação do resultado: após estabilização, snap para quaternion da face correta via `snapToResult`
- [x] 2.5 Resultado visível bate com número rolado pelo servidor (server-authoritative)

## 3. Renderização e composição visual

- [x] 3.1 Criar `Dice3DCanvas.tsx`: componente React com `<canvas>` 400×280, loop via `requestAnimationFrame` em `useEffect`
- [x] 3.2 Material `MeshStandardMaterial` com textura canvas (couro escuro + números dourados `#c8a84b`)
- [x] 3.3 Iluminação: `AmbientLight` (0.45) + `DirectionalLight` (0.85) com sombras
- [x] 3.4 Fundo semi-transparente + `backdrop-filter: blur(4px)` via `.dice-3d-container`
- [x] 3.5 Resultado final: overlay de texto com dezenas+unidades+total em CSS animado

## 4. Som (opcional, progressivo)

- [x] 4.1 Criar `DiceSounds.ts` com Web Audio API: buffer de ruído curto com decay exponencial
- [x] 4.2 Controle de mute em `localStorage` (`wfrp-dice-sound-enabled`) — desabilitado por padrão
- [x] 4.3 Som ativado apenas após gesto do usuário (`markUserGesture()` chamado no primeiro render)

## 5. Acessibilidade e fallback

- [x] 5.1 Detectar `prefers-reduced-motion` via `useReducedMotion` hook, renderizar `DiceOverlay2D` quando ativo
- [x] 5.2 `DiceOverlay.tsx` antigo renomeado para `DiceOverlay2D.tsx`; mantido como fallback
- [x] 5.3 `aria-live="assertive"` no container 3D com resultado lido por screen reader + `.sr-only`
- [x] 5.4 Fallback WebGL: `try/catch` no renderer, detecção via `useWebGLSupported` hook

## 6. Integração e cleanup

- [x] 6.1 Substituir `DiceOverlay` por `Dice3DOverlay` em `play/[sessionId]/page.tsx`
- [x] 6.2 Estilos `.dice-3d-container` adicionados em `globals.css`; `.d100-cube` antigo mantido para fallback 2D
- [x] 6.3 `Dice3DOverlay` carregado via `next/dynamic` (ssr: false) → bundle split automático
- [x] 6.4 Build sem erros; rota `/play/[sessionId]` compila com sucesso (`npm run build` ✓)

## 7. Testes e validação

- [ ] 7.1 Teste visual: dois d10 rolam, somem, exibem resultado numérico correto
- [ ] 7.2 Teste de resultado: verificar em 10 rolagens que o número exibido no 3D bate com `roll_results[0].roll` do backend
- [ ] 7.3 Teste de fallback: com `prefers-reduced-motion: reduce`, exibir overlay 2D em vez de WebGL
- [ ] 7.4 Teste de performance: animação não deve cair abaixo de 30 fps em hardware típico
