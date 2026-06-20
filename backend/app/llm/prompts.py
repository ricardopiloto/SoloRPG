from pathlib import Path


def load_gm_system_prompt() -> str:
    docs_path = Path(__file__).resolve().parents[3] / "Docs" / "gm-system-prompt.md"
    if not docs_path.exists():
        return _fallback_prompt()
    content = docs_path.read_text(encoding="utf-8")
    start = content.find("```")
    if start == -1:
        return _fallback_prompt()
    start = content.find("\n", start) + 1
    end = content.find("```", start)
    return content[start:end].strip()


def _fallback_prompt() -> str:
    return (
        "Você é o Mestre de uma campanha solo WFRP4e. "
        "Nunca quebre personagem. Responda em PT-BR. "
        "Emita sinais [TESTE], [IMAGEM], [FIM_SESSAO] conforme necessário."
    )
