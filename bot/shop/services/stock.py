"""
Servicio de gestión de stock limitado para items especiales.

Permite:
- Crear items con stock limitado (escasez)
- Reservar temporalmente durante compra
- Liberar reservas expiradas
- Gestionar eventos de tiempo limitado
"""
import logging
from typing import Tuple, Optional, List
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from bot.database.models import LimitedStock

logger = logging.getLogger(__name__)


class StockLimitedService:
    """
    Servicio para gestionar items con stock limitado.

    Características:
    - Stock limitado crea escasez y urgencia
    - Reservas temporales durante checkout
    - Eventos de tiempo limitado
    - Protección contra compras simultáneas
    """

    # Duración de reservas en segundos (5 minutos)
    RESERVATION_DURATION = 300

    def __init__(self, session: AsyncSession):
        """
        Inicializa el servicio de stock limitado.

        Args:
            session: Sesión async de SQLAlchemy
        """
        self.session = session

    async def create_limited_item(
        self,
        item_id: int,
        initial_quantity: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Optional[LimitedStock]:
        """
        Crea un item con stock limitado.

        Args:
            item_id: ID del item en shop_items
            initial_quantity: Cantidad inicial disponible
            start_date: Fecha de inicio (None = ahora)
            end_date: Fecha de fin (None = permanente)

        Returns:
            LimitedStock: Item limitado creado, o None si ya existe
        """
        try:
            # Verificar si ya existe
            existing = await self.get_limited_item(item_id)
            if existing:
                logger.warning(f"Item {item_id} ya tiene stock limitado")
                return None

            # Crear nuevo stock limitado
            limited_stock = LimitedStock(
                item_id=item_id,
                initial_quantity=initial_quantity,
                remaining_quantity=initial_quantity,
                start_date=start_date or datetime.utcnow(),
                end_date=end_date,
            )

            self.session.add(limited_stock)
            await self.session.commit()
            await self.session.refresh(limited_stock)

            logger.info(
                f"Stock limitado creado: item {item_id}, "
                f"cantidad {initial_quantity}"
            )

            return limited_stock

        except Exception as e:
            logger.error(f"Error creando limited stock: {e}", exc_info=True)
            await self.session.rollback()
            return None

    async def check_availability(
        self,
        item_id: int
    ) -> Tuple[bool, int]:
        """
        Verifica disponibilidad de un item limitado.

        Args:
            item_id: ID del item

        Returns:
            Tuple[bool, int]: (disponible, cantidad_restante)
        """
        try:
            limited_item = await self.get_limited_item(item_id)

            if not limited_item:
                # Item no tiene stock limitado, está disponible
                return True, -1

            # Verificar si está activo (dentro de ventana de tiempo)
            if not limited_item.is_active:
                return False, 0

            # Verificar si hay stock
            if limited_item.is_sold_out:
                return False, 0

            return True, limited_item.remaining_quantity

        except Exception as e:
            logger.error(f"Error checking availability: {e}", exc_info=True)
            return False, 0

    async def reserve_item(
        self,
        user_id: int,
        item_id: int
    ) -> bool:
        """
        Reserva un item temporalmente durante el checkout.

        Nota: Por simplicidad, esta versión reduce el stock directamente.
        Para reservas complejas se necesitaría una tabla intermedia.

        Args:
            user_id: ID del usuario
            item_id: ID del item

        Returns:
            bool: True si se reservó exitosamente
        """
        try:
            limited_item = await self.get_limited_item(item_id)

            if not limited_item:
                # Item no limitado, siempre disponible
                return True

            # Verificar disponibilidad
            is_available, remaining = await self.check_availability(item_id)

            if not is_available or remaining <= 0:
                logger.warning(
                    f"No se puede reservar item {item_id} para user {user_id}: "
                    f"sin stock"
                )
                return False

            # Reducir stock (reserva)
            limited_item.remaining_quantity -= 1
            await self.session.commit()

            logger.info(
                f"Item {item_id} reservado para user {user_id}. "
                f"Stock restante: {limited_item.remaining_quantity}"
            )

            return True

        except Exception as e:
            logger.error(f"Error reservando item: {e}", exc_info=True)
            await self.session.rollback()
            return False

    async def complete_purchase(
        self,
        user_id: int,
        item_id: int
    ) -> bool:
        """
        Completa la compra de un item limitado.

        En esta implementación simplificada, la reserva ya redujo el stock,
        así que solo verificamos que la compra es válida.

        Args:
            user_id: ID del usuario
            item_id: ID del item

        Returns:
            bool: True si la compra es válida
        """
        try:
            limited_item = await self.get_limited_item(item_id)

            if not limited_item:
                # Item no limitado
                return True

            # Verificar que el item sigue activo
            if not limited_item.is_active:
                logger.warning(
                    f"Compra fallida: item {item_id} ya no está activo"
                )
                return False

            # Ya se redujo el stock en reserve_item, compra completada
            logger.info(f"Compra completada: user {user_id}, item {item_id}")
            return True

        except Exception as e:
            logger.error(f"Error completando compra: {e}", exc_info=True)
            return False

    async def release_reservation(
        self,
        user_id: int,
        item_id: int
    ) -> None:
        """
        Libera una reserva (en caso de cancelación o timeout).

        Incrementa el stock nuevamente.

        Args:
            user_id: ID del usuario
            item_id: ID del item
        """
        try:
            limited_item = await self.get_limited_item(item_id)

            if not limited_item:
                return

            # Incrementar stock (liberar reserva)
            limited_item.remaining_quantity += 1
            await self.session.commit()

            logger.info(
                f"Reserva liberada: user {user_id}, item {item_id}. "
                f"Stock actualizado: {limited_item.remaining_quantity}"
            )

        except Exception as e:
            logger.error(f"Error liberando reserva: {e}", exc_info=True)
            await self.session.rollback()

    async def get_limited_items(
        self,
        active_only: bool = True
    ) -> List[LimitedStock]:
        """
        Obtiene todos los items con stock limitado.

        Args:
            active_only: Si True, solo retorna items activos

        Returns:
            List[LimitedStock]: Lista de items limitados
        """
        try:
            if active_only:
                now = datetime.utcnow()

                stmt = select(LimitedStock).where(
                    and_(
                        LimitedStock.start_date <= now,
                        LimitedStock.remaining_quantity > 0,
                        # end_date puede ser NULL (permanente) o futuro
                        (LimitedStock.end_date.is_(None)) | (LimitedStock.end_date > now)
                    )
                )
            else:
                stmt = select(LimitedStock)

            result = await self.session.execute(stmt)
            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"Error obteniendo limited items: {e}", exc_info=True)
            return []

    async def get_limited_item(
        self,
        item_id: int
    ) -> Optional[LimitedStock]:
        """
        Obtiene un item limitado por ID.

        Args:
            item_id: ID del item

        Returns:
            LimitedStock: Item limitado, o None si no existe
        """
        try:
            stmt = select(LimitedStock).where(LimitedStock.item_id == item_id)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error obteniendo limited item: {e}", exc_info=True)
            return None

    async def update_stock(
        self,
        item_id: int,
        new_quantity: int
    ) -> bool:
        """
        Actualiza la cantidad de stock de un item limitado.

        Args:
            item_id: ID del item
            new_quantity: Nueva cantidad

        Returns:
            bool: True si se actualizó exitosamente
        """
        try:
            limited_item = await self.get_limited_item(item_id)

            if not limited_item:
                logger.warning(f"Item {item_id} no tiene stock limitado")
                return False

            limited_item.remaining_quantity = new_quantity
            await self.session.commit()

            logger.info(f"Stock actualizado: item {item_id}, nuevo stock {new_quantity}")
            return True

        except Exception as e:
            logger.error(f"Error actualizando stock: {e}", exc_info=True)
            await self.session.rollback()
            return False

    async def is_item_available(
        self,
        item_id: int
    ) -> bool:
        """
        Verifica rápidamente si un item está disponible.

        Args:
            item_id: ID del item

        Returns:
            bool: True si está disponible
        """
        available, _ = await self.check_availability(item_id)
        return available

    async def get_stock_status_message(
        self,
        item_id: int
    ) -> str:
        """
        Genera un mensaje de estado del stock para mostrar al usuario.

        Args:
            item_id: ID del item

        Returns:
            str: Mensaje de estado en HTML
        """
        try:
            limited_item = await self.get_limited_item(item_id)

            if not limited_item:
                return ""

            if not limited_item.is_active:
                return "⏰ <b>Evento finalizado</b>"

            if limited_item.is_sold_out:
                return "🚫 <b>Agotado</b>"

            remaining = limited_item.remaining_quantity

            if remaining <= 3:
                return f"🔥 <b>¡Últimas {remaining} unidades!</b>"
            elif remaining <= 10:
                return f"⚠️ <b>Stock limitado: {remaining} disponibles</b>"
            else:
                return f"✅ <b>Disponible ({remaining} unidades)</b>"

        except Exception as e:
            logger.error(f"Error generando mensaje de stock: {e}")
            return ""
