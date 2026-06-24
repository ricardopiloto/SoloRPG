from dataclasses import dataclass, field
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Campaign, CharacterStatus, GameSession, MapRegion
from app.llm.adapter import get_llm_adapter
from app.llm.prompts import load_gm_system_prompt
from app.llm.signals import ParsedSignal, parse_signals
from app.rules.careers import validate_xp
from app.rules.criticals import apply_wounds, resolve_critical
from app.rules.fate import spend_fate_point, spend_fortune_point
from app.rules.tests import resolve_test
from app.services.campaign import apply_nova_campanha, mark_campaign_unfinished
from app.services.memory import load_memory_context, persist_session_summary
from app.services.session import (
    advance_combat_turn,
    append_turn,
    end_combat,
    end_session,
    enter_combat,
    session_time_remaining_minutes,
    should_end_session,
)


@dataclass
class TurnResult:
    narrative: str = ""
    roll_results: list[dict] = field(default_factory=list)
    images: list[dict] = field(default_factory=list)
    session_ended: bool = False
    xp_awarded: int = 0
    player_summary: str | None = None
    signals_processed: list[str] = field(default_factory=list)
    turn_phase: str = "normal"
    pending_test: dict | None = None
    combat_state: dict | None = None
    scene_mood: str | None = None


from app.rules.skills import SKILL_CATALOG

# Verb stems (≥4 chars) that trigger inventory checking.
# Using stems covers infinitives and common conjugations (e.g. "sac" → saco/saca/sacar/sacou).
_INVENTORY_VERB_STEMS = [
    "sacar", "saco", "saca", "sacou",
    "usar", "uso", "usa", "usou",
    "pegar", "pego", "pega", "pegou",
    "empunhar", "empunho", "empunha", "empunhou",
    "equipar", "equipo", "equipa", "equipou",
    "atirar", "atiro", "atira", "atirou",
    "lancar", "lanco", "lanca", "lancou",
    "beber", "bebo", "bebe", "bebeu",
    "aplicar", "aplico", "aplica", "aplicou",
    "carregar", "carrego", "carrega", "carregou",
    "erguer", "ergo", "ergue", "ergueu",
    "tirar", "tiro", "tira", "tirou",
    "desembainhar", "desembainho", "desembainhou",
    "empurrar", "empurro", "empurra", "empurrou",
    "utilizar", "utilizo", "utiliza", "utilizou",
    "segurar", "seguro", "segura", "segurou",
]


def _normalize(text: str) -> str:
    import unicodedata
    nfkd = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _check_inventory_reference(action: str, trappings: list[dict]) -> str | None:
    """
    Heuristic check: if the player action contains an inventory-use verb/conjugation
    followed by tokens that match no trapping name, return a system-note string.
    Returns None when no absent item is detected or when detection is inconclusive.
    """
    norm_action = _normalize(action)
    action_words = norm_action.split()
    norm_trapping_names = [_normalize(t.get("name", "")) for t in trappings]

    for i, word in enumerate(action_words):
        if word not in _INVENTORY_VERB_STEMS:
            continue

        # Extract the next up to 4 words as item candidate
        tokens = action_words[i + 1: i + 5]
        if not tokens:
            continue
        candidate = " ".join(tokens)

        # Skip filler/preposition-only candidates
        fillers = {"minha", "meu", "seu", "sua", "o", "a", "um", "uma", "de", "da", "do", "em", "na", "no"}
        meaningful = [t for t in tokens if t not in fillers]
        if not meaningful:
            continue
        candidate = " ".join(meaningful)

        # Check whether any trapping name covers the candidate
        found = any(
            norm_name and (norm_name in candidate or candidate in norm_name)
            for norm_name in norm_trapping_names
            if norm_name
        )
        if not found:
            inventory_list = ", ".join(
                t.get("name", "") for t in trappings if t.get("name")
            ) or "(inventário vazio)"
            item_label = " ".join(meaningful[:3])
            return (
                f"[NOTA DO SISTEMA — INVENTÁRIO] O jogador mencionou \"{item_label}\". "
                f"Este item NÃO consta no inventário do personagem: {inventory_list}. "
                "Negue o uso narrativamente dentro do universo do jogo sem quebrar personagem."
            )

    return None


