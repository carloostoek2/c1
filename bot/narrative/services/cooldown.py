"""
Servicio de gestión de cooldowns narrativos.

Administra cooldowns temporales que limitan acceso a fragmentos,
capítulos, decisiones y challenges para crear ritmo en la narrativa.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple, List

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from bot.narrative.database.models_immersive import (
    NarrativeCooldown,
    FragmentTimeWindow,
)
from bot.narrative.database.enums import CooldownType

logger = logging.getLogger(__name__)


class CooldownService:
    """Servicio de gestión de cooldowns y ventanas de tiempo."""

    def __init__(self, session: AsyncSession):
        """
        Inicializa el servicio.

        Args:
            session: Sesión async de SQLAlchemy
        """
        self.session = session

    async def check_cooldown(
        self, user_id: int, cooldown_type: CooldownType, target_key: str
    ) -> Tuple[bool, Optional[datetime], Optional[str]]:
        """
        Verifica si el usuario tiene un cooldown activo.

        Args:
            user_id: ID del usuario
            cooldown_type: Tipo de cooldown (FRAGMENT, CHAPTER, DECISION, CHALLENGE)
            target_key: Clave del objetivo (fragment_key, chapter_slug, etc.)

        Returns:
            Tuple[bool, Optional[datetime], Optional[str]]:
                - is_active: True si hay cooldown activo
                - expires_at: Cuándo expira (None si no hay cooldown)
                - message: Mensaje narrativo (None si no hay cooldown)
        """
        # Buscar cooldown activo
        stmt = select(NarrativeCooldown).where(
            and_(
                NarrativeCooldown.user_id == user_id,
                NarrativeCooldown.cooldown_type == cooldown_type,
                NarrativeCooldown.target_key == target_key,
                NarrativeCooldown.expires_at > datetime.utcnow(),
            )
        )
        result = await self.session.execute(stmt)
        cooldown = result.scalar_one_or_none()

        if cooldown:
            return True, cooldown.expires_at, cooldown.narrative_message
        else:
            return False, None, None

    async def set_cooldown(
        self,
        user_id: int,
        cooldown_type: CooldownType,
        target_key: str,
        duration_seconds: int,
        message: Optional[str] = None,
    ) -> NarrativeCooldown:
        """
        Establece un nuevo cooldown para el usuario.

        Si ya existe un cooldown para el mismo tipo/target, lo reemplaza.

        Args:
            user_id: ID del usuario
            cooldown_type: Tipo de cooldown
            target_key: Clave del objetivo
            duration_seconds: Duración del cooldown en segundos
            message: Mensaje narrativo personalizado

        Returns:
            NarrativeCooldown: Cooldown creado
        """
        # Buscar cooldown existente
        stmt = select(NarrativeCooldown).where(
            and_(
                NarrativeCooldown.user_id == user_id,
                NarrativeCooldown.cooldown_type == cooldown_type,
                NarrativeCooldown.target_key == target_key,
            )
        )
        result = await self.session.execute(stmt)
        cooldown = result.scalar_one_or_none()

        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=duration_seconds)

        if cooldown:
            # Actualizar existente
            cooldown.started_at = now
            cooldown.expires_at = expires_at
            if message:
                cooldown.narrative_message = message
            logger.debug(
                f"Cooldown actualizado: user {user_id}, tipo '{cooldown_type.value}', target '{target_key}', expira en {duration_seconds}s"
            )
        else:
            # Crear nuevo
            default_messages = {
                CooldownType.FRAGMENT: "Diana necesita un momento...",
                CooldownType.CHAPTER: "Este capítulo estará disponible pronto. Lucien te avisará.",
                CooldownType.DECISION: "No puedes decidir tan rápido. Reflexiona.",
                CooldownType.CHALLENGE: "El desafío requiere tiempo. Inténtalo más tarde.",
            }

            cooldown = NarrativeCooldown(
                user_id=user_id,
                cooldown_type=cooldown_type,
                target_key=target_key,
                started_at=now,
                expires_at=expires_at,
                narrative_message=message or default_messages.get(cooldown_type),
            )
            self.session.add(cooldown)
            logger.info(
                f"Cooldown creado: user {user_id}, tipo '{cooldown_type.value}', target '{target_key}', expira en {duration_seconds}s"
            )

        await self.session.commit()
        await self.session.refresh(cooldown)
        return cooldown

    async def clear_cooldown(
        self, user_id: int, cooldown_type: CooldownType, target_key: str
    ) -> bool:
        """
        Elimina un cooldown activo.

        Args:
            user_id: ID del usuario
            cooldown_type: Tipo de cooldown
            target_key: Clave del objetivo

        Returns:
            bool: True si se eliminó, False si no existía
        """
        stmt = select(NarrativeCooldown).where(
            and_(
                NarrativeCooldown.user_id == user_id,
                NarrativeCooldown.cooldown_type == cooldown_type,
                NarrativeCooldown.target_key == target_key,
            )
        )
        result = await self.session.execute(stmt)
        cooldown = result.scalar_one_or_none()

        if cooldown:
            await self.session.delete(cooldown)
            await self.session.commit()
            logger.info(
                f"Cooldown eliminado: user {user_id}, tipo '{cooldown_type.value}', target '{target_key}'"
            )
            return True
        else:
            return False

    async def get_active_cooldowns(
        self, user_id: int
    ) -> List[NarrativeCooldown]:
        """
        Obtiene todos los cooldowns activos del usuario.

        Args:
            user_id: ID del usuario

        Returns:
            List[NarrativeCooldown]: Lista de cooldowns activos ordenados por expiración
        """
        stmt = (
            select(NarrativeCooldown)
            .where(
                and_(
                    NarrativeCooldown.user_id == user_id,
                    NarrativeCooldown.expires_at > datetime.utcnow(),
                )
            )
            .order_by(NarrativeCooldown.expires_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def cleanup_expired_cooldowns(self) -> int:
        """
        Elimina cooldowns expirados de la base de datos.

        Este método debe ejecutarse periódicamente en un background task
        para evitar acumulación de registros obsoletos.

        Returns:
            int: Número de cooldowns eliminados
        """
        stmt = select(NarrativeCooldown).where(
            NarrativeCooldown.expires_at <= datetime.utcnow()
        )
        result = await self.session.execute(stmt)
        expired = result.scalars().all()

        count = 0
        for cooldown in expired:
            await self.session.delete(cooldown)
            count += 1

        await self.session.commit()

        if count > 0:
            logger.info(f"Cleanup: {count} cooldowns expirados eliminados")

        return count

    async def check_time_window(
        self, fragment_key: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Verifica si un fragmento está dentro de su ventana de disponibilidad temporal.

        Args:
            fragment_key: Clave del fragmento

        Returns:
            Tuple[bool, Optional[str]]:
                - is_available: True si está disponible ahora
                - unavailable_message: Mensaje si no está disponible (None si disponible)
        """
        # Buscar ventana de tiempo para el fragmento
        stmt = select(FragmentTimeWindow).where(
            and_(
                FragmentTimeWindow.fragment_key == fragment_key,
                FragmentTimeWindow.is_active == True,
            )
        )
        result = await self.session.execute(stmt)
        window = result.scalar_one_or_none()

        if not window:
            # No tiene restricción de ventana de tiempo
            return True, None

        now = datetime.utcnow()

        # Verificar fechas especiales
        if window.special_dates:
            today_str = now.strftime("%Y-%m-%d")
            in_special_dates = today_str in window.special_dates

            if window.special_dates_inclusive:
                # Solo disponible en fechas especiales
                if not in_special_dates:
                    return False, window.unavailable_message
            else:
                # NO disponible en fechas especiales (exclusivo)
                if in_special_dates:
                    return False, window.unavailable_message

        # Verificar día de la semana (0=Lunes, 6=Domingo)
        if window.available_days is not None:
            current_weekday = now.weekday()
            if current_weekday not in window.available_days:
                return False, window.unavailable_message

        # Verificar hora del día
        if window.available_hours is not None:
            current_hour = now.hour
            if current_hour not in window.available_hours:
                return False, window.unavailable_message

        # Todas las verificaciones pasaron
        return True, None

    async def create_time_window(
        self,
        fragment_key: str,
        available_hours: Optional[List[int]] = None,
        available_days: Optional[List[int]] = None,
        special_dates: Optional[List[str]] = None,
        special_dates_inclusive: bool = True,
        unavailable_message: Optional[str] = None,
    ) -> FragmentTimeWindow:
        """
        Crea una ventana de disponibilidad temporal para un fragmento.

        Args:
            fragment_key: Clave del fragmento
            available_hours: Horas disponibles (0-23) o None para cualquier hora
            available_days: Días disponibles (0-6, 0=Lunes) o None para cualquier día
            special_dates: Fechas especiales (formato "YYYY-MM-DD")
            special_dates_inclusive: Si True, solo disponible en fechas especiales
            unavailable_message: Mensaje cuando no está disponible

        Returns:
            FragmentTimeWindow: Ventana creada
        """
        default_message = (
            "Este momento de la historia solo está disponible en ciertos horarios..."
        )

        window = FragmentTimeWindow(
            fragment_key=fragment_key,
            available_hours=available_hours,
            available_days=available_days,
            special_dates=special_dates,
            special_dates_inclusive=special_dates_inclusive,
            unavailable_message=unavailable_message or default_message,
            is_active=True,
        )

        self.session.add(window)
        await self.session.commit()
        await self.session.refresh(window)

        logger.info(f"Ventana de tiempo creada para fragmento '{fragment_key}'")

        return window

    async def get_time_window(
        self, fragment_key: str
    ) -> Optional[FragmentTimeWindow]:
        """
        Obtiene la ventana de tiempo de un fragmento.

        Args:
            fragment_key: Clave del fragmento

        Returns:
            FragmentTimeWindow: Ventana de tiempo, o None si no tiene
        """
        stmt = select(FragmentTimeWindow).where(
            and_(
                FragmentTimeWindow.fragment_key == fragment_key,
                FragmentTimeWindow.is_active == True,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_time_window(
        self, window_id: int, **updates
    ) -> Optional[FragmentTimeWindow]:
        """
        Actualiza una ventana de tiempo existente.

        Args:
            window_id: ID de la ventana
            **updates: Campos a actualizar

        Returns:
            FragmentTimeWindow: Ventana actualizada, o None si no existe
        """
        stmt = select(FragmentTimeWindow).where(
            FragmentTimeWindow.id == window_id
        )
        result = await self.session.execute(stmt)
        window = result.scalar_one_or_none()

        if not window:
            return None

        for key, value in updates.items():
            if hasattr(window, key):
                setattr(window, key, value)

        await self.session.commit()
        await self.session.refresh(window)

        logger.info(f"Ventana de tiempo {window_id} actualizada")

        return window

    async def delete_time_window(self, window_id: int) -> bool:
        """
        Elimina una ventana de tiempo.

        Args:
            window_id: ID de la ventana

        Returns:
            bool: True si se eliminó, False si no existía
        """
        stmt = select(FragmentTimeWindow).where(
            FragmentTimeWindow.id == window_id
        )
        result = await self.session.execute(stmt)
        window = result.scalar_one_or_none()

        if not window:
            return False

        await self.session.delete(window)
        await self.session.commit()

        logger.info(f"Ventana de tiempo {window_id} eliminada")

        return True

    async def get_remaining_time(
        self, user_id: int, cooldown_type: CooldownType, target_key: str
    ) -> Optional[int]:
        """
        Obtiene los segundos restantes de un cooldown.

        Args:
            user_id: ID del usuario
            cooldown_type: Tipo de cooldown
            target_key: Clave del objetivo

        Returns:
            int: Segundos restantes, o None si no hay cooldown activo
        """
        is_active, expires_at, _ = await self.check_cooldown(
            user_id, cooldown_type, target_key
        )

        if not is_active or not expires_at:
            return None

        remaining = (expires_at - datetime.utcnow()).total_seconds()
        return max(0, int(remaining))
