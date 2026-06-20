## Context

`@3d-dice/dice-box` é a biblioteca de dados 3D recomendada pelo próprio Dice So Nice para uso standalone. Ela oferece:

- **BabylonJS** (engine profissional): rendering PBR, sombras, iluminação HDR
- **AmmoJS** (port do Bullet Physics via Emscripten WASM): física rigorosa de corpos rígidos, colliders exatos para cada geometria de dado
- **Web workers + offscreenCanvas**: o loop de física e de rendering roda em thread separada — não bloqueia a UI do React, não causa jank
- **Sistema de temas**: diffuse map, normal map, specular map por tema; `themeColor` ajustável por HEX
- **Física configurável**: `gravity`, `mass`, `friction`, `restitution`, `angularDamping`, `linearDamping`, `spinForce`, `throwForce`, `startingHeight`, `settleTimeout`
- **API simples e estável**: `init()`, `roll(notation)`, `clear()`, `updateConfig()`, `onRollComplete` callback

## Goals / Non-Goals

**Goals:**
- Animações 3D de alta qualidade com física real (Bullet Physics)
- Desempenho sem janks: web workers isolam o rendering da UI
- Tema visual WFRP: dados escuros
- Resultado server-authoritative sempre exibido como texto de resultado
- Fallback 2D para `prefers-reduced-motion` / WebGL ausente

**Non-Goals:**
- Faces de dados mostrando o valor exato do servidor (animação é decorativa)
- Sistema de temas customizados além de `themeColor`
- Dados diferentes de d10 (WFRP usa d100 = 2×d10)
- Sons de impacto de dado (fora do escopo desta mudança)

## Architecture

```
page.tsx
  └── Dice3DOverlay.tsx            ← decide: 3D ou fallback 2D
        ├── DiceBoxWrapper.tsx     ← wrapper React do @3d-dice/dice-box
        │     └── DiceBox          ← BabylonJS + AmmoJS em web worker
        │           ├── world.offscreen.js  (servido de /assets/dice-box/)
        │           ├── Dice.js             (AmmoJS physics worker)
        │           └── themes/default/     (diffuse/normal/specular maps)
        └── DiceOverlay2D.tsx      ← fallback existente (mantido)
```

### Fluxo de rolagem

```
1. useSessionPlay.rollTest() → servidor retorna roll_results[0].roll = 47
2. Dice3DOverlay recebe prop `roll={47}` → muda de null para número
3. DiceBoxWrapper detecta mudança em `roll` → chama diceBox.roll("2d10")
4. BabylonJS renderiza animação (thread separada, ~2–4 segundos)
5. onRollComplete dispara → DiceBoxWrapper chama onSettled(47)  ← valor DO SERVIDOR, não do dado
6. Dice3DOverlay exibe overlay com "47" em destaque
7. Após 2s, onDismiss → clear() + overlay fecha
```

**Por que `onSettled` recebe o valor do servidor, não o da física?**

O `@3d-dice/dice-box` não suporta pré-determinação de outcome (isso era específico do fork `@3d-dice/dice-box-threejs`). A física rola livremente e os dados podem mostrar qualquer valor. A solução é:
- Chamar `roll("2d10")` para a animação (decorativa)
- Ignorar o valor retornado por `onRollComplete`
- Usar o valor do servidor (`props.roll`) para exibir o resultado

Isso é seguro e correto: o resultado do jogo vem sempre do servidor.

### Container e canvas

O `DiceBox` recebe `container` como seletor CSS ou elemento DOM. O componente `DiceBoxWrapper` renderiza um `<div id="dice-canvas-container">` e passa `container: "#dice-canvas-container"` na config. O BabylonJS injeta seu `<canvas>` dentro deste div.

### Assets estáticos

O package requer que os seguintes arquivos sejam servidos via HTTP (não bundlados):

```
public/assets/dice-box/
├── themes/
│   └── default/
│       ├── default.json
│       ├── diffuse-dark.png
│       ├── diffuse-light.png
│       ├── normal.png
│       ├── specular.jpg
│       └── theme.config.json
├── ammo/
│   └── ammo.wasm.wasm
├── Dice.js            (physics worker)
├── world.offscreen.js
├── world.onscreen.js
└── world.none.js
```

Origem: `node_modules/@3d-dice/dice-box/dist/` → cópia manual para `public/assets/dice-box/`.

Estes arquivos são grandes (Dice.js ≈ 1.4MB, world.offscreen.js ≈ 1.4MB) e binários → adicionados ao `.gitignore`.

### Next.js e web workers

O `@3d-dice/dice-box` constrói a URL do worker usando `assetPath + 'world.offscreen.js'`. Como esses arquivos estão em `public/`, o Next.js os serve como arquivos estáticos sem nenhuma configuração adicional de webpack. O dynamic import com `ssr: false` garante que o código não execute no servidor.

### Configuração física para estética WFRP

```javascript
{
  assetPath: "/assets/dice-box/",
  container: "#dice-canvas-container",
  gravity: 1,
  mass: 1,
  friction: 0.8,
  restitution: 0.3,       // leve bounce, não muito
  angularDamping: 0.4,
  linearDamping: 0.4,
  spinForce: 6,            // spin expressivo
  throwForce: 5,
  startingHeight: 8,
  settleTimeout: 5000,
  offscreen: true,         // usa offscreenCanvas quando disponível
  enableShadows: true,
  shadowTransparency: 0.8,
  lightIntensity: 1.2,
  theme: "default",
  themeColor: "#1a120b",   // couro escuro WFRP
  scale: 6,
  onRollComplete: handleComplete
}
```

## Risks / Trade-offs

| Risco | Mitigação |
|---|---|
| Dado mostra valor diferente do resultado do servidor | Overlay de texto exibe sempre o valor do servidor; animação é declarada como decorativa |
| Assets grandes (total ~4MB) não são servidos de CDN | Servidos localmente de `public/`; comprimidos pelo servidor (gzip/br) em produção |
| `themeColor` pode não cobrir números dourados | Aceitar limitação visual de tema; dados escuros já identificam o WFRP |
| Web workers podem não funcionar em alguns browsers | `offscreen: false` no fallback; browser coverage >97% suporta web workers |
| Inicialização assíncrona ~500ms (carrega WASM) | Spinner durante `init()`; não bloqueia a UI |
| OffscreenCanvas não disponível em Firefox < 105 | Package faz fallback automático para `world.onscreen.js` |

## Open Questions (respondidas)

- **Predetermined outcomes?** Não disponível na versão BabylonJS; animação é decorativa ✓
- **Worker files precisam de webpack config?** Não; são servidos de `public/` como estáticos ✓
- **SSR é problema?** Resolvido com `next/dynamic` + `ssr: false` ✓
- **three e cannon-es ficam no projeto?** Sim, mas não são usados pelos dados 3D; podem ser removidos em mudança futura separada ✓
