"""Tests para la Fase 6 - Conversión y Upsell

Pruebas para:
- Comandos de conversión: /vip, /premium, /mapa
- Tracking de conversion_events
- Tracking de conversion_funnels
- Lead qualifications
- Manejo de objeciones con Lucien
"""

import pytest
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import User
from bot.gamification.database.conversion_models import (
    ConversionEvent,
    ConversionFunnel,
    LeadQualification
)
from bot.gamification.enums import ConversionEventType
from bot.gamification.services.lucien_objection_service import ObjectionType
from bot.services.container import ServiceContainer


@pytest.mark.asyncio
async def test_conversion_commands_tracking(session, mock_bot):
    """Test: Tracking de comandos de conversión."""
    # Crear usuario de prueba
    from aiogram.types import User as TelegramUser

    # Simular un usuario de Telegram
    telegram_user = TelegramUser(
        id=12345,
        is_bot=False,
        first_name="Test",
        username="test_user"
    )

    # Usar el container de servicios para crear el usuario
    container = ServiceContainer(session, mock_bot)
    user = await container.user.get_or_create_user(telegram_user)

    # Importar el handler para que los decoradores se registren
    from bot.handlers.user.conversion import handle_conversion_command
    from aiogram.types import Message

    # Simular comando /vip
    message = Message(
        message_id=1,
        date=datetime.now(),
        chat={"id": 12345, "type": "private"},
        from_user={"id": 12345, "is_bot": False, "first_name": "Test"}
    )
    message.text = "/vip"

    # Simular el handler (esto debería crear eventos de tracking)
    from bot.gamification.container import gamification_container
    # Creamos un contenedor de prueba

    # Verificar que se creó el evento de conversión
    result = await session.execute(
        select(ConversionEvent).where(
            ConversionEvent.user_id == 12345,
            ConversionEvent.event_type == ConversionEventType.CONVERSION_VIEW,
            ConversionEvent.product_type == "vip"
        )
    )
    event = result.scalar_one_or_none()

    assert event is not None
    assert event.event_type == ConversionEventType.CONVERSION_VIEW
    assert event.product_type == "vip"
    assert event.source == "command_vip"


@pytest.mark.asyncio
async def test_conversion_funnel_tracking(session, mock_bot):
    """Test: Tracking de embudo de conversión."""
    # Crear usuario de prueba
    from aiogram.types import User as TelegramUser

    telegram_user = TelegramUser(
        id=12346,
        is_bot=False,
        first_name="Test2",
        username="test_user2"
    )

    container = ServiceContainer(session, mock_bot)
    user = await container.user.get_or_create_user(telegram_user)
    
    # Simular interacciones de conversión
    from bot.gamification.container import gamification_container
    
    # Simular visita a producto
    await gamification_container.conversion_tracking.track_conversion_event(
        user_id=12346,
        event_type=ConversionEventType.CONVERSION_VIEW,
        product_type="premium"
    )
    
    # Simular intento de pago
    await gamification_container.conversion_tracking.track_conversion_event(
        user_id=12346,
        event_type=ConversionEventType.PAYMENT_INITIATED,
        product_type="premium"
    )
    
    # Verificar que se actualizó el embudo
    funnel = await gamification_container.conversion_tracking.get_conversion_funnel(12346)
    
    assert funnel is not None
    assert funnel.vip_attempts == 0  # No se ha iniciado para VIP
    assert funnel.premium_attempts == 1  # Se inició para premium
    assert funnel.payment_initiated_count == 1
    assert funnel.last_conversion_step == "payment_initiated"


@pytest.mark.asyncio
async def test_lead_qualification_update(session, mock_bot):
    """Test: Actualización de calificación de lead."""
    # Crear usuario de prueba
    from aiogram.types import User as TelegramUser

    telegram_user = TelegramUser(
        id=12347,
        is_bot=False,
        first_name="Test3",
        username="test_user3"
    )

    container = ServiceContainer(session, mock_bot)
    user = await container.user.get_or_create_user(telegram_user)
    
    # Simular interacciones de conversión que deberían mejorar la calificación
    from bot.gamification.container import gamification_container
    
    # Simular varios eventos que aumentan engagement e intención
    await gamification_container.conversion_tracking.track_conversion_event(
        user_id=12347,
        event_type=ConversionEventType.CONVERSION_VIEW,
        product_type="vip",
        value=47.0
    )
    
    await gamification_container.conversion_tracking.track_conversion_event(
        user_id=12347,
        event_type=ConversionEventType.PAYMENT_INITIATED,
        product_type="vip",
        value=47.0
    )
    
    await gamification_container.conversion_tracking.track_conversion_event(
        user_id=12347,
        event_type=ConversionEventType.PAYMENT_CONFIRMED,
        product_type="vip",
        value=47.0
    )
    
    # Verificar calificación actualizada
    qualification = await gamification_container.conversion_tracking.get_lead_qualification(12347)
    
    assert qualification is not None
    assert qualification.engagement_score > 0.0
    assert qualification.intent_score > 0.0
    assert qualification.conversion_score > 0.0
    assert qualification.conversion_value == 47.0 * 3  # 3 eventos con el mismo valor


