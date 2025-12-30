"""Servicio de gestión de reacciones personalizadas en broadcasting.

Responsabilidades:
- Registrar reacciones de usuarios en mensajes de broadcasting
- Validar y prevenir reacciones duplicadas
- Otorgar besitos por reaccionar (usando economy_config)
- Actualizar estadísticas de mensajes
- Obtener reacciones de usuarios
- Límites diarios configurables (F2.5)
- Bonus primera reacción del día (F2.6)
- Actualización de rachas (F2.3)
- Bonus por hitos de racha 7/30 días (F2.3)
"""

from typing import Optional, Dict, List
from datetime import datetime, UTC, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import logging

from bot.gamification.database.models import (
    CustomReaction,
    Reaction,
    UserStreak
)
from bot.database.models import BroadcastMessage
from bot.gamification.database.enums import TransactionType

logger = logging.getLogger(__name__)


class CustomReactionService:
    """Servicio de gestión de reacciones personalizadas."""

    def __init__(self, session: AsyncSession):
        """
        Inicializa el servicio.

        Args:
            session: Sesión async de SQLAlchemy
        """
        self.session = session

    async def register_custom_reaction(
        self,
        broadcast_message_id: int,
        user_id: int,
        reaction_type_id: int,
        emoji: str
    ) -> Dict:
        """Registra reacción cuando usuario presiona botón.

        Implementa:
        - F2.5: Límites diarios configurables
        - F2.6: Bonus primera reacción del día
        - F2.3: Actualización de rachas y bonus hitos

        Args:
            broadcast_message_id: ID del mensaje de broadcasting
            user_id: ID del usuario que reacciona
            reaction_type_id: ID del tipo de reacción
            emoji: Emoji de la reacción

        Returns:
            {
                "success": True,
                "besitos_earned": 0.6,
                "total_besitos": 1245.5,
                "already_reacted": False,
                "multiplier_applied": 1.0,
                "is_first_today": True,
                "streak_days": 5,
                "daily_limit_reached": False
            }
        """
        # 1. Verificar si ya reaccionó con este emoji
        stmt = select(CustomReaction).where(
            CustomReaction.broadcast_message_id == broadcast_message_id,
            CustomReaction.user_id == user_id,
            CustomReaction.reaction_type_id == reaction_type_id
        )
        result = await self.session.execute(stmt)
        existing_reaction = result.scalar_one_or_none()

        if existing_reaction:
            logger.warning(
                f"User {user_id} already reacted with {emoji} "
                f"on message {broadcast_message_id}"
            )
            return {
                "success": False,
                "already_reacted": True,
                "besitos_earned": 0,
                "total_besitos": 0,
                "multiplier_applied": 1.0,
                "is_first_today": False,
                "streak_days": 0,
                "daily_limit_reached": False
            }

        # 2. Obtener ReactionType para verificar activo
        stmt = select(Reaction).where(Reaction.id == reaction_type_id)
        result = await self.session.execute(stmt)
        reaction_type = result.scalar_one_or_none()

        if not reaction_type or not reaction_type.active:
            logger.error(
                f"Reaction type {reaction_type_id} not found or inactive"
            )
            return {
                "success": False,
                "already_reacted": False,
                "besitos_earned": 0,
                "total_besitos": 0,
                "multiplier_applied": 1.0,
                "error": "Reaction type not found or inactive",
                "is_first_today": False,
                "streak_days": 0,
                "daily_limit_reached": False
            }

        # 3. F2.5: Verificar límite diario
        can_earn, reactions_today = await self._check_daily_limit(user_id)
        if not can_earn:
            # Aún registrar la reacción pero sin otorgar besitos
            custom_reaction = CustomReaction(
                broadcast_message_id=broadcast_message_id,
                user_id=user_id,
                reaction_type_id=reaction_type_id,
                emoji=emoji,
                besitos_earned=0
            )
            self.session.add(custom_reaction)
            await self.session.commit()

            logger.info(
                f"User {user_id} reacted with {emoji} but daily limit reached "
                f"({reactions_today} reactions today)"
            )

            return {
                "success": True,
                "already_reacted": False,
                "besitos_earned": 0,
                "total_besitos": await self._get_user_balance(user_id),
                "multiplier_applied": 1.0,
                "is_first_today": False,
                "streak_days": 0,
                "daily_limit_reached": True,
                "message": f"Límite diario alcanzado ({reactions_today} reacciones)"
            }

        # 4. F2.6: Detectar si es primera reacción del día
        is_first_today = await self._is_first_reaction_today(user_id)

        # 5. Obtener valores de economía
        from bot.gamification.services.economy_config import EconomyConfigService
        economy_service = EconomyConfigService(self.session)

        base_amount = await economy_service.get_reaction_base()
        total_amount = base_amount

        description = f"Reacción {emoji} en broadcast {broadcast_message_id}"

        if is_first_today:
            bonus = await economy_service.get_first_reaction_day()
            total_amount += bonus
            description = f"Reacción {emoji} + Bonus primera del día"
            logger.info(f"User {user_id} gets first reaction bonus: +{bonus}")

        multiplier = 1.0  # Por ahora sin multiplicadores adicionales
        besitos_to_grant = total_amount * multiplier

        # 6. Crear CustomReaction
        try:
            custom_reaction = CustomReaction(
                broadcast_message_id=broadcast_message_id,
                user_id=user_id,
                reaction_type_id=reaction_type_id,
                emoji=emoji,
                besitos_earned=besitos_to_grant
            )
            self.session.add(custom_reaction)
            await self.session.flush()  # Para obtener el ID

            logger.info(
                f"User {user_id} reacted with {emoji} "
                f"on message {broadcast_message_id}, earning {besitos_to_grant} Favores"
            )

        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f"Failed to create CustomReaction: {e}")
            return {
                "success": False,
                "already_reacted": True,
                "besitos_earned": 0,
                "total_besitos": 0,
                "multiplier_applied": multiplier,
                "is_first_today": False,
                "streak_days": 0,
                "daily_limit_reached": False
            }

        # 7. Otorgar besitos via BesitoService
        from bot.gamification.services.besito import BesitoService
        besito_service = BesitoService(self.session)

        await besito_service.grant_besitos(
            user_id=user_id,
            amount=besitos_to_grant,
            transaction_type=TransactionType.REACTION_CUSTOM,
            description=description,
            reference_id=custom_reaction.id
        )

        # 8. F2.3: Actualizar racha
        streak = await self._update_user_streak(user_id, economy_service)

        # Obtener total de besitos después de otorgar
        total_besitos = await besito_service.get_balance(user_id)

        # 9. Actualizar stats del mensaje
        await self._update_message_stats(broadcast_message_id)

        # 10. Commit de todos los cambios
        await self.session.commit()

        # 11. Retornar resultado
        return {
            "success": True,
            "already_reacted": False,
            "besitos_earned": besitos_to_grant,
            "total_besitos": total_besitos,
            "multiplier_applied": multiplier,
            "is_first_today": is_first_today,
            "streak_days": streak.current_streak if streak else 0,
            "daily_limit_reached": False
        }

    # ========================================
    # VALIDACIONES (F2.5, F2.6)
    # ========================================

    async def _check_daily_limit(self, user_id: int) -> tuple[bool, int]:
        """Verifica límite diario de reacciones (F2.5).

        Args:
            user_id: ID del usuario

        Returns:
            (can_earn, reactions_count_today)
        """
        from bot.gamification.services.economy_config import EconomyConfigService
        economy_service = EconomyConfigService(self.session)

        max_daily_reactions = await economy_service.get_reactions_daily_limit()

        if max_daily_reactions is None or max_daily_reactions <= 0:
            return True, 0  # Sin límite

        # Contar reacciones de hoy
        today_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)

        stmt = select(func.count()).select_from(CustomReaction).where(
            CustomReaction.user_id == user_id,
            CustomReaction.created_at >= today_start
        )
        result = await self.session.execute(stmt)
        reactions_today = result.scalar() or 0

        can_earn = reactions_today < max_daily_reactions
        return can_earn, reactions_today

    async def _is_first_reaction_today(self, user_id: int) -> bool:
        """Detecta si esta es la primera reacción del día (F2.6).

        Args:
            user_id: ID del usuario

        Returns:
            True si es la primera reacción del día
        """
        today_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)

        stmt = select(func.count()).select_from(CustomReaction).where(
            CustomReaction.user_id == user_id,
            CustomReaction.created_at >= today_start
        )
        result = await self.session.execute(stmt)
        count = result.scalar() or 0

        # Si count es 0, es la primera reacción del día
        return count == 0

    # ========================================
    # RACHAS (F2.3)
    # ========================================

    async def _update_user_streak(self, user_id: int, economy_service) -> Optional[UserStreak]:
        """Actualiza racha del usuario (F2.3).

        Lógica:
        1. Obtener UserStreak (crear si no existe)
        2. Comparar last_reaction_date con hoy
        3. Si es consecutivo → current_streak += 1
        4. Si saltó días → current_streak = 1
        5. Si current_streak > longest_streak → actualizar récord
        6. Actualizar last_reaction_date
        7. Otorgar bonus al alcanzar hitos (7, 30 días)

        Args:
            user_id: ID del usuario
            economy_service: Servicio de configuración de economía

        Returns:
            UserStreak actualizado o None si falla
        """
        # Obtener o crear streak
        streak = await self._get_or_create_streak(user_id)
        if not streak:
            return None

        today = datetime.now(UTC).date()
        last_date = streak.last_reaction_date.date() if streak.last_reaction_date else None

        old_streak = streak.current_streak  # Guardar para detectar hitos

        if last_date is None:
            # Primera reacción
            streak.current_streak = 1
        elif last_date == today:
            # Ya reaccionó hoy, no modificar streak
            pass
        elif last_date == today - timedelta(days=1):
            # Día consecutivo
            streak.current_streak += 1
        else:
            # Rompió racha
            streak.current_streak = 1

        # Actualizar récord
        if streak.current_streak > streak.longest_streak:
            streak.longest_streak = streak.current_streak

        streak.last_reaction_date = datetime.now(UTC)

        # F2.3: Otorgar bonus por hitos de racha
        if old_streak < 7 and streak.current_streak >= 7:
            await self._grant_streak_bonus(user_id, 7, streak.id, economy_service)

        if old_streak < 30 and streak.current_streak >= 30:
            await self._grant_streak_bonus(user_id, 30, streak.id, economy_service)

        logger.info(
            f"User {user_id} streak updated: {old_streak} -> {streak.current_streak}"
        )

        return streak

    async def _get_or_create_streak(self, user_id: int) -> Optional[UserStreak]:
        """Obtiene o crea racha del usuario.

        Args:
            user_id: ID del usuario

        Returns:
            UserStreak del usuario o None si falla
        """
        stmt = select(UserStreak).where(UserStreak.user_id == user_id)
        result = await self.session.execute(stmt)
        streak = result.scalar_one_or_none()

        if not streak:
            try:
                streak = UserStreak(user_id=user_id)
                self.session.add(streak)
                await self.session.flush()
                logger.info(f"Created UserStreak for user {user_id}")
            except IntegrityError:
                # Puede fallar si UserGamification no existe
                logger.warning(f"Could not create UserStreak for user {user_id}")
                await self.session.rollback()
                return None

        return streak

    async def _grant_streak_bonus(
        self,
        user_id: int,
        streak_days: int,
        streak_id: int,
        economy_service
    ) -> None:
        """Otorga bonus de Favores por alcanzar hito de racha.

        Args:
            user_id: ID del usuario
            streak_days: Cantidad de días de racha alcanzados (7 o 30)
            streak_id: ID del UserStreak para referencia
            economy_service: Servicio de configuración de economía
        """
        from bot.gamification.services.besito import BesitoService

        # Obtener valor del bonus desde configuración
        if streak_days == 7:
            amount = await economy_service.get_streak_7_days()
        elif streak_days == 30:
            amount = await economy_service.get_streak_30_days()
        else:
            logger.warning(f"Invalid streak_days: {streak_days}")
            return

        # Otorgar besitos
        besito_service = BesitoService(self.session)
        await besito_service.grant_besitos(
            user_id=user_id,
            amount=amount,
            transaction_type=TransactionType.STREAK_BONUS,
            description=f"Bonus por racha de {streak_days} días consecutivos",
            reference_id=streak_id
        )

        logger.info(
            f"🔥 Streak milestone! User {user_id} reached {streak_days} days "
            f"and earned {amount} Favores"
        )

    # ========================================
    # UTILIDADES
    # ========================================

    async def _get_user_balance(self, user_id: int) -> float:
        """Obtiene balance de besitos del usuario.

        Args:
            user_id: ID del usuario

        Returns:
            Balance actual de besitos
        """
        from bot.gamification.services.besito import BesitoService
        besito_service = BesitoService(self.session)
        return await besito_service.get_balance(user_id)

    async def get_user_reactions_for_message(
        self,
        broadcast_message_id: int,
        user_id: int
    ) -> List[int]:
        """Retorna IDs de reaction_types que el usuario ya usó.

        Para marcar botones como "ya reaccionado".

        Args:
            broadcast_message_id: ID del mensaje de broadcasting
            user_id: ID del usuario

        Returns:
            Lista de reaction_type_ids que el usuario ya usó
        """
        stmt = select(CustomReaction.reaction_type_id).where(
            CustomReaction.broadcast_message_id == broadcast_message_id,
            CustomReaction.user_id == user_id
        )
        result = await self.session.execute(stmt)
        reaction_ids = [row[0] for row in result.all()]

        logger.debug(
            f"User {user_id} has {len(reaction_ids)} reactions "
            f"on message {broadcast_message_id}"
        )

        return reaction_ids

    async def get_message_reaction_stats(
        self,
        broadcast_message_id: int
    ) -> Dict[str, int]:
        """Stats de reacciones de un mensaje.

        Returns:
            {
                "👍": 45,
                "❤️": 32,
                "🔥": 28
            }
        """
        stmt = select(
            CustomReaction.emoji,
            func.count(CustomReaction.id).label("count")
        ).where(
            CustomReaction.broadcast_message_id == broadcast_message_id
        ).group_by(CustomReaction.emoji)

        result = await self.session.execute(stmt)
        stats = {row.emoji: row.count for row in result.all()}

        logger.debug(
            f"Message {broadcast_message_id} has {len(stats)} different reactions"
        )

        return stats

    async def get_message_reaction_stats_by_type(
        self,
        broadcast_message_id: int
    ) -> Dict[int, int]:
        """Stats de reacciones por reaction_type_id.

        Args:
            broadcast_message_id: ID del mensaje de broadcasting

        Returns:
            {1: 45, 2: 33, 3: 28}  # reaction_type_id → count
        """
        stmt = select(
            CustomReaction.reaction_type_id,
            func.count(CustomReaction.id).label("count")
        ).where(
            CustomReaction.broadcast_message_id == broadcast_message_id
        ).group_by(CustomReaction.reaction_type_id)

        result = await self.session.execute(stmt)
        stats = {row.reaction_type_id: row.count for row in result.all()}

        return stats

    async def get_user_reactions_today(self, user_id: int) -> int:
        """Obtiene cantidad de reacciones del usuario hoy.

        Args:
            user_id: ID del usuario

        Returns:
            Cantidad de reacciones hoy
        """
        today_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)

        stmt = select(func.count()).select_from(CustomReaction).where(
            CustomReaction.user_id == user_id,
            CustomReaction.created_at >= today_start
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_user_streak(self, user_id: int) -> Optional[UserStreak]:
        """Obtiene la racha actual del usuario.

        Args:
            user_id: ID del usuario

        Returns:
            UserStreak o None si no existe
        """
        stmt = select(UserStreak).where(UserStreak.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def _update_message_stats(self, broadcast_message_id: int):
        """Actualiza cache de stats en BroadcastMessage.

        Args:
            broadcast_message_id: ID del mensaje de broadcasting
        """
        # Obtener mensaje
        stmt = select(BroadcastMessage).where(
            BroadcastMessage.id == broadcast_message_id
        )
        result = await self.session.execute(stmt)
        broadcast_msg = result.scalar_one_or_none()

        if not broadcast_msg:
            logger.warning(
                f"BroadcastMessage {broadcast_message_id} not found for stats update"
            )
            return

        # Calcular total de reacciones
        stmt_total = select(func.count(CustomReaction.id)).where(
            CustomReaction.broadcast_message_id == broadcast_message_id
        )
        result = await self.session.execute(stmt_total)
        total_reactions = result.scalar() or 0

        # Calcular usuarios únicos que reaccionaron
        stmt_unique = select(func.count(func.distinct(CustomReaction.user_id))).where(
            CustomReaction.broadcast_message_id == broadcast_message_id
        )
        result = await self.session.execute(stmt_unique)
        unique_reactors = result.scalar() or 0

        # Actualizar cache
        broadcast_msg.total_reactions = total_reactions
        broadcast_msg.unique_reactors = unique_reactors

        logger.debug(
            f"Updated stats for message {broadcast_message_id}: "
            f"{total_reactions} reactions, {unique_reactors} unique users"
        )

        # No hacemos commit aquí, se hace en el método que llama
