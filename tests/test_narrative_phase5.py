"""
Tests para funcionalidades de Fase 5 - Narrativa.

Cubre:
- Sistema de flags narrativos
- Integración de flags en decisiones
- Delays entre fragmentos
- Campos extendidos en modelos
"""
import pytest
from bot.database.engine import init_db, get_session
from bot.narrative.services.container import NarrativeContainer
from bot.narrative.database.enums import ChapterType


@pytest.fixture(scope="session", autouse=True)
async def init_database():
    """Inicializa BD una sola vez para todos los tests."""
    await init_db()


async def create_test_data():
    """Helper para crear datos de prueba."""
    async with get_session() as session:
        container = NarrativeContainer(session)

        # Crear capítulo de prueba
        chapter = await container.chapter.create_chapter(
            name="Test Chapter",
            slug="test-chapter-phase5",
            chapter_type=ChapterType.FREE,
            description="Capítulo de prueba"
        )

        # Crear fragmento de prueba
        fragment = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="test_fragment_phase5",
            title="Test Fragment",
            speaker="diana",
            content="Test content",
            order=0,
            is_entry_point=True
        )

        await session.commit()

        return container, chapter, fragment


@pytest.mark.asyncio
async def test_set_and_get_flag():
    """Test: Setear y obtener flags narrativos."""
    async with get_session() as session:
        container = NarrativeContainer(session)
        user_id = 999991

        # Setear flag
        result = await container.progress.set_flag(user_id, "curious", True)
        assert result is True

        # Obtener flag
        value = await container.progress.get_flag(user_id, "curious")
        assert value is True

        # Flag inexistente retorna default
        value = await container.progress.get_flag(user_id, "nonexistent", False)
        assert value is False


@pytest.mark.asyncio
async def test_has_flag():
    """Test: Verificar existencia de flags."""
    async with get_session() as session:
        container = NarrativeContainer(session)
        user_id = 999992

        # Flag no existe inicialmente
        exists = await container.progress.has_flag(user_id, "test_flag")
        assert exists is False

        # Setear flag
        await container.progress.set_flag(user_id, "test_flag", "some_value")

        # Flag ahora existe
        exists = await container.progress.has_flag(user_id, "test_flag")
        assert exists is True


@pytest.mark.asyncio
async def test_get_all_flags():
    """Test: Obtener todos los flags de un usuario."""
    async with get_session() as session:
        container = NarrativeContainer(session)
        user_id = 999993

        # Sin flags inicialmente
        flags = await container.progress.get_all_flags(user_id)
        assert flags == {}

        # Agregar múltiples flags
        await container.progress.set_flag(user_id, "curious", True)
        await container.progress.set_flag(user_id, "reaction_time", 45)
        await container.progress.set_flag(user_id, "depth", True)

        # Verificar todos los flags
        flags = await container.progress.get_all_flags(user_id)
        assert len(flags) == 3
        assert flags["curious"] is True
        assert flags["reaction_time"] == 45
        assert flags["depth"] is True


@pytest.mark.asyncio
async def test_clear_flag():
    """Test: Eliminar flag específico."""
    async with get_session() as session:
        container = NarrativeContainer(session)
        user_id = 999994

        # Setear flag
        await container.progress.set_flag(user_id, "test_flag", True)

        # Verificar que existe
        exists = await container.progress.has_flag(user_id, "test_flag")
        assert exists is True

        # Eliminar flag
        result = await container.progress.clear_flag(user_id, "test_flag")
        assert result is True

        # Verificar que ya no existe
        exists = await container.progress.has_flag(user_id, "test_flag")
        assert exists is False

        # Intentar eliminar flag inexistente
        result = await container.progress.clear_flag(user_id, "nonexistent")
        assert result is False


@pytest.mark.asyncio
async def test_decision_sets_flag():
    """Test: Decisión setea flag automáticamente."""
    async with get_session() as session:
        container = NarrativeContainer(session)
        container_test, chapter, fragment = await create_test_data()

    user_id = 12345

    # Crear fragmento destino
    target_fragment = await container.fragment.create_fragment(
        chapter_id=chapter.id,
        fragment_key="target_fragment",
        title="Target",
        speaker="diana",
        content="Target content",
        order=1
    )

    # Crear decisión con sets_flag
    decision = await container.decision.create_decision(
        fragment_id=fragment.id,
        button_text="Test Decision",
        target_fragment_key="target_fragment",
        sets_flag="test_decision_flag"
    )

    # Verificar que el flag NO existe antes de tomar la decisión
    has_flag = await container.progress.has_flag(user_id, "test_decision_flag")
    assert has_flag is False

    # Procesar decisión
    success, msg, next_frag = await container.decision.process_decision(
        user_id=user_id,
        decision_id=decision.id
    )

    assert success is True
    assert next_frag.fragment_key == "target_fragment"

    # Verificar que el flag FUE seteado
    has_flag = await container.progress.has_flag(user_id, "test_decision_flag")
    assert has_flag is True

    flag_value = await container.progress.get_flag(user_id, "test_decision_flag")
    assert flag_value is True


