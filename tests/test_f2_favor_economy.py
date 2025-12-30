"""
Tests para FASE 2 - Economía de Favores.

Verifica:
- F2.1: Soporte de decimales en besitos
- F2.2: Configuración de economía
"""
import pytest
from datetime import datetime, UTC

from bot.gamification.services.besito import BesitoService
from bot.gamification.services.economy_config import EconomyConfigService
from bot.gamification.database.models import UserGamification, GamificationConfig
from bot.gamification.database.enums import TransactionType


@pytest.mark.asyncio
async def test_f21_grant_decimal_besitos(session):
    """F2.1: Verificar que se pueden otorgar besitos decimales."""
    user_id = 999001
    besito_service = BesitoService(session)

    # Otorgar 0.1 besitos
    amount = await besito_service.grant_besitos(
        user_id=user_id,
        amount=0.1,
        transaction_type=TransactionType.REACTION,
        description="Test reaction"
    )

    assert amount == 0.1

    # Verificar balance
    balance = await besito_service.get_balance(user_id)
    assert balance == 0.1

    # Otorgar más decimales
    await besito_service.grant_besitos(
        user_id=user_id,
        amount=0.5,
        transaction_type=TransactionType.DAILY_MISSION,
        description="Test daily mission"
    )

    # Verificar balance total
    balance = await besito_service.get_balance(user_id)
    assert balance == pytest.approx(0.6, rel=1e-6)


@pytest.mark.asyncio
async def test_f21_deduct_decimal_besitos(session):
    """F2.1: Verificar que se pueden deducir besitos decimales."""
    user_id = 999002
    besito_service = BesitoService(session)

    # Otorgar inicial
    await besito_service.grant_besitos(
        user_id=user_id,
        amount=5.0,
        transaction_type=TransactionType.LEVEL_UP,
        description="Initial grant"
    )

    # Deducir 0.5
    success, msg, balance = await besito_service.deduct_besitos(
        user_id=user_id,
        amount=0.5,
        transaction_type=TransactionType.PURCHASE,
        description="Test purchase"
    )

    assert success is True
    assert balance == pytest.approx(4.5, rel=1e-6)

    # Deducir 1.3
    success, msg, balance = await besito_service.deduct_besitos(
        user_id=user_id,
        amount=1.3,
        transaction_type=TransactionType.PURCHASE,
        description="Another purchase"
    )

    assert success is True
    assert balance == pytest.approx(3.2, rel=1e-6)


@pytest.mark.asyncio
async def test_f21_decimal_precision(session):
    """F2.1: Verificar precisión de decimales en operaciones múltiples."""
    user_id = 999003
    besito_service = BesitoService(session)

    # Simular 10 reacciones de 0.1 cada una
    for _ in range(10):
        await besito_service.grant_besitos(
            user_id=user_id,
            amount=0.1,
            transaction_type=TransactionType.REACTION,
            description="Reaction"
        )

    balance = await besito_service.get_balance(user_id)

    # Debería ser exactamente 1.0 (o muy cercano debido a float precision)
    assert balance == pytest.approx(1.0, rel=1e-6)


@pytest.mark.asyncio
async def test_f21_user_gamification_stores_floats(session):
    """F2.1: Verificar que UserGamification almacena correctamente floats."""
    user_id = 999004
    besito_service = BesitoService(session)

    await besito_service.grant_besitos(
        user_id=user_id,
        amount=3.75,
        transaction_type=TransactionType.CUSTOM,
        description="Custom grant"
    )

    # Consultar directamente la BD
    from sqlalchemy import select
    stmt = select(UserGamification).where(UserGamification.user_id == user_id)
    result = await session.execute(stmt)
    user_gamif = result.scalar_one()

    # Verificar que el valor es float
    assert isinstance(user_gamif.total_besitos, float)
    assert user_gamif.total_besitos == pytest.approx(3.75, rel=1e-6)
    assert isinstance(user_gamif.besitos_earned, float)
    assert user_gamif.besitos_earned == pytest.approx(3.75, rel=1e-6)


@pytest.mark.asyncio
async def test_f22_economy_config_exists(session):
    """F2.2: Verificar que GamificationConfig tiene campos de economía."""
    economy_service = EconomyConfigService(session)

    config = await economy_service.get_config()

    # Verificar que los campos existen
    assert hasattr(config, 'earn_reaction_base')
    assert hasattr(config, 'earn_first_reaction_day')
    assert hasattr(config, 'limit_reactions_per_day')
    assert hasattr(config, 'earn_mission_daily')
    assert hasattr(config, 'earn_mission_weekly')
    assert hasattr(config, 'earn_level_evaluation')
    assert hasattr(config, 'earn_streak_7_days')
    assert hasattr(config, 'earn_streak_30_days')
    assert hasattr(config, 'earn_easter_egg_min')
    assert hasattr(config, 'earn_easter_egg_max')
    assert hasattr(config, 'earn_referral_active')


@pytest.mark.asyncio
async def test_f22_economy_config_defaults(session):
    """F2.2: Verificar valores por defecto de configuración de economía."""
    economy_service = EconomyConfigService(session)

    # Obtener valores
    reaction_base = await economy_service.get_reaction_base()
    first_reaction = await economy_service.get_first_reaction_day()
    reactions_limit = await economy_service.get_reactions_daily_limit()
    mission_daily = await economy_service.get_mission_daily()

    # Verificar valores por defecto (según FAVOR_REWARDS en formatters.py)
    assert reaction_base == 0.1
    assert first_reaction == 0.5
    assert reactions_limit == 10
    assert mission_daily == 1.0


