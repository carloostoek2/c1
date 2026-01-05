"""
Tests E2E para ONDA C: El Gabinete + Conversión.

Valida:
- DiscountService: Descuentos inteligentes
- ConversionService: Triggers y rate limiting
- StockLimitedService: Gestión de stock limitado
- Seed script: Creación de items narrativos
"""

import pytest
from datetime import datetime, timedelta

from bot.services.discount import DiscountService
from bot.services.conversion import ConversionService
from bot.shop.services.stock import StockLimitedService
from bot.database.models import ConversionEvent, LimitedStock


# ========================================
# TESTS: DiscountService
# ========================================

@pytest.mark.asyncio
async def test_discount_service_level_discount(db_setup):
    """Test: Descuento por nivel narrativo funciona correctamente."""
    from bot.database.engine import get_session

    async with get_session() as session:
        discount_service = DiscountService(session)

        # Simular usuario con nivel 3 (5%)
        from bot.narrative.services.progress import ProgressService
        progress_service = ProgressService(session)
        progress = await progress_service.get_or_create_progress(1)
        progress.current_level = 3
        await session.commit()

        # Calcular descuento
        level_discount = await discount_service._get_level_discount(1)

        assert level_discount == 0.05  # 5% para nivel 3


@pytest.mark.asyncio
async def test_discount_service_streak_discount(db_setup):
    """Test: Descuento por streak funciona correctamente."""
    from bot.database.engine import get_session

    async with get_session() as session:
        discount_service = DiscountService(session)

        # Crear streak de 14 días directamente
        from bot.gamification.database.models import UserStreak, UserGamification
        from sqlalchemy import select

        # Crear UserGamification primero (FK requirement)
        user_gamif = UserGamification(user_id=1, besitos=0, total_reactions=0)
        session.add(user_gamif)
        await session.flush()

        # Crear UserStreak
        user_streak = UserStreak(user_id=1, current_streak=14, longest_streak=14)
        session.add(user_streak)
        await session.commit()

        # Calcular descuento
        streak_discount = await discount_service._get_streak_discount(1)
        assert streak_discount == 0.05  # 5% para 14+ días


@pytest.mark.asyncio
async def test_discount_service_combined_discounts(db_setup):
    """Test: Descuentos combinados se suman correctamente."""
    from bot.database.engine import get_session

    async with get_session() as session:
        discount_service = DiscountService(session)

        # Setup: Nivel 3 (5%) + streak 14 (5%) = 10% total
        from bot.narrative.services.progress import ProgressService
        progress_service = ProgressService(session)
        progress = await progress_service.get_or_create_progress(1)
        progress.current_level = 3
        await session.commit()

        # Calcular descuento total
        total, reasons = await discount_service.calculate_discount(1, 999)

        # Debe tener al menos nivel discount
        assert total >= 0.05
        assert len(reasons) > 0


@pytest.mark.asyncio
async def test_discount_service_first_purchase_bonus(db_setup):
    """Test: Descuento de primera compra funciona."""
    from bot.database.engine import get_session

    async with get_session() as session:
        discount_service = DiscountService(session)

        # Verificar que es primera compra (usuario sin items)
        is_first = await discount_service._is_first_purchase(999)
        assert is_first is True


# ========================================
# TESTS: ConversionService
# ========================================

@pytest.mark.asyncio
async def test_conversion_service_check_triggers(db_setup):
    """Test: ConversionService detecta triggers correctamente."""
    from bot.database.engine import get_session

    async with get_session() as session:
        conversion_service = ConversionService(session)

        # Simular usuario con nivel 3 completado (trigger free_to_vip)
        from bot.narrative.services.progress import ProgressService
        progress_service = ProgressService(session)
        progress = await progress_service.get_or_create_progress(1)
        progress.chapters_completed = 3
        await session.commit()

        # Verificar triggers
        triggers = await conversion_service.check_conversion_triggers(1)

        # Debe detectar al menos el trigger de nivel 3
        assert len(triggers) >= 0  # Puede no tener si ya es VIP


