"""
Servicio de Recomendaciones del Gabinete (Fase 4).

Responsabilidades:
- Recomendaciones por arquetipo
- Recomendaciones por historial de compras
- Mensajes personalizados de Lucien
- Notificaciones proactivas
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, UTC, timedelta
from dataclasses import dataclass
import logging

from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from bot.shop.database.models import (
    ShopItem,
    ItemCategory,
    ItemPurchase,
    UserInventory,
    UserInventoryItem,
    GabineteNotification,
)
from bot.shop.database.enums import (
    GabineteCategory,
    NotificationType,
)

logger = logging.getLogger(__name__)


# ============================================================
# MAPEO ARQUETIPO -> CATEGORIA RECOMENDADA
# ============================================================

ARCHETYPE_RECOMMENDATIONS = {
    "explorer": {
        "categories": ["keys", "secret"],
        "reason": "Su curiosidad merece recompensa. Las Llaves abren puertas que otros no ven.",
        "item_types": ["narrative_key", "archive", "easter_egg"],
    },
    "direct": {
        "categories": ["ephemeral"],
        "reason": "Usted prefiere resultados inmediatos. Los Efimeros le daran satisfaccion rapida.",
        "item_types": ["badge_temp", "audio", "text"],
    },
    "romantic": {
        "categories": ["relics"],
        "reason": "Busca conexion profunda. Las Reliquias contienen historias emotivas.",
        "item_types": ["collectible", "text"],
    },
    "analytical": {
        "categories": ["keys"],
        "reason": "Le interesa entender, no solo consumir. Las Llaves revelan informacion oculta.",
        "item_types": ["narrative_key", "archive"],
    },
    "persistent": {
        "categories": ["distinctive"],
        "reason": "Su constancia merece reconocimiento. Los Distintivos marcan su progreso.",
        "item_types": ["badge_perm"],
    },
    "patient": {
        "categories": ["relics"],
        "reason": "La paciencia trae recompensas duraderas. Las Reliquias son inversiones de largo plazo.",
        "item_types": ["collectible", "midnight", "master_key"],
    },
}

# Mensajes de Lucien para recomendaciones
LUCIEN_RECOMMENDATION_MESSAGES = {
    "explorer": "\"He notado su tendencia a explorar cada rincon. Quizas le interese lo que hay detras de estas Llaves...\"",
    "direct": "\"Usted va al grano. Estos Efimeros le daran lo que busca sin rodeos.\"",
    "romantic": "\"Percibo un corazon que busca conexion. Estas Reliquias contienen historias que podrian resonar con usted.\"",
    "analytical": "\"Su mente busca patrones y explicaciones. Estas Llaves revelan verdades ocultas.\"",
    "persistent": "\"La constancia merece reconocimiento visible. Estos Distintivos proclamaran su dedicacion.\"",
    "patient": "\"La paciencia es una virtud subestimada. Estas Reliquias recompensan a quienes saben esperar.\"",
}


@dataclass
class Recommendation:
    """Una recomendacion de item."""
    item: ShopItem
    reason: str
    priority: int  # 1-10, mayor = mas relevante
    source: str  # "archetype", "history", "trending"


class RecommendationService:
    """Servicio de recomendaciones del Gabinete."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_recommendations_for_user(
        self,
        user_id: int,
        user_level: int,
        archetype: Optional[str] = None,
        limit: int = 3
    ) -> List[Recommendation]:
        """
        Obtiene recomendaciones personalizadas para un usuario.

        Args:
            user_id: ID del usuario
            user_level: Nivel actual
            archetype: Arquetipo del usuario (opcional)
            limit: Numero maximo de recomendaciones

        Returns:
            Lista de Recommendation ordenadas por prioridad
        """
        recommendations = []

        # 1. Recomendaciones por arquetipo
        if archetype:
            archetype_recs = await self._get_archetype_recommendations(
                user_id, user_level, archetype
            )
            recommendations.extend(archetype_recs)

        # 2. Recomendaciones por historial
        history_recs = await self._get_history_recommendations(user_id, user_level)
        recommendations.extend(history_recs)

        # 3. Items trending (mas vendidos)
        trending_recs = await self._get_trending_recommendations(user_id, user_level)
        recommendations.extend(trending_recs)

        # Ordenar por prioridad y eliminar duplicados
        seen_items = set()
        unique_recs = []
        for rec in sorted(recommendations, key=lambda r: r.priority, reverse=True):
            if rec.item.id not in seen_items:
                seen_items.add(rec.item.id)
                unique_recs.append(rec)

        return unique_recs[:limit]

    async def _get_archetype_recommendations(
        self,
        user_id: int,
        user_level: int,
        archetype: str
    ) -> List[Recommendation]:
        """Obtiene recomendaciones basadas en arquetipo."""
        recommendations = []

        config = ARCHETYPE_RECOMMENDATIONS.get(archetype.lower())
        if not config:
            return []

        # Buscar items en categorias recomendadas
        for category_slug in config["categories"]:
            result = await self.session.execute(
                select(ShopItem)
                .join(ItemCategory)
                .where(
                    and_(
                        ItemCategory.slug == category_slug,
                        ShopItem.is_active == True,
                        ShopItem.min_level_to_buy <= user_level,
                        ShopItem.visibility == "public"
                    )
                )
                .order_by(ShopItem.order)
                .limit(2)
            )
            items = result.scalars().all()

            for item in items:
                # Verificar que el usuario no lo tenga
                if not await self._user_has_item(user_id, item.id):
                    recommendations.append(Recommendation(
                        item=item,
                        reason=config["reason"],
                        priority=8,
                        source="archetype"
                    ))

        return recommendations

    async def _get_history_recommendations(
        self,
        user_id: int,
        user_level: int
    ) -> List[Recommendation]:
        """Obtiene recomendaciones basadas en historial de compras."""
        recommendations = []

        # Buscar categorias mas compradas
        result = await self.session.execute(
            select(
                ItemCategory.slug,
                func.count(ItemPurchase.id).label('count')
            )
            .join(ShopItem, ItemPurchase.item_id == ShopItem.id)
            .join(ItemCategory)
            .where(ItemPurchase.user_id == user_id)
            .group_by(ItemCategory.slug)
            .order_by(func.count(ItemPurchase.id).desc())
            .limit(2)
        )
        top_categories = result.all()

        for cat_slug, _ in top_categories:
            # Buscar items no comprados en esa categoria
            subquery = select(ItemPurchase.item_id).where(
                ItemPurchase.user_id == user_id
            )

            result = await self.session.execute(
                select(ShopItem)
                .join(ItemCategory)
                .where(
                    and_(
                        ItemCategory.slug == cat_slug,
                        ShopItem.is_active == True,
                        ShopItem.min_level_to_buy <= user_level,
                        ShopItem.id.notin_(subquery)
                    )
                )
                .order_by(ShopItem.price_besitos)
                .limit(1)
            )
            item = result.scalar_one_or_none()

            if item:
                recommendations.append(Recommendation(
                    item=item,
                    reason="Basado en sus compras anteriores.",
                    priority=6,
                    source="history"
                ))

        return recommendations

    async def _get_trending_recommendations(
        self,
        user_id: int,
        user_level: int
    ) -> List[Recommendation]:
        """Obtiene items mas vendidos recientemente."""
        recommendations = []

        # Items mas vendidos en ultimos 30 dias
        thirty_days_ago = datetime.now(UTC) - timedelta(days=30)

        result = await self.session.execute(
            select(
                ShopItem,
                func.count(ItemPurchase.id).label('sales')
            )
            .join(ItemPurchase)
            .join(ItemCategory)
            .where(
                and_(
                    ItemPurchase.purchased_at >= thirty_days_ago,
                    ShopItem.is_active == True,
                    ShopItem.min_level_to_buy <= user_level,
                    ItemCategory.is_gabinete == True
                )
            )
            .group_by(ShopItem.id)
            .order_by(func.count(ItemPurchase.id).desc())
            .limit(3)
        )
        trending = result.all()

        for item, sales in trending:
            if not await self._user_has_item(user_id, item.id):
                recommendations.append(Recommendation(
                    item=item,
                    reason=f"Popular - {sales} adquisiciones recientes.",
                    priority=4,
                    source="trending"
                ))

        return recommendations

    async def _user_has_item(
        self,
        user_id: int,
        item_id: int
    ) -> bool:
        """Verifica si el usuario tiene un item."""
        result = await self.session.execute(
            select(UserInventoryItem.id)
            .join(UserInventory)
            .where(
                and_(
                    UserInventory.user_id == user_id,
                    UserInventoryItem.item_id == item_id
                )
            )
            .limit(1)
        )
        return result.scalar_one_or_none() is not None

    def get_lucien_message_for_archetype(
        self,
        archetype: str
    ) -> str:
        """Obtiene mensaje de Lucien para un arquetipo."""
        return LUCIEN_RECOMMENDATION_MESSAGES.get(
            archetype.lower(),
            "\"Basandome en lo que he observado de usted... quizas le interese explorar.\""
        )


