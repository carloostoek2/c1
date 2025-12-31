"""
Service for managing premium products and catalog.

Handles F6.3: VIP to Premium content sales.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from bot.database.models import User
from bot.shop.database.models import ShopItem, ItemCategory, UserInventoryItem, UserInventory

logger = logging.getLogger(__name__)


class PremiumCatalogService:
    """
    Service for managing premium products and user purchases.
    """
    
    def __init__(self, session: AsyncSession, bot: Bot):
        self.session = session
        self.bot = bot

    async def create_premium_categories(self):
        """
        Create premium-related categories in the shop.
        """
        # Check if premium categories already exist
        existing_categories = await self.session.execute(
            select(ItemCategory).where(ItemCategory.slug.in_(['premium', 'individual-content']))
        )
        existing = existing_categories.scalars().all()
        
        existing_slugs = [cat.slug for cat in existing]
        
        # Create premium category if it doesn't exist
        if 'premium' not in existing_slugs:
            premium_category = ItemCategory(
                name="Contenido Premium",
                slug="premium",
                description="Contenido individual exclusivo para miembros VIP",
                emoji="📹",
                order=10,
                is_active=True,
                is_gabinete=True,
                gabinete_category="ephemeral",  # Premium content is ephemeral in nature
                lucien_description="Contenido especial producido exclusivamente para miembros VIP. Cada pieza representa un momento único con Diana."
            )
            self.session.add(premium_category)
        
        # Create individual content category
        if 'individual-content' not in existing_slugs:
            individual_category = ItemCategory(
                name="Contenido Individual",
                slug="individual-content",
                description="Contenido vendido por unidad",
                emoji="🎬",
                order=11,
                is_active=True,
                is_gabinete=True,
                gabinete_category="ephemeral",
                lucien_description="Colecciones y producciones especiales vendidas individualmente. Cada compra es una inversión personal en contenido exclusivo."
            )
            self.session.add(individual_category)
        
        await self.session.commit()

    async def create_premium_product(self, name: str, description: str, price: int, 
                                   duration: str = "10 min", category_slug: str = "premium", 
                                   metadata: Optional[Dict[str, Any]] = None) -> ShopItem:
        """
        Create a new premium product.
        """
        # Get the category
        category_result = await self.session.execute(
            select(ItemCategory).where(ItemCategory.slug == category_slug)
        )
        category = category_result.scalar_one_or_none()
        
        if not category:
            raise ValueError(f"Category with slug '{category_slug}' not found")
        
        # Create the shop item
        shop_item = ShopItem(
            category_id=category.id,
            name=name,
            slug=name.lower().replace(" ", "-").replace("#", ""),
            description=description,
            long_description=f"Contenido Premium exclusivo: {description}",
            item_type="narrative",
            rarity="rare",  # Premium content is rare
            price_besitos=price,
            icon="📹",
            item_metadata=str(metadata) if metadata else None,
            
            # Configurable limits
            stock=None,  # Unlimited stock
            max_per_user=1,  # Only one per user
            
            # Requirements
            requires_vip=True,  # Only VIP can buy
            
            # Display settings
            is_featured=True,
            is_active=True,
            order=1,
            
            # Premium-specific metadata
            lucien_description=f"Este contenido especial fue creado exclusivamente para miembros VIP. {description}",
            purchase_message="¡Gracias por adquirir este contenido Premium! Diana lo ha preparado especialmente para usted.",
            post_use_message="Esperamos que haya disfrutado este contenido exclusivo de Diana.",
            min_level_to_view=1,
            min_level_to_buy=1,
            visibility="public",  # Available to all VIPs
            gabinete_item_type="premium_content",
            duration_hours=24*30,  # Access for 30 days (or permanent depending on business logic)
            available_from=datetime.utcnow(),
            event_name="Premium Content Release",
            is_limited=False,
            total_stock=None
        )
        
        self.session.add(shop_item)
        await self.session.commit()
        await self.session.refresh(shop_item)
        
        return shop_item

    async def get_premium_catalog(self) -> List[ShopItem]:
        """
        Get all active premium products.
        """
        result = await self.session.execute(
            select(ShopItem)
            .join(ItemCategory)
            .where(
                ItemCategory.slug.in_(['premium', 'individual-content']),
                ShopItem.is_active == True,
                ShopItem.requires_vip == True
            )
            .order_by(ShopItem.order, ShopItem.created_at.desc())
        )
        return result.scalars().all()

    async def initialize_premium_catalog(self):
        """
        Initialize the premium catalog with sample products.
        This would typically be called during system setup.
        """
        await self.create_premium_categories()

        # Create sample premium products
        sample_products = [
            {
                "name": "Sesión Íntima #1",
                "description": "Una sesión especial de 20 minutos con Diana, explorando temas profundos",
                "price": 35,
                "duration": "20 min",
                "metadata": {"type": "intimate_session", "quality": "high", "exclusive": True}
            },
            {
                "name": "Detrás de Escenas - Temporada 1",
                "description": "Contenido exclusivo de cómo se crean las producciones",
                "price": 25,
                "duration": "15 min",
                "metadata": {"type": "behind_scenes", "includes": ["making_of", "director_commentary"]}
            },
            {
                "name": "Selección Curada #1",
                "description": "Colección especial de momentos seleccionados por Diana",
                "price": 40,
                "duration": "25 min",
                "metadata": {"type": "curated_selection", "curation_by": "diana", "theme": "intimate_moments"}
            },
            {
                "name": "Acceso Anticipado - Nuevo Contenido",
                "description": "Acceso 48h antes al nuevo contenido de Diana",
                "price": 15,
                "duration": "48 horas",
                "metadata": {"type": "early_access", "duration_hours": 48, "feature": "exclusive_viewing"}
            }
        ]

        existing_items = await self.get_premium_catalog()
        existing_names = [item.name for item in existing_items]

        for product in sample_products:
            if product["name"] not in existing_names:
                await self.create_premium_product(
                    name=product["name"],
                    description=product["description"],
                    price=product["price"],
                    duration=product["duration"],
                    metadata=product["metadata"]
                )
                logger.info(f"Created premium product: {product['name']}")

    async def purchase_premium_content(self, user_id: int, item_id: int) -> bool:
        """
        Process a premium content purchase for a VIP user.
        """
        user = await self.session.get(User, user_id)
        if not user or not user.is_vip:
            return False  # Only VIP users can purchase premium content
        
        item = await self.session.get(ShopItem, item_id)
        if not item:
            return False  # Item doesn't exist
        
        # Check if user already has this item
        existing_item_result = await self.session.execute(
            select(UserInventoryItem)
            .join(UserInventory)
            .where(
                UserInventory.user_id == user_id,
                UserInventoryItem.item_id == item_id
            )
        )
        if existing_item_result.scalar_one_or_none():
            # User already has this item
            return False
        
        # Check if user has enough besitos
        from bot.gamification.services.besito import BesitoService
        besito_service = BesitoService(self.session)
        user_gamification = await besito_service.get_user_gamification(user_id)
        
        if user_gamification.total_besitos < item.price_besitos:
            return False  # Insufficient funds
        
        # Process the purchase
        success = await besito_service.transfer_besitos(
            from_user_id=user_id,
            to_user_id=None,  # Transfer to system/economy sink
            amount=item.price_besitos,
            description=f"Compra de contenido Premium: {item.name}"
        )
        
        if not success:
            return False  # Transfer failed
        
        # Add item to user's inventory
        user_inventory = await self.session.get(UserInventory, user_id)
        if not user_inventory:
            user_inventory = UserInventory(
                user_id=user_id,
                total_items=0,
                total_spent=item.price_besitos
            )
            self.session.add(user_inventory)
        else:
            user_inventory.total_spent += item.price_besitos
            
        inventory_item = UserInventoryItem(
            user_id=user_id,
            item_id=item.id,
            quantity=1,
            obtained_at=datetime.utcnow(),
            obtained_via="purchase",
            is_used=False
        )
        
        self.session.add(inventory_item)
        await self.session.commit()
        
        # Send confirmation to user
        await self.bot.send_message(
            user_id,
            f"🎉 ¡Adquisición exitosa!\n\n"
            f"Ha adquirido: {item.name}\n"
            f"Precio: {item.price_besitos} Favores\n\n"
            f"{item.purchase_message or 'Gracias por su compra.'}"
        )
        
        return True

    async def get_user_premium_content(self, user_id: int) -> List[ShopItem]:
        """
        Get all premium content purchased by a user.
        """
        result = await self.session.execute(
            select(ShopItem)
            .join(UserInventoryItem, ShopItem.id == UserInventoryItem.item_id)
            .join(UserInventory, UserInventoryItem.user_id == UserInventory.user_id)
            .where(
                UserInventory.user_id == user_id,
                ShopItem.category.has(ItemCategory.slug.in_(['premium', 'individual-content']))
            )
        )
        return result.scalars().all()

    async def has_purchased_content(self, user_id: int, item_id: int) -> bool:
        """
        Check if user has purchased specific premium content.
        """
        result = await self.session.execute(
            select(UserInventoryItem.id)
            .join(UserInventory)
            .where(
                UserInventory.user_id == user_id,
                UserInventoryItem.item_id == item_id
            )
            .limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def get_premium_content_by_id(self, item_id: int) -> Optional[ShopItem]:
        """
        Get a specific premium content item by ID.
        """
        result = await self.session.execute(
            select(ShopItem)
            .join(ItemCategory)
            .where(
                ShopItem.id == item_id,
                ItemCategory.slug.in_(['premium', 'individual-content']),
                ShopItem.is_active == True
            )
        )
        return result.scalar_one_or_none()

    async def get_featured_premium_content(self, limit: int = 3) -> List[ShopItem]:
        """
        Get featured/premium content for promotion.
        """
        result = await self.session.execute(
            select(ShopItem)
            .join(ItemCategory)
            .where(
                ItemCategory.slug.in_(['premium', 'individual-content']),
                ShopItem.is_active == True,
                ShopItem.requires_vip == True,
                ShopItem.is_featured == True
            )
            .order_by(ShopItem.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()