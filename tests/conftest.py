"""
Pytest Configuration and Shared Fixtures.

Proporciona fixtures comunes para todos los tests:
- mock_bot: Mock del bot de Telegram
- session: Sesión async de SQLAlchemy
"""
import pytest
import asyncio
import os
from unittest.mock import AsyncMock, Mock

from bot.database import init_db, close_db, get_session
from config import Config


@pytest.fixture
def event_loop():
    """
    Fixture: Event loop para tests async.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


# Hook para inicializar BD antes de cada test async
@pytest.fixture(autouse=True)
def db_setup(event_loop):
    """
    Setup BD antes de cada test.

    Elimina la BD existente para asegurar tests aislados.
    """
    # Eliminar archivo de BD si existe (para tests limpios)
    db_path = Config.DATABASE_URL.replace("sqlite+aiosqlite:///", "")
    if os.path.exists(db_path):
        os.remove(db_path)
    # También eliminar archivos auxiliares de WAL
    for suffix in ["-wal", "-shm"]:
        aux_path = db_path + suffix
        if os.path.exists(aux_path):
            os.remove(aux_path)

    # Ejecutar init_db antes del test
    event_loop.run_until_complete(init_db())

    yield

    # Limpiar BD despues del test
    event_loop.run_until_complete(close_db())


@pytest.fixture
def mock_bot():
    """
    Fixture: Mock del bot de Telegram.

    Proporciona mock de métodos Telegram API necesarios:
    - get_chat
    - get_chat_member
    - create_chat_invite_link
    - ban_chat_member
    - unban_chat_member
    - send_message
    - approve_chat_join_request
    - decline_chat_join_request
    """
    bot = Mock()
    bot.id = 123456789

    # Mock de métodos necesarios (retornan AsyncMock)
    bot.get_chat = AsyncMock()
    bot.get_chat_member = AsyncMock()
    bot.create_chat_invite_link = AsyncMock()
    bot.ban_chat_member = AsyncMock()
    bot.unban_chat_member = AsyncMock()
    bot.send_message = AsyncMock()
    bot.approve_chat_join_request = AsyncMock()
    bot.decline_chat_join_request = AsyncMock()

    return bot


@pytest.fixture
async def session():
    """
    Fixture: Sesión async de SQLAlchemy.

    Proporciona una sesión de BD para tests que manipulan datos.
    La sesión se cierra automáticamente al final del test.
    """
    async with get_session() as session:
        yield session
