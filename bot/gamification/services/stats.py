"""
Servicio de estadísticas y métricas del sistema de gamificación.
"""

from datetime import datetime, timedelta, UTC
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List

from bot.gamification.database.models import (
    UserGamification, UserMission, UserReward, UserReaction,
    UserStreak, Mission, Level, Reaction, CustomReaction, GamificationConfig
)
from bot.gamification.database.enums import MissionStatus
from bot.database.models import BroadcastMessage, User

import logging
logger = logging.getLogger(__name__)


class StatsService:
    """Servicio de estadísticas del sistema."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_system_overview(self) -> dict:
        """Métricas generales del sistema."""
        # Total usuarios
        stmt = select(func.count()).select_from(UserGamification)
        total_users = (await self.session.execute(stmt)).scalar()

        # Usuarios activos últimos 7 días
        week_ago = datetime.now(UTC) - timedelta(days=7)
        stmt = select(func.count(func.distinct(UserReaction.user_id))).select_from(UserReaction).where(
            UserReaction.reacted_at >= week_ago
        )
        active_7d = (await self.session.execute(stmt)).scalar()

        # Total besitos distribuidos
        stmt = select(func.sum(UserGamification.besitos_earned))
        total_besitos = (await self.session.execute(stmt)).scalar() or 0

        # Misiones y recompensas
        stmt = select(func.count()).select_from(Mission).where(Mission.active == True)
        total_missions = (await self.session.execute(stmt)).scalar()

        stmt = select(func.count()).select_from(UserMission).where(
            UserMission.status == MissionStatus.CLAIMED
        )
        missions_completed = (await self.session.execute(stmt)).scalar()

        stmt = select(func.count()).select_from(UserReward)
        rewards_claimed = (await self.session.execute(stmt)).scalar()

        return {
            'total_users': total_users,
            'active_users_7d': active_7d,
            'total_besitos_distributed': total_besitos,
            'total_missions': total_missions,
            'missions_completed': missions_completed,
            'rewards_claimed': rewards_claimed
        }

    async def get_user_distribution(self) -> dict:
        """Distribución de usuarios por nivel."""
        # Por nivel
        stmt = (
            select(Level.name, func.count(UserGamification.user_id))
            .join(UserGamification, UserGamification.current_level_id == Level.id)
            .group_by(Level.name)
        )
        result = await self.session.execute(stmt)
        by_level = {name: count for name, count in result}

        # Top 10
        stmt = (
            select(UserGamification, Level.name)
            .join(Level, UserGamification.current_level_id == Level.id)
            .order_by(UserGamification.total_besitos.desc())
            .limit(10)
        )
        result = await self.session.execute(stmt)
        top_users = [
            {
                'user_id': ug.user_id,
                'besitos': ug.total_besitos,
                'level_name': level_name
            }
            for ug, level_name in result
        ]

        # Promedio
        stmt = select(func.avg(UserGamification.total_besitos))
        avg_besitos = (await self.session.execute(stmt)).scalar() or 0

        return {
            'by_level': by_level,
            'top_users': top_users,
            'avg_besitos': round(avg_besitos, 2)
        }

    async def get_mission_stats(self) -> dict:
        """Estadísticas de misiones."""
        # Total starts
        stmt = select(func.count()).select_from(UserMission)
        total_starts = (await self.session.execute(stmt)).scalar()

        # Completions
        stmt = select(func.count()).select_from(UserMission).where(
            UserMission.status.in_([MissionStatus.COMPLETED, MissionStatus.CLAIMED])
        )
        total_completions = (await self.session.execute(stmt)).scalar()

        # Rate
        completion_rate = (total_completions / total_starts * 100) if total_starts > 0 else 0

        # Por tipo
        stmt = (
            select(Mission.mission_type, func.count(UserMission.id))
            .join(UserMission)
            .where(UserMission.status == MissionStatus.CLAIMED)
            .group_by(Mission.mission_type)
        )
        result = await self.session.execute(stmt)
        by_type = {str(mtype): count for mtype, count in result}

        # Top misiones
        stmt = (
            select(Mission.name, func.count(UserMission.id))
            .join(UserMission)
            .where(UserMission.status == MissionStatus.CLAIMED)
            .group_by(Mission.id, Mission.name)
            .order_by(func.count(UserMission.id).desc())
            .limit(5)
        )
        result = await self.session.execute(stmt)
        top_missions = [
            {'mission_name': name, 'completions': count}
            for name, count in result
        ]

        return {
            'total_starts': total_starts,
            'total_completions': total_completions,
            'completion_rate': round(completion_rate, 2),
            'by_type': by_type,
            'top_missions': top_missions
        }

    async def get_engagement_stats(self) -> dict:
        """Estadísticas de engagement."""
        # Total reacciones
        stmt = select(func.count()).select_from(UserReaction)
        total_reactions = (await self.session.execute(stmt)).scalar()

        # Últimos 7 días
        week_ago = datetime.now(UTC) - timedelta(days=7)
        stmt = select(func.count()).select_from(UserReaction).where(
            UserReaction.reacted_at >= week_ago
        )
        reactions_7d = (await self.session.execute(stmt)).scalar()

        # Promedio por usuario
        stmt = select(func.count(UserGamification.user_id))
        total_users = (await self.session.execute(stmt)).scalar()
        avg_reactions = (total_reactions / total_users) if total_users > 0 else 0

        # Top emojis
        stmt = (
            select(Reaction.emoji, func.count(UserReaction.id))
            .join(UserReaction, UserReaction.reaction_id == Reaction.id)
            .group_by(Reaction.emoji)
            .order_by(func.count(UserReaction.id).desc())
            .limit(5)
        )
        result = await self.session.execute(stmt)
        top_emojis = {emoji: count for emoji, count in result}

        # Rachas activas
        stmt = select(func.count()).select_from(UserStreak).where(
            UserStreak.current_streak > 0
        )
        active_streaks = (await self.session.execute(stmt)).scalar()

        # Racha más larga
        stmt = select(func.max(UserStreak.longest_streak))
        longest_streak = (await self.session.execute(stmt)).scalar() or 0

        return {
            'total_reactions': total_reactions,
            'reactions_7d': reactions_7d,
            'avg_reactions_per_user': round(avg_reactions, 2),
            'top_emojis': top_emojis,
            'active_streaks': active_streaks,
            'longest_streak': longest_streak
        }

    async def get_broadcast_reaction_stats(
        self,
        broadcast_message_id: int
    ) -> Dict:
        """
        Estadísticas de reacciones de una publicación específica.

        Args:
            broadcast_message_id: ID del BroadcastMessage

        Returns:
            {
                "total_reactions": 1234,
                "unique_users": 567,
                "breakdown": {
                    "👍": 456,
                    "❤️": 345,
                    "🔥": 433
                },
                "besitos_distributed": 12340,
                "top_reactors": [
                    {"user_id": 123, "username": "user1", "reactions": 3},
                    ...
                ]
            }
        """
        # Total de reacciones
        stmt = select(func.count()).select_from(CustomReaction).where(
            CustomReaction.broadcast_message_id == broadcast_message_id
        )
        total_reactions = (await self.session.execute(stmt)).scalar() or 0

        # Usuarios únicos
        stmt = select(func.count(func.distinct(CustomReaction.user_id))).select_from(CustomReaction).where(
            CustomReaction.broadcast_message_id == broadcast_message_id
        )
        unique_users = (await self.session.execute(stmt)).scalar() or 0

        # Breakdown por emoji
        stmt = (
            select(CustomReaction.emoji, func.count(CustomReaction.id))
            .where(CustomReaction.broadcast_message_id == broadcast_message_id)
            .group_by(CustomReaction.emoji)
            .order_by(func.count(CustomReaction.id).desc())
        )
        result = await self.session.execute(stmt)
        breakdown = {emoji: count for emoji, count in result}

        # Total besitos distribuidos
        stmt = select(func.sum(CustomReaction.besitos_earned)).where(
            CustomReaction.broadcast_message_id == broadcast_message_id
        )
        besitos_distributed = (await self.session.execute(stmt)).scalar() or 0

        # Top 5 reactores
        stmt = (
            select(
                CustomReaction.user_id,
                func.count(CustomReaction.id).label('reaction_count')
            )
            .where(CustomReaction.broadcast_message_id == broadcast_message_id)
            .group_by(CustomReaction.user_id)
            .order_by(func.count(CustomReaction.id).desc())
            .limit(5)
        )
        result = await self.session.execute(stmt)
        top_reactors_data = result.all()

        # Enriquecer con info de usuario (evitar N+1 query)
        top_reactors = []
        if top_reactors_data:
            # Obtener todos los user_ids
            user_ids = [user_id for user_id, _ in top_reactors_data]

            # Fetch todos los usuarios en una sola query
            stmt_users = select(User).where(User.user_id.in_(user_ids))
            users_result = await self.session.execute(stmt_users)
            users_map = {user.user_id: user for user in users_result.scalars()}

            # Construir lista de top reactors
            for user_id, reaction_count in top_reactors_data:
                user = users_map.get(user_id)
                top_reactors.append({
                    "user_id": user_id,
                    "username": user.username if user and user.username else "Usuario",
                    "reactions": reaction_count
                })

        logger.info(
            f"Broadcast stats for message {broadcast_message_id}: "
            f"{total_reactions} reactions, {unique_users} unique users"
        )

        return {
            "total_reactions": total_reactions,
            "unique_users": unique_users,
            "breakdown": breakdown,
            "besitos_distributed": besitos_distributed,
            "top_reactors": top_reactors
        }

    async def get_top_performing_broadcasts(
        self,
        limit: int = 10
    ) -> List[Dict]:
        """
        Publicaciones con más engagement (ordenadas por total de reacciones).

        Args:
            limit: Cantidad máxima de resultados (default: 10)

        Returns:
            [
                {
                    "broadcast_id": 1,
                    "sent_at": datetime,
                    "chat_id": -1001234567890,
                    "total_reactions": 1234,
                    "unique_reactors": 567,
                    "content_preview": "Texto del mensaje..." (primeros 50 chars)
                },
                ...
            ]
        """
        # Query: BroadcastMessages ordenados por total_reactions DESC
        stmt = (
            select(BroadcastMessage)
            .where(BroadcastMessage.gamification_enabled == True)
            .order_by(BroadcastMessage.total_reactions.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        broadcasts = result.scalars().all()

        # Formatear resultados
        top_broadcasts = []
        for broadcast in broadcasts:
            # Preview del contenido (primeros 50 caracteres)
            content_preview = ""
            if broadcast.content_text:
                content_preview = (
                    broadcast.content_text[:50] + "..."
                    if len(broadcast.content_text) > 50
                    else broadcast.content_text
                )
            elif broadcast.content_type == "photo":
                content_preview = "📷 Foto"
            elif broadcast.content_type == "video":
                content_preview = "🎥 Video"

            top_broadcasts.append({
                "broadcast_id": broadcast.id,
                "sent_at": broadcast.sent_at,
                "chat_id": broadcast.chat_id,
                "total_reactions": broadcast.total_reactions,
                "unique_reactors": broadcast.unique_reactors,
                "content_preview": content_preview
            })

        logger.info(f"Retrieved top {len(top_broadcasts)} performing broadcasts")

        return top_broadcasts

    # ========================================
    # ECONOMÍA - ESTADÍSTICAS GLOBALES
    # ========================================

    async def get_economy_overview(self) -> dict:
        """
        Obtiene resumen global de economía de besitos.

        Returns:
            {
                'total_in_circulation': int,      # Sum de total_besitos
                'average_per_user': float,        # Avg de total_besitos
                'total_earned_historical': int,   # Sum de besitos_earned
                'total_spent_historical': int,    # Sum de besitos_spent
                'total_users_with_besitos': int,  # Count con total_besitos > 0
                'top_holders': List[Dict],        # Top 5 usuarios
                'by_level': Dict[str, int]        # {level_name: total_besitos}
            }
        """
        # Query 1: Agregaciones principales (optimizado en una sola query)
        stmt = select(
            func.sum(UserGamification.total_besitos).label('total_circulation'),
            func.avg(UserGamification.total_besitos).label('avg_besitos'),
            func.sum(UserGamification.besitos_earned).label('total_earned'),
            func.sum(UserGamification.besitos_spent).label('total_spent'),
            func.count().filter(UserGamification.total_besitos > 0).label('users_with_besitos')
        )
        result = await self.session.execute(stmt)
        row = result.one()

        # Query 2: Top 5 holders (requiere ordenamiento)
        top_stmt = select(UserGamification).order_by(
            UserGamification.total_besitos.desc()
        ).limit(5)
        top_result = await self.session.execute(top_stmt)
        top_users = top_result.scalars().all()

        # Query 3: Distribución por nivel (requiere join y agrupación)
        by_level_stmt = select(
            Level.name,
            func.sum(UserGamification.total_besitos).label('total')
        ).join(
            UserGamification, UserGamification.current_level_id == Level.id
        ).group_by(Level.name)

        by_level_result = await self.session.execute(by_level_stmt)
        by_level = {name: total for name, total in by_level_result}

        logger.info(
            f"Economy overview: {row.total_circulation or 0} besitos in circulation, "
            f"{row.users_with_besitos or 0} users with besitos"
        )

        return {
            'total_in_circulation': row.total_circulation or 0,
            'average_per_user': float(row.avg_besitos or 0),
            'total_earned_historical': row.total_earned or 0,
            'total_spent_historical': row.total_spent or 0,
            'total_users_with_besitos': row.users_with_besitos or 0,
            'top_holders': [
                {
                    'user_id': u.user_id,
                    'total_besitos': u.total_besitos
                }
                for u in top_users
            ],
            'by_level': by_level
        }

    async def get_besitos_sources_config(self) -> dict:
        """
        Obtiene configuración de fuentes que otorgan besitos.

        Returns:
            {
                'reactions': List[Dict],  # [{emoji, name, besitos_value}, ...]
                'missions': List[Dict],   # [{id, title, besitos_reward}, ...]
                'daily_gift': Dict,       # {enabled, amount}
                'levels': List[Dict]      # [{level_number, name, besitos_bonus}, ...]
            }
        """
        # 1. Reacciones activas (ordenadas por valor DESC)
        reactions_stmt = select(Reaction).where(
            Reaction.active == True
        ).order_by(Reaction.besitos_value.desc())
        reactions_result = await self.session.execute(reactions_stmt)
        reactions = reactions_result.scalars().all()

        reactions_list = [
            {
                'emoji': r.emoji,
                'name': r.name,
                'besitos_value': r.besitos_value
            }
            for r in reactions
        ]

        # 2. Misiones activas con recompensa > 0
        missions_stmt = select(Mission).where(
            Mission.active == True,
            Mission.besitos_reward > 0
        ).order_by(Mission.besitos_reward.desc())
        missions_result = await self.session.execute(missions_stmt)
        missions = missions_result.scalars().all()

        missions_list = [
            {
                'id': m.id,
                'name': m.name,
                'besitos_reward': m.besitos_reward
            }
            for m in missions
        ]

        # 3. Daily Gift (desde GamificationConfig singleton id=1)
        config = await self.session.get(GamificationConfig, 1)
        daily_gift = {
            'enabled': config.daily_gift_enabled if config else False,
            'amount': config.daily_gift_besitos if config else 0
        }

        # 4. Niveles con bonificación
        # NOTA: El modelo Level actualmente no tiene campo besitos_bonus
        # Los niveles no otorgan besitos automáticamente al subir
        # Esta sección se mantiene para futura extensibilidad
        levels_list = []

        logger.info(
            f"Besitos sources: {len(reactions_list)} reactions, "
            f"{len(missions_list)} missions, {len(levels_list)} levels, "
            f"daily_gift={'enabled' if daily_gift['enabled'] else 'disabled'}"
        )

        return {
            'reactions': reactions_list,
            'missions': missions_list,
            'daily_gift': daily_gift,
            'levels': levels_list
        }