class GMOrchestrator:
    def __init__(self) -> None:
        self.llm = get_llm_adapter()
        self.system_prompt = load_gm_system_prompt()

    async def _load_session(self, db: AsyncSession, session_id: UUID) -> GameSession:
        session = await db.scalar(
            select(GameSession)
            .where(GameSession.id == session_id)
            .options(selectinload(GameSession.campaign).selectinload(Campaign.character))
        )
        if not session or not session.is_active:
            raise ValueError("Sessão inválida ou encerrada")
        return session

    def _to_turn_result(self, result: TurnResult, session: GameSession) -> TurnResult:
        result.turn_phase = session.turn_phase
        result.pending_test = session.pending_test
        result.combat_state = session.combat_state
        return result

    async def process_turn(
        self, db: AsyncSession, session_id: UUID, player_action: str
    ) -> TurnResult:
        session = await self._load_session(db, session_id)
        if session.turn_phase == "awaiting_roll":
            raise ValueError("Rolagem pendente — clique em 'Rolar dado' antes de continuar")
        if session.turn_phase == "awaiting_narrate":
            raise ValueError("Aguardando narração da rolagem — conclua o teste atual")

        campaign = session.campaign
        character = campaign.character
        result = TurnResult()

        await append_turn(db, session, "player", player_action)

        encerrar = should_end_session(session)
        memory = await load_memory_context(db, campaign, session, query=player_action)
        context_xml = self._build_context(campaign, character, session, memory, {
            "primeira_sessao": session.is_first_session,
            "encerrar_sessao": encerrar,
        })

        inventory_note = _check_inventory_reference(
            player_action, character.trappings or []
        )
        action_block = (
            f"{inventory_note}\n\nAção do jogador: {player_action}"
            if inventory_note
            else f"Ação do jogador: {player_action}"
        )
        messages = [
            {"role": "user", "content": f"{context_xml}\n\n{action_block}"},
        ]

        llm_text = await self.llm.complete(self.system_prompt, messages)
        parsed = parse_signals(llm_text)

        for signal in parsed.signals:
            if signal.tag == "TESTE":
                continue
            result.signals_processed.append(signal.tag)
            await self._handle_signal(db, session, campaign, character, signal, result)

        test_signals = [s for s in parsed.signals if s.tag == "TESTE"]
        if test_signals:
            result.signals_processed.append("TESTE")
            session.pending_test = {
                "payload": test_signals[0].payload,
                "setup_narrative": parsed.narrative,
                "all_payloads": [s.payload for s in test_signals],
            }
            session.turn_phase = "awaiting_roll"
            result.narrative = parsed.narrative
            result.pending_test = session.pending_test
            await db.commit()
        else:
            result.narrative = parsed.narrative
            await append_turn(db, session, "gm", result.narrative, {"rolls": result.roll_results})

        if encerrar and not result.session_ended and session.turn_phase == "normal":
            result.narrative += "\n\n[O tempo da sessão está acabando. Conduza a um ponto de pausa natural.]"

        return self._to_turn_result(result, session)

    async def execute_roll(
        self, db: AsyncSession, session_id: UUID, roll_override: int | None = None
    ) -> TurnResult:
        session = await self._load_session(db, session_id)
        if session.turn_phase != "awaiting_roll" or not session.pending_test:
            raise ValueError("Nenhum teste pendente para rolar")

        campaign = session.campaign
        character = campaign.character
        result = TurnResult()
        pending = session.pending_test
        payloads = pending.get("all_payloads") or [pending.get("payload", {})]

        roll_texts = []
        wounds_before = character.wounds_current
        for payload in payloads:
            roll_data = self._resolve_test_signal(character, payload, roll_override=roll_override)
            result.roll_results.append(roll_data)
            roll_texts.append(roll_data["llm_text"])
            await self._apply_roll_wounds(db, session, campaign, character, roll_data, result)

        session.pending_roll_result = {
            "roll_results": result.roll_results,
            "roll_texts": roll_texts,
            "setup_narrative": pending.get("setup_narrative", ""),
            "payloads": payloads,
            "wounds_before": wounds_before,
            "fortune_reroll_used": False,
        }
        session.pending_test = None
        session.turn_phase = "awaiting_narrate"
        await db.commit()

        result.turn_phase = session.turn_phase
        result.combat_state = session.combat_state
        return result

    async def execute_fortune_reroll(
        self, db: AsyncSession, session_id: UUID, roll_override: int | None = None
    ) -> TurnResult:
        session = await self._load_session(db, session_id)
        if session.turn_phase != "awaiting_narrate" or not session.pending_roll_result:
            raise ValueError("Nenhum teste aguardando re-roll com Fortuna")

        campaign = session.campaign
        character = campaign.character
        stored = session.pending_roll_result
        prior_results = stored.get("roll_results", [])
        if not any(r.get("success") is False for r in prior_results):
            raise ValueError("Teste bem-sucedido — Fortuna não aplicável")
        if stored.get("fortune_reroll_used", False):
            raise ValueError("Fortuna já usada neste teste — apenas um re-roll permitido")

        fortune = spend_fortune_point(character.fortune_current, "reroll")
        if not fortune.success:
            raise ValueError(fortune.message)

        character.fortune_current = fortune.fortune_remaining
        character.wounds_current = stored.get("wounds_before", character.wounds_current)

        result = TurnResult()
        roll_texts = []
        payloads = stored.get("payloads") or []
        for payload in payloads:
            roll_data = self._resolve_test_signal(character, payload, roll_override=roll_override)
            result.roll_results.append(roll_data)
            roll_texts.append(roll_data["llm_text"])
            await self._apply_roll_wounds(db, session, campaign, character, roll_data, result)

        session.pending_roll_result = {
            **stored,
            "roll_results": result.roll_results,
            "roll_texts": roll_texts,
            "wounds_before": stored.get("wounds_before", character.wounds_current),
            "fortune_reroll_used": True,
        }
        await db.commit()

        result.turn_phase = session.turn_phase
        result.combat_state = session.combat_state
        return result

    async def narrate_roll(self, db: AsyncSession, session_id: UUID) -> TurnResult:
        session = await self._load_session(db, session_id)
        if session.turn_phase != "awaiting_narrate" or not session.pending_roll_result:
            raise ValueError("Nenhuma rolagem aguardando narração")

        campaign = session.campaign
        character = campaign.character
        stored = session.pending_roll_result
        result = TurnResult(roll_results=stored.get("roll_results", []))

        memory = await load_memory_context(db, campaign, session)
        context_xml = self._build_context(campaign, character, session, memory, {})
        setup = stored.get("setup_narrative", "")
        roll_texts = stored.get("roll_texts", [])

        messages = [
            {"role": "user", "content": context_xml},
            {"role": "assistant", "content": setup},
            {"role": "user", "content": "Resultado do teste:\n" + "\n".join(roll_texts)},
        ]

        narrative = await self.llm.complete(self.system_prompt, messages)
        parsed = parse_signals(narrative)

        for signal in parsed.signals:
            if signal.tag == "TESTE":
                continue
            result.signals_processed.append(signal.tag)
            await self._handle_signal(db, session, campaign, character, signal, result)

        result.narrative = parsed.narrative or narrative
        session.pending_roll_result = None
        session.turn_phase = "normal"
        await append_turn(db, session, "gm", result.narrative, {"rolls": result.roll_results})
        await db.commit()

        return self._to_turn_result(result, session)

    async def stream_narrate_roll(self, db: AsyncSession, session_id: UUID):
        import json

        session = await self._load_session(db, session_id)
        if session.turn_phase != "awaiting_narrate" or not session.pending_roll_result:
            raise ValueError("Nenhuma rolagem aguardando narração")

        campaign = session.campaign
        character = campaign.character
        stored = session.pending_roll_result
        result = TurnResult(roll_results=stored.get("roll_results", []))

        memory = await load_memory_context(db, campaign, session)
        context_xml = self._build_context(campaign, character, session, memory, {})
        setup = stored.get("setup_narrative", "")
        roll_texts = stored.get("roll_texts", [])

        messages = [
            {"role": "user", "content": context_xml},
            {"role": "assistant", "content": setup},
            {"role": "user", "content": "Resultado do teste:\n" + "\n".join(roll_texts)},
        ]

        llm_text_parts: list[str] = []
        async for chunk in self.llm.stream(self.system_prompt, messages):
            llm_text_parts.append(chunk)
            yield f"data: {json.dumps({'type': 'token', 'content': chunk}, ensure_ascii=False)}\n\n"

        llm_text = "".join(llm_text_parts)
        parsed = parse_signals(llm_text)

        for signal in parsed.signals:
            if signal.tag == "TESTE":
                continue
            result.signals_processed.append(signal.tag)
            await self._handle_signal(db, session, campaign, character, signal, result)

        narrative = parsed.narrative or llm_text
        result.narrative = narrative
        session.pending_roll_result = None
        session.turn_phase = "normal"
        await append_turn(db, session, "gm", result.narrative, {"rolls": result.roll_results})
        await db.commit()

        done_payload = {
            "type": "done",
            "narrative": narrative,
            "roll_results": result.roll_results,
            "images": result.images,
            "session_ended": result.session_ended,
            "xp_awarded": result.xp_awarded,
            "player_summary": result.player_summary,
            "time_remaining_minutes": session_time_remaining_minutes(session),
            "mode": session.mode.value,
            "turn_phase": session.turn_phase,
            "pending_test": None,
            "combat_state": session.combat_state,
            "scene_mood": result.scene_mood,
        }
        yield f"data: {json.dumps(done_payload, ensure_ascii=False)}\n\n"

    async def execute_quick_roll(
        self,
        db: AsyncSession,
        session_id: UUID,
        roll_type: str,
        key: str,
        modifier: int = 0,
        roll_override: int | None = None,
    ):
        from app.schemas.api import QuickRollResponse

        session = await self._load_session(db, session_id)
        if session.turn_phase == "awaiting_roll" or session.pending_test:
            raise ValueError("Resolva o teste do GM antes de rolar na sidebar")

        character = session.campaign.character
        attrs = character.attributes or {}
        attr_val = 30
        skill_advances = 0
        label = key

        roll_type = roll_type.lower()
        if roll_type == "attribute":
            if key not in attrs:
                raise ValueError(f"Atributo '{key}' não encontrado")
            attr_val = attrs[key]
        elif roll_type == "skill":
            if key not in SKILL_CATALOG:
                raise ValueError(f"Perícia '{key}' inválida")
            linked = SKILL_CATALOG[key]
            attr_val = attrs.get(linked, 30)
            skill = next((s for s in (character.skills or []) if s.get("name") == key), None)
            skill_advances = skill.get("advances", 0) if skill else 0
        elif roll_type == "weapon":
            trapping = next((t for t in (character.trappings or []) if t.get("name") == key), None)
            if not trapping:
                raise ValueError(f"Arma '{key}' não encontrada")
            attr_val = attrs.get("WS", 30)
        else:
            raise ValueError("roll_type deve ser attribute, skill ou weapon")

        test = resolve_test(attr_val, skill_advances, modifier, label, roll=roll_override)
        result_label = "sucesso" if test.success else "falha"
        spontaneous_note = (
            f"[NOTA DO SISTEMA] O jogador verificou {label} ({roll_type}) espontaneamente "
            f"— resultado: {result_label} ({test.roll} vs {test.target}). "
            "Nenhum [TESTE] foi solicitado por você. Reaja narrativamente ao gesto físico do personagem "
            "sem criar uma situação retroativa para justificar o dado."
        )
        roll_data = {
            "type": "quick_roll",
            "roll_type": roll_type,
            "key": key,
            "roll": test.roll,
            "target": test.target,
            "success": test.success,
            "levels": test.levels,
            "modifier": modifier,
            "llm_text": test.to_llm_text(label),
        }
        await append_turn(db, session, "system", spontaneous_note, {"quick_roll": roll_data})
        await db.commit()

        return QuickRollResponse(
            roll=test.roll,
            target=test.target,
            success=test.success,
            levels=test.levels,
            roll_type=roll_type,
            key=key,
            modifier=modifier,
            narration_hint=roll_data["llm_text"],
        )

    async def stream_turn(self, db: AsyncSession, session_id: UUID, player_action: str):
        import json

        session = await self._load_session(db, session_id)
        if session.turn_phase == "awaiting_roll":
            raise ValueError("Rolagem pendente — clique em 'Rolar dado' antes de continuar")
        if session.turn_phase == "awaiting_narrate":
            raise ValueError("Aguardando narração da rolagem — conclua o teste atual")

        campaign = session.campaign
        character = campaign.character
        result = TurnResult()

        await append_turn(db, session, "player", player_action)

        encerrar = should_end_session(session)
        memory = await load_memory_context(db, campaign, session, query=player_action)
        context_xml = self._build_context(campaign, character, session, memory, {
            "primeira_sessao": session.is_first_session,
            "encerrar_sessao": encerrar,
        })

        inventory_note = _check_inventory_reference(
            player_action, character.trappings or []
        )
        action_block = (
            f"{inventory_note}\n\nAção do jogador: {player_action}"
            if inventory_note
            else f"Ação do jogador: {player_action}"
        )
        messages = [
            {"role": "user", "content": f"{context_xml}\n\n{action_block}"},
        ]

        llm_text_parts: list[str] = []
        async for chunk in self.llm.stream(self.system_prompt, messages):
            llm_text_parts.append(chunk)
            yield f"data: {json.dumps({'type': 'token', 'content': chunk}, ensure_ascii=False)}\n\n"

        llm_text = "".join(llm_text_parts)
        parsed = parse_signals(llm_text)

        for signal in parsed.signals:
            if signal.tag == "TESTE":
                continue
            result.signals_processed.append(signal.tag)
            await self._handle_signal(db, session, campaign, character, signal, result)

        test_signals = [s for s in parsed.signals if s.tag == "TESTE"]
        if test_signals:
            result.signals_processed.append("TESTE")
            session.pending_test = {
                "payload": test_signals[0].payload,
                "setup_narrative": parsed.narrative,
                "all_payloads": [s.payload for s in test_signals],
            }
            session.turn_phase = "awaiting_roll"
            result.narrative = parsed.narrative
            result.pending_test = session.pending_test
            await db.commit()
        else:
            narrative = parsed.narrative
            result.narrative = narrative
            await append_turn(db, session, "gm", result.narrative, {"rolls": result.roll_results})

            if encerrar and not result.session_ended:
                suffix = "\n\n[O tempo da sessão está acabando. Conduza a um ponto de pausa natural.]"
                narrative += suffix
                yield f"data: {json.dumps({'type': 'token', 'content': suffix}, ensure_ascii=False)}\n\n"

        done_payload = {
            "type": "done",
            "narrative": result.narrative,
            "roll_results": result.roll_results,
            "images": result.images,
            "session_ended": result.session_ended,
            "xp_awarded": result.xp_awarded,
            "player_summary": result.player_summary,
            "time_remaining_minutes": session_time_remaining_minutes(session),
            "mode": session.mode.value,
            "turn_phase": session.turn_phase,
            "pending_test": session.pending_test,
            "combat_state": session.combat_state,
            "scene_mood": result.scene_mood,
        }
        yield f"data: {json.dumps(done_payload, ensure_ascii=False)}\n\n"

    def _build_context(self, campaign, character, session, memory, flags) -> str:
        from app.services.memory import build_context_xml
        return build_context_xml(campaign, character, session, memory, flags)

    async def _handle_signal(
        self, db, session, campaign, character, signal: ParsedSignal, result: TurnResult
    ) -> None:
        if signal.tag == "NOVA_CAMPANHA":
            await apply_nova_campanha(db, campaign, signal.payload)
            mins = signal.payload.get("duracao_estimada_sessao_minutos", 45)
            session.duration_minutes = mins

        elif signal.tag == "IMAGEM":
            if not session.images_enabled:
                return
            from app.services.images import queue_image, placeholder_url
            image_type = signal.payload.get("tipo", "cena")
            description = signal.payload.get("descricao", "")
            job = await queue_image(
                db,
                campaign.id,
                session.id,
                image_type,
                description,
                signal.payload.get("prioridade", "normal"),
            )
            result.images.append({
                "job_id": str(job.id),
                "type": job.image_type,
                "status": job.status,
                "url": job.image_url,
            })
            if image_type == "mapa":
                db.add(
                    MapRegion(
                        campaign_id=campaign.id,
                        name=description[:120] or "Região",
                        description=description,
                        image_url=job.image_url or placeholder_url("mapa"),
                        revealed=True,
                    )
                )
                await db.commit()

        elif signal.tag == "FIM_SESSAO":
            xp = validate_xp(signal.payload.get("resumo_sistema", {}).get("xp_sugerido", 50))
            player_summary = signal.payload.get("resumo_jogador", "")
            system_summary = signal.payload.get("resumo_sistema", {})
            await persist_session_summary(db, campaign, session, player_summary, system_summary)
            await end_session(db, session, xp)
            result.session_ended = True
            result.xp_awarded = xp
            result.player_summary = player_summary

        elif signal.tag == "ACAO_SISTEMA":
            await self._handle_system_action(db, session, campaign, character, signal.payload, result)

        elif signal.tag == "ESTADO_COMBATE":
            await self._handle_combat_state(db, session, campaign, character, signal.payload, result)

        elif signal.tag == "MUSICA":
            mood = signal.payload.get("mood")
            if mood in ("tensão", "normal"):
                result.scene_mood = mood

    async def _handle_combat_state(self, db, session, campaign, character, payload, result):
        action = payload.get("acao", "sincronizar")

        if action == "iniciar":
            combatants = payload.get("combatentes")
            if not combatants:
                attrs = character.attributes or {}
                combatants = [
                    {
                        "nome": character.name,
                        "agility": attrs.get("Ag", 30),
                        "tipo": "player",
                    }
                ]
                for enemy in payload.get("inimigos", []):
                    combatants.append({
                        "nome": enemy.get("nome", "Inimigo"),
                        "agility": enemy.get("agilidade", enemy.get("agility", 30)),
                        "tipo": "npc",
                    })
            state = await enter_combat(db, session, combatants)
            result.combat_state = state

        elif action == "avancar":
            state = await advance_combat_turn(db, session)
            result.combat_state = state

        elif action == "encerrar":
            await end_combat(db, session)
            result.combat_state = None

        else:
            if payload.get("estado"):
                session.combat_state = payload["estado"]
            state = dict(session.combat_state or {})
            if payload.get("turno"):
                state["turn"] = payload["turno"]
                if payload.get("ativo_index") is not None:
                    state["current_index"] = payload["ativo_index"]
            inimigos = payload.get("inimigos")
            if inimigos is not None:
                for enemy_update in inimigos:
                    nome = enemy_update.get("nome")
                    status = enemy_update.get("status")
                    for combatant in state.get("combatants", []):
                        if combatant.get("nome") == nome:
                            combatant["status"] = status
            proxima_acao = payload.get("proxima_acao")
            if proxima_acao is not None:
                state["proxima_acao"] = proxima_acao
            session.combat_state = state
            if payload.get("modo") == "EXPLORACAO":
                await end_combat(db, session)
                result.combat_state = None
            else:
                await db.commit()
                result.combat_state = session.combat_state

    async def _handle_system_action(self, db, session, campaign, character, payload, result):
        tipo = payload.get("tipo")
        if tipo == "usar_ponto_destino":
            motivo = payload.get("motivo", "avoid_death")
            if motivo not in ("avoid_wound", "avoid_death"):
                motivo = "avoid_death"
            fate = spend_fate_point(
                character.fate_current,
                character.wounds_current,
                character.wounds_max,
                reason=motivo,
            )
            if fate.success:
                character.fate_current = fate.fate_remaining
                character.wounds_current = fate.wounds_after
                result.roll_results.append({"type": "fate", "message": fate.message, "motivo": motivo})
            await db.commit()
        elif tipo == "usar_ponto_fortuna":
            effect = payload.get("efeito", "reroll")
            fortune = spend_fortune_point(character.fortune_current, effect)
            if fortune.success:
                character.fortune_current = fortune.fortune_remaining
                result.roll_results.append({
                    "type": "fortune",
                    "message": fortune.message,
                })
            await db.commit()
        elif tipo == "morte_personagem":
            character.status = CharacterStatus.DEAD
            character.wounds_current = 0
            await mark_campaign_unfinished(db, campaign.id, payload.get("causa", ""))
            session.is_active = False
            result.session_ended = True
            await db.commit()

    async def _apply_roll_wounds(self, db, session, campaign, character, roll_data, result):
        if roll_data.get("wounds_applied"):
            character.wounds_current = roll_data["wounds_after"]
            if roll_data["wounds_after"] == 0 and roll_data.get("critical"):
                crit = resolve_critical()
                roll_data["critical_effect"] = crit.effect
                if crit.lethal and character.fate_current <= 0:
                    character.status = CharacterStatus.DEAD
                    await mark_campaign_unfinished(db, campaign.id, crit.effect)
                    result.session_ended = True
            await db.commit()

    def _resolve_test_signal(
        self, character, payload: dict, roll_override: int | None = None
    ) -> dict:
        from app.rules.combat import resolve_melee_attack, resolve_ranged_attack

        attrs = character.attributes or {}
        tipo = payload.get("tipo", "teste_atributo")

        if tipo == "teste_atributo":
            attr_name = payload.get("atributo", "Ag")
            attr_val = attrs.get(attr_name, 30)
            skill_name = payload.get("pericia")
            skill_advances = 0
            if skill_name:
                for s in character.skills or []:
                    if s.get("name") == skill_name:
                        skill_advances = s.get("advances", 0)
            from app.rules.tests import resolve_test
            test = resolve_test(
                attr_val,
                skill_advances,
                payload.get("modificador", 0),
                payload.get("descricao", ""),
                roll=roll_override,
            )
            return {
                "type": "test",
                "roll": test.roll,
                "target": test.target,
                "success": test.success,
                "levels": test.levels,
                "llm_text": test.to_llm_text(attr_name),
                "skill": skill_name,
                "attribute": attr_name,
                "modifier": payload.get("modificador", 0),
            }

        if tipo == "ataque_cc":
            ws = attrs.get("WS", 30)
            s = attrs.get("S", 30)
            attack = resolve_melee_attack(
                ws,
                s,
                payload.get("bonus_arma", 0),
                payload.get("modificador", 0),
                payload.get("reducao_dano", 0),
                payload.get("atacante", "personagem"),
                payload.get("alvo", "inimigo"),
                payload.get("arma", "arma"),
                roll=roll_override,
            )
            data = {
                "type": "melee",
                "roll": attack.test.roll,
                "target": attack.test.target,
                "success": attack.hit,
                "damage": attack.damage,
                "llm_text": attack.to_llm_text(),
            }
            if attack.hit and payload.get("alvo", "").lower() in ("personagem", character.name.lower()):
                wounds_after, at_zero = apply_wounds(character.wounds_current, attack.damage)
                data["wounds_applied"] = True
                data["wounds_after"] = wounds_after
                data["critical"] = attack.critical and at_zero
            return data

        if tipo == "ataque_distancia":
            bs = attrs.get("BS", 30)
            s = attrs.get("S", 25)
            attack = resolve_ranged_attack(
                bs,
                payload.get("modificador", 0),
                payload.get("alcance", "medio"),
                s,
                payload.get("reducao_dano", 0),
                payload.get("atacante", "personagem"),
                payload.get("alvo", "inimigo"),
                payload.get("arma", "arma"),
                roll=roll_override,
            )
            data = {
                "type": "ranged",
                "roll": attack.test.roll,
                "target": attack.test.target,
                "success": attack.hit,
                "damage": attack.damage,
                "llm_text": attack.to_llm_text(),
            }
            if attack.hit and payload.get("alvo", "").lower() in ("personagem", character.name.lower()):
                wounds_after, at_zero = apply_wounds(character.wounds_current, attack.damage)
                data["wounds_applied"] = True
                data["wounds_after"] = wounds_after
                data["critical"] = attack.critical and at_zero
            return data

        return {"type": "unknown", "llm_text": "Teste não reconhecido."}
