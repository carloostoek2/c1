"""
Tests para el panel de estadísticas de economía.

Incluye:
- Tests unitarios de StatsService (get_economy_overview, get_besitos_sources_config)
- Tests de integración del handler economy.py
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from bot.gamification.services.stats import StatsService
from bot.gamification.database.models import (
    UserGamification, Reaction, Mission, Level, GamificationConfig
)


# ========================================
# TESTS UNITARIOS - StatsService
# ========================================

@pytest.mark.asyncio
async def test_get_economy_overview_empty_database(db_session):
    """Verificar que retorna zeros cuando no hay usuarios."""
    stats = StatsService(db_session)
    overview = await stats.get_economy_overview()

    assert overview['total_in_circulation'] == 0
    assert overview['average_per_user'] == 0.0
    assert overview['total_earned_historical'] == 0
    assert overview['total_spent_historical'] == 0
    assert overview['total_users_with_besitos'] == 0
    assert overview['top_holders'] == []
    assert overview['by_level'] == {}


@pytest.mark.asyncio
async def test_get_economy_overview_with_data(db_session, sample_level):
    """Verificar cálculos correctos con datos reales."""
    # Crear 3 usuarios con besitos
    user1 = UserGamification(
        user_id=1,
        total_besitos=100,
        besitos_earned=200,
        besitos_spent=100,
        current_level_id=sample_level.id
    )
    user2 = UserGamification(
        user_id=2,
        total_besitos=50,
        besitos_earned=80,
        besitos_spent=30,
        current_level_id=sample_level.id
    )
    user3 = UserGamification(
        user_id=3,
        total_besitos=0,
        besitos_earned=10,
        besitos_spent=10,
        current_level_id=sample_level.id
    )

    db_session.add_all([user1, user2, user3])
    await db_session.commit()

    stats = StatsService(db_session)
    overview = await stats.get_economy_overview()

    assert overview['total_in_circulation'] == 150  # 100 + 50 + 0
    assert overview['average_per_user'] == 50.0    # 150 / 3
    assert overview['total_earned_historical'] == 290  # 200 + 80 + 10
    assert overview['total_spent_historical'] == 140   # 100 + 30 + 10
    assert overview['total_users_with_besitos'] == 2   # user1 y user2
    assert len(overview['top_holders']) == 3  # Top 5, pero solo hay 3 usuarios
    assert overview['top_holders'][0]['user_id'] == 1
    assert overview['top_holders'][0]['total_besitos'] == 100
    assert sample_level.name in overview['by_level']
    assert overview['by_level'][sample_level.name] == 150


@pytest.mark.asyncio
async def test_get_besitos_sources_config_all_active(db_session, sample_level):
    """Verificar que retorna todas las fuentes activas."""
    # Crear reacciones activas
    r1 = Reaction(emoji="❤️", name="Corazón", besitos_value=5, active=True)
    r2 = Reaction(emoji="🔥", name="Fuego", besitos_value=10, active=True)
    db_session.add_all([r1, r2])

    # Crear misiones activas con recompensa
    m1 = Mission(
        name="Test Mission",
        description="Test",
        besitos_reward=50,
        active=True,
        mission_type="one_time",
        criteria='{"type": "one_time"}',
        created_by=1  # Admin user ID
    )
    db_session.add_all([m1])

    # Crear configuración de regalo diario
    config = GamificationConfig(id=1, daily_gift_enabled=True, daily_gift_besitos=10)
    db_session.add(config)

    await db_session.commit()

    stats = StatsService(db_session)
    sources = await stats.get_besitos_sources_config()

    assert len(sources['reactions']) == 2
    assert sources['reactions'][0]['emoji'] == "🔥"  # Ordenado por valor DESC
    assert sources['reactions'][1]['emoji'] == "❤️"

    assert len(sources['missions']) == 1
    assert sources['missions'][0]['name'] == "Test Mission"
    assert sources['missions'][0]['besitos_reward'] == 50

    # Los niveles actualmente no otorgan besitos automáticamente
    assert len(sources['levels']) == 0

    assert sources['daily_gift']['enabled'] is True
    assert sources['daily_gift']['amount'] == 10


@pytest.mark.asyncio
async def test_get_besitos_sources_config_filters_inactive(db_session):
    """Verificar que NO retorna elementos inactivos."""
    # Crear reacciones inactivas
    r1 = Reaction(emoji="❤️", name="Corazón", besitos_value=5, active=False)
    db_session.add(r1)

    # Crear misiones inactivas
    m1 = Mission(
        name="Inactive Mission",
        description="Test",
        besitos_reward=50,
        active=False,
        mission_type="one_time",
        criteria='{"type": "one_time"}',
        created_by=1  # Admin user ID
    )
    db_session.add(m1)

    # Crear misiones activas pero sin recompensa
    m2 = Mission(
        name="No Reward",
        description="Test",
        besitos_reward=0,
        active=True,
        mission_type="one_time",
        criteria='{"type": "one_time"}',
        created_by=1  # Admin user ID
    )
    db_session.add(m2)

    await db_session.commit()

    stats = StatsService(db_session)
    sources = await stats.get_besitos_sources_config()

    assert len(sources['reactions']) == 0
    assert len(sources['missions']) == 0


@pytest.mark.asyncio
async def test_get_besitos_sources_config_no_gamification_config(db_session):
    """Verificar manejo correcto cuando no existe GamificationConfig."""
    stats = StatsService(db_session)
    sources = await stats.get_besitos_sources_config()

    # Debe retornar valores por defecto
    assert sources['daily_gift']['enabled'] is False
    assert sources['daily_gift']['amount'] == 0


# ========================================
# TESTS DE INTEGRACIÓN - Handler
# ========================================

@pytest.mark.asyncio
async def test_economy_handler_callback_data():
    """Verificar que el handler escucha el callback correcto."""
    from bot.gamification.handlers.admin.economy import router

    # Verificar que existe handler para "gamif:admin:economy"
    handlers = [h for h in router.callback_query.handlers]

    # El router debe tener al menos un handler registrado
    assert len(handlers) > 0


@pytest.mark.asyncio
async def test_economy_message_format_with_data():
    """Verificar que el mensaje se formatea correctamente con datos."""
    from bot.gamification.handlers.admin.economy import _format_economy_message

    # Mock de datos completos
    overview = {
        'total_in_circulation': 12450,
        'average_per_user': 124.5,
        'total_earned_historical': 45600,
        'total_spent_historical': 33150,
        'total_users_with_besitos': 100,
        'top_holders': [
            {'user_id': 123, 'total_besitos': 2500},
            {'user_id': 456, 'total_besitos': 1800}
        ],
        'by_level': {'Novato': 3200, 'Bronce': 5100}
    }

    sources = {
        'reactions': [{'emoji': '❤️', 'name': 'Corazón', 'besitos_value': 5}],
        'missions': [{'id': 1, 'name': 'Test Mission', 'besitos_reward': 50}],
        'daily_gift': {'enabled': True, 'amount': 10},
        'levels': []  # Los niveles actualmente no otorgan besitos
    }

    message_text = _format_economy_message(overview, sources)

    # Verificar contenido del mensaje
    assert "💰 <b>Estadísticas de Economía</b>" in message_text
    assert "12,450" in message_text  # Total en circulación formateado
    assert "124.5" in message_text   # Promedio
    assert "🥇 Usuario #123: 2,500 besitos" in message_text
    assert "❤️ Corazón: 5 besitos" in message_text
    assert "Test Mission: 50 besitos" in message_text
    assert "Habilitado" in message_text
    assert "✅" in message_text


@pytest.mark.asyncio
async def test_economy_handler_edge_case_no_data():
    """Verificar que el handler maneja correctamente caso sin datos."""
    from bot.gamification.handlers.admin.economy import _format_economy_message

    overview = {
        'total_in_circulation': 0,
        'average_per_user': 0.0,
        'total_earned_historical': 0,
        'total_spent_historical': 0,
        'total_users_with_besitos': 0,
        'top_holders': [],
        'by_level': {}
    }

    sources = {
        'reactions': [],
        'missions': [],
        'daily_gift': {'enabled': False, 'amount': 0},
        'levels': []
    }

    message_text = _format_economy_message(overview, sources)

    assert "No hay usuarios con besitos" in message_text
    assert "No hay reacciones configuradas" in message_text
    assert "No hay misiones con recompensas" in message_text
    assert "Deshabilitado" in message_text
    assert "❌" in message_text


@pytest.mark.asyncio
async def test_economy_message_limits_lists_to_5():
    """Verificar que las listas se limitan a 5 elementos + '... y N más'."""
    from bot.gamification.handlers.admin.economy import _format_economy_message

    overview = {
        'total_in_circulation': 100,
        'average_per_user': 10.0,
        'total_earned_historical': 200,
        'total_spent_historical': 100,
        'total_users_with_besitos': 10,
        'top_holders': [
            {'user_id': i, 'total_besitos': 100 - i}
            for i in range(10)  # 10 holders
        ],
        'by_level': {}
    }

    sources = {
        'reactions': [
            {'emoji': f'emoji{i}', 'name': f'Reaction {i}', 'besitos_value': i}
            for i in range(8)  # 8 reacciones
        ],
        'missions': [],
        'daily_gift': {'enabled': False, 'amount': 0},
        'levels': []
    }

    message_text = _format_economy_message(overview, sources)

    # Verificar que solo se muestran 5 holders
    assert message_text.count('Usuario #') == 5

    # Verificar que solo se muestran 5 reacciones
    assert message_text.count('Reaction') == 5

    # Verificar mensaje "... y N más"
    assert "... y 3 más" in message_text  # 8 - 5 = 3 reacciones más
