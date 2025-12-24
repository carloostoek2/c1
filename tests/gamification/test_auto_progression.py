"""
Tests para Auto-Progression Checker (G5.1).

Valida:
- Verificación de level-ups pendientes
- Procesamiento en batch
- Notificaciones a usuarios
- Manejo de errores
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from bot.gamification.database.models import UserGamification, Level
from bot.gamification.background.auto_progression_checker import (
    check_all_users_progression,
    notify_level_up
)
from bot.gamification.services.level import LevelService


@pytest_asyncio.fixture
async def levels(db_session):
    """Crea niveles de prueba."""
    level1 = Level(name="Novato", min_besitos=0, order=1, active=True)
    level2 = Level(name="Intermedio", min_besitos=100, order=2, active=True)
    level3 = Level(name="Avanzado", min_besitos=500, order=3, active=True)

    db_session.add_all([level1, level2, level3])
    await db_session.commit()

    return [level1, level2, level3]


@pytest_asyncio.fixture
async def users_with_besitos(db_session, levels):
    """
    Crea usuarios con diferentes cantidades de besitos.

    - User 1: 0 besitos → Novato (no cambia)
    - User 2: 150 besitos → Debe subir a Intermedio
    - User 3: 600 besitos → Debe subir a Avanzado
    """
    user1 = UserGamification(user_id=1001, total_besitos=0, current_level_id=levels[0].id)
    user2 = UserGamification(user_id=1002, total_besitos=150, current_level_id=levels[0].id)
    user3 = UserGamification(user_id=1003, total_besitos=600, current_level_id=levels[0].id)

    db_session.add_all([user1, user2, user3])
    await db_session.commit()

    return [user1, user2, user3]


@pytest.mark.asyncio
async def test_check_all_users_progression_applies_level_ups(
    db_session,
    users_with_besitos,
    levels
):
    """Verifica que se aplican level-ups automáticamente."""
    # Mock del bot
    mock_bot = AsyncMock()
    mock_bot.send_message = AsyncMock()

    # Ejecutar verificación
    await check_all_users_progression(db_session, mock_bot)

    # Verificar que User 2 subió a Intermedio
    await db_session.refresh(users_with_besitos[1])
    assert users_with_besitos[1].current_level_id == levels[1].id

    # Verificar que User 3 subió a Avanzado
    await db_session.refresh(users_with_besitos[2])
    assert users_with_besitos[2].current_level_id == levels[2].id

    # Verificar que User 1 no cambió
    await db_session.refresh(users_with_besitos[0])
    assert users_with_besitos[0].current_level_id == levels[0].id


@pytest.mark.asyncio
async def test_check_all_users_sends_notifications(
    db_session,
    users_with_besitos,
    levels
):
    """Verifica que se envían notificaciones a usuarios que suben de nivel."""
    # Mock del bot
    mock_bot = AsyncMock()
    mock_bot.send_message = AsyncMock()

    # Ejecutar verificación
    await check_all_users_progression(db_session, mock_bot)

    # Verificar que se enviaron 2 notificaciones (User 2 y User 3)
    assert mock_bot.send_message.call_count == 2

    # Verificar contenido de las notificaciones
    calls = mock_bot.send_message.call_args_list

    # Primera notificación (User 2)
    # call_args: (args, kwargs)
    assert calls[0][0][0] == 1002  # Primer argumento posicional
    assert "Subiste de nivel" in calls[0][0][1]  # Segundo argumento posicional (mensaje)
    assert "Intermedio" in calls[0][0][1]

    # Segunda notificación (User 3)
    assert calls[1][0][0] == 1003
    assert "Subiste de nivel" in calls[1][0][1]
    assert "Avanzado" in calls[1][0][1]


@pytest.mark.asyncio
async def test_notify_level_up_sends_correct_message(db_session, levels):
    """Verifica que notify_level_up envía el mensaje correcto."""
    # Mock del bot
    mock_bot = AsyncMock()
    mock_bot.send_message = AsyncMock()

    # Llamar a notify_level_up
    await notify_level_up(mock_bot, 12345, levels[0], levels[1])

    # Verificar llamada
    mock_bot.send_message.assert_called_once()

    # Verificar contenido del mensaje
    call_args = mock_bot.send_message.call_args
    # call_args[0] = argumentos posicionales, call_args[1] = kwargs
    assert call_args[0][0] == 12345  # user_id
    message_text = call_args[0][1]   # message text
    assert "🎉" in message_text
    assert "Subiste de nivel" in message_text
    assert levels[0].name in message_text  # Nivel anterior
    assert levels[1].name in message_text  # Nivel nuevo
    assert str(levels[1].min_besitos) in message_text
    assert call_args[1]["parse_mode"] == "HTML"


@pytest.mark.asyncio
async def test_notify_level_up_handles_send_error(db_session, levels):
    """Verifica que notify_level_up maneja errores al enviar mensajes."""
    # Mock del bot que falla al enviar
    mock_bot = AsyncMock()
    mock_bot.send_message = AsyncMock(side_effect=Exception("User blocked bot"))

    # No debería lanzar excepción
    await notify_level_up(mock_bot, 12345, levels[0], levels[1])

    # Verificar que intentó enviar
    mock_bot.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_batch_processing_with_many_users(db_session, levels):
    """Verifica que el procesamiento en batch funciona correctamente."""
    # Crear 250 usuarios (más de 2 batches de 100)
    users = []
    for i in range(250):
        user = UserGamification(
            user_id=2000 + i,
            total_besitos=0,
            current_level_id=levels[0].id
        )
        users.append(user)

    db_session.add_all(users)
    await db_session.commit()

    # Mock del bot
    mock_bot = AsyncMock()
    mock_bot.send_message = AsyncMock()

    # Ejecutar verificación (no debería fallar)
    await check_all_users_progression(db_session, mock_bot)

    # Verificar que se procesaron todos (aunque no haya level-ups)
    # Simplemente verificar que no hubo errores
    assert True  # Si llegó aquí, el batch processing funcionó


@pytest.mark.asyncio
async def test_check_all_users_handles_individual_errors(
    db_session,
    users_with_besitos,
    levels
):
    """Verifica que errores en usuarios individuales no detienen el proceso."""
    # Mock del bot que falla para el segundo usuario
    mock_bot = AsyncMock()

    call_count = 0
    def side_effect_send(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:  # Primera llamada falla
            raise Exception("User blocked bot")
        # Segunda llamada funciona
        return AsyncMock()

    mock_bot.send_message = AsyncMock(side_effect=side_effect_send)

    # Ejecutar verificación (no debería lanzar excepción)
    await check_all_users_progression(db_session, mock_bot)

    # Verificar que ambos usuarios subieron de nivel a pesar del error
    await db_session.refresh(users_with_besitos[1])
    assert users_with_besitos[1].current_level_id == levels[1].id

    await db_session.refresh(users_with_besitos[2])
    assert users_with_besitos[2].current_level_id == levels[2].id


@pytest.mark.asyncio
async def test_no_level_ups_if_users_already_at_correct_level(db_session, levels):
    """Verifica que no se hacen level-ups si el usuario ya está en el nivel correcto."""
    # Usuario ya en nivel correcto
    user = UserGamification(
        user_id=3001,
        total_besitos=150,
        current_level_id=levels[1].id  # Ya en Intermedio
    )
    db_session.add(user)
    await db_session.commit()

    # Mock del bot
    mock_bot = AsyncMock()
    mock_bot.send_message = AsyncMock()

    # Ejecutar verificación
    await check_all_users_progression(db_session, mock_bot)

    # Verificar que no se envió notificación
    mock_bot.send_message.assert_not_called()

    # Verificar que el nivel no cambió
    await db_session.refresh(user)
    assert user.current_level_id == levels[1].id
