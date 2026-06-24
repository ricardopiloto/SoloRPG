# Change: Melhorias de UX no chat de jogo

## Why

A área de narrativa do chat exibe texto puro, sem renderização Markdown. Negrito, itálico e outros elementos visuais que o GM emite chegam ao jogador como caracteres literais (`**palavra**`), quebrando a imersão. Além disso, novas mensagens não recebem foco automático, obrigando o jogador a rolar manualmente. Não há registro visível das rolagens feitas durante a sessão.

## What Changes

- **Markdown no chat narrativo:** blocos de narrativa do GM e resumos renderizam Markdown (negrito, itálico, listas, separadores). Linhas do jogador e mensagens de sistema permanecem sem renderização para distinguir visualmente.
- **Auto-scroll:** toda vez que uma nova entrada é adicionada ao ChatLog, a visualização rola automaticamente para a última mensagem. Durante streaming, o scroll segue token a token.
- **Histórico de rolagens na sidebar direita:** nova aba "Rolagens" na DiarySidebar mostra todas as rolagens da sessão em ordem cronológica (atributo/perícia testado, valor rolado, alvo, sucesso/falha, níveis de sucesso).

## Impact

- Affected specs: `session-ui`
- Affected code:
  - `frontend/src/components/session/ChatLog.tsx` — adicionar react-markdown para blocos narrativos; adicionar ref de scroll
  - `frontend/src/components/diary/DiarySidebar.tsx` — adicionar aba "Rolagens"
  - `frontend/src/hooks/useSessionPlay.ts` — acumular histórico de rolls da sessão
  - `frontend/src/app/play/[sessionId]/page.tsx` — passar rolls para DiarySidebar
- New dependency: `react-markdown` (frontend)
