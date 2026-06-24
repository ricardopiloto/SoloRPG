# session-ux Specification

## Purpose
TBD - created by archiving change update-session-pausable-ux. Update Purpose after archive.
## Requirements
### Requirement: Hint do input reflete capacidade de pausa

O texto de dica exibido abaixo do campo de ação durante a sessão (quando não há teste pendente) SHALL indicar que o jogador pode pausar usando o botão no header, em vez de afirmar incorretamente que a sessão não é pausável.

#### Scenario: Hint correto durante exploração sem teste pendente

- **Dado** que o jogador está numa sessão ativa no modo EXPLORAÇÃO
- **E** não há teste pendente (`awaitingRoll === false`)
- **Quando** a área de input é renderizada
- **Então** o hint SHALL exibir "Use ⏸ no topo para pausar." (ou equivalente)
- **E** o hint SHALL NOT conter a palavra "não pausável" ou qualquer afirmação de impossibilidade de pausa

#### Scenario: Hint de teste pendente não é afetado

- **Dado** que há um teste pendente (`awaitingRoll === true`)
- **Quando** a área de input é renderizada
- **Então** o hint SHALL exibir a mensagem de teste pendente inalterada

---

### Requirement: Overlay de início informa pausabilidade corretamente

O modal exibido antes do início da sessão (`SessionPrepareOverlay`) SHALL informar que a sessão pode ser pausada e retomada, em vez de afirmar que não pode ser pausada.

#### Scenario: Texto correto no modal de início

- **Dado** que o jogador abre o modal de início de sessão
- **Quando** `SessionPrepareOverlay` é renderizado
- **Então** o texto SHALL conter a duração estimada em minutos
- **E** o texto SHALL afirmar que a sessão pode ser pausada e retomada ("pausar e retomar quando quiser" ou equivalente)
- **E** o texto SHALL NOT conter "não pode ser pausada" ou qualquer afirmação negativa sobre pausa

---

### Requirement: Documentação técnica reflete sessões pausáveis

Os documentos `openspec/project.md`, `README.md`, `Docs/product-brief.md` e `Docs/mvp-validation-checklist.md` SHALL descrever sessões como pausáveis, alinhando-se com a implementação real do `add-session-pause-resume`.

#### Scenario: project.md atualizado

- **Dado** que `openspec/project.md` contém a restrição de sessão
- **Então** o documento SHALL descrever sessões como pausáveis com opção de retomada
- **E** SHALL NOT afirmar que sessões são não-pausáveis

#### Scenario: README e Docs atualizados

- **Dado** que `README.md` e `Docs/` descrevem as sessões do sistema
- **Então** esses documentos SHALL descrever sessões como pausáveis
- **E** SHALL NOT mencionar limitação de pausa que não existe mais