@pytest.mark.asyncio
async def test_decision_requires_flag(setup_narrative):
    """Test: Decisión con requires_flag solo visible si usuario tiene el flag."""
    container, chapter, fragment = await setup_narrative

    user_id = 12345

    # Crear fragmento destino
    await container.fragment.create_fragment(
        chapter_id=chapter.id,
        fragment_key="target_fragment",
        title="Target",
        speaker="diana",
        content="Target content",
        order=1
    )

    # Crear decisión pública (sin requires_flag)
    public_decision = await container.decision.create_decision(
        fragment_id=fragment.id,
        button_text="Public Decision",
        target_fragment_key="target_fragment"
    )

    # Crear decisión con requires_flag
    private_decision = await container.decision.create_decision(
        fragment_id=fragment.id,
        button_text="Private Decision",
        target_fragment_key="target_fragment",
        requires_flag="secret_flag"
    )

    # Sin el flag, solo debe verse la decisión pública
    decisions = await container.decision.get_available_decisions(
        fragment_key=fragment.fragment_key,
        user_id=user_id
    )

    assert len(decisions) == 1
    assert decisions[0].id == public_decision.id

    # Setear el flag requerido
    await container.progress.set_flag(user_id, "secret_flag", True)

    # Ahora deben verse ambas decisiones
    decisions = await container.decision.get_available_decisions(
        fragment_key=fragment.fragment_key,
        user_id=user_id
    )

    assert len(decisions) == 2
    decision_ids = [d.id for d in decisions]
    assert public_decision.id in decision_ids
    assert private_decision.id in decision_ids


@pytest.mark.asyncio
async def test_fragment_delay_field(setup_narrative):
    """Test: Campo delay_seconds en fragmento."""
    container, chapter, _ = await setup_narrative

    # Crear fragmento con delay
    fragment = await container.fragment.create_fragment(
        chapter_id=chapter.id,
        fragment_key="delayed_fragment",
        title="Delayed Fragment",
        speaker="diana",
        content="This appears after delay",
        order=2
    )

    # Configurar delay
    fragment.delay_seconds = 3

    async with get_session() as session:
        await session.commit()

    # Verificar que el delay se guardó
    async with get_session() as session:
        frag = await container.fragment.get_fragment("delayed_fragment")
        assert frag.delay_seconds == 3


@pytest.mark.asyncio
async def test_chapter_phase5_fields(setup_narrative):
    """Test: Campos Fase 5 en capítulo."""
    container, chapter, _ = await setup_narrative

    # Configurar campos Fase 5
    chapter.level = 1
    chapter.favor_reward = 10.0
    chapter.badge_reward = "test_badge"
    chapter.estimated_duration_minutes = 15

    async with get_session() as session:
        await session.commit()

    # Verificar campos guardados
    async with get_session() as session:
        loaded_chapter = await container.chapter.get_chapter_by_slug("test-chapter")
        assert loaded_chapter.level == 1
        assert loaded_chapter.favor_reward == 10.0
        assert loaded_chapter.badge_reward == "test_badge"
        assert loaded_chapter.estimated_duration_minutes == 15


@pytest.mark.asyncio
async def test_user_progress_current_level(setup_narrative):
    """Test: Campo current_level en UserNarrativeProgress."""
    container, _, _ = await setup_narrative

    user_id = 12345

    # Obtener o crear progreso
    progress = await container.progress.get_or_create_progress(user_id)

    # Verificar que current_level está inicializado
    assert progress.current_level == 1

    # Cambiar nivel
    progress.current_level = 2

    async with get_session() as session:
        await session.commit()

    # Verificar que se guardó
    async with get_session() as session:
        loaded_progress = await container.progress.get_or_create_progress(user_id)
        assert loaded_progress.current_level == 2


# ========================================
# TESTS SPRINT 2 - NIVELES 2 Y 3
# ========================================

