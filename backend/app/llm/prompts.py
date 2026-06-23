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


def load_character_background_prompt() -> str:
    docs_path = Path(__file__).resolve().parents[3] / "Docs" / "character-background-prompt.md"
    if not docs_path.exists():
        return _fallback_background_prompt()
    content = docs_path.read_text(encoding="utf-8")
    start = content.find("```")
    if start == -1:
        return _fallback_background_prompt()
    start = content.find("\n", start) + 1
    end = content.find("```", start)
    return content[start:end].strip()


def _fallback_background_prompt() -> str:
    return (
        "Escreva um background curto em PT-BR para um personagem de WFRP4e. "
        "Tom sombrio. Apenas prosa, sem stats ou tags de jogo."
    )


def _fallback_prompt() -> str:
    return (
        "Você é o Mestre de uma campanha solo WFRP4e. "
        "Nunca quebre personagem. Responda em PT-BR. "
        "Emita sinais [TESTE], [IMAGEM], [FIM_SESSAO] conforme necessário."
    )
