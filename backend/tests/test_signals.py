"""Tests for GM signal parsing and narrative sanitization."""

from app.llm.signals import parse_signals, strip_signal_artifacts


def test_nova_campanha_typo_close_tag_extracted_and_stripped():
    text = """[NOVA_CAMPANHA] {"tom": "sombrio", "ponto_de_partida": "Bögenhafen"} [/NOVA_CAMAPANHA]

Severin inclina a cabeça."""
    parsed = parse_signals(text)
    assert len(parsed.signals) == 1
    assert parsed.signals[0].tag == "NOVA_CAMPANHA"
    assert parsed.signals[0].payload["tom"] == "sombrio"
    assert "NOVA_CAMPANHA" not in parsed.narrative
    assert "Severin inclina" in parsed.narrative
    assert "sombrio" not in parsed.narrative


def test_musica_removed_from_narrative():
    text = """[MUSICA]
{"mood":"tensão","descricao":"perseguição"}
[/MUSICA]

Você corre pelos becos."""
    parsed = parse_signals(text)
    assert parsed.signals[0].tag == "MUSICA"
    assert "MUSICA" not in parsed.narrative
    assert "Você corre" in parsed.narrative


def test_strip_preserves_dialogue_with_brackets():
    text = "— [sussurra] algo na escuridão."
    assert strip_signal_artifacts(text) == text


def test_loose_block_stripped_without_parseable_signal():
    text = '[TESTE] {"broken": } [/TESTE]\n\nNarração limpa.'
    parsed = parse_signals(text)
    assert len(parsed.signals) == 0
    assert "TESTE" not in parsed.narrative
    assert "Narração limpa" in parsed.narrative
