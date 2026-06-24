# Tasks: refine-chat-attribution-visual

## 1. CSS — `globals.css`

- [x] 1.1 Adicionar classe `.chat-attribution` com estilo do eyebrow GM:
  `text-[10px] uppercase tracking-[0.18em] text-wfrp-accent/40 mb-1 select-none font-sans`
- [x] 1.2 Adicionar modificador `.chat-attribution--player` para alinhar à direita:
  `text-right mr-2`

## 2. `ChatLog.tsx` — Agrupamento de turnos por autor

- [x] 2.1 Implementar função `isGroupStart(entries, index)` que verifica se a entrada atual inicia um novo grupo — percorre para trás ignorando entradas `other` para comparar com o último autor
- [x] 2.2 No render da entrada `narrative` (GM): quando `isGroupStart === true`, renderizar `<div className="chat-attribution">Mestre</div>` imediatamente antes do `<MarkdownNarrative>`
- [x] 2.3 No render da entrada `player`: quando `isGroupStart === true`, renderizar `<div className="chat-attribution chat-attribution--player">Você</div>` imediatamente antes do `<p className="player-line">`
- [x] 2.4 Entradas do tipo `roll`, `image` e `dice-roll` quebram sequência mas NÃO recebem label próprio — o próximo bloco `narrative` ou `player` após elas começa um novo grupo com `isGroupStart: true`

## 3. Validação

- [x] 3.1 `npm run build` — zero erros TypeScript ✓
- [ ] 3.2 Revisão visual: turno GM seguido de outro turno GM mostra "MESTRE" apenas antes do primeiro
- [ ] 3.3 Revisão visual: turno do jogador intercalado redefine o grupo — próximo GM tem "MESTRE" novamente
- [ ] 3.4 Revisão visual: labels têm opacidade baixa o suficiente para não chamar atenção em primeira leitura, mas legíveis ao focar
- [ ] 3.5 Confirmar que `select-none` impede que o texto "MESTRE" / "VOCÊ" seja copiado junto com a narrativa
