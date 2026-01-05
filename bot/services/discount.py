"""
Servicio de descuentos inteligentes.

Gestiona descuentos basados en:
- Nivel del usuario (0-15%)
- Streak de participación (0-10%)
- Arquetipo del usuario (0-5%)
- Primera compra (10%)
- Eventos de tiempo limitado
"""
import logging
from typing import Tuple, List, Dict, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from bot.narrative.database.enums import ArchetypeType

logger = logging.getLogger(__name__)


class DiscountService:
    """
    Servicio para calcular descuentos inteligentes en compras.

    Combina múltiples fuentes de descuento:
    - Nivel narrativo del usuario
    - Días consecutivos de streak
    - Arquetipo del usuario
    - Primera compra
    - Eventos especiales
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el servicio de descuentos.

        Args:
            session: Sesión async de SQLAlchemy
        """
        self.session = session

    async def calculate_discount(
        self,
        user_id: int,
        item_id: int,
        item_category: Optional[str] = None
    ) -> Tuple[float, List[str]]:
        """
        Calcula el descuento total para un usuario en un item específico.

        Args:
            user_id: ID del usuario
            item_id: ID del item de la tienda
            item_category: Categoría del item (para descuento por arquetipo)

        Returns:
            Tuple[float, List[str]]: (descuento_total, lista_de_razones)
                - descuento_total: Porcentaje total (0.0 a 1.0)
                - lista_de_razones: Razones del descuento para mostrar al usuario
        """
        reasons = []
        total_discount = 0.0

        # 1. Descuento por nivel
        level_discount = await self._get_level_discount(user_id)
        if level_discount > 0:
            total_discount += level_discount
            reasons.append(f"Nivel: {int(level_discount * 100)}%")

        # 2. Descuento por streak
        streak_discount = await self._get_streak_discount(user_id)
        if streak_discount > 0:
            total_discount += streak_discount
            reasons.append(f"Racha: {int(streak_discount * 100)}%")

        # 3. Descuento por arquetipo (si aplica)
        if item_category:
            archetype_discount = await self._get_archetype_discount(user_id, item_category)
            if archetype_discount > 0:
                total_discount += archetype_discount
                reasons.append(f"Arquetipo: {int(archetype_discount * 100)}%")

        # 4. Descuento primera compra
        is_first_purchase = await self._is_first_purchase(user_id)
        if is_first_purchase:
            first_purchase_discount = 0.10  # 10%
            total_discount += first_purchase_discount
            reasons.append(f"Primera compra: {int(first_purchase_discount * 100)}%")

        # Limitar descuento máximo a 40%
        total_discount = min(total_discount, 0.40)

        logger.debug(
            f"Descuento para user {user_id} en item {item_id}: "
            f"{int(total_discount * 100)}% - Razones: {reasons}"
        )

        return total_discount, reasons

    async def get_applicable_discounts(self, user_id: int) -> Dict[str, float]:
        """
        Obtiene todos los descuentos aplicables para el usuario.

        Args:
            user_id: ID del usuario

        Returns:
            Dict[str, float]: Diccionario de descuentos disponibles
        """
        discounts = {}

        # Nivel
        level_discount = await self._get_level_discount(user_id)
        if level_discount > 0:
            discounts["level"] = level_discount

        # Streak
        streak_discount = await self._get_streak_discount(user_id)
        if streak_discount > 0:
            discounts["streak"] = streak_discount

        # Primera compra
        if await self._is_first_purchase(user_id):
            discounts["first_purchase"] = 0.10

        return discounts

    # ========================================
    # MÉTODOS PRIVADOS
    # ========================================

    async def _get_level_discount(self, user_id: int) -> float:
        """
        Calcula descuento basado en el nivel narrativo del usuario.

        Tabla de descuentos:
        - Nivel 1-2: 0%
        - Nivel 3: 5%
        - Nivel 4: 8%
        - Nivel 5: 10%
        - Nivel 6+: 15%

        Args:
            user_id: ID del usuario

        Returns:
            float: Descuento (0.0 a 0.15)
        """
        try:
            from bot.narrative.services.progress import ProgressService

            progress_service = ProgressService(self.session)
            progress = await progress_service.get_or_create_progress(user_id)

            current_level = progress.current_level

            if current_level >= 6:
                return 0.15
            elif current_level == 5:
                return 0.10
            elif current_level == 4:
                return 0.08
            elif current_level == 3:
                return 0.05
            else:
                return 0.0

        except Exception as e:
            logger.error(f"Error calculando descuento por nivel: {e}", exc_info=True)
            return 0.0

    async def _get_streak_discount(self, user_id: int) -> float:
        """
        Calcula descuento basado en días consecutivos de streak.

        Tabla de descuentos:
        - 7+ días: 3%
        - 14+ días: 5%
        - 30+ días: 7%
        - 60+ días: 10%

        Args:
            user_id: ID del usuario

        Returns:
            float: Descuento (0.0 a 0.10)
        """
        try:
            from bot.gamification.database.models import UserStreak

            stmt = select(UserStreak).where(UserStreak.user_id == user_id)
            result = await self.session.execute(stmt)
            user_streak = result.scalar_one_or_none()

            if not user_streak:
                return 0.0

            current_streak = user_streak.current_streak

            if current_streak >= 60:
                return 0.10
            elif current_streak >= 30:
                return 0.07
            elif current_streak >= 14:
                return 0.05
            elif current_streak >= 7:
                return 0.03
            else:
                return 0.0

        except Exception as e:
            logger.error(f"Error calculando descuento por streak: {e}", exc_info=True)
            return 0.0

    async def _get_archetype_discount(
        self,
        user_id: int,
        item_category: str
    ) -> float:
        """
        Calcula descuento basado en afinidad entre arquetipo y categoría.

        Arquetipos y categorías afines:
        - EXPLORER: llaves, reliquias, fragmentos (5%)
        - ROMANTIC: distintivos, confesiones (5%)
        - ANALYTICAL: archivos, fragmentos (5%)
        - PERSISTENT: distintivos, sellos, emblemas (5%)
        - DIRECT: pases, accesos, prioridades (5%)
        - PATIENT: reliquias, archivos, cristales (5%)

        Args:
            user_id: ID del usuario
            item_category: Categoría del item

        Returns:
            float: Descuento (0.0 a 0.05)
        """
        try:
            from bot.services.archetype_advanced import AdvancedArchetypeService

            archetype_service = AdvancedArchetypeService(self.session)
            archetype, confidence = await archetype_service.get_dominant_archetype(user_id)

            # Solo aplicar si confianza >= 60%
            if confidence < 0.6:
                return 0.0

            # Mapeo de arquetipos a categorías afines
            archetype_preferences = {
                ArchetypeType.EXPLORER: ["llaves", "reliquias", "fragmentos"],
                ArchetypeType.ROMANTIC: ["distintivos", "confesiones"],
                ArchetypeType.ANALYTICAL: ["archivos", "fragmentos"],
                ArchetypeType.PERSISTENT: ["distintivos", "sellos", "emblemas"],
                ArchetypeType.DIRECT: ["pases", "accesos", "prioridades"],
                ArchetypeType.PATIENT: ["reliquias", "archivos", "cristales"],
            }

            # Verificar afinidad
            preferred_categories = archetype_preferences.get(archetype, [])

            if item_category.lower() in preferred_categories:
                return 0.05
            else:
                return 0.0

        except Exception as e:
            logger.error(f"Error calculando descuento por arquetipo: {e}", exc_info=True)
            return 0.0

    async def _is_first_purchase(self, user_id: int) -> bool:
        """
        Verifica si esta es la primera compra del usuario.

        Args:
            user_id: ID del usuario

        Returns:
            bool: True si es primera compra
        """
        try:
            from bot.gamification.database.models import InventoryItem

            stmt = select(InventoryItem).where(InventoryItem.user_id == user_id).limit(1)

            result = await self.session.execute(stmt)
            first_item = result.scalar_one_or_none()

            # Si no tiene items, es primera compra
            return first_item is None

        except Exception as e:
            logger.error(f"Error verificando primera compra: {e}", exc_info=True)
            return False

    async def apply_limited_time_discount(
        self,
        event_id: str
    ) -> float:
        """
        Calcula descuento para eventos de tiempo limitado.

        Args:
            event_id: ID del evento especial

        Returns:
            float: Descuento del evento (0.0 a 0.20)
        """
        # TODO: Implementar sistema de eventos especiales
        # Por ahora retorna 0.0
        return 0.0

    async def format_discount_message(
        self,
        discount: float,
        reasons: List[str]
    ) -> str:
        """
        Formatea el mensaje de descuento para mostrar al usuario.

        Args:
            discount: Descuento total (0.0 a 1.0)
            reasons: Lista de razones del descuento

        Returns:
            str: Mensaje formateado en HTML
        """
        if discount == 0.0:
            return ""

        message = f"💰 <b>Descuento Total: {int(discount * 100)}%</b>\n\n"
        message += "<b>Razones:</b>\n"

        for reason in reasons:
            message += f"• {reason}\n"

        return message
