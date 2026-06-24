# Design: fix-progression-skill-advance-count

## Diagnóstico

### Fluxo atual

```
ProgressionPage.buySkill()
  → POST /characters/{id}/progression/skill
  → purchase_skill_advance()
      char.skills = apply_skill_advance(char.skills, name, attr)
      char.xp_spent += 5
      db.commit()
  → GET /characters/{id}/progression
  → get_progression_options()
      owned_skills = {name: advances for s in char.skills}
      current_advances = owned_skills.get(skill_name, 0)
```

### Reprodução (script local)

```python
for _ in range(4):
    await purchase_skill_advance(db, char.id, "Percepção", "I")
# xp_spent == 20  ✓
# skills[-1]["advances"] == 1  ✗ (esperado 4)
```

### Por que só a primeira compra persiste

`PlayerCharacter.skills` é `Mapped[list] = mapped_column(JSON)`.

`apply_skill_advance` hoje:

```python
updated = list(skills)          # cópia rasa — mesmos dicts internos
for skill in updated:
    if skill["name"] == skill_name:
        skill["advances"] += 1    # mutação in-place no dict
        return updated
```

SQLAlchemy compara o JSON serializado antes/depois do `commit`. A cópia rasa com dict mutado pode não alterar o snapshot que o ORM considera "dirty" para updates subsequentes na mesma sessão, enquanto `xp_spent` (inteiro escalar) sempre persiste.

A **primeira** compra funciona porque adiciona um **novo dict** à lista (`append`), mudando a estrutura de forma detectável.

---

## Solução

### 1. `apply_skill_advance` imutável

```python
def apply_skill_advance(skills: list, skill_name: str, linked_attribute: str) -> list:
    for i, skill in enumerate(skills):
        if skill.get("name") == skill_name:
            new_adv = skill.get("advances", 0) + 1
            return [
                *skills[:i],
                {**skill, "advances": new_adv},
                *skills[i + 1 :],
            ]
    return [
        *skills,
        {"name": skill_name, "advances": 1, "linked_attribute": linked_attribute},
    ]
```

Cada compra produz lista e dicts novos → JSON serializado sempre diferente.

### 2. `flag_modified` (reforço)

Em `purchase_skill_advance`, após atribuir `char.skills`:

```python
from sqlalchemy.orm.attributes import flag_modified
flag_modified(char, "skills")
```

Baixo custo; protege contra edge cases do tipo JSON no SQLite.

### 3. Agregação na leitura

```python
def skill_advances_by_name(skills: list) -> dict[str, int]:
    totals: dict[str, int] = {}
    for s in skills or []:
        name = s.get("name")
        if name:
            totals[name] = totals.get(name, 0) + s.get("advances", 0)
    return totals
```

Usado em `get_progression_options` no lugar do dict comprehension que sobrescreve duplicatas.

### 4. UI — talentos

Trocar string literal em `progression/page.tsx`:

```tsx
{talent.owned && " · adquirido"}
```

---

## Validação

| Caso | Esperado |
|------|----------|
| 0 compras de Percepção | `atual +0` |
| 1 compra | `atual +1`, `xp_spent +5` |
| 4 compras | `atual +4`, `xp_spent +20` |
| Compra de talento owned | botão desabilitado, texto `· adquirido` |
| Sidebar em sessão | target de Percepção usa `I + advances` corretos |

---

## Riscos

| Risco | Mitigação |
|-------|-----------|
| Personagens com XP gasto mas avanços subcontados | Jogador pode comprar de novo se tiver XP; ou ajuste manual no DB |
| Duplicatas legadas no JSON | Soma na leitura + testes |
| Testes existentes fracos | `test_api_progression_after_xp` só verifica 1 compra — estender para N compras |