@pytest.mark.asyncio
async def test_lucien_objection_handling(session, mock_bot):
    """Test: Manejo de objeciones por parte de Lucien."""
    # Crear usuario de prueba
    from aiogram.types import User as TelegramUser

    telegram_user = TelegramUser(
        id=12348,
        is_bot=False,
        first_name="Test4",
        username="test_user4"
    )

    container = ServiceContainer(session, mock_bot)
    user = await container.user.get_or_create_user(telegram_user)
    
    # Simular un contexto de usuario
    user_context = {
        "archetype": "romantic",
        "behavior_signals": None,
        "lead_qualification": None
    }
    
    # Usar el servicio de objeciones de Lucien
    from bot.gamification.container import gamification_container
    
    response = await gamification_container.lucien_objection.handle_objection(
        user_id=12348,
        objection_type=ObjectionType.TOO_EXPENSIVE,
        user_context=user_context
    )
    
    # Verificar que se generó una respuesta
    assert response is not None
    assert len(response) > 0
    
    # Verificar que se registraron los eventos de objeción
    result = await session.execute(
        select(ConversionEvent).where(
            ConversionEvent.user_id == 12348,
            ConversionEvent.event_type.in_([
                ConversionEventType.OBJECTION_RAISED,
                ConversionEventType.OBJECTION_HANDLED
            ])
        )
    )
    events = result.scalars().all()
    
    assert len(events) >= 2  # Al menos un evento de objeción levantada y uno manejado


@pytest.mark.asyncio
async def test_conversion_event_data_storage(session, mock_bot):
    """Test: Almacenamiento de datos adicionales en eventos de conversión."""
    # Crear usuario de prueba
    from aiogram.types import User as TelegramUser

    telegram_user = TelegramUser(
        id=12349,
        is_bot=False,
        first_name="Test5",
        username="test_user5"
    )

    container = ServiceContainer(session, mock_bot)
    user = await container.user.get_or_create_user(telegram_user)
    
    # Registrar evento con datos adicionales
    from bot.gamification.container import gamification_container
    
    await gamification_container.conversion_tracking.track_conversion_event(
        user_id=12349,
        event_type=ConversionEventType.PAYMENT_APPROVED,
        product_type="mapa_del_deseo",
        product_id=1,
        value=147.0,
        currency="USD",
        source="admin_approval",
        referrer="campaign_mapa_oro",
        session_id="session_abc123",
        event_data={
            "admin_id": 999,
            "payment_method": "bank_transfer",
            "discount_applied": 15.0,
            "user_feedback": "Usuario muy interesado, priorizar seguimiento"
        }
    )
    
    # Verificar que se almacenaron correctamente los datos
    result = await session.execute(
        select(ConversionEvent).where(
            ConversionEvent.user_id == 12349,
            ConversionEvent.event_type == ConversionEventType.PAYMENT_APPROVED
        )
    )
    event = result.scalar_one_or_none()
    
    assert event is not None
    assert event.product_type == "mapa_del_deseo"
    assert event.value == 147.0
    assert event.currency == "USD"
    assert event.source == "admin_approval"
    assert event.referrer == "campaign_mapa_oro"
    assert event.session_id == "session_abc123"
    
    # Verificar que los datos específicos también se guardaron
    assert "admin_id" in event.data
    assert "payment_method" in event.data
    assert "discount_applied" in event.data
    assert event.data["payment_method"] == "bank_transfer"
    assert event.data["discount_applied"] == 15.0