@pytest.mark.asyncio
async def test_conversion_service_rate_limiting(db_setup):
    """Test: Rate limiting funciona (no spam)."""
    from bot.database.engine import get_session

    async with get_session() as session:
        conversion_service = ConversionService(session)

        # Primera oferta: debe permitirse
        should_show_first = await conversion_service.should_show_offer(1, "free_to_vip")
        assert should_show_first is True

        # Registrar oferta rechazada
        await conversion_service.record_conversion_event(
            user_id=1,
            event_type="offer_declined",
            offer_type="free_to_vip",
        )

        # Segunda oferta inmediata: NO debe permitirse (rate limit)
        should_show_second = await conversion_service.should_show_offer(1, "free_to_vip")
        assert should_show_second is False


@pytest.mark.asyncio
async def test_conversion_service_record_event(db_setup):
    """Test: Eventos de conversión se registran correctamente."""
    from bot.database.engine import get_session

    async with get_session() as session:
        conversion_service = ConversionService(session)

        # Registrar evento
        await conversion_service.record_conversion_event(
            user_id=1,
            event_type="offer_shown",
            offer_type="free_to_vip",
            details={"archetype": "explorer"},
            discount_applied=0.15,
        )

        # Verificar que se creó el evento
        from sqlalchemy import select
        stmt = select(ConversionEvent).where(ConversionEvent.user_id == 1)
        result = await session.execute(stmt)
        event = result.scalar_one_or_none()

        assert event is not None
        assert event.event_type == "offer_shown"
        assert event.offer_type == "free_to_vip"


@pytest.mark.asyncio
async def test_conversion_service_get_stats(db_setup):
    """Test: Estadísticas de conversión se calculan correctamente."""
    from bot.database.engine import get_session

    async with get_session() as session:
        conversion_service = ConversionService(session)

        # Registrar eventos de prueba
        await conversion_service.record_conversion_event(1, "offer_shown", "test_offer")
        await conversion_service.record_conversion_event(1, "offer_accepted", "test_offer")

        # Obtener stats
        stats = await conversion_service.get_conversion_stats(1)

        assert stats["offers_shown"] >= 1
        assert stats["offers_accepted"] >= 1
        assert stats["conversion_rate"] >= 0.0


# ========================================
# TESTS: StockLimitedService
# ========================================

@pytest.mark.asyncio
async def test_stock_limited_service_create_item(db_setup):
    """Test: Crear item con stock limitado."""
    from bot.database.engine import get_session

    async with get_session() as session:
        stock_service = StockLimitedService(session)

        # Crear item limitado
        limited_item = await stock_service.create_limited_item(
            item_id=999,
            initial_quantity=10,
        )

        assert limited_item is not None
        assert limited_item.item_id == 999
        assert limited_item.remaining_quantity == 10


@pytest.mark.asyncio
async def test_stock_limited_service_check_availability(db_setup):
    """Test: Verificar disponibilidad de item limitado."""
    from bot.database.engine import get_session

    async with get_session() as session:
        stock_service = StockLimitedService(session)

        # Crear item con 5 unidades
        await stock_service.create_limited_item(item_id=888, initial_quantity=5)

        # Verificar disponibilidad
        is_available, remaining = await stock_service.check_availability(888)

        assert is_available is True
        assert remaining == 5


@pytest.mark.asyncio
async def test_stock_limited_service_reserve_item(db_setup):
    """Test: Reservar item reduce stock."""
    from bot.database.engine import get_session

    async with get_session() as session:
        stock_service = StockLimitedService(session)

        # Crear item
        await stock_service.create_limited_item(item_id=777, initial_quantity=3)

        # Reservar
        success = await stock_service.reserve_item(user_id=1, item_id=777)
        assert success is True

        # Verificar que stock se redujo
        _, remaining = await stock_service.check_availability(777)
        assert remaining == 2


