import pytest

from app.rules.careers import validate_xp
from app.rules.combat import resolve_melee_attack
from app.rules.criticals import resolve_critical
from app.rules.dice import roll_d100, roll_d10
from app.rules.fate import spend_fate_point
from app.rules.tests import resolve_test
from app.llm.signals import parse_signals


def test_roll_d100_range():
    for _ in range(100):
        assert 1 <= roll_d100() <= 100


def test_roll_d10_range():
    for _ in range(50):
        assert 1 <= roll_d10() <= 10


def test_resolve_test_success():
    result = resolve_test(50, skill_advances=2, modifier=0)
    assert result.target == 52
    assert isinstance(result.success, bool)


def test_melee_attack_structure():
    attack = resolve_melee_attack(40, 30, 4, 0, 2, "personagem", "inimigo", "Espada")
    assert attack.attacker == "personagem"
    assert attack.damage >= 0 or not attack.hit


def test_critical_result():
    crit = resolve_critical()
    assert 1 <= crit.severity <= 5
    assert crit.effect


def test_fate_point_spend():
    ok = spend_fate_point(2, 12)
    assert ok.success
    assert ok.fate_remaining == 1
    assert ok.wounds_after == 1

    fail = spend_fate_point(0, 12)
    assert not fail.success


def test_xp_validation():
    assert validate_xp(10) == 30
    assert validate_xp(50) == 50
    assert validate_xp(200) == 100


def test_signal_parser():
    text = """Você avança.

[TESTE]
{"tipo": "teste_atributo", "atributo": "Ag", "modificador": 0, "descricao": "teste"}
[/TESTE]

O que você faz?"""
    parsed = parse_signals(text)
    assert len(parsed.signals) == 1
    assert parsed.signals[0].tag == "TESTE"
    assert "Você avança" in parsed.narrative