class GabineteNotificationService:
    """Servicio de notificaciones del Gabinete."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_notification(
        self,
        user_id: int,
        notification_type: NotificationType,
        title: str,
        message: str,
        item_id: Optional[int] = None
    ) -> GabineteNotification:
        """Crea una notificacion para un usuario."""
        notification = GabineteNotification(
            user_id=user_id,
            item_id=item_id,
            notification_type=notification_type.value,
            title=title,
            message=message
        )
        self.session.add(notification)
        await self.session.commit()
        await self.session.refresh(notification)

        logger.info(f"Created notification: user={user_id}, type={notification_type.value}")
        return notification

    async def notify_new_item(
        self,
        item: ShopItem,
        user_ids: List[int]
    ) -> int:
        """
        Notifica a usuarios sobre un nuevo item.

        Returns:
            Numero de notificaciones creadas
        """
        count = 0
        title = f"Nuevo en el Gabinete: {item.name}"
        message = (
            f"El Gabinete tiene algo nuevo.\n\n"
            f"'{item.name}' ha sido agregado a la coleccion.\n"
            f"{item.description}\n\n"
            f"Precio: {item.price_besitos} Favores"
        )

        for user_id in user_ids:
            await self.create_notification(
                user_id=user_id,
                notification_type=NotificationType.NEW_ITEM,
                title=title,
                message=message,
                item_id=item.id
            )
            count += 1

        return count

    async def notify_low_stock(
        self,
        item: ShopItem,
        user_ids: List[int]
    ) -> int:
        """Notifica sobre stock bajo."""
        count = 0
        title = f"Stock bajo: {item.name}"
        message = (
            f"Aviso del Gabinete:\n\n"
            f"'{item.name}' esta casi agotado.\n"
            f"Quedan solo {item.stock} unidades.\n\n"
            f"Si lo deseaba... el momento es ahora."
        )

        for user_id in user_ids:
            await self.create_notification(
                user_id=user_id,
                notification_type=NotificationType.LOW_STOCK,
                title=title,
                message=message,
                item_id=item.id
            )
            count += 1

        return count

    async def notify_expiring_soon(
        self,
        item: ShopItem,
        hours_remaining: int,
        user_ids: List[int]
    ) -> int:
        """Notifica sobre item por expirar."""
        count = 0
        title = f"Ultima oportunidad: {item.name}"
        message = (
            f"Recordatorio del Gabinete:\n\n"
            f"'{item.name}' dejara de estar disponible en {hours_remaining} horas.\n\n"
            f"Es la ultima oportunidad."
        )

        for user_id in user_ids:
            await self.create_notification(
                user_id=user_id,
                notification_type=NotificationType.EXPIRING_SOON,
                title=title,
                message=message,
                item_id=item.id
            )
            count += 1

        return count

    async def get_unread_notifications(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[GabineteNotification]:
        """Obtiene notificaciones no leidas de un usuario."""
        result = await self.session.execute(
            select(GabineteNotification)
            .where(
                and_(
                    GabineteNotification.user_id == user_id,
                    GabineteNotification.read_at == None
                )
            )
            .order_by(GabineteNotification.sent_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def mark_as_read(
        self,
        notification_id: int
    ) -> bool:
        """Marca una notificacion como leida."""
        result = await self.session.execute(
            select(GabineteNotification).where(
                GabineteNotification.id == notification_id
            )
        )
        notification = result.scalar_one_or_none()

        if notification:
            notification.read_at = datetime.now(UTC)
            await self.session.commit()
            return True

        return False

    async def mark_all_as_read(
        self,
        user_id: int
    ) -> int:
        """Marca todas las notificaciones de un usuario como leidas."""
        from sqlalchemy import update

        now = datetime.now(UTC)
        result = await self.session.execute(
            update(GabineteNotification)
            .where(
                and_(
                    GabineteNotification.user_id == user_id,
                    GabineteNotification.read_at == None
                )
            )
            .values(read_at=now)
        )
        await self.session.commit()

        return result.rowcount

    async def get_notification_count(
        self,
        user_id: int
    ) -> int:
        """Obtiene cantidad de notificaciones no leidas."""
        result = await self.session.execute(
            select(func.count())
            .select_from(GabineteNotification)
            .where(
                and_(
                    GabineteNotification.user_id == user_id,
                    GabineteNotification.read_at == None
                )
            )
        )
        return result.scalar() or 0
