"""
Tests unitarios para CustomReactionService.

Tests:
- Registro de reacción válida
- Prevención de reacciones duplicadas
- Otorgamiento de besitos (usando economy_config)
- Actualización de estadísticas
- Obtención de reacciones de usuario
- Obtención de estadísticas de mensaje

Nota: Los valores de besitos provienen de EconomyConfigService, no de Reaction.besitos_value.
"""

import pytest
from sqlalchemy import select

from bot.database.models import User, BroadcastMessage
from bot.gamification.database.models import (
    Reaction,
    CustomReaction,
    UserGamification,
    GamificationConfig
)
from bot.gamification.services.custom_reaction import CustomReactionService
from bot.gamification.services.economy_config import EconomyConfigService


class TestCustomReactionService:
    """Tests para CustomReactionService."""

    @pytest.mark.asyncio
    async def test_register_custom_reaction_success(self, db_setup, event_loop):
        """Test: Registrar reacción válida y otorgar besitos."""
        from bot.database.engine import get_session

        async with get_session() as session:
            # Setup: Crear usuario, reacción y broadcast message
            user = User(
                user_id=900000001,
                username="reactor1",
                first_name="Reactor1",
                role="VIP"
            )
            session.add(user)

            # Crear UserGamification para el usuario
            user_gamif = UserGamification(user_id=user.user_id)
            session.add(user_gamif)

            reaction = Reaction(
                emoji="👍",
                name="Like",
                besitos_value=10,  # Este valor ya no se usa directamente
                active=True,
                button_emoji="👍",
                button_label="Me Gusta",
                sort_order=1
            )
            session.add(reaction)

            broadcast_msg = BroadcastMessage(
                message_id=700000001,
                chat_id=-1001234567890,
                content_type="text",
                content_text="Test broadcast",
                sent_by=user.user_id,
                gamification_enabled=True
            )
            session.add(broadcast_msg)
            await session.commit()

            # Obtener valores de economía (para verificar)
            economy = EconomyConfigService(session)
            base_value = await economy.get_reaction_base()
            first_bonus = await economy.get_first_reaction_day()
            expected_besitos = base_value + first_bonus  # Primera reacción del día

            # Obtener IDs
            reaction_id = reaction.id
            broadcast_id = broadcast_msg.id

            # Test: Registrar reacción
            service = CustomReactionService(session)
            result = await service.register_custom_reaction(
                broadcast_message_id=broadcast_id,
                user_id=user.user_id,
                reaction_type_id=reaction_id,
                emoji="👍"
            )

            # Verificar resultado
            assert result["success"] is True
            assert result["already_reacted"] is False
            assert result["besitos_earned"] == pytest.approx(expected_besitos, rel=1e-6)
            assert result["total_besitos"] == pytest.approx(expected_besitos, rel=1e-6)
            assert result["multiplier_applied"] == 1.0
            assert result["is_first_today"] is True

            # Verificar CustomReaction creado
            stmt = select(CustomReaction).where(
                CustomReaction.broadcast_message_id == broadcast_id,
                CustomReaction.user_id == user.user_id
            )
            result_db = await session.execute(stmt)
            custom_reaction = result_db.scalar_one()

            assert custom_reaction is not None
            assert custom_reaction.emoji == "👍"
            assert custom_reaction.besitos_earned == pytest.approx(expected_besitos, rel=1e-6)

            # Verificar besitos otorgados
            await session.refresh(user_gamif)
            assert user_gamif.total_besitos == pytest.approx(expected_besitos, rel=1e-6)
            assert user_gamif.besitos_earned == pytest.approx(expected_besitos, rel=1e-6)

            # Verificar stats actualizados
            await session.refresh(broadcast_msg)
            assert broadcast_msg.total_reactions == 1
            assert broadcast_msg.unique_reactors == 1

    @pytest.mark.asyncio
    async def test_register_custom_reaction_duplicate(self, db_setup, event_loop):
        """Test: Prevenir reacciones duplicadas."""
        from bot.database.engine import get_session

        async with get_session() as session:
            # Setup
            user = User(
                user_id=900000002,
                username="reactor2",
                first_name="Reactor2",
                role="VIP"
            )
            session.add(user)

            user_gamif = UserGamification(user_id=user.user_id)
            session.add(user_gamif)

            reaction = Reaction(
                emoji="❤️",
                name="Love",
                besitos_value=15,
                active=True
            )
            session.add(reaction)

            broadcast_msg = BroadcastMessage(
                message_id=700000002,
                chat_id=-1001234567890,
                content_type="text",
                content_text="Test",
                sent_by=user.user_id,
                gamification_enabled=True
            )
            session.add(broadcast_msg)
            await session.commit()

            # Obtener valores de economía
            economy = EconomyConfigService(session)
            base_value = await economy.get_reaction_base()
            first_bonus = await economy.get_first_reaction_day()
            expected_first = base_value + first_bonus

            reaction_id = reaction.id
            broadcast_id = broadcast_msg.id

            # Primer registro (debe funcionar)
            service = CustomReactionService(session)
            result1 = await service.register_custom_reaction(
                broadcast_message_id=broadcast_id,
                user_id=user.user_id,
                reaction_type_id=reaction_id,
                emoji="❤️"
            )

            assert result1["success"] is True
            assert result1["besitos_earned"] == pytest.approx(expected_first, rel=1e-6)

            # Segundo registro (debe fallar por duplicado)
            result2 = await service.register_custom_reaction(
                broadcast_message_id=broadcast_id,
                user_id=user.user_id,
                reaction_type_id=reaction_id,
                emoji="❤️"
            )

            assert result2["success"] is False
            assert result2["already_reacted"] is True
            assert result2["besitos_earned"] == 0

            # Verificar que solo hay 1 CustomReaction
            stmt = select(CustomReaction).where(
                CustomReaction.broadcast_message_id == broadcast_id
            )
            result_db = await session.execute(stmt)
            reactions = result_db.scalars().all()

            assert len(reactions) == 1

            # Verificar besitos solo otorgados una vez
            await session.refresh(user_gamif)
            assert user_gamif.total_besitos == pytest.approx(expected_first, rel=1e-6)

    @pytest.mark.asyncio
    async def test_get_user_reactions_for_message(self, db_setup, event_loop):
        """Test: Obtener IDs de reacciones de un usuario."""
        from bot.database.engine import get_session

        async with get_session() as session:
            # Setup
            user = User(
                user_id=900000003,
                username="reactor3",
                first_name="Reactor3",
                role="VIP"
            )
            session.add(user)

            user_gamif = UserGamification(user_id=user.user_id)
            session.add(user_gamif)

            reaction1 = Reaction(emoji="👍", name="Like", besitos_value=10, active=True)
            reaction2 = Reaction(emoji="❤️", name="Love", besitos_value=15, active=True)
            session.add_all([reaction1, reaction2])

            broadcast_msg = BroadcastMessage(
                message_id=700000003,
                chat_id=-1001234567890,
                content_type="text",
                content_text="Test",
                sent_by=user.user_id,
                gamification_enabled=True
            )
            session.add(broadcast_msg)
            await session.commit()

            reaction1_id = reaction1.id
            reaction2_id = reaction2.id
            broadcast_id = broadcast_msg.id

            # Registrar dos reacciones
            service = CustomReactionService(session)
            await service.register_custom_reaction(broadcast_id, user.user_id, reaction1_id, "👍")
            await service.register_custom_reaction(broadcast_id, user.user_id, reaction2_id, "❤️")

            # Test: Obtener reacciones del usuario
            user_reactions = await service.get_user_reactions_for_message(
                broadcast_id, user.user_id
            )

            # Verificar
            assert len(user_reactions) == 2
            assert reaction1_id in user_reactions
            assert reaction2_id in user_reactions

    @pytest.mark.asyncio
    async def test_get_message_reaction_stats(self, db_setup, event_loop):
        """Test: Obtener estadísticas de reacciones de un mensaje."""
        from bot.database.engine import get_session

        async with get_session() as session:
            # Setup: 3 usuarios, 2 reacciones
            users = [
                User(user_id=900000004, username="u1", first_name="U1", role="VIP"),
                User(user_id=900000005, username="u2", first_name="U2", role="VIP"),
                User(user_id=900000006, username="u3", first_name="U3", role="VIP"),
            ]
            session.add_all(users)

            # Crear UserGamification para cada usuario
            for u in users:
                session.add(UserGamification(user_id=u.user_id))

            reaction1 = Reaction(emoji="👍", name="Like", besitos_value=10, active=True)
            reaction2 = Reaction(emoji="❤️", name="Love", besitos_value=15, active=True)
            session.add_all([reaction1, reaction2])

            broadcast_msg = BroadcastMessage(
                message_id=700000004,
                chat_id=-1001234567890,
                content_type="text",
                content_text="Test",
                sent_by=users[0].user_id,
                gamification_enabled=True
            )
            session.add(broadcast_msg)
            await session.commit()

            reaction1_id = reaction1.id
            reaction2_id = reaction2.id
            broadcast_id = broadcast_msg.id

            # Registrar reacciones:
            # - User 1: 👍
            # - User 2: 👍
            # - User 3: ❤️
            service = CustomReactionService(session)
            await service.register_custom_reaction(broadcast_id, users[0].user_id, reaction1_id, "👍")
            await service.register_custom_reaction(broadcast_id, users[1].user_id, reaction1_id, "👍")
            await service.register_custom_reaction(broadcast_id, users[2].user_id, reaction2_id, "❤️")

            # Test: Obtener estadísticas
            stats = await service.get_message_reaction_stats(broadcast_id)

            # Verificar
            assert stats["👍"] == 2
            assert stats["❤️"] == 1

    @pytest.mark.asyncio
    async def test_stats_update_after_reaction(self, db_setup, event_loop):
        """Test: Stats de BroadcastMessage se actualizan correctamente."""
        from bot.database.engine import get_session

        async with get_session() as session:
            # Setup
            user = User(
                user_id=900000007,
                username="reactor4",
                first_name="Reactor4",
                role="VIP"
            )
            session.add(user)

            user_gamif = UserGamification(user_id=user.user_id)
            session.add(user_gamif)

            reaction = Reaction(emoji="🔥", name="Fire", besitos_value=20, active=True)
            session.add(reaction)

            broadcast_msg = BroadcastMessage(
                message_id=700000005,
                chat_id=-1001234567890,
                content_type="text",
                content_text="Test",
                sent_by=user.user_id,
                gamification_enabled=True
            )
            session.add(broadcast_msg)
            await session.commit()

            reaction_id = reaction.id
            broadcast_id = broadcast_msg.id

            # Verificar stats iniciales
            assert broadcast_msg.total_reactions == 0
            assert broadcast_msg.unique_reactors == 0

            # Registrar reacción
            service = CustomReactionService(session)
            await service.register_custom_reaction(broadcast_id, user.user_id, reaction_id, "🔥")

            # Verificar stats actualizados
            await session.refresh(broadcast_msg)
            assert broadcast_msg.total_reactions == 1
            assert broadcast_msg.unique_reactors == 1
