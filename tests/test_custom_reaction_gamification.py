"""
Tests para CustomReactionService con características de gamificación F2.3-F2.6.

Verifica:
- F2.3: Actualización de rachas y bonus por hitos (7/30 días)
- F2.5: Límites diarios configurables
- F2.6: Bonus primera reacción del día
"""

import pytest
from datetime import datetime, UTC, timedelta
from sqlalchemy import select

from bot.database.models import User, BroadcastMessage
from bot.gamification.database.models import (
    Reaction,
    CustomReaction,
    UserGamification,
    UserStreak,
    GamificationConfig
)
from bot.gamification.services.custom_reaction import CustomReactionService
from bot.gamification.services.economy_config import EconomyConfigService


class TestCustomReactionGamification:
    """Tests para gamificación en CustomReactionService."""

    @pytest.mark.asyncio
    async def test_f25_daily_limit_blocks_after_limit(self, db_setup, event_loop):
        """F2.5: Verificar que el límite diario bloquea después de alcanzarlo."""
        from bot.database.engine import get_session

        async with get_session() as session:
            # Setup: Usuario y reacciones
            user = User(
                user_id=800000001,
                username="limit_user",
                first_name="LimitUser",
                role="VIP"
            )
            session.add(user)

            # Crear UserGamification
            user_gamif = UserGamification(user_id=user.user_id)
            session.add(user_gamif)

            # Crear múltiples reacciones para poder registrar varias
            reactions = []
            for i in range(15):  # Más del límite por defecto (10)
                reaction = Reaction(
                    emoji=f"E{i}",
                    name=f"Reaction {i}",
                    besitos_value=1,
                    active=True
                )
                reactions.append(reaction)
                session.add(reaction)

            # Crear broadcast messages
            broadcasts = []
            for i in range(15):
                broadcast_msg = BroadcastMessage(
                    message_id=800000001 + i,
                    chat_id=-1001234567890,
                    content_type="text",
                    content_text=f"Test {i}",
                    sent_by=user.user_id,
                    gamification_enabled=True
                )
                broadcasts.append(broadcast_msg)
                session.add(broadcast_msg)

            await session.commit()

            # Configurar límite diario a 5 para test más rápido
            economy = EconomyConfigService(session)
            await economy.update_reactions_daily_limit(5)

            service = CustomReactionService(session)

            # Registrar 5 reacciones (dentro del límite)
            for i in range(5):
                result = await service.register_custom_reaction(
                    broadcast_message_id=broadcasts[i].id,
                    user_id=user.user_id,
                    reaction_type_id=reactions[i].id,
                    emoji=f"E{i}"
                )
                assert result["success"] is True
                assert result["daily_limit_reached"] is False
                # Primera reacción tiene bonus
                if i == 0:
                    assert result["is_first_today"] is True

            # Intentar 6ta reacción (excede límite)
            result = await service.register_custom_reaction(
                broadcast_message_id=broadcasts[5].id,
                user_id=user.user_id,
                reaction_type_id=reactions[5].id,
                emoji="E5"
            )

            # Debería registrarse pero sin besitos
            assert result["success"] is True
            assert result["daily_limit_reached"] is True
            assert result["besitos_earned"] == 0
            assert "Límite diario" in result.get("message", "")

    @pytest.mark.asyncio
    async def test_f26_first_reaction_bonus(self, db_setup, event_loop):
        """F2.6: Verificar bonus por primera reacción del día."""
        from bot.database.engine import get_session

        async with get_session() as session:
            # Setup
            user = User(
                user_id=800000002,
                username="first_react_user",
                first_name="FirstReact",
                role="VIP"
            )
            session.add(user)

            user_gamif = UserGamification(user_id=user.user_id)
            session.add(user_gamif)

            reaction1 = Reaction(emoji="R1", name="R1", besitos_value=1, active=True)
            reaction2 = Reaction(emoji="R2", name="R2", besitos_value=1, active=True)
            session.add_all([reaction1, reaction2])

            broadcast1 = BroadcastMessage(
                message_id=800000100,
                chat_id=-1001234567890,
                content_type="text",
                content_text="Test 1",
                sent_by=user.user_id,
                gamification_enabled=True
            )
            broadcast2 = BroadcastMessage(
                message_id=800000101,
                chat_id=-1001234567890,
                content_type="text",
                content_text="Test 2",
                sent_by=user.user_id,
                gamification_enabled=True
            )
            session.add_all([broadcast1, broadcast2])
            await session.commit()

            # Obtener valores de economía (defaults: base=0.1, first=0.5)
            economy = EconomyConfigService(session)
            base_value = await economy.get_reaction_base()
            first_bonus = await economy.get_first_reaction_day()

            service = CustomReactionService(session)

            # Primera reacción del día: base + bonus
            result1 = await service.register_custom_reaction(
                broadcast_message_id=broadcast1.id,
                user_id=user.user_id,
                reaction_type_id=reaction1.id,
                emoji="R1"
            )

            assert result1["success"] is True
            assert result1["is_first_today"] is True
            expected_first = base_value + first_bonus  # 0.1 + 0.5 = 0.6
            assert result1["besitos_earned"] == pytest.approx(expected_first, rel=1e-6)

            # Segunda reacción del día: solo base
            result2 = await service.register_custom_reaction(
                broadcast_message_id=broadcast2.id,
                user_id=user.user_id,
                reaction_type_id=reaction2.id,
                emoji="R2"
            )

            assert result2["success"] is True
            assert result2["is_first_today"] is False
            assert result2["besitos_earned"] == pytest.approx(base_value, rel=1e-6)

    @pytest.mark.asyncio
    async def test_f23_streak_update(self, db_setup, event_loop):
        """F2.3: Verificar que las rachas se actualizan correctamente."""
        from bot.database.engine import get_session

        async with get_session() as session:
            # Setup
            user = User(
                user_id=800000003,
                username="streak_user",
                first_name="StreakUser",
                role="VIP"
            )
            session.add(user)

            user_gamif = UserGamification(user_id=user.user_id)
            session.add(user_gamif)

            reaction = Reaction(emoji="S1", name="S1", besitos_value=1, active=True)
            session.add(reaction)

            broadcast = BroadcastMessage(
                message_id=800000200,
                chat_id=-1001234567890,
                content_type="text",
                content_text="Test",
                sent_by=user.user_id,
                gamification_enabled=True
            )
            session.add(broadcast)
            await session.commit()

            service = CustomReactionService(session)

            # Registrar reacción (crea streak con current=1)
            result = await service.register_custom_reaction(
                broadcast_message_id=broadcast.id,
                user_id=user.user_id,
                reaction_type_id=reaction.id,
                emoji="S1"
            )

            assert result["success"] is True
            assert result["streak_days"] == 1

            # Verificar UserStreak creado
            streak = await service.get_user_streak(user.user_id)
            assert streak is not None
            assert streak.current_streak == 1
            assert streak.longest_streak == 1

    @pytest.mark.asyncio
    async def test_f23_streak_bonus_7_days(self, db_setup, event_loop):
        """F2.3: Verificar bonus al alcanzar racha de 7 días."""
        from bot.database.engine import get_session

        async with get_session() as session:
            # Setup
            user = User(
                user_id=800000004,
                username="streak7_user",
                first_name="Streak7",
                role="VIP"
            )
            session.add(user)

            user_gamif = UserGamification(user_id=user.user_id)
            session.add(user_gamif)

            # Crear streak con 6 días (a punto de alcanzar 7)
            yesterday = datetime.now(UTC) - timedelta(days=1)
            user_streak = UserStreak(
                user_id=user.user_id,
                current_streak=6,
                longest_streak=6,
                last_reaction_date=yesterday
            )
            session.add(user_streak)

            reaction = Reaction(emoji="S7", name="S7", besitos_value=1, active=True)
            session.add(reaction)

            broadcast = BroadcastMessage(
                message_id=800000300,
                chat_id=-1001234567890,
                content_type="text",
                content_text="Test",
                sent_by=user.user_id,
                gamification_enabled=True
            )
            session.add(broadcast)
            await session.commit()

            # Obtener valores de economía
            economy = EconomyConfigService(session)
            streak_7_bonus = await economy.get_streak_7_days()
            base_value = await economy.get_reaction_base()
            first_bonus = await economy.get_first_reaction_day()

            service = CustomReactionService(session)

            # Registrar reacción (alcanza día 7)
            result = await service.register_custom_reaction(
                broadcast_message_id=broadcast.id,
                user_id=user.user_id,
                reaction_type_id=reaction.id,
                emoji="S7"
            )

            assert result["success"] is True
            assert result["streak_days"] == 7

            # Verificar balance incluye bonus de racha
            # Total = base + first_bonus + streak_7_bonus = 0.1 + 0.5 + 2.0 = 2.6
            expected_total = base_value + first_bonus + streak_7_bonus
            assert result["total_besitos"] == pytest.approx(expected_total, rel=1e-6)

    @pytest.mark.asyncio
    async def test_economy_config_values_used(self, db_setup, event_loop):
        """Verificar que se usan los valores de EconomyConfigService."""
        from bot.database.engine import get_session

        async with get_session() as session:
            # Setup
            user = User(
                user_id=800000005,
                username="economy_user",
                first_name="EconomyUser",
                role="VIP"
            )
            session.add(user)

            user_gamif = UserGamification(user_id=user.user_id)
            session.add(user_gamif)

            reaction = Reaction(emoji="EC", name="EC", besitos_value=99, active=True)
            session.add(reaction)

            broadcast = BroadcastMessage(
                message_id=800000400,
                chat_id=-1001234567890,
                content_type="text",
                content_text="Test",
                sent_by=user.user_id,
                gamification_enabled=True
            )
            session.add(broadcast)
            await session.commit()

            # Cambiar valores de economía
            economy = EconomyConfigService(session)
            await economy.update_reaction_base(0.25)
            await economy.update_first_reaction_day(1.0)

            # Verificar valores actualizados
            new_base = await economy.get_reaction_base()
            new_first = await economy.get_first_reaction_day()
            assert new_base == 0.25
            assert new_first == 1.0

            service = CustomReactionService(session)

            # Registrar reacción
            result = await service.register_custom_reaction(
                broadcast_message_id=broadcast.id,
                user_id=user.user_id,
                reaction_type_id=reaction.id,
                emoji="EC"
            )

            # Debe usar valores de economía, no de Reaction.besitos_value
            expected = 0.25 + 1.0  # base + first bonus
            assert result["besitos_earned"] == pytest.approx(expected, rel=1e-6)
            assert result["besitos_earned"] != 99  # No usa Reaction.besitos_value

    @pytest.mark.asyncio
    async def test_streak_not_incremented_same_day(self, db_setup, event_loop):
        """Verificar que múltiples reacciones el mismo día no incrementan racha."""
        from bot.database.engine import get_session

        async with get_session() as session:
            # Setup
            user = User(
                user_id=800000006,
                username="sameday_user",
                first_name="SameDay",
                role="VIP"
            )
            session.add(user)

            user_gamif = UserGamification(user_id=user.user_id)
            session.add(user_gamif)

            reaction1 = Reaction(emoji="D1", name="D1", besitos_value=1, active=True)
            reaction2 = Reaction(emoji="D2", name="D2", besitos_value=1, active=True)
            session.add_all([reaction1, reaction2])

            broadcast1 = BroadcastMessage(
                message_id=800000500,
                chat_id=-1001234567890,
                content_type="text",
                content_text="Test 1",
                sent_by=user.user_id,
                gamification_enabled=True
            )
            broadcast2 = BroadcastMessage(
                message_id=800000501,
                chat_id=-1001234567890,
                content_type="text",
                content_text="Test 2",
                sent_by=user.user_id,
                gamification_enabled=True
            )
            session.add_all([broadcast1, broadcast2])
            await session.commit()

            service = CustomReactionService(session)

            # Primera reacción: streak = 1
            result1 = await service.register_custom_reaction(
                broadcast_message_id=broadcast1.id,
                user_id=user.user_id,
                reaction_type_id=reaction1.id,
                emoji="D1"
            )
            assert result1["streak_days"] == 1

            # Segunda reacción mismo día: streak sigue en 1
            result2 = await service.register_custom_reaction(
                broadcast_message_id=broadcast2.id,
                user_id=user.user_id,
                reaction_type_id=reaction2.id,
                emoji="D2"
            )
            assert result2["streak_days"] == 1

            # Verificar en BD
            streak = await service.get_user_streak(user.user_id)
            assert streak.current_streak == 1

    @pytest.mark.asyncio
    async def test_get_user_reactions_today(self, db_setup, event_loop):
        """Verificar método auxiliar get_user_reactions_today."""
        from bot.database.engine import get_session

        async with get_session() as session:
            # Setup
            user = User(
                user_id=800000007,
                username="count_user",
                first_name="CountUser",
                role="VIP"
            )
            session.add(user)

            user_gamif = UserGamification(user_id=user.user_id)
            session.add(user_gamif)

            reactions = [
                Reaction(emoji=f"C{i}", name=f"C{i}", besitos_value=1, active=True)
                for i in range(3)
            ]
            session.add_all(reactions)

            broadcasts = [
                BroadcastMessage(
                    message_id=800000600 + i,
                    chat_id=-1001234567890,
                    content_type="text",
                    content_text=f"Test {i}",
                    sent_by=user.user_id,
                    gamification_enabled=True
                )
                for i in range(3)
            ]
            session.add_all(broadcasts)
            await session.commit()

            service = CustomReactionService(session)

            # Verificar inicio en 0
            count0 = await service.get_user_reactions_today(user.user_id)
            assert count0 == 0

            # Registrar 3 reacciones
            for i in range(3):
                await service.register_custom_reaction(
                    broadcast_message_id=broadcasts[i].id,
                    user_id=user.user_id,
                    reaction_type_id=reactions[i].id,
                    emoji=f"C{i}"
                )

            # Verificar cuenta
            count3 = await service.get_user_reactions_today(user.user_id)
            assert count3 == 3

    @pytest.mark.asyncio
    async def test_inactive_reaction_rejected(self, db_setup, event_loop):
        """Verificar que reacciones inactivas son rechazadas."""
        from bot.database.engine import get_session

        async with get_session() as session:
            # Setup
            user = User(
                user_id=800000008,
                username="inactive_user",
                first_name="InactiveUser",
                role="VIP"
            )
            session.add(user)

            user_gamif = UserGamification(user_id=user.user_id)
            session.add(user_gamif)

            # Reacción inactiva
            reaction = Reaction(emoji="IN", name="Inactive", besitos_value=10, active=False)
            session.add(reaction)

            broadcast = BroadcastMessage(
                message_id=800000700,
                chat_id=-1001234567890,
                content_type="text",
                content_text="Test",
                sent_by=user.user_id,
                gamification_enabled=True
            )
            session.add(broadcast)
            await session.commit()

            service = CustomReactionService(session)

            # Intentar registrar reacción inactiva
            result = await service.register_custom_reaction(
                broadcast_message_id=broadcast.id,
                user_id=user.user_id,
                reaction_type_id=reaction.id,
                emoji="IN"
            )

            assert result["success"] is False
            assert "not found or inactive" in result.get("error", "")
