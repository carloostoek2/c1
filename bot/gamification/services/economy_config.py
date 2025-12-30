"""Servicio de configuración de economía de Favores.

Responsabilidades:
- Obtener configuración de economía (singleton)
- Actualizar valores de economía
- Proveer getters para cada tipo de acción
"""

from typing import Optional
from datetime import datetime, UTC
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from bot.gamification.database.models import GamificationConfig

logger = logging.getLogger(__name__)


class EconomyConfigService:
    """Servicio de gestión de configuración de economía de Favores."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_config(self) -> GamificationConfig:
        """Obtiene configuración de economía (singleton id=1).

        Si no existe, crea una con valores por defecto.

        Returns:
            GamificationConfig con valores de economía
        """
        stmt = select(GamificationConfig).where(GamificationConfig.id == 1)
        result = await self.session.execute(stmt)
        config = result.scalar_one_or_none()

        if not config:
            # Crear configuración con valores por defecto
            config = GamificationConfig(id=1)
            self.session.add(config)
            await self.session.commit()
            await self.session.refresh(config)
            logger.info("Created GamificationConfig with default economy values")

        return config

    # ========================================
    # GETTERS DE VALORES DE ECONOMÍA
    # ========================================

    async def get_reaction_base(self) -> float:
        """Obtiene valor base por reacción.

        Returns:
            Cantidad de Favores por reacción base (default: 0.1)
        """
        config = await self.get_config()
        return config.earn_reaction_base

    async def get_first_reaction_day(self) -> float:
        """Obtiene bonus por primera reacción del día.

        Returns:
            Cantidad de Favores por primera reacción del día (default: 0.5)
        """
        config = await self.get_config()
        return config.earn_first_reaction_day

    async def get_reactions_daily_limit(self) -> int:
        """Obtiene límite diario de reacciones que otorgan Favores.

        Returns:
            Número máximo de reacciones por día (default: 10)
        """
        config = await self.get_config()
        return config.limit_reactions_per_day

    async def get_mission_daily(self) -> float:
        """Obtiene valor por completar misión diaria.

        Returns:
            Cantidad de Favores por misión diaria (default: 1.0)
        """
        config = await self.get_config()
        return config.earn_mission_daily

    async def get_mission_weekly(self) -> float:
        """Obtiene valor por completar misión semanal.

        Returns:
            Cantidad de Favores por misión semanal (default: 3.0)
        """
        config = await self.get_config()
        return config.earn_mission_weekly

    async def get_level_evaluation(self) -> float:
        """Obtiene valor por completar evaluación de nivel.

        Returns:
            Cantidad de Favores por evaluación de nivel (default: 5.0)
        """
        config = await self.get_config()
        return config.earn_level_evaluation

    async def get_streak_7_days(self) -> float:
        """Obtiene bonus por racha de 7 días.

        Returns:
            Cantidad de Favores por racha de 7 días (default: 2.0)
        """
        config = await self.get_config()
        return config.earn_streak_7_days

    async def get_streak_30_days(self) -> float:
        """Obtiene bonus por racha de 30 días.

        Returns:
            Cantidad de Favores por racha de 30 días (default: 10.0)
        """
        config = await self.get_config()
        return config.earn_streak_30_days

    async def get_easter_egg_range(self) -> tuple[float, float]:
        """Obtiene rango de Favores por easter egg.

        Returns:
            Tupla (min, max) de Favores por easter egg (default: 2.0, 5.0)
        """
        config = await self.get_config()
        return (config.earn_easter_egg_min, config.earn_easter_egg_max)

    async def get_referral_active(self) -> float:
        """Obtiene valor por referido activo.

        Returns:
            Cantidad de Favores por referido activo (default: 5.0)
        """
        config = await self.get_config()
        return config.earn_referral_active

    # ========================================
    # SETTERS DE VALORES DE ECONOMÍA
    # ========================================

    async def update_reaction_base(self, value: float) -> bool:
        """Actualiza valor base por reacción.

        Args:
            value: Nueva cantidad (debe ser >= 0)

        Returns:
            True si actualizó correctamente
        """
        if value < 0:
            logger.warning(f"Attempted to set negative reaction_base: {value}")
            return False

        config = await self.get_config()
        config.earn_reaction_base = value
        config.updated_at = datetime.now(UTC)
        await self.session.commit()

        logger.info(f"Updated earn_reaction_base to {value}")
        return True

    async def update_first_reaction_day(self, value: float) -> bool:
        """Actualiza bonus por primera reacción del día.

        Args:
            value: Nueva cantidad (debe ser >= 0)

        Returns:
            True si actualizó correctamente
        """
        if value < 0:
            logger.warning(f"Attempted to set negative first_reaction_day: {value}")
            return False

        config = await self.get_config()
        config.earn_first_reaction_day = value
        config.updated_at = datetime.now(UTC)
        await self.session.commit()

        logger.info(f"Updated earn_first_reaction_day to {value}")
        return True

    async def update_reactions_daily_limit(self, value: int) -> bool:
        """Actualiza límite diario de reacciones.

        Args:
            value: Nuevo límite (debe ser >= 1)

        Returns:
            True si actualizó correctamente
        """
        if value < 1:
            logger.warning(f"Attempted to set invalid reactions_daily_limit: {value}")
            return False

        config = await self.get_config()
        config.limit_reactions_per_day = value
        config.updated_at = datetime.now(UTC)
        await self.session.commit()

        logger.info(f"Updated limit_reactions_per_day to {value}")
        return True

    async def update_mission_daily(self, value: float) -> bool:
        """Actualiza valor por misión diaria.

        Args:
            value: Nueva cantidad (debe ser >= 0)

        Returns:
            True si actualizó correctamente
        """
        if value < 0:
            return False

        config = await self.get_config()
        config.earn_mission_daily = value
        config.updated_at = datetime.now(UTC)
        await self.session.commit()

        logger.info(f"Updated earn_mission_daily to {value}")
        return True

    async def update_mission_weekly(self, value: float) -> bool:
        """Actualiza valor por misión semanal.

        Args:
            value: Nueva cantidad (debe ser >= 0)

        Returns:
            True si actualizó correctamente
        """
        if value < 0:
            return False

        config = await self.get_config()
        config.earn_mission_weekly = value
        config.updated_at = datetime.now(UTC)
        await self.session.commit()

        logger.info(f"Updated earn_mission_weekly to {value}")
        return True

    # ========================================
    # MÉTODO BULK UPDATE
    # ========================================

    async def update_economy_values(self, values: dict) -> tuple[bool, str]:
        """Actualiza múltiples valores de economía de una vez.

        Args:
            values: Dict con claves como 'earn_reaction_base', 'limit_reactions_per_day', etc.

        Returns:
            (success, message)

        Example:
            >>> await economy.update_economy_values({
            ...     'earn_reaction_base': 0.2,
            ...     'earn_first_reaction_day': 1.0,
            ...     'limit_reactions_per_day': 15
            ... })
            (True, "Updated 3 economy values")
        """
        config = await self.get_config()
        updated_count = 0

        # Mapeo de claves válidas
        valid_fields = {
            'earn_reaction_base', 'earn_first_reaction_day', 'limit_reactions_per_day',
            'earn_mission_daily', 'earn_mission_weekly', 'earn_level_evaluation',
            'earn_streak_7_days', 'earn_streak_30_days',
            'earn_easter_egg_min', 'earn_easter_egg_max',
            'earn_referral_active'
        }

        for key, value in values.items():
            if key in valid_fields and hasattr(config, key):
                # Validación básica
                if isinstance(value, (int, float)) and value >= 0:
                    setattr(config, key, value)
                    updated_count += 1
                else:
                    logger.warning(f"Invalid value for {key}: {value}")

        if updated_count > 0:
            config.updated_at = datetime.now(UTC)
            await self.session.commit()
            logger.info(f"Bulk updated {updated_count} economy values")
            return True, f"Updated {updated_count} economy values"

        return False, "No valid values to update"

    # ========================================
    # RESET A VALORES POR DEFECTO
    # ========================================

    async def reset_to_defaults(self) -> bool:
        """Resetea todos los valores de economía a sus defaults.

        Returns:
            True si reseteo correctamente
        """
        config = await self.get_config()

        # Reacciones
        config.earn_reaction_base = 0.1
        config.earn_first_reaction_day = 0.5
        config.limit_reactions_per_day = 10

        # Misiones
        config.earn_mission_daily = 1.0
        config.earn_mission_weekly = 3.0
        config.earn_level_evaluation = 5.0

        # Rachas
        config.earn_streak_7_days = 2.0
        config.earn_streak_30_days = 10.0

        # Easter eggs
        config.earn_easter_egg_min = 2.0
        config.earn_easter_egg_max = 5.0

        # Referidos
        config.earn_referral_active = 5.0

        config.updated_at = datetime.now(UTC)
        await self.session.commit()

        logger.info("Reset economy configuration to defaults")
        return True
