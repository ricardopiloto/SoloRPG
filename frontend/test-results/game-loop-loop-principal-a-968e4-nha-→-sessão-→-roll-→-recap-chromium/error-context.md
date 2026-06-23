# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: game-loop.spec.ts >> loop principal: auth → pregen → campanha → sessão → roll → recap
- Location: e2e/game-loop.spec.ts:22:5

# Error details

```
Error: locator.click: Target page, context or browser has been closed
Call log:
  - waiting for getByRole('button', { name: /Iniciar sessão/ })

```

```
Error: browserContext.close: Target page, context or browser has been closed
```