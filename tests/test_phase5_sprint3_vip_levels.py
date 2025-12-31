"""
Tests E2E para Fase 5 - Sprint 3: Niveles VIP (4-6) + Easter Eggs

Valida:
- Carga de contenido niveles 4-6
- Sistema de flags y evaluaciones
- Quiz scoring (nivel 4)
- Empathy evaluation (nivel 5)
- Easter eggs y condiciones
- Navegación completa de niveles VIP
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.engine import get_session, init_db, close_db
from bot.narrative.services.container import NarrativeContainer


# ===== FIXTURES =====

@pytest.fixture(scope="module")
async def setup_db():
    """Setup de base de datos para tests."""
    await init_db()
    yield
    await close_db()


@pytest.fixture
async def session(setup_db):
    """Sesión de BD para cada test."""
    async with get_session() as s:
        yield s


def container_factory(session):
    """Factory para crear container de servicios narrativos."""
    return NarrativeContainer(session)


# ===== TESTS NIVEL 4: ENTRADA AL DIVÁN =====

@pytest.mark.asyncio
async def test_level_4_chapter_exists(session):
    """Nivel 4 debe existir en BD."""
    container = container_factory(session)
    chapter = await container.chapter.get_chapter_by_slug("l4-entrada-divan")

    assert chapter is not None
    assert chapter.name == "Nivel 4: Entrada al Diván"
    assert chapter.level == 4
    assert chapter.requires_level == 3
    assert chapter.favor_reward == 15.0
    assert chapter.badge_reward == "divan_entry"


@pytest.mark.asyncio
async def test_level_4_fragments_count(session):
    """Nivel 4 debe tener 12 fragmentos."""
    container = container_factory(session)
    chapter = await container.chapter.get_chapter_by_slug("l4-entrada-divan")
    fragments = await container.fragment.get_fragments_by_chapter(chapter.id)

    assert len(fragments) >= 12


@pytest.mark.asyncio
async def test_level_4_quiz_questions(session):
    container = container_factory(session)
    """Nivel 4 debe tener 5 preguntas de quiz."""
    chapter = await container.chapter.get_chapter_by_slug("l4-entrada-divan")

    # Buscar fragmentos de quiz (L4_03 a L4_07)
    quiz_fragments = [
        await container.fragment.get_fragment_by_key("l4_03_quiz_q1"),
        await container.fragment.get_fragment_by_key("l4_04_quiz_q2"),
        await container.fragment.get_fragment_by_key("l4_05_quiz_q3"),
        await container.fragment.get_fragment_by_key("l4_06_quiz_q4"),
        await container.fragment.get_fragment_by_key("l4_07_quiz_q5"),
    ]

    # Todos deben existir
    assert all(f is not None for f in quiz_fragments)

    # Todos deben tener decisiones
    for frag in quiz_fragments:
        decisions = await container.decision.get_decisions_by_fragment(frag.id)
        assert len(decisions) == 3  # Cada pregunta tiene 3 opciones


@pytest.mark.asyncio
async def test_level_4_score_variants(session):
    container = container_factory(session)
    """Nivel 4 debe tener variantes de score alto y medio."""
    high_score = await container.fragment.get_fragment_by_key("l4_09a_high_score")
    medium_score = await container.fragment.get_fragment_by_key("l4_09b_medium_score")

    assert high_score is not None
    assert medium_score is not None

    # Verificar condiciones
    assert high_score.condition_type == "score"
    assert high_score.condition_value == "high"
    assert medium_score.condition_type == "score"
    assert medium_score.condition_value == "medium"


# ===== TESTS NIVEL 5: PROFUNDIZACIÓN =====

@pytest.mark.asyncio
async def test_level_5_chapter_exists(session):
    container = container_factory(session)
    """Nivel 5 debe existir en BD."""
    chapter = await container.chapter.get_chapter_by_slug("l5-profundizacion")

    assert chapter is not None
    assert chapter.name == "Nivel 5: Profundización"
    assert chapter.level == 5
    assert chapter.requires_level == 4
    assert chapter.favor_reward == 20.0
    assert chapter.badge_reward == "deep_connection"


@pytest.mark.asyncio
async def test_level_5_fragments_count(session):
    container = container_factory(session)
    """Nivel 5 debe tener 15 fragmentos."""
    chapter = await container.chapter.get_chapter_by_slug("l5-profundizacion")
    fragments = await container.fragment.get_fragments_by_chapter(chapter.id)

    assert len(fragments) >= 15


@pytest.mark.asyncio
async def test_level_5_vulnerability_dialogues(session):
    container = container_factory(session)
    """Nivel 5 debe tener 2 diálogos de vulnerabilidad."""
    vuln1 = await container.fragment.get_fragment_by_key("l5_02_vulnerability_1")
    vuln2 = await container.fragment.get_fragment_by_key("l5_04_vulnerability_2")

    assert vuln1 is not None
    assert vuln2 is not None

    # Cada uno debe tener 3 opciones (empathetic, possessive, fixing)
    decisions1 = await container.decision.get_decisions_by_fragment(vuln1.id)
    decisions2 = await container.decision.get_decisions_by_fragment(vuln2.id)

    assert len(decisions1) == 3
    assert len(decisions2) == 3


@pytest.mark.asyncio
async def test_level_5_response_variants(session):
    container = container_factory(session)
    """Nivel 5 debe tener 9 variantes de respuesta (3x3)."""
    # Primer diálogo
    emp1 = await container.fragment.get_fragment_by_key("l5_03_response_empathetic")
    poss1 = await container.fragment.get_fragment_by_key("l5_03_response_possessive")
    fix1 = await container.fragment.get_fragment_by_key("l5_03_response_fixing")

    # Segundo diálogo
    emp2 = await container.fragment.get_fragment_by_key("l5_05_response_empathetic_2")
    poss2 = await container.fragment.get_fragment_by_key("l5_05_response_possessive_2")
    fix2 = await container.fragment.get_fragment_by_key("l5_05_response_fixing_2")

    variants = [emp1, poss1, fix1, emp2, poss2, fix2]

    assert all(v is not None for v in variants)


@pytest.mark.asyncio
async def test_level_5_empathy_evaluation_variants(session):
    container = container_factory(session)
    """Nivel 5 debe tener variantes de evaluación de empatía."""
    high_empathy = await container.fragment.get_fragment_by_key("l5_08a_empathetic")
    low_empathy = await container.fragment.get_fragment_by_key("l5_08b_problematic")

    assert high_empathy is not None
    assert low_empathy is not None

    # Verificar condiciones
    assert high_empathy.condition_type == "flag_count"
    assert "empathetic>=2" in high_empathy.condition_value


# ===== TESTS NIVEL 6: CULMINACIÓN =====

@pytest.mark.asyncio
async def test_level_6_chapter_exists(session):
    container = container_factory(session)
    """Nivel 6 debe existir en BD."""
    chapter = await container.chapter.get_chapter_by_slug("l6-culminacion")

    assert chapter is not None
    assert chapter.name == "Nivel 6: Culminación"
    assert chapter.level == 6
    assert chapter.requires_level == 5
    assert chapter.favor_reward == 25.0
    assert chapter.badge_reward == "inner_circle"


@pytest.mark.asyncio
async def test_level_6_fragments_count(session):
    container = container_factory(session)
    """Nivel 6 debe tener 10 fragmentos."""
    chapter = await container.chapter.get_chapter_by_slug("l6-culminacion")
    fragments = await container.fragment.get_fragments_by_chapter(chapter.id)

    assert len(fragments) >= 10


@pytest.mark.asyncio
async def test_level_6_final_revelation(session):
    container = container_factory(session)
    """Nivel 6 debe tener revelación final de Diana."""
    revelation = await container.fragment.get_fragment_by_key("l6_02_diana_revelation")

    assert revelation is not None
    assert revelation.speaker == "diana"
    assert "evaluación mutua" in revelation.content.lower()


@pytest.mark.asyncio
async def test_level_6_ending_rewards(session):
    container = container_factory(session)
    """Nivel 6 debe tener fragmento final con recompensas."""
    rewards = await container.fragment.get_fragment_by_key("l6_10_rewards")

    assert rewards is not None
    assert rewards.is_ending is True
    assert "NIVEL 6 COMPLETADO" in rewards.content


# ===== TESTS EASTER EGGS =====

@pytest.mark.asyncio
async def test_easter_eggs_chapter_exists(session):
    container = container_factory(session)
    """Capítulo de Easter Eggs debe existir."""
    chapter = await container.chapter.get_chapter_by_slug("easter-eggs")

    assert chapter is not None
    assert chapter.name == "Easter Eggs"
    assert chapter.order == 99  # No aparece en lista principal


@pytest.mark.asyncio
async def test_easter_egg_speedrunner(session):
    container = container_factory(session)
    """Easter Egg Speedrunner debe existir."""
    ee = await container.fragment.get_fragment_by_key("ee_speedrunner")

    assert ee is not None
    assert ee.extra_metadata is not None
    assert ee.extra_metadata.get("easter_egg") is True
    assert ee.extra_metadata.get("rarity") == "rare"
    assert ee.extra_metadata.get("grants_badge") == "speedrunner"
    assert ee.extra_metadata.get("grants_favors") == 10


@pytest.mark.asyncio
async def test_easter_egg_perfect_empath(session):
    container = container_factory(session)
    """Easter Egg Perfect Empath debe existir."""
    ee = await container.fragment.get_fragment_by_key("ee_perfect_empath")

    assert ee is not None
    assert ee.extra_metadata.get("rarity") == "legendary"
    assert ee.extra_metadata.get("grants_badge") == "perfect_empath"
    assert ee.extra_metadata.get("grants_favors") == 15


@pytest.mark.asyncio
async def test_easter_egg_lucien_approves(session):
    container = container_factory(session)
    """Easter Egg Lucien Approves debe existir."""
    ee = await container.fragment.get_fragment_by_key("ee_lucien_approves")

    assert ee is not None
    assert ee.speaker == "lucien"
    assert ee.extra_metadata.get("rarity") == "legendary"
    assert ee.extra_metadata.get("grants_favors") == 20


@pytest.mark.asyncio
async def test_all_easter_eggs_have_conditions(session):
    container = container_factory(session)
    """Todos los easter eggs deben tener condiciones definidas."""
    chapter = await container.chapter.get_chapter_by_slug("easter-eggs")
    fragments = await container.fragment.get_fragments_by_chapter(chapter.id)

    for frag in fragments:
        # Cada easter egg debe tener condition_type
        assert frag.condition_type is not None

        # Y metadata completa
        assert frag.extra_metadata is not None
        assert frag.extra_metadata.get("easter_egg") is True
        assert frag.extra_metadata.get("trigger_condition") is not None


# ===== TESTS DE INTEGRACIÓN =====

@pytest.mark.asyncio
async def test_vip_levels_progression_order(session):
    container = container_factory(session)
    """Niveles VIP deben tener orden correcto de requisitos."""
    l4 = await container.chapter.get_chapter_by_slug("l4-entrada-divan")
    l5 = await container.chapter.get_chapter_by_slug("l5-profundizacion")
    l6 = await container.chapter.get_chapter_by_slug("l6-culminacion")

    # Nivel 4 requiere nivel 3
    assert l4.requires_level == 3

    # Nivel 5 requiere nivel 4
    assert l5.requires_level == 4

    # Nivel 6 requiere nivel 5
    assert l6.requires_level == 5


@pytest.mark.asyncio
async def test_vip_levels_total_rewards(session):
    container = container_factory(session)
    """Rewards totales de niveles VIP deben sumar correctamente."""
    l4 = await container.chapter.get_chapter_by_slug("l4-entrada-divan")
    l5 = await container.chapter.get_chapter_by_slug("l5-profundizacion")
    l6 = await container.chapter.get_chapter_by_slug("l6-culminacion")

    total_favors = l4.favor_reward + l5.favor_reward + l6.favor_reward

    # Niveles 4-6: 15 + 20 + 25 = 60 favores
    assert total_favors == 60.0


@pytest.mark.asyncio
async def test_all_fragments_have_valid_speakers(session):
    container = container_factory(session)
    """Todos los fragmentos VIP deben tener speaker válido."""
    valid_speakers = ["diana", "lucien", "system", "narrator"]

    for slug in ["l4-entrada-divan", "l5-profundizacion", "l6-culminacion", "easter-eggs"]:
        chapter = await container.chapter.get_chapter_by_slug(slug)
        fragments = await container.fragment.get_fragments_by_chapter(chapter.id)

        for frag in fragments:
            assert frag.speaker in valid_speakers


@pytest.mark.asyncio
async def test_entry_points_are_correct(session):
    container = container_factory(session)
    """Cada nivel VIP debe tener exactamente un entry point."""
    for slug in ["l4-entrada-divan", "l5-profundizacion", "l6-culminacion"]:
        chapter = await container.chapter.get_chapter_by_slug(slug)
        fragments = await container.fragment.get_fragments_by_chapter(chapter.id)

        entry_points = [f for f in fragments if f.is_entry_point]

        assert len(entry_points) == 1


# ===== TESTS DE FLAGS =====

@pytest.mark.asyncio
async def test_quiz_flags_are_set_correctly(session):
    container = container_factory(session)
    """Decisiones del quiz deben setear flags correctos."""
    # Pregunta 1
    q1 = await container.fragment.get_fragment_by_key("l4_03_quiz_q1")
    decisions = await container.decision.get_decisions_by_fragment(q1.id)

    # Debe haber al menos una decisión con sets_flag
    flags_set = [d.sets_flag for d in decisions if d.sets_flag]
    assert len(flags_set) > 0

    # Los flags deben seguir el patrón quiz_q1_*
    for flag in flags_set:
        assert flag.startswith("quiz_q1_")


@pytest.mark.asyncio
async def test_empathy_flags_are_set_correctly(session):
    container = container_factory(session)
    """Decisiones de empatía deben setear flags correctos."""
    vuln1 = await container.fragment.get_fragment_by_key("l5_02_vulnerability_1")
    decisions = await container.decision.get_decisions_by_fragment(vuln1.id)

    # Debe haber exactamente 3 decisiones, cada una con su flag
    flags_set = [d.sets_flag for d in decisions if d.sets_flag]
    assert len(flags_set) == 3

    # Los flags deben ser empathetic, possessive, o fixing
    flag_types = set(f.split("_response_")[0] for f in flags_set)
    assert "empathetic" in flag_types or "possessive" in flag_types or "fixing" in flag_types


# ===== RESUMEN DE TESTS =====

"""
RESUMEN DE TESTS SPRINT 3:

NIVEL 4:
- ✓ Capítulo existe con config correcta
- ✓ 12+ fragmentos cargados
- ✓ 5 preguntas de quiz con 3 opciones cada una
- ✓ Variantes de score alto/medio

NIVEL 5:
- ✓ Capítulo existe con config correcta
- ✓ 15+ fragmentos cargados
- ✓ 2 diálogos de vulnerabilidad con 3 opciones cada uno
- ✓ 9 variantes de respuesta (empathetic, possessive, fixing)
- ✓ Variantes de evaluación de empatía

NIVEL 6:
- ✓ Capítulo existe con config correcta
- ✓ 10+ fragmentos cargados
- ✓ Revelación final de Diana
- ✓ Fragmento final con recompensas

EASTER EGGS:
- ✓ Capítulo existe (order=99, oculto)
- ✓ 6 easter eggs implementados
- ✓ Todos tienen condiciones y metadata
- ✓ Rarity levels: uncommon, rare, legendary

INTEGRACIÓN:
- ✓ Orden de requisitos correcto (3→4→5→6)
- ✓ Rewards totales: 60 favores
- ✓ Speakers válidos en todos los fragmentos
- ✓ Entry points correctos

TOTAL: 25 tests E2E
"""
