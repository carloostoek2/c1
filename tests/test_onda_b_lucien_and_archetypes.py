"""
Tests E2E para ONDA B: Voz de Lucien + Arquetipos Avanzados.

Valida el funcionamiento de:
- LucienVoiceService
- AdvancedArchetypeService
- PersonalizationService
"""
import pytest
from datetime import datetime, timedelta

from bot.services.lucien_voice import LucienVoiceService
from bot.services.archetype_advanced import AdvancedArchetypeService
from bot.services.personalization import PersonalizationService
from bot.narrative.database.enums import ArchetypeType


@pytest.mark.asyncio
async def test_lucien_voice_welcome_messages(db_setup):
    """Test: Mensajes de bienvenida con voz de Lucien."""
    service = LucienVoiceService()

    # Usuario nuevo sin arquetipo
    message = await service.get_welcome_message("new_user")
    assert "Lucien" in message
    assert "Diana" in message

    # Usuario nuevo EXPLORER
    message_explorer = await service.get_welcome_message(
        "new_user", user_context={"archetype": "explorer"}
    )
    assert "curiosidad" in message_explorer.lower()

    # Usuario que regresa
    message_return = await service.get_welcome_message(
        "returning_user", user_context={"days_absent": 10}
    )
    assert "días" in message_return.lower()

    # Admin
    message_admin = await service.get_welcome_message("admin")
    assert "/admin" in message_admin


@pytest.mark.asyncio
async def test_lucien_voice_error_messages(db_setup):
    """Test: Mensajes de error con voz de Lucien."""
    service = LucienVoiceService()

    # Permission denied
    error = await service.format_error("permission_denied")
    assert "no es para ti" in error.lower()

    # Not configured
    error = await service.format_error(
        "not_configured", details={"element": "canal VIP"}
    )
    assert "canal VIP" in error
    assert "preparado" in error.lower()

    # Cooldown active
    error = await service.format_error(
        "cooldown_active", details={"time_seconds": 120}
    )
    assert "Diana" in error
    assert "minuto" in error.lower()


@pytest.mark.asyncio
async def test_lucien_voice_confirmation_messages(db_setup):
    """Test: Mensajes de confirmación con voz de Lucien."""
    service = LucienVoiceService()

    # Purchase complete
    confirmation = await service.format_confirmation(
        "purchase_complete",
        details={"item_name": "Fragmento I", "cost": 10},
    )
    assert "Fragmento I" in confirmation
    assert "10" in confirmation
    assert "Diana" in confirmation

    # Level up
    confirmation = await service.format_confirmation(
        "level_up", details={"level_name": "Iniciado"}
    )
    assert "Iniciado" in confirmation
    assert "progreso" in confirmation.lower()


@pytest.mark.asyncio
async def test_lucien_voice_notifications(db_setup):
    """Test: Notificaciones con voz de Lucien."""
    service = LucienVoiceService()

    # Streak milestone
    notification = await service.get_notification(
        "streak_milestone",
        data={"streak_days": 7, "bonus_besitos": 5},
    )
    assert "7 días" in notification
    assert "5" in notification

    # Streak lost
    notification = await service.get_notification(
        "streak_lost", data={"streak_days": 14}
    )
    assert "14" in notification
    assert "perdido" in notification.lower()

    # VIP expiring
    notification = await service.get_notification(
        "vip_expiring_soon", data={"days_remaining": 3}
    )
    assert "3 días" in notification or "3" in notification


@pytest.mark.asyncio
async def test_lucien_voice_conversion_messages(db_setup):
    """Test: Mensajes de conversión personalizados."""
    service = LucienVoiceService()

    # Free to VIP - default
    message = await service.get_conversion_message("free_to_vip")
    assert "Diván" in message
    assert "Diana" in message

    # Free to VIP - EXPLORER
    message_explorer = await service.get_conversion_message(
        "free_to_vip", archetype="explorer"
    )
    assert "explora" in message_explorer.lower() or "secretos" in message_explorer.lower()

    # Free to VIP - ROMANTIC
    message_romantic = await service.get_conversion_message(
        "free_to_vip", archetype="romantic"
    )
    assert "conexión" in message_romantic.lower() or "íntim" in message_romantic.lower()


@pytest.mark.asyncio
async def test_lucien_voice_personalization(db_setup):
    """Test: Personalización de mensajes por arquetipo."""
    service = LucienVoiceService()

    base_message = "Tienes nuevo contenido disponible."

    # Personalizar para EXPLORER
    personalized = await service.personalize_by_archetype(
        base_message, "explorer"
    )
    assert len(personalized) >= len(base_message)

    # Personalizar para DIRECT (sin prefijo)
    personalized_direct = await service.personalize_by_archetype(
        base_message, "direct"
    )
    assert personalized_direct == base_message


