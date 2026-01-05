"""
Servicio de tracking de engagement y visitas.

Gestiona el registro y análisis de visitas de usuarios a fragmentos narrativos,
cálculo de tiempo de lectura, y límites diarios.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, List

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from bot.narrative.database.models_immersive import (
    UserFragmentVisit,
    DailyNarrativeLimit,
)
from bot.narrative.config import NarrativeConfig

logger = logging.getLogger(__name__)


class EngagementService:
    """Servicio de tracking de engagement y visitas de usuario."""

    def __init__(self, session: AsyncSession):
        """
        Inicializa el servicio.

        Args:
            session: Sesión async de SQLAlchemy
        """
        self.session = session

    async def record_visit(
        self, user_id: int, fragment_key: str
    ) -> UserFragmentVisit:
        """
        Registra una visita de usuario a un fragmento.

        Si es la primera visita, crea el registro. Si ya visitó,
        incrementa el contador y actualiza last_visit.

        Args:
            user_id: ID del usuario
            fragment_key: Clave del fragmento visitado

        Returns:
            UserFragmentVisit: Registro de visita (nuevo o actualizado)
        """
        # Buscar registro existente
        stmt = select(UserFragmentVisit).where(
            and_(
                UserFragmentVisit.user_id == user_id,
                UserFragmentVisit.fragment_key == fragment_key,
            )
        )
        result = await self.session.execute(stmt)
        visit = result.scalar_one_or_none()

        if visit:
            # Ya visitó: incrementar contador y actualizar timestamp
            visit.visit_count += 1
            visit.last_visit = datetime.utcnow()
            visit.reading_started_at = datetime.utcnow()
            logger.debug(
                f"User {user_id} revisita fragmento '{fragment_key}' (visita #{visit.visit_count})"
            )
        else:
            # Primera visita: crear registro
            visit = UserFragmentVisit(
                user_id=user_id,
                fragment_key=fragment_key,
                visit_count=1,
                first_visit=datetime.utcnow(),
                last_visit=datetime.utcnow(),
                total_time_seconds=0,
                reading_started_at=datetime.utcnow(),
            )
            self.session.add(visit)
            logger.info(
                f"User {user_id} primera visita a fragmento '{fragment_key}'"
            )

        await self.session.commit()
        await self.session.refresh(visit)
        return visit

    async def finalize_visit(
        self, user_id: int, fragment_key: str
    ) -> Optional[int]:
        """
        Finaliza una visita y calcula tiempo de lectura.

        Calcula el tiempo entre reading_started_at y ahora,
        y lo suma a total_time_seconds.

        Args:
            user_id: ID del usuario
            fragment_key: Clave del fragmento

        Returns:
            int: Segundos de lectura calculados, o None si no hay visita activa
        """
        stmt = select(UserFragmentVisit).where(
            and_(
                UserFragmentVisit.user_id == user_id,
                UserFragmentVisit.fragment_key == fragment_key,
            )
        )
        result = await self.session.execute(stmt)
        visit = result.scalar_one_or_none()

        if not visit or not visit.reading_started_at:
            return None

        # Calcular tiempo transcurrido
        now = datetime.utcnow()
        elapsed = (now - visit.reading_started_at).total_seconds()

        # Validar rango razonable (evitar outliers si usuario dejó abierto)
        min_time = NarrativeConfig.MIN_READING_TIME_SECONDS
        max_time = NarrativeConfig.MAX_READING_TIME_SECONDS

        if elapsed < min_time:
            # Muy rápido, probablemente no leyó
            elapsed = min_time
        elif elapsed > max_time:
            # Dejó abierto demasiado tiempo, asumir max
            elapsed = max_time

        # Sumar al total y limpiar started_at
        visit.total_time_seconds += int(elapsed)
        visit.reading_started_at = None

        await self.session.commit()

        logger.debug(
            f"User {user_id} terminó lectura '{fragment_key}': {int(elapsed)}s (total: {visit.total_time_seconds}s)"
        )

        return int(elapsed)

    async def get_visit_count(self, user_id: int, fragment_key: str) -> int:
        """
        Obtiene el número de veces que un usuario visitó un fragmento.

        Args:
            user_id: ID del usuario
            fragment_key: Clave del fragmento

        Returns:
            int: Número de visitas (0 si nunca visitó)
        """
        stmt = select(UserFragmentVisit.visit_count).where(
            and_(
                UserFragmentVisit.user_id == user_id,
                UserFragmentVisit.fragment_key == fragment_key,
            )
        )
        result = await self.session.execute(stmt)
        count = result.scalar_one_or_none()
        return count or 0

    async def get_total_time_spent(
        self, user_id: int, fragment_key: str
    ) -> int:
        """
        Obtiene el tiempo total (segundos) que un usuario pasó en un fragmento.

        Args:
            user_id: ID del usuario
            fragment_key: Clave del fragmento

        Returns:
            int: Segundos totales (0 si nunca visitó)
        """
        stmt = select(UserFragmentVisit.total_time_seconds).where(
            and_(
                UserFragmentVisit.user_id == user_id,
                UserFragmentVisit.fragment_key == fragment_key,
            )
        )
        result = await self.session.execute(stmt)
        time_spent = result.scalar_one_or_none()
        return time_spent or 0

    async def get_user_engagement_stats(self, user_id: int) -> Dict:
        """
        Obtiene estadísticas de engagement del usuario.

        Args:
            user_id: ID del usuario

        Returns:
            dict: Estadísticas completas de engagement
                - total_fragments_visited: Cantidad única de fragmentos visitados
                - total_visits: Suma de todas las visitas (con revisitas)
                - total_reading_time: Tiempo total de lectura en segundos
                - avg_time_per_fragment: Promedio de tiempo por fragmento
                - most_revisited: Fragmento más revisitado
        """
        # Total de fragmentos únicos visitados
        stmt_count = select(func.count(UserFragmentVisit.id)).where(
            UserFragmentVisit.user_id == user_id
        )
        result = await self.session.execute(stmt_count)
        total_fragments = result.scalar_one()

        # Suma de visitas y tiempo total
        stmt_sums = select(
            func.sum(UserFragmentVisit.visit_count),
            func.sum(UserFragmentVisit.total_time_seconds),
        ).where(UserFragmentVisit.user_id == user_id)
        result = await self.session.execute(stmt_sums)
        sums = result.one()
        total_visits = sums[0] or 0
        total_time = sums[1] or 0

        # Promedio de tiempo por fragmento
        avg_time = int(total_time / total_fragments) if total_fragments > 0 else 0

        # Fragmento más revisitado
        stmt_most = (
            select(UserFragmentVisit)
            .where(UserFragmentVisit.user_id == user_id)
            .order_by(UserFragmentVisit.visit_count.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt_most)
        most_visited = result.scalar_one_or_none()

        return {
            "total_fragments_visited": total_fragments,
            "total_visits": total_visits,
            "total_reading_time": total_time,
            "avg_time_per_fragment": avg_time,
            "most_revisited": {
                "fragment_key": most_visited.fragment_key,
                "visit_count": most_visited.visit_count,
            }
            if most_visited
            else None,
        }

    async def check_daily_limit(
        self, user_id: int, limit_type: str
    ) -> Tuple[bool, int]:
        """
        Verifica si el usuario alcanzó su límite diario.

        Args:
            user_id: ID del usuario
            limit_type: Tipo de límite ("fragments", "decisions", "challenges")

        Returns:
            Tuple[bool, int]: (puede_continuar, restante)
        """
        # Obtener o crear registro de límites
        limit_record = await self._get_or_create_daily_limit(user_id)

        # Obtener límite máximo (custom o global)
        if limit_type == "fragments":
            current_count = limit_record.fragments_viewed
            max_limit = (
                limit_record.max_fragments_per_day
                or NarrativeConfig.DAILY_FRAGMENT_LIMIT
            )
        elif limit_type == "decisions":
            current_count = limit_record.decisions_made
            max_limit = NarrativeConfig.DAILY_DECISION_LIMIT
        elif limit_type == "challenges":
            current_count = limit_record.challenges_attempted
            max_limit = NarrativeConfig.DAILY_CHALLENGE_ATTEMPTS
        else:
            raise ValueError(f"Tipo de límite inválido: {limit_type}")

        # Si max_limit es 0, significa ilimitado
        if max_limit == 0:
            return True, 9999

        remaining = max_limit - current_count
        can_continue = remaining > 0

        return can_continue, max(0, remaining)

    async def increment_daily_counter(
        self, user_id: int, limit_type: str
    ) -> None:
        """
        Incrementa el contador diario de un tipo específico.

        Args:
            user_id: ID del usuario
            limit_type: Tipo de límite ("fragments", "decisions", "challenges")
        """
        limit_record = await self._get_or_create_daily_limit(user_id)

        if limit_type == "fragments":
            limit_record.fragments_viewed += 1
        elif limit_type == "decisions":
            limit_record.decisions_made += 1
        elif limit_type == "challenges":
            limit_record.challenges_attempted += 1
        else:
            raise ValueError(f"Tipo de límite inválido: {limit_type}")

        await self.session.commit()

        logger.debug(
            f"User {user_id} incrementó contador '{limit_type}': {getattr(limit_record, f'{limit_type}_{"viewed" if limit_type == "fragments" else "made" if limit_type == "decisions" else "attempted"}')}"
        )

    async def reset_daily_limits(self) -> int:
        """
        Reset de límites diarios (ejecutar a medianoche).

        Resetea todos los contadores de usuarios cuya fecha de límite
        sea anterior al día de hoy.

        Returns:
            int: Número de usuarios reseteados
        """
        today = datetime.utcnow().date()

        # Obtener registros con fecha anterior a hoy
        stmt = select(DailyNarrativeLimit).where(
            func.date(DailyNarrativeLimit.limit_date) < today
        )
        result = await self.session.execute(stmt)
        old_limits = result.scalars().all()

        count = 0
        for limit_record in old_limits:
            limit_record.limit_date = datetime.utcnow()
            limit_record.fragments_viewed = 0
            limit_record.decisions_made = 0
            limit_record.challenges_attempted = 0
            count += 1

        await self.session.commit()

        if count > 0:
            logger.info(f"Reset de límites diarios: {count} usuarios procesados")

        return count

    async def _get_or_create_daily_limit(
        self, user_id: int
    ) -> DailyNarrativeLimit:
        """
        Obtiene o crea el registro de límites diarios para un usuario.

        Si el registro existe pero es de un día anterior, resetea los contadores.

        Args:
            user_id: ID del usuario

        Returns:
            DailyNarrativeLimit: Registro de límites
        """
        stmt = select(DailyNarrativeLimit).where(
            DailyNarrativeLimit.user_id == user_id
        )
        result = await self.session.execute(stmt)
        limit_record = result.scalar_one_or_none()

        today = datetime.utcnow().date()

        if limit_record:
            # Si es de un día anterior, resetear contadores
            if limit_record.limit_date.date() < today:
                limit_record.limit_date = datetime.utcnow()
                limit_record.fragments_viewed = 0
                limit_record.decisions_made = 0
                limit_record.challenges_attempted = 0
                await self.session.commit()
        else:
            # Crear nuevo registro
            limit_record = DailyNarrativeLimit(
                user_id=user_id,
                limit_date=datetime.utcnow(),
                fragments_viewed=0,
                decisions_made=0,
                challenges_attempted=0,
            )
            self.session.add(limit_record)
            await self.session.commit()

        await self.session.refresh(limit_record)
        return limit_record

    async def get_visit_history(
        self, user_id: int, limit: int = 10
    ) -> List[UserFragmentVisit]:
        """
        Obtiene el historial de visitas recientes del usuario.

        Args:
            user_id: ID del usuario
            limit: Número máximo de registros

        Returns:
            List[UserFragmentVisit]: Lista de visitas ordenadas por última visita
        """
        stmt = (
            select(UserFragmentVisit)
            .where(UserFragmentVisit.user_id == user_id)
            .order_by(UserFragmentVisit.last_visit.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
