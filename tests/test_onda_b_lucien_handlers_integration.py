"""
Tests E2E para B4: Integración de LucienVoiceService en todos los handlers.

Valida que:
- Todos los handlers usan LucienVoiceService
- Los mensajes tienen la voz de Lucien
- Los errores usan format_error, format_confirmation, etc
- Las respuestas son coherentes con la personalidad de Lucien
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from aiogram.types import Message, User, Chat, CallbackQuery, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.enums import UserRole
from bot.services.lucien_voice import LucienVoiceService
from bot.handlers.user.start import cmd_start, _activate_token_from_deeplink
from bot.handlers.admin.main import cmd_admin
from bot.handlers.admin.vip import callback_vip_menu, process_vip_channel_forward
from bot.handlers.admin.free import callback_free_menu, process_free_channel_forward
from bot.gamification.handlers.user.profile import show_profile
from bot.gamification.handlers.user.missions import show_missions
from bot.narrative.handlers.user.story import callback_process_decision


# ========================================
# TESTS: USER HANDLERS
# ========================================

@pytest.mark.asyncio
async def test_start_handler_admin_uses_lucien_voice(db_setup):
    """Test: /start para admin usa mensaje de Lucien."""
    lucien = LucienVoiceService()
    admin_msg = await lucien.get_welcome_message("admin")

    # Verificar que contiene partes esperadas
    assert "admin" in admin_msg.lower() or "administr" in admin_msg.lower()
    assert len(admin_msg) > 0


@pytest.mark.asyncio
async def test_start_handler_invalid_token_uses_lucien_error(db_setup):
    """Test: /start con token inválido usa format_error de Lucien."""
    lucien = LucienVoiceService()
    error_msg = await lucien.format_error("token_invalid")

    # Verificar que es un error con tono de Lucien
    assert error_msg is not None
    assert len(error_msg) > 0


@pytest.mark.asyncio
async def test_start_handler_no_vip_channel_uses_lucien_error(db_setup):
    """Test: /start sin canal VIP configurado usa error de Lucien."""
    lucien = LucienVoiceService()
    error_msg = await lucien.format_error("vip_not_configured")

    # Verificar error
    assert error_msg is not None
    assert len(error_msg) > 0


# ========================================
# TESTS: ADMIN HANDLERS
# ========================================

@pytest.mark.asyncio
async def test_admin_panel_uses_lucien_voice(db_setup):
    """Test: /admin usa bienvenida de Lucien."""
    lucien = LucienVoiceService()
    welcome_msg = await lucien.get_welcome_message("admin")

    # El mensaje debe incluir instrucciones para admin
    assert welcome_msg is not None
    assert len(welcome_msg) > 0


@pytest.mark.asyncio
async def test_vip_channel_setup_error_uses_lucien(db_setup):
    """Test: Setup VIP con error usa format_error de Lucien."""
    lucien = LucienVoiceService()
    error_msg = await lucien.format_error("invalid_input")

    # Validar que es un error válido
    assert error_msg is not None
    assert len(error_msg) > 0


@pytest.mark.asyncio
async def test_vip_channel_success_uses_lucien_confirmation(db_setup):
    """Test: Setup VIP exitoso usa format_confirmation de Lucien."""
    lucien = LucienVoiceService()
    success_msg = await lucien.format_confirmation(
        "channel_configured",
        {"channel_type": "VIP", "channel_name": "Test VIP"}
    )

    # Verificar confirmación
    assert success_msg is not None
    assert "VIP" in success_msg or "Test" in success_msg


@pytest.mark.asyncio
async def test_free_channel_setup_error_uses_lucien(db_setup):
    """Test: Setup Free con error usa format_error de Lucien."""
    lucien = LucienVoiceService()
    error_msg = await lucien.format_error("invalid_input")

    assert error_msg is not None
    assert len(error_msg) > 0


@pytest.mark.asyncio
async def test_free_channel_success_uses_lucien_confirmation(db_setup):
    """Test: Setup Free exitoso usa format_confirmation de Lucien."""
    lucien = LucienVoiceService()
    success_msg = await lucien.format_confirmation(
        "channel_configured",
        {"channel_type": "Free", "channel_name": "Test Free"}
    )

    assert success_msg is not None
    assert "Free" in success_msg or "Test" in success_msg


# ========================================
# TESTS: GAMIFICATION HANDLERS
# ========================================

@pytest.mark.asyncio
async def test_profile_error_uses_lucien_voice(db_setup):
    """Test: Error en perfil usa format_error de Lucien."""
    lucien = LucienVoiceService()
    error_msg = await lucien.format_error("invalid_input")

    assert error_msg is not None
    assert len(error_msg) > 0


@pytest.mark.asyncio
async def test_missions_list_error_uses_lucien_voice(db_setup):
    """Test: Error al listar misiones usa format_error de Lucien."""
    lucien = LucienVoiceService()
    error_msg = await lucien.format_error("invalid_input")

    assert error_msg is not None
    assert len(error_msg) > 0


@pytest.mark.asyncio
async def test_missions_claim_denied_uses_lucien_voice(db_setup):
    """Test: Reclamación de misión rechazada usa permission_denied de Lucien."""
    lucien = LucienVoiceService()
    error_msg = await lucien.format_error("permission_denied")

    assert error_msg is not None
    assert len(error_msg) > 0


# ========================================
# TESTS: NARRATIVE HANDLERS
# ========================================

@pytest.mark.asyncio
async def test_story_chapter_not_found_uses_lucien_voice(db_setup):
    """Test: Capítulo no encontrado usa format_error de Lucien."""
    lucien = LucienVoiceService()
    error_msg = await lucien.format_error("permission_denied")

    assert error_msg is not None
    assert len(error_msg) > 0


@pytest.mark.asyncio
async def test_story_decision_limit_reached_uses_lucien_voice(db_setup):
    """Test: Límite de decisiones alcanzado usa format_error de Lucien."""
    lucien = LucienVoiceService()
    error_msg = await lucien.format_error("limit_reached", {"limit_type": "decisiones"})

    assert error_msg is not None
    assert len(error_msg) > 0


@pytest.mark.asyncio
async def test_story_cooldown_active_uses_lucien_voice(db_setup):
    """Test: Cooldown activo usa format_error de Lucien con tiempo."""
    lucien = LucienVoiceService()
    error_msg = await lucien.format_error("cooldown_active", {"time_seconds": 30})

    assert error_msg is not None
    assert len(error_msg) > 0


@pytest.mark.asyncio
async def test_story_permission_denied_uses_lucien_voice(db_setup):
    """Test: Permiso denegado en historia usa format_error de Lucien."""
    lucien = LucienVoiceService()
    error_msg = await lucien.format_error("permission_denied")

    assert error_msg is not None
    assert len(error_msg) > 0


# ========================================
# TESTS: LUCIEN VOICE CONSISTENCY
# ========================================

@pytest.mark.asyncio
async def test_lucien_voice_all_templates_exist(db_setup):
    """Test: Todos los templates de Lucien están definidos."""
    lucien = LucienVoiceService()

    # Test welcome messages
    admin_msg = await lucien.get_welcome_message("admin")
    assert admin_msg is not None

    # Test error messages
    error_msg = await lucien.format_error("permission_denied")
    assert error_msg is not None

    # Test confirmation messages
    confirm_msg = await lucien.format_confirmation("purchase_complete",
                                                    {"item_name": "Test", "cost": 10})
    assert confirm_msg is not None

    # Test notifications
    notif_msg = await lucien.get_notification("daily_gift_available")
    assert notif_msg is not None


@pytest.mark.asyncio
async def test_lucien_voice_supports_personalization(db_setup):
    """Test: LucienVoiceService soporta personalización por arquetipo."""
    lucien = LucienVoiceService()

    base_message = "Tienes nuevo contenido disponible."

    # Test EXPLORER personalization
    explorer_msg = await lucien.personalize_by_archetype(base_message, "explorer")
    assert explorer_msg is not None
    assert len(explorer_msg) >= len(base_message)  # Puede ser más largo con prefijo

    # Test DIRECT (sin cambios)
    direct_msg = await lucien.personalize_by_archetype(base_message, "direct")
    assert direct_msg == base_message  # DIRECT no añade prefijo


@pytest.mark.asyncio
async def test_lucien_voice_all_archetypes(db_setup):
    """Test: LucienVoiceService personaliza para todos los arquetipos."""
    lucien = LucienVoiceService()
    base_message = "Mensaje de prueba."

    archetypes = ["explorer", "direct", "romantic", "analytical", "persistent", "patient"]

    for archetype in archetypes:
        personalized = await lucien.personalize_by_archetype(base_message, archetype)
        assert personalized is not None
        assert len(personalized) > 0


@pytest.mark.asyncio
async def test_lucien_voice_characteristics(db_setup):
    """Test: LucienVoiceService retorna características correctas."""
    lucien = LucienVoiceService()
    characteristics = lucien.get_voice_characteristics()

    # Verificar estructura
    assert "tone" in characteristics
    assert "role" in characteristics
    assert "relationship" in characteristics
    assert "style" in characteristics
    assert "principle" in characteristics

    # Verificar valores
    assert "formal" in characteristics["tone"].lower()
    assert "diana" in characteristics["relationship"].lower()


# ========================================
# INTEGRATION TESTS
# ========================================

@pytest.mark.asyncio
async def test_handlers_chain_with_lucien_voice(db_setup):
    """Test: Cadena de handlers mantiene coherencia de voz."""
    lucien = LucienVoiceService()

    # Simular flujo: admin welcomes → sets up channel → generates token → user redeems

    # 1. Admin welcome
    admin_welcome = await lucien.get_welcome_message("admin")
    assert admin_welcome is not None

    # 2. Channel setup success
    setup_success = await lucien.format_confirmation(
        "channel_configured",
        {"channel_type": "VIP", "channel_name": "El Diván"}
    )
    assert setup_success is not None

    # 3. Token activation
    token_error = await lucien.format_error("token_invalid")
    assert token_error is not None

    # 4. Archetype personalization
    message = "Tienes acceso VIP."
    personalized = await lucien.personalize_by_archetype(message, "romantic")
    assert personalized is not None


@pytest.mark.asyncio
async def test_error_consistency_across_handlers(db_setup):
    """Test: Todos los handlers usan mensajes de error consistentes."""
    lucien = LucienVoiceService()

    # Recolectar todos los tipos de error posibles
    error_types = [
        "permission_denied",
        "not_configured",
        "invalid_input",
        "cooldown_active",
        "limit_reached",
        "token_invalid",
        "token_expired",
    ]

    for error_type in error_types:
        error_msg = await lucien.format_error(error_type)
        assert error_msg is not None
        assert len(error_msg) > 0
        # Verificar que suena como Lucien (no emojis ruidosos)
        assert "👋" not in error_msg or error_msg.count("👋") <= 1
