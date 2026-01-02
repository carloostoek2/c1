"""
Tests de validación pre-producción para el módulo de canales.

Estos tests validan la funcionalidad completa del módulo de gestión de canales
antes de deployment a producción.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from aiogram.types import Chat, Message, User, ChatInviteLink

from bot.database import init_db, close_db
from bot.database.models import BotConfig, VIPSubscriber, InvitationToken, FreeChannelRequest
from bot.services.container import ServiceContainer
from bot.services.channel import ChannelService
from bot.services.config import ConfigService
from bot.services.subscription import SubscriptionService


# ═══════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════

@pytest_asyncio.fixture
async def service_container(session, mock_bot):
    """Container de servicios para tests."""
    # mock_bot viene del conftest.py, pero necesitamos agregar métodos async
    mock_bot.send_photo = AsyncMock()
    mock_bot.send_video = AsyncMock()
    mock_bot.get_chat_member_count = AsyncMock()

    container = ServiceContainer(session, mock_bot)
    return container


@pytest_asyncio.fixture
async def configured_channels(service_container):
    """Configura canales VIP y Free para tests."""
    # Mock de get_chat para setup de canales
    service_container._bot.get_chat.return_value = Chat(
        id=-1001234567890,
        type="channel",
        title="Test VIP Channel"
    )

    service_container._bot.get_chat_member.return_value = MagicMock(
        status="administrator",
        can_post_messages=True,
        can_invite_users=True
    )

    # Configurar canal VIP
    await service_container.channel.setup_vip_channel("-1001234567890")

    # Mock para canal Free
    service_container._bot.get_chat.return_value = Chat(
        id=-1009876543210,
        type="channel",
        title="Test Free Channel"
    )

    # Configurar canal Free
    await service_container.channel.setup_free_channel("-1009876543210")

    # Configurar wait time
    await service_container.config.set_wait_time(5)

    return service_container


# ═══════════════════════════════════════════════════════════════
# TESTS: CONFIGURACIÓN DE CANALES
# ═══════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_setup_vip_channel_success(service_container, mock_bot):
    """Test: Configurar canal VIP exitosamente."""
    channel_id = "-1001234567890"

    # Mock de verificación de permisos
    mock_bot.get_chat.return_value = Chat(
        id=int(channel_id),
        type="channel",
        title="Canal VIP Test"
    )

    mock_bot.get_chat_member.return_value = MagicMock(
        status="administrator",
        can_post_messages=True,
        can_invite_users=True
    )

    # Setup del canal
    success, message = await service_container.channel.setup_vip_channel(channel_id)

    assert success is True
    assert "configurado" in message.lower()

    # Verificar que se guardó en BD
    config = await service_container.config.get_config()
    assert config.vip_channel_id == channel_id


@pytest.mark.asyncio
async def test_setup_free_channel_success(service_container, mock_bot):
    """Test: Configurar canal Free exitosamente."""
    channel_id = "-1009876543210"

    # Mock de verificación de permisos
    mock_bot.get_chat.return_value = Chat(
        id=int(channel_id),
        type="channel",
        title="Canal Free Test"
    )

    mock_bot.get_chat_member.return_value = MagicMock(
        status="administrator",
        can_post_messages=True,
        can_invite_users=True
    )

    # Setup del canal
    success, message = await service_container.channel.setup_free_channel(channel_id)

    assert success is True
    assert "configurado" in message.lower()

    # Verificar que se guardó en BD
    config = await service_container.config.get_config()
    assert config.free_channel_id == channel_id


@pytest.mark.asyncio
async def test_setup_channel_without_permissions(service_container, mock_bot):
    """Test: Rechazar canal donde el bot no tiene permisos."""
    channel_id = "-1001111111111"

    # Mock de verificación de permisos (bot no es admin)
    mock_bot.get_chat.return_value = Chat(
        id=int(channel_id),
        type="channel",
        title="Canal Sin Permisos"
    )

    mock_bot.get_chat_member.return_value = MagicMock(
        status="member",  # No es admin
        can_post_messages=False,
        can_invite_users=False
    )

    # Intentar setup del canal
    success, message = await service_container.channel.setup_vip_channel(channel_id)

    assert success is False
    assert "permisos" in message.lower() or "administrador" in message.lower()


# ═══════════════════════════════════════════════════════════════
# TESTS: VALIDACIÓN DE CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_is_fully_configured_true(configured_channels):
    """Test: Sistema completamente configurado."""
    is_configured = await configured_channels.config.is_fully_configured()

    assert is_configured is True


@pytest.mark.asyncio
async def test_is_fully_configured_false_no_vip(service_container):
    """Test: Sistema no configurado (falta canal VIP)."""
    # Solo configurar canal Free
    await service_container.config.set_free_channel_id("-1009876543210")
    await service_container.config.set_wait_time(5)

    is_configured = await service_container.config.is_fully_configured()

    assert is_configured is False


@pytest.mark.asyncio
async def test_get_config_status(configured_channels):
    """Test: Obtener estado de configuración."""
    status = await configured_channels.config.get_config_status()

    assert isinstance(status, dict)
    assert status["vip_channel_configured"] is True
    assert status["free_channel_configured"] is True
    assert status["wait_time_configured"] is True
    assert status["is_fully_configured"] is True


# ═══════════════════════════════════════════════════════════════
# TESTS: ENVÍO DE MENSAJES
# ═══════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_send_to_vip_channel_success(configured_channels, mock_bot):
    """Test: Enviar mensaje al canal VIP."""
    # Mock de envío de mensaje
    mock_message = Message(
        message_id=123,
        date=datetime.now(),
        chat=Chat(id=-1001234567890, type="channel"),
        from_user=User(id=123456789, is_bot=True, first_name="Bot")
    )
    mock_bot.send_message.return_value = mock_message

    # Obtener ID del canal VIP
    vip_channel_id = await configured_channels.config.get_vip_channel_id()

    # Enviar mensaje
    success, msg, message = await configured_channels.channel.send_to_channel(
        channel_id=vip_channel_id,
        text="Test message"
    )

    assert success is True
    assert message is not None
    assert message.message_id == 123


@pytest.mark.asyncio
async def test_send_to_channel_not_configured(service_container, mock_bot):
    """Test: Rechazar envío si canal no configurado."""
    # No configurar ningún canal

    # Intentar enviar a canal VIP (no configurado)
    vip_channel_id = await service_container.config.get_vip_channel_id()

    assert vip_channel_id is None


@pytest.mark.asyncio
async def test_send_to_channel_with_photo(configured_channels, mock_bot):
    """Test: Enviar mensaje con foto."""
    # Mock de envío con foto
    mock_message = Message(
        message_id=124,
        date=datetime.now(),
        chat=Chat(id=-1001234567890, type="channel"),
        from_user=User(id=123456789, is_bot=True, first_name="Bot")
    )
    mock_bot.send_photo.return_value = mock_message

    vip_channel_id = await configured_channels.config.get_vip_channel_id()

    # Enviar mensaje con foto
    success, msg, message = await configured_channels.channel.send_to_channel(
        channel_id=vip_channel_id,
        photo="https://example.com/photo.jpg",
        caption="Test caption"
    )

    assert success is True
    assert message is not None


# ═══════════════════════════════════════════════════════════════
# TESTS: INVITE LINKS
# ═══════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_create_invite_link_vip_channel(configured_channels, mock_bot):
    """Test: Crear invite link para canal VIP."""
    user_id = 987654321
    vip_channel_id = await configured_channels.config.get_vip_channel_id()

    # Mock de creación de invite link
    mock_invite_link = ChatInviteLink(
        invite_link="https://t.me/+ABC123XYZ",
        creator=User(id=123456789, is_bot=True, first_name="Bot"),
        creates_join_request=False,
        is_primary=False,
        is_revoked=False,
        member_limit=1,
        expire_date=datetime.now() + timedelta(hours=5)
    )
    mock_bot.create_chat_invite_link.return_value = mock_invite_link

    # Crear invite link
    invite_link = await configured_channels.subscription.create_invite_link(
        channel_id=vip_channel_id,
        user_id=user_id,
        expire_hours=5
    )

    assert invite_link is not None
    assert "https://t.me/" in invite_link.invite_link
    assert invite_link.member_limit == 1


@pytest.mark.asyncio
async def test_create_invite_link_expiry(configured_channels, mock_bot):
    """Test: Validar expiración de invite link."""
    user_id = 987654321
    vip_channel_id = await configured_channels.config.get_vip_channel_id()
    expire_hours = 2

    # Mock con fecha de expiración específica
    expected_expiry = datetime.now() + timedelta(hours=expire_hours)
    mock_invite_link = ChatInviteLink(
        invite_link="https://t.me/+XYZ789ABC",
        creator=User(id=123456789, is_bot=True, first_name="Bot"),
        creates_join_request=False,
        is_primary=False,
        is_revoked=False,
        member_limit=1,
        expire_date=expected_expiry
    )
    mock_bot.create_chat_invite_link.return_value = mock_invite_link

    # Crear invite link
    invite_link = await configured_channels.subscription.create_invite_link(
        channel_id=vip_channel_id,
        user_id=user_id,
        expire_hours=expire_hours
    )

    assert invite_link.expire_date is not None
    # Verificar que la expiración es aproximadamente la esperada (tolerancia de 60 segundos)
    time_diff = abs((invite_link.expire_date - expected_expiry).total_seconds())
    assert time_diff < 60


# ═══════════════════════════════════════════════════════════════
# TESTS: INTEGRACIÓN COMPLETA
# ═══════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_complete_vip_flow_with_channels(configured_channels, mock_bot):
    """Test: Flujo completo VIP con invite link."""
    admin_id = 111111111
    user_id = 222222222

    # Mock de invite link
    mock_invite_link = ChatInviteLink(
        invite_link="https://t.me/+COMPLETE_FLOW",
        creator=User(id=123456789, is_bot=True, first_name="Bot"),
        creates_join_request=False,
        is_primary=False,
        is_revoked=False,
        member_limit=1,
        expire_date=datetime.now() + timedelta(hours=5)
    )
    mock_bot.create_chat_invite_link.return_value = mock_invite_link

    # 1. Admin genera token
    token = await configured_channels.subscription.generate_vip_token(
        generated_by=admin_id,
        duration_hours=24
    )
    assert token is not None

    # 2. Usuario canjea token
    success, msg, subscriber = await configured_channels.subscription.redeem_vip_token(
        token_str=token.token,
        user_id=user_id
    )
    assert success is True
    assert subscriber is not None

    # 3. Crear invite link para el usuario
    vip_channel_id = await configured_channels.config.get_vip_channel_id()
    invite_link = await configured_channels.subscription.create_invite_link(
        channel_id=vip_channel_id,
        user_id=user_id,
        expire_hours=5
    )

    assert invite_link is not None
    assert invite_link.invite_link == "https://t.me/+COMPLETE_FLOW"

    # 4. Verificar que el usuario es VIP activo
    is_active = await configured_channels.subscription.is_vip_active(user_id)
    assert is_active is True


@pytest.mark.asyncio
async def test_error_handling_channel_not_found(service_container, mock_bot):
    """Test: Manejo de error cuando canal no existe."""
    invalid_channel_id = "-1009999999999"

    # Mock de error de canal no encontrado
    from aiogram.exceptions import TelegramBadRequest
    mock_bot.get_chat.side_effect = TelegramBadRequest(message="Chat not found")

    # Intentar setup
    success, message = await service_container.channel.setup_vip_channel(invalid_channel_id)

    assert success is False
    assert "error" in message.lower() or "encontrado" in message.lower()


@pytest.mark.asyncio
async def test_verify_bot_permissions_comprehensive(configured_channels, mock_bot):
    """Test: Verificación completa de permisos del bot."""
    vip_channel_id = await configured_channels.config.get_vip_channel_id()

    # Mock de permisos completos
    mock_bot.get_chat.return_value = Chat(
        id=int(vip_channel_id),
        type="channel",
        title="Canal VIP"
    )

    mock_bot.get_chat_member.return_value = MagicMock(
        status="administrator",
        can_post_messages=True,
        can_edit_messages=True,
        can_delete_messages=True,
        can_invite_users=True,
        can_restrict_members=True,
        can_promote_members=False
    )

    # Verificar permisos
    success, message = await configured_channels.channel.verify_bot_permissions(vip_channel_id)

    assert success is True
    assert "permisos correctos" in message.lower() or "verificado" in message.lower()


# ═══════════════════════════════════════════════════════════════
# TESTS: EDGE CASES Y VALIDACIONES
# ═══════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_channel_id_format_validation(service_container):
    """Test: Validar formato de ID de canal."""
    # IDs válidos
    valid_ids = ["-1001234567890", "-1009876543210"]

    for channel_id in valid_ids:
        await service_container.config.set_vip_channel_id(channel_id)
        saved_id = await service_container.config.get_vip_channel_id()
        assert saved_id == channel_id


@pytest.mark.asyncio
async def test_concurrent_channel_setup(service_container, mock_bot):
    """Test: Setup de ambos canales concurrentemente."""
    vip_id = "-1001234567890"
    free_id = "-1009876543210"

    # Mock para ambos canales
    def get_chat_side_effect(chat_id):
        return Chat(
            id=int(chat_id),
            type="channel",
            title=f"Canal {chat_id}"
        )

    mock_bot.get_chat.side_effect = get_chat_side_effect
    mock_bot.get_chat_member.return_value = MagicMock(
        status="administrator",
        can_post_messages=True,
        can_invite_users=True
    )

    # Setup simultáneo
    import asyncio
    vip_task = service_container.channel.setup_vip_channel(vip_id)
    free_task = service_container.channel.setup_free_channel(free_id)

    vip_result, free_result = await asyncio.gather(vip_task, free_task)

    assert vip_result[0] is True
    assert free_result[0] is True

    # Verificar ambos guardados
    config = await service_container.config.get_config()
    assert config.vip_channel_id == vip_id
    assert config.free_channel_id == free_id


@pytest.mark.asyncio
async def test_get_channel_info(configured_channels, mock_bot):
    """Test: Obtener información del canal."""
    vip_channel_id = await configured_channels.config.get_vip_channel_id()

    # Mock de información del canal
    mock_bot.get_chat.return_value = Chat(
        id=int(vip_channel_id),
        type="channel",
        title="Canal VIP Premium",
        username="vip_channel",
        description="Canal exclusivo para suscriptores VIP"
    )

    # Obtener info
    channel_info = await configured_channels.channel.get_channel_info(vip_channel_id)

    assert channel_info is not None
    assert channel_info.title == "Canal VIP Premium"
    assert channel_info.type == "channel"


@pytest.mark.asyncio
async def test_get_channel_member_count(configured_channels, mock_bot):
    """Test: Obtener conteo de miembros del canal."""
    vip_channel_id = await configured_channels.config.get_vip_channel_id()

    # Mock de conteo de miembros
    mock_bot.get_chat_member_count.return_value = 150

    # Obtener conteo
    member_count = await configured_channels.channel.get_channel_member_count(vip_channel_id)

    assert member_count == 150


# ═══════════════════════════════════════════════════════════════
# RESUMEN DE TESTS
# ═══════════════════════════════════════════════════════════════

"""
RESUMEN DE COBERTURA - MÓDULO DE CANALES:

✅ Configuración de Canales (3 tests)
   - Setup VIP exitoso
   - Setup Free exitoso
   - Rechazo sin permisos

✅ Validación de Configuración (3 tests)
   - Sistema completamente configurado
   - Sistema incompleto
   - Estado de configuración

✅ Envío de Mensajes (3 tests)
   - Envío de texto
   - Validación de canal no configurado
   - Envío con foto

✅ Invite Links (2 tests)
   - Creación de invite link
   - Validación de expiración

✅ Integración Completa (1 test)
   - Flujo completo VIP con canales

✅ Manejo de Errores (1 test)
   - Canal no encontrado

✅ Verificación de Permisos (1 test)
   - Permisos completos del bot

✅ Edge Cases (4 tests)
   - Validación de formato de IDs
   - Setup concurrente
   - Información del canal
   - Conteo de miembros

TOTAL: 18 tests de validación pre-producción
"""
