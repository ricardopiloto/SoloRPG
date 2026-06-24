# Tasks: remove-quickroll-countdown

- [x] **T1** Em `QuickRollPopover.tsx`: remover `const [countdown, setCountdown] = useState(2)`
- [x] **T2** Em `QuickRollPopover.tsx`: remover o `useEffect` inteiro (os 5 lines que decrementam countdown e disparam `onRoll`)
- [x] **T3** Em `QuickRollPopover.tsx`: remover `{!rolling && <p>Rolando em {countdown}s…</p>}` do JSX
- [x] **T4** Import de `useEffect` removido (não havia outros usos no arquivo)
- [x] **T5** Lint / TypeScript check: nenhum erro