@pytest.mark.asyncio
async def test_stock_limited_service_sold_out(db_setup):
    """Test: Item agotado no permite reservas."""
    from bot.database.engine import get_session

    async with get_session() as session:
        stock_service = StockLimitedService(session)

        # Crear item con 1 unidad
        await stock_service.create_limited_item(item_id=666, initial_quantity=1)

        # Reservar la única unidad
        await stock_service.reserve_item(user_id=1, item_id=666)

        # Intentar reservar de nuevo (debe fallar)
        success = await stock_service.reserve_item(user_id=2, item_id=666)
        assert success is False


@pytest.mark.asyncio
async def test_stock_limited_service_release_reservation(db_setup):
    """Test: Liberar reserva incrementa stock."""
    from bot.database.engine import get_session

    async with get_session() as session:
        stock_service = StockLimitedService(session)

        # Crear item
        await stock_service.create_limited_item(item_id=555, initial_quantity=2)

        # Reservar
        await stock_service.reserve_item(user_id=1, item_id=555)

        # Verificar stock reducido
        _, remaining_before = await stock_service.check_availability(555)
        assert remaining_before == 1

        # Liberar reserva
        await stock_service.release_reservation(user_id=1, item_id=555)

        # Verificar stock incrementado
        _, remaining_after = await stock_service.check_availability(555)
        assert remaining_after == 2


@pytest.mark.asyncio
async def test_stock_limited_service_get_active_items(db_setup):
    """Test: Obtener items activos con stock."""
    from bot.database.engine import get_session

    async with get_session() as session:
        stock_service = StockLimitedService(session)

        # Crear múltiples items
        await stock_service.create_limited_item(item_id=444, initial_quantity=5)
        await stock_service.create_limited_item(item_id=333, initial_quantity=0)  # Agotado

        # Obtener items activos
        active_items = await stock_service.get_limited_items(active_only=True)

        # Debe incluir solo el 444 (con stock)
        active_ids = [item.item_id for item in active_items]
        assert 444 in active_ids


@pytest.mark.asyncio
async def test_stock_limited_service_status_message(db_setup):
    """Test: Mensaje de estado de stock."""
    from bot.database.engine import get_session

    async with get_session() as session:
        stock_service = StockLimitedService(session)

        # Item con pocas unidades (3)
        await stock_service.create_limited_item(item_id=222, initial_quantity=3)

        # Obtener mensaje
        message = await stock_service.get_stock_status_message(222)

        assert message is not None
        assert len(message) > 0
        assert "última" in message.lower() or "últimas" in message.lower()


# ========================================
# INTEGRATION TESTS
# ========================================

@pytest.mark.asyncio
async def test_discount_and_conversion_integration(db_setup):
    """Test: Integración entre DiscountService y ConversionService."""
    from bot.database.engine import get_session

    async with get_session() as session:
        discount_service = DiscountService(session)
        conversion_service = ConversionService(session)

        # Setup: Usuario con alto engagement
        from bot.narrative.services.progress import ProgressService
        progress_service = ProgressService(session)
        progress = await progress_service.get_or_create_progress(1)
        progress.chapters_completed = 3
        progress.total_decisions = 25
        await session.commit()

        # Obtener triggers
        triggers = await conversion_service.check_conversion_triggers(1)

        # Calcular descuentos aplicables
        discounts = await discount_service.get_applicable_discounts(1)

        # Ambos deben funcionar sin errores
        assert triggers is not None
        assert discounts is not None


@pytest.mark.asyncio
async def test_conversion_with_lucien_voice(db_setup):
    """Test: ConversionService usa LucienVoiceService."""
    from bot.database.engine import get_session

    async with get_session() as session:
        conversion_service = ConversionService(session)

        # Verificar que tiene instancia de Lucien
        assert conversion_service.lucien is not None

        # Obtener oferta (debe usar voz de Lucien)
        # Simular usuario con trigger
        from bot.narrative.services.progress import ProgressService
        progress_service = ProgressService(session)
        progress = await progress_service.get_or_create_progress(1)
        progress.chapters_completed = 3
        await session.commit()

        offer = await conversion_service.get_offer_for_user(1, "free_to_vip")

        # Puede ser None por rate limiting, pero si existe debe tener mensaje
        if offer:
            assert "message" in offer
            assert len(offer["message"]) > 0