@pytest.mark.asyncio
async def test_archetype_detection_from_flags():
    """Test: Detección de arquetipo basada en flags narrativos del cuestionario."""
    from bot.narrative.services.archetype_detector import ArchetypeDetector
    from bot.narrative.database.enums import ArchetypeType

    async with get_session() as session:
        detector = ArchetypeDetector(session)

        # Test 1: EXPLORER (curious + mystery)
        flags_explorer = {
            "curious": True,
            "mystery": True,
            "seeking": True
        }
        archetype, confidence = detector.detect_from_narrative_flags(flags_explorer)
        assert archetype == ArchetypeType.EXPLORER
        assert confidence >= 0.6  # Al menos 60% confianza

        # Test 2: ROMANTIC (connection + personal)
        flags_romantic = {
            "connection": True,
            "personal": True,
            "attracted": True
        }
        archetype, confidence = detector.detect_from_narrative_flags(flags_romantic)
        assert archetype == ArchetypeType.ROMANTIC
        assert confidence >= 0.6

        # Test 3: ANALYTICAL (understanding + perceptive)
        flags_analytical = {
            "understanding": True,
            "perceptive": True,
            "verbal": True
        }
        archetype, confidence = detector.detect_from_narrative_flags(flags_analytical)
        assert archetype == ArchetypeType.ANALYTICAL
        assert confidence >= 0.6

        # Test 4: DIRECT (pleasure + visual)
        flags_direct = {
            "pleasure": True,
            "visual": True,
            "surface": True
        }
        archetype, confidence = detector.detect_from_narrative_flags(flags_direct)
        assert archetype == ArchetypeType.DIRECT
        assert confidence >= 0.6

        # Test 5: PATIENT (open + cautious)
        flags_patient = {
            "open": True,
            "cautious": True,
            "depth": True
        }
        archetype, confidence = detector.detect_from_narrative_flags(flags_patient)
        assert archetype == ArchetypeType.PATIENT
        assert confidence >= 0.6

        # Test 6: PERSISTENT (default si no hay flags claros)
        flags_persistent = {
            "intuitive": True
        }
        archetype, confidence = detector.detect_from_narrative_flags(flags_persistent)
        assert archetype == ArchetypeType.PERSISTENT
        assert confidence > 0.0


@pytest.mark.asyncio
async def test_active_mission_tracking():
    """Test: Tracking de misiones activas en UserNarrativeProgress."""
    from datetime import datetime, UTC

    async with get_session() as session:
        container = NarrativeContainer(session)
        user_id = 888881

        # Obtener progreso del usuario
        progress = await container.progress.get_or_create_progress(user_id)

        # Simular inicio de misión de observación
        progress.active_mission_id = "observation"
        progress.mission_started_at = datetime.now(UTC)
        progress.mission_data = {
            "hints_found": 0,
            "hints_required": 3,
            "mission_duration_hours": 72
        }

        await session.commit()

        # Verificar que se guardó
        await session.refresh(progress)
        assert progress.active_mission_id == "observation"
        assert progress.mission_data["hints_found"] == 0
        assert progress.mission_data["hints_required"] == 3

        # Simular progreso de misión
        # Necesitamos crear un nuevo dict y reasignarlo para que SQLAlchemy detecte el cambio
        mission_data = dict(progress.mission_data)  # Crear copia
        mission_data["hints_found"] = 2
        progress.mission_data = mission_data

        from sqlalchemy.orm import attributes
        attributes.flag_modified(progress, "mission_data")  # Marcar como modificado

        await session.commit()

        # Verificar progreso actualizado
        await session.refresh(progress)
        assert progress.mission_data["hints_found"] == 2


@pytest.mark.asyncio
async def test_multiple_flags_persistence():
    """Test: Múltiples flags narrativos persisten correctamente."""
    async with get_session() as session:
        container = NarrativeContainer(session)
        user_id = 888882

        # Simular cuestionario completo del Nivel 3
        questionnaire_flags = {
            "curious": True,
            "visual": True,
            "depth": True,
            "connection": True
        }

        # Setear todos los flags
        for flag_key, flag_value in questionnaire_flags.items():
            await container.progress.set_flag(user_id, flag_key, flag_value)

        # Commit para guardar cambios
        await session.commit()

        # Verificar que todos se guardaron
        all_flags = await container.progress.get_all_flags(user_id)

        assert len(all_flags) == 4
        assert all_flags["curious"] is True
        assert all_flags["visual"] is True
        assert all_flags["depth"] is True
        assert all_flags["connection"] is True


@pytest.mark.asyncio
async def test_narrative_flags_json_storage():
    """Test: Flags narrativos se almacenan correctamente en JSON."""
    async with get_session() as session:
        container = NarrativeContainer(session)
        user_id = 888883

        # Crear varios tipos de valores
        await container.progress.set_flag(user_id, "bool_flag", True)
        await container.progress.set_flag(user_id, "int_flag", 42)
        await container.progress.set_flag(user_id, "str_flag", "test_value")
        await container.progress.set_flag(user_id, "float_flag", 3.14)

        # Commit para guardar cambios
        await session.commit()

        # Obtener todos
        flags = await container.progress.get_all_flags(user_id)

        assert flags["bool_flag"] is True
        assert flags["int_flag"] == 42
        assert flags["str_flag"] == "test_value"
        assert flags["float_flag"] == 3.14


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
