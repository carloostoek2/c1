"""
Tests básicos para Fase 5 - Narrativa.

Tests simples que validan las funcionalidades core:
1. Sistema de flags
2. Delays en fragmentos
3. Campos extendidos en modelos
"""
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import asyncio
from bot.database.engine import init_db, get_session
from bot.narrative.services.container import NarrativeContainer


@pytest.mark.asyncio
async def test_flags_basic():
    """Test básico: Setear, obtener y verificar flags."""
    # Inicializar BD
    await init_db()

    async with get_session() as session:
        container = NarrativeContainer(session)
        user_id = 888888

        # Setear flag
        await container.progress.set_flag(user_id, "test_flag", True)

        # Obtener flag
        value = await container.progress.get_flag(user_id, "test_flag")
        assert value is True, "Flag debería ser True"

        # Verificar existencia
        exists = await container.progress.has_flag(user_id, "test_flag")
        assert exists is True, "Flag debería existir"

        # Flag inexistente
        exists = await container.progress.has_flag(user_id, "nonexistent")
        assert exists is False, "Flag inexistente no debería existir"

    print("✅ Test flags básico: PASÓ")


@pytest.mark.asyncio
async def test_phase5_model_fields():
    """Test básico: Campos Fase 5 en modelos."""
    await init_db()

    async with get_session() as session:
        from bot.narrative.database.enums import ChapterType

        container = NarrativeContainer(session)

        # Crear capítulo con campos Fase 5
        chapter = await container.chapter.create_chapter(
            name="Test Chapter Phase5",
            slug="test-phase5-chapter",
            chapter_type=ChapterType.FREE,
            description="Test"
        )

        # Setear campos Fase 5
        chapter.level = 1
        chapter.favor_reward = 10.0
        chapter.badge_reward = "test_badge"

        await session.commit()

        # Verificar que se guardaron
        assert chapter.level == 1
        assert chapter.favor_reward == 10.0
        assert chapter.badge_reward == "test_badge"

    print("✅ Test campos Fase 5: PASÓ")


@pytest.mark.asyncio
async def test_delay_field():
    """Test básico: Campo delay_seconds en fragmento."""
    await init_db()

    async with get_session() as session:
        from bot.narrative.database.enums import ChapterType

        container = NarrativeContainer(session)

        # Crear capítulo
        chapter = await container.chapter.create_chapter(
            name="Test Delay Chapter",
            slug="test-delay-chapter",
            chapter_type=ChapterType.FREE
        )

        # Crear fragmento con delay
        fragment = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="test_delayed_fragment",
            title="Delayed Fragment",
            speaker="diana",
            content="This has delay"
        )

        # Setear delay
        fragment.delay_seconds = 3

        await session.commit()

        # Verificar
        assert fragment.delay_seconds == 3

    print("✅ Test delay_seconds: PASÓ")


if __name__ == "__main__":
    # Ejecutar tests directamente
    asyncio.run(test_flags_basic())
    asyncio.run(test_phase5_model_fields())
    asyncio.run(test_delay_field())
    print("\n🎉 Todos los tests básicos PASARON")