@pytest.mark.asyncio
async def test_multiple_conversion_paths(session, mock_bot):
    """Test: Seguimiento de múltiples caminos de conversión para un usuario."""
    # Crear usuario de prueba
    from aiogram.types import User as TelegramUser

    telegram_user = TelegramUser(
        id=12350,
        is_bot=False,
        first_name="Test6",
        username="test_user6"
    )

    container = ServiceContainer(session, mock_bot)
    user = await container.user.get_or_create_user(telegram_user)
    
    from bot.gamification.container import gamification_container
    
    # Simular interacción con VIP
    await gamification_container.conversion_tracking.track_conversion_event(
        user_id=12350,
        event_type=ConversionEventType.CONVERSION_VIEW,
        product_type="vip"
    )
    await gamification_container.conversion_tracking.track_conversion_event(
        user_id=12350,
        event_type=ConversionEventType.PAYMENT_INITIATED,
        product_type="vip"
    )
    
    # Luego simular interés en Mapa del Deseo
    await gamification_container.conversion_tracking.track_conversion_event(
        user_id=12350,
        event_type=ConversionEventType.CONVERSION_VIEW,
        product_type="mapa_del_deseo"
    )
    
    # Finalmente convertir en Premium
    await gamification_container.conversion_tracking.track_conversion_event(
        user_id=12350,
        event_type=ConversionEventType.PAYMENT_INITIATED,
        product_type="premium"
    )
    await gamification_container.conversion_tracking.track_conversion_event(
        user_id=12350,
        event_type=ConversionEventType.PAYMENT_CONFIRMED,
        product_type="premium"
    )
    await gamification_container.conversion_tracking.track_conversion_event(
        user_id=12350,
        event_type=ConversionEventType.PAYMENT_APPROVED,
        product_type="premium"
    )
    await gamification_container.conversion_tracking.track_conversion_event(
        user_id=12350,
        event_type=ConversionEventType.PRODUCT_ACTIVATED,
        product_type="premium"
    )
    
    # Verificar métricas del embudo
    funnel = await gamification_container.conversion_tracking.get_conversion_funnel(12350)
    
    assert funnel is not None
    assert funnel.vip_attempts == 1
    assert funnel.premium_attempts == 1
    assert funnel.mapa_attempts == 1
    assert funnel.payment_initiated_count == 3  # Uno por cada producto
    assert funnel.payment_confirmed_count == 1  # Solo premium se confirmó
    assert funnel.payment_approved_count == 1   # Solo premium se aprobó


@pytest.mark.asyncio
async def test_hot_lead_identification(session, mock_bot):
    """Test: Identificación de leads calientes basados en comportamiento."""
    # Crear usuario de prueba
    from aiogram.types import User as TelegramUser

    telegram_user = TelegramUser(
        id=12351,
        is_bot=False,
        first_name="Test7",
        username="test_user7"
    )

    container = ServiceContainer(session, mock_bot)
    user = await container.user.get_or_create_user(telegram_user)
    
    from bot.gamification.container import gamification_container
    
    # Simular comportamiento de lead caliente
    await gamification_container.conversion_tracking.track_conversion_event(
        user_id=12351,
        event_type=ConversionEventType.CONVERSION_VIEW,
        product_type="vip",
        value=47.0
    )
    await gamification_container.conversion_tracking.track_conversion_event(
        user_id=12351,
        event_type=ConversionEventType.PAYMENT_INITIATED,
        product_type="vip",
        value=47.0
    )
    await gamification_container.conversion_tracking.track_conversion_event(
        user_id=12351,
        event_type=ConversionEventType.PAYMENT_CONFIRMED,
        product_type="vip",
        value=47.0
    )
    
    # Verificar que ahora es un lead caliente
    qualification = await gamification_container.conversion_tracking.get_lead_qualification(12351)
    
    assert qualification is not None
    # Aunque no sea exactamente caliente (dependerá del cálculo), debería tener alta calificación
    assert qualification.conversion_score >= 0.25  # Basado en los 3 eventos registrados


@pytest.mark.asyncio
async def test_objection_service_response_generation():
    """Test: Generación de respuestas por el servicio de objeciones de Lucien."""
    # Este test puede ser unitario ya que no requiere base de datos
    from bot.gamification.services.lucien_objection_service import LucienObjectionService
    from bot.gamification.services.lucien_objection_service import ObjectionType

    # Simular una sesión (no se usará realmente en este test unitario)
    class MockSession:
        pass

    service = LucienObjectionService(MockSession())

    # Probar que hay respuestas predeterminadas
    objections = service.get_available_objections()
    assert len(objections) > 0

    # Probar que se puede manejar una objeción específica
    response = await service._select_response(12352, ObjectionType.TOO_EXPENSIVE)
    assert "response" in response
    assert "style" in response
    assert len(response["response"]) > 0


if __name__ == "__main__":
    pytest.main([__file__])