@pytest.mark.asyncio
async def test_advanced_archetype_score_calculation(db_setup):
    """Test: Cálculo de scores de arquetipos."""
    from bot.database.engine import get_session

    async with get_session() as session:
        service = AdvancedArchetypeService(session)

        # Calcular scores para usuario de prueba
        scores = await service.calculate_archetype_scores(user_id=1)

        # Verificar que retorna scores para todos los arquetipos
        assert "EXPLORER" in scores
        assert "DIRECT" in scores
        assert "ROMANTIC" in scores
        assert "ANALYTICAL" in scores
        assert "PERSISTENT" in scores
        assert "PATIENT" in scores

        # Todos los scores deben estar entre 0 y 1
        for archetype, score in scores.items():
            assert 0.0 <= score <= 1.0


@pytest.mark.asyncio
async def test_advanced_archetype_dominant_detection(db_setup):
    """Test: Detección de arquetipo dominante."""
    from bot.database.engine import get_session
    from bot.narrative.services.progress import ProgressService
    from bot.narrative.database.models import UserDecisionHistory

    async with get_session() as session:
        # Crear progreso con decisiones suficientes
        progress_service = ProgressService(session)
        progress = await progress_service.get_or_create_progress(user_id=1)
        progress.total_decisions = 10
        await session.commit()

        # Crear algunas decisiones con tiempos rápidos (DIRECT)
        for i in range(5):
            decision = UserDecisionHistory(
                user_id=1,
                fragment_key=f"test_fragment_{i}",
                decision_id=i + 1,
                response_time_seconds=5,  # Muy rápido = DIRECT
                decided_at=datetime.utcnow(),
            )
            session.add(decision)
        await session.commit()

        # Detectar arquetipo
        service = AdvancedArchetypeService(session)
        archetype, confidence = await service.get_dominant_archetype(user_id=1)

        # Debe detectar algún arquetipo
        assert archetype != ArchetypeType.UNKNOWN
        assert 0.0 <= confidence <= 1.0


@pytest.mark.asyncio
async def test_advanced_archetype_profile(db_setup):
    """Test: Perfil completo de arquetipos."""
    from bot.database.engine import get_session
    from bot.narrative.services.progress import ProgressService

    async with get_session() as session:
        # Crear progreso
        progress_service = ProgressService(session)
        progress = await progress_service.get_or_create_progress(user_id=1)
        progress.total_decisions = 10
        await session.commit()

        # Obtener perfil completo
        service = AdvancedArchetypeService(session)
        profile = await service.get_archetype_profile(user_id=1)

        # Verificar estructura del perfil
        assert "dominant" in profile
        assert "confidence" in profile
        assert "scores" in profile
        assert "secondary" in profile
        assert "metrics" in profile

        # Scores debe ser un dict
        assert isinstance(profile["scores"], dict)
        assert len(profile["scores"]) == 6  # 6 arquetipos expandidos


@pytest.mark.asyncio
async def test_personalization_service_content(db_setup):
    """Test: Personalización de contenido."""
    from bot.database.engine import get_session

    async with get_session() as session:
        service = PersonalizationService(session)

        # Obtener contenido personalizado
        content = await service.get_personalized_content(
            user_id=1, content_key="welcome"
        )

        assert isinstance(content, str)
        assert len(content) > 0


@pytest.mark.asyncio
async def test_personalization_conversion_triggers(db_setup):
    """Test: Triggers de conversión."""
    from bot.database.engine import get_session
    from bot.narrative.services.progress import ProgressService

    async with get_session() as session:
        # Crear progreso con capítulos completados (trigger free→vip)
        progress_service = ProgressService(session)
        progress = await progress_service.get_or_create_progress(user_id=1)
        progress.chapters_completed = 3
        progress.total_decisions = 10
        await session.commit()

        # Verificar trigger
        service = PersonalizationService(session)
        trigger = await service.get_conversion_trigger(user_id=1)

        # Debe retornar trigger free_to_vip
        assert trigger is not None
        assert trigger["type"] == "free_to_vip"
        assert "message" in trigger
        assert len(trigger["message"]) > 0


@pytest.mark.asyncio
async def test_personalization_recommended_items(db_setup):
    """Test: Recomendación de items por arquetipo."""
    from bot.database.engine import get_session

    async with get_session() as session:
        service = PersonalizationService(session)

        # Obtener recomendaciones
        recommendations = await service.get_recommended_items(
            user_id=1, limit=5
        )

        # Debe retornar una lista (aunque esté vacía en tests)
        assert isinstance(recommendations, list)


@pytest.mark.asyncio
async def test_personalization_personality_summary(db_setup):
    """Test: Resumen de personalidad."""
    from bot.database.engine import get_session
    from bot.narrative.services.progress import ProgressService

    async with get_session() as session:
        # Crear progreso
        progress_service = ProgressService(session)
        progress = await progress_service.get_or_create_progress(user_id=1)
        progress.total_decisions = 10
        await session.commit()

        # Obtener resumen
        service = PersonalizationService(session)
        summary = await service.get_user_personality_summary(user_id=1)

        # Verificar estructura
        assert "dominant_archetype" in summary
        assert "confidence" in summary
        assert "traits" in summary
        assert "scores" in summary
        assert "recommendations" in summary

        # Traits debe ser una lista
        assert isinstance(summary["traits"], list)