@pytest.mark.asyncio
async def test_f22_update_economy_values(session):
    """F2.2: Verificar actualización de valores de economía."""
    economy_service = EconomyConfigService(session)

    # Actualizar valor base de reacción
    success = await economy_service.update_reaction_base(0.2)
    assert success is True

    # Verificar que se actualizó
    new_value = await economy_service.get_reaction_base()
    assert new_value == 0.2

    # Actualizar múltiples valores
    success, msg = await economy_service.update_economy_values({
        'earn_mission_daily': 2.0,
        'earn_mission_weekly': 5.0,
        'limit_reactions_per_day': 15
    })

    assert success is True
    assert "3 economy values" in msg

    # Verificar actualizaciones
    daily = await economy_service.get_mission_daily()
    weekly = await economy_service.get_mission_weekly()
    limit = await economy_service.get_reactions_daily_limit()

    assert daily == 2.0
    assert weekly == 5.0
    assert limit == 15


@pytest.mark.asyncio
async def test_f22_reset_to_defaults(session):
    """F2.2: Verificar reset de configuración a valores por defecto."""
    economy_service = EconomyConfigService(session)

    # Cambiar algunos valores
    await economy_service.update_reaction_base(999.0)
    await economy_service.update_first_reaction_day(999.0)

    # Reset
    success = await economy_service.reset_to_defaults()
    assert success is True

    # Verificar que volvieron a defaults
    reaction_base = await economy_service.get_reaction_base()
    first_reaction = await economy_service.get_first_reaction_day()

    assert reaction_base == 0.1
    assert first_reaction == 0.5


@pytest.mark.asyncio
async def test_f22_invalid_values_rejected(session):
    """F2.2: Verificar que valores inválidos son rechazados."""
    economy_service = EconomyConfigService(session)

    # Intentar valor negativo
    success = await economy_service.update_reaction_base(-1.0)
    assert success is False

    # Intentar límite inválido (< 1)
    success = await economy_service.update_reactions_daily_limit(0)
    assert success is False

    # Valores deben permanecer sin cambios
    reaction_base = await economy_service.get_reaction_base()
    limit = await economy_service.get_reactions_daily_limit()

    assert reaction_base >= 0
    assert limit >= 1


@pytest.mark.asyncio
async def test_f21_transaction_history_with_decimals(session):
    """F2.1: Verificar historial de transacciones con decimales."""
    user_id = 999005
    besito_service = BesitoService(session)

    # Realizar varias transacciones con decimales
    await besito_service.grant_besitos(
        user_id=user_id,
        amount=0.1,
        transaction_type=TransactionType.REACTION,
        description="Reaction 1"
    )

    await besito_service.grant_besitos(
        user_id=user_id,
        amount=0.5,
        transaction_type=TransactionType.DAILY_MISSION,
        description="Daily mission"
    )

    await besito_service.deduct_besitos(
        user_id=user_id,
        amount=0.3,
        transaction_type=TransactionType.PURCHASE,
        description="Purchase"
    )

    # Obtener historial
    history = await besito_service.get_transaction_history(
        user_id=user_id,
        limit=10
    )

    # Verificar que hay 3 transacciones
    assert len(history) == 3

    # Verificar que los amounts son floats
    for trans in history:
        assert isinstance(trans.amount, float)
        assert isinstance(trans.balance_after, float)

    # Verificar orden (más reciente primero)
    assert history[0].description == "Purchase"
    assert history[0].amount == -0.3  # Negativo para deducción
    assert history[1].description == "Daily mission"
    assert history[1].amount == 0.5
    assert history[2].description == "Reaction 1"
    assert history[2].amount == 0.1


@pytest.mark.asyncio
async def test_f2_integration_economy_config_and_service(session):
    """F2: Test de integración entre EconomyConfigService y BesitoService."""
    user_id = 999006
    economy_service = EconomyConfigService(session)
    besito_service = BesitoService(session)

    # Obtener valor configurado para reacciones
    reaction_value = await economy_service.get_reaction_base()

    # Otorgar besitos usando ese valor
    await besito_service.grant_besitos(
        user_id=user_id,
        amount=reaction_value,
        transaction_type=TransactionType.REACTION,
        description="Using configured value"
    )

    # Verificar balance
    balance = await besito_service.get_balance(user_id)
    assert balance == pytest.approx(reaction_value, rel=1e-6)

    # Cambiar configuración
    await economy_service.update_reaction_base(0.3)
    new_reaction_value = await economy_service.get_reaction_base()

    # Otorgar con nuevo valor
    await besito_service.grant_besitos(
        user_id=user_id,
        amount=new_reaction_value,
        transaction_type=TransactionType.REACTION,
        description="Using updated value"
    )

    # Verificar balance actualizado
    balance = await besito_service.get_balance(user_id)
    expected = reaction_value + new_reaction_value  # 0.1 + 0.3 = 0.4
    assert balance == pytest.approx(expected, rel=1e-6)
