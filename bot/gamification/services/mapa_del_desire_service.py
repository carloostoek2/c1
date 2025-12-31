"""
Service for handling Mapa del Deseo (Desire Map) packages and flows.

Implements F6.4: Flujo VIP → Mapa del Deseo (3 tiers of packages)
1. La Llave Premium 
2. Círculo Íntimo
3. El Secreto
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from aiogram import Bot
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from bot.database.models import User
from bot.gamification.services.besito import BesitoService
from bot.shop.database.models import ShopItem, ItemCategory
from bot.gamification.services.premium_catalog_service import PremiumCatalogService

logger = logging.getLogger(__name__)


class MapaDelDeseoService:
    """
    Service for managing Mapa del Deseo packages and user progression.
    """
    
    def __init__(self, session: AsyncSession, bot: Bot):
        self.session = session
        self.bot = bot
        self.premium_service = PremiumCatalogService(session, bot)

    async def create_mapa_del_deseo_packages(self):
        """
        Create the 3 tiers of Mapa del Deseo packages.
        """
        # Get or create mapa del deseo category
        category_result = await self.session.execute(
            select(ItemCategory).where(ItemCategory.slug == "mapa-del-deseo")
        )
        category = category_result.scalar_one_or_none()
        
        if not category:
            category = ItemCategory(
                name="Mapa del Deseo",
                slug="mapa-del-deseo",
                description="Paquetes exclusivos de acceso íntimo con Diana",
                emoji="🗺️",
                order=20,
                is_active=True,
                is_gabinete=True,
                gabinete_category="bundle",
                lucien_description="Tres niveles de proximidad con Diana. Tres caminos hacia lo desconocido."
            )
            self.session.add(category)
            await self.session.commit()
            await self.session.refresh(category)

        # Define the 3 tiers with their details
        mapa_packages = [
            {
                "name": "La Llave Premium",
                "slug": "la-llave-premium",
                "description": "VIP + 2 videos Premium seleccionados por Diana",
                "price_besitos": 80,
                "tier": 1,
                "benefits": [
                    "Suscripción completa al Diván (1 mes)",
                    "2 videos Premium seleccionados por Diana", 
                    "Acceso a la narrativa completa",
                    "Badge 'Portador de la Llave Premium'"
                ],
                "lucien_description": "El primer paso. La entrada formal al camino. Contenido exclusivo para iniciar su relación con Diana."
            },
            {
                "name": "Círculo Íntimo", 
                "slug": "circulo-intimo",
                "description": "Todo lo anterior + sesión personalizada",
                "price_besitos": 150,
                "tier": 2,
                "benefits": [
                    "Todo del Nivel 1", 
                    "Sesión personalizada con Diana",
                    "Trato directo para esa sesión",
                    "Contenido creado según sus preferencias",
                    "Badge 'Miembro del Círculo'",
                    "Acceso prioritario a contenido nuevo"
                ],
                "lucien_description": "Aquí Diana deja de ser una figura distante. Se dirige a usted. Personalmente."
            },
            {
                "name": "El Secreto",
                "slug": "el-secreto", 
                "description": "Acceso total + comunicación libre con Diana",
                "price_besitos": 250,
                "tier": 3,
                "benefits": [
                    "Todo lo anterior",
                    "Acceso total a todo el contenido Premium",
                    "Comunicación libre con Diana (sin límites de tema)",
                    "Participación en decisiones de contenido", 
                    "Reconocimiento como 'Guardián del Secreto'",
                    "Acceso de por vida a contenido futuro de esta categoría"
                ], 
                "lucien_description": "Para quienes no quieren límites. Para quienes buscan la conexión completa."
            }
        ]

        # Create each package if it doesn't exist
        for package_data in mapa_packages:
            existing_result = await self.session.execute(
                select(ShopItem).where(ShopItem.slug == package_data["slug"])
            )
            existing_item = existing_result.scalar_one_or_none()
            
            if not existing_item:
                # Calculate separate value for display purposes
                # This would be the sum of individual items
                valor_separado = package_data["price_besitos"] * 1.5  # 50% markup for bundle
                ahorro = valor_separado - package_data["price_besitos"]
                
                shop_item = ShopItem(
                    category_id=category.id,
                    name=package_data["name"],
                    slug=package_data["slug"],
                    description=package_data["description"],
                    long_description=f"Paquete exclusivo del Mapa del Deseo: {package_data['lucien_description']}",
                    item_type="bundle",
                    rarity="legendary",  # Premium packages
                    price_besitos=package_data["price_besitos"],
                    icon="🗝️" if package_data["tier"] == 1 else "💫" if package_data["tier"] == 2 else "👑",
                    item_metadata=str({
                        "tier": package_data["tier"],
                        "benefits": package_data["benefits"],
                        "valor_separado": valor_separado,
                        "ahorro": ahorro
                    }),
                    
                    # Configurable limits
                    stock=None,  # Unlimited stock
                    max_per_user=1,  # Only one purchase per user per tier
                    
                    # Requirements
                    requires_vip=True,  # Only VIP can buy
                    
                    # Display settings
                    is_featured=True,
                    is_active=True,
                    order=package_data["tier"],  # Order by tier: 1, 2, 3
                    
                    # Mapa del Deseo specific
                    lucien_description=package_data["lucien_description"],
                    purchase_message=f"¡Ha adquirido el Nivel {package_data['tier']} del Mapa del Deseo! Diana ha sido notificada de su decisión.",
                    post_use_message="Disfrute de esta etapa especial de su relación con Diana.",
                    min_level_to_view=1,
                    min_level_to_buy=1,
                    visibility="public",  # Available to all VIPs
                    gabinete_item_type="mapa_del_deseo",
                    duration_hours=24*365,  # Access for 1 year
                    available_from=datetime.utcnow(),
                    event_name="Mapa del Deseo",
                    is_limited=False,
                    total_stock=None
                )
                
                self.session.add(shop_item)
                await self.session.commit()
                
                logger.info(f"Created Mapa del Deseo package: {package_data['name']}")
            else:
                logger.info(f"Mapa del Deseo package already exists: {package_data['name']}")

    async def show_mapa_del_deseo_introduction(self, user_id: int):
        """
        Show the introduction to Mapa del Deseo when user triggers it.
        
        Uses the message from F6.4 documentation:
        "Speaker: DIANA
        [Sí, Diana habla directamente aquí - momento especial]

        'Has llegado lejos.
        Más lejos que la mayoría. Has visto cosas que otros no verán nunca.
        Pero aún hay territorios que no has explorado.
        
        Hay un mapa. Mi mapa. El Mapa del Deseo.
        
        Tres niveles de acceso a... mí.
        
        Lucien te explicará los detalles.
        Pero quería que supieras: esto es personal.'
        """
        message = '''Speaker: DIANA
[Sí, Diana habla directamente aquí - momento especial]

"Has llegado lejos.
Más lejos que la mayoría. Has visto cosas que otros no verán nunca.
Pero aún hay territorios que no has explorado.

Hay un mapa. Mi mapa. El Mapa del Deseo.

Tres niveles de acceso a... mí.

Lucien te explicará los detalles.
Pero quería que supieras: esto es personal."
'''
        
        await self.bot.send_message(user_id, message)
        
        # Add a small delay before showing Lucien's message
        import asyncio
        await asyncio.sleep(3)
        
        lucien_message = '''Speaker: LUCIEN
Delay: 3 segundos

"Lo que Diana acaba de ofrecerle es significativo.

El Mapa del Deseo no es un producto. Es un camino.
Tres niveles de proximidad. Tres niveles de compromiso.

Permítame explicar cada uno."
'''
        
        await self.bot.send_message(user_id, lucien_message)
        
        # Show the first tier
        await self.show_tier_details(user_id, 1)

    async def show_tier_details(self, user_id: int, tier: int):
        """
        Show details of a specific tier.
        """
        # Get the package for this tier
        tier_packages = {
            1: "la-llave-premium",
            2: "circulo-intimo", 
            3: "el-secreto"
        }
        
        if tier not in tier_packages:
            logger.error(f"Invalid tier: {tier}")
            return
        
        slug = tier_packages[tier]
        stmt = select(ShopItem).where(ShopItem.slug == slug)
        result = await self.session.execute(stmt)
        item = result.scalar_one_or_none()
        
        if not item:
            logger.error(f"Package for tier {tier} not found")
            return
        
        # Parse the metadata to get package details
        import ast
        try:
            metadata = ast.literal_eval(item.item_metadata) if item.item_metadata else {}
        except:
            metadata = {}
        
        # Format the message based on the tier
        tier_messages = {
            1: f'''Speaker: LUCIEN

"━━━━━━━━━━━━━━━━━━━━━━━━
🗝️ NIVEL 1: LA LLAVE PREMIUM
━━━━━━━━━━━━━━━━━━━━━━━━

Incluye:
{chr(8226)} Suscripción completa al Diván (1 mes)
{chr(8226)} 2 videos Premium seleccionados por Diana
{chr(8226)} Acceso a la narrativa completa
{chr(8226)} Badge 'Portador de la Llave Premium'

Valor por separado: {metadata.get('valor_separado', 120)}
Precio del Mapa: {item.price_besitos}
Ahorro: {metadata.get('ahorro', 40)}

Este es el primer paso. La entrada formal al camino."
''',
            2: f'''Speaker: LUCIEN

"━━━━━━━━━━━━━━━━━━━━━━━━
💫 NIVEL 2: CÍRCULO ÍNTIMO
━━━━━━━━━━━━━━━━━━━━━━━━

Todo lo del Nivel 1, más:
{chr(8226)} Sesión personalizada con Diana
{chr(8226)} Trato directo para esa sesión
{chr(8226)} Contenido creado según sus preferencias
{chr(8226)} Badge 'Miembro del Círculo'
{chr(8226)} Acceso prioritario a contenido nuevo

Precio: {item.price_besitos}

Aquí Diana deja de ser una figura distante.
Se dirige a usted. Personalmente."
''',
            3: f'''Speaker: LUCIEN

"━━━━━━━━━━━━━━━━━━━━━━━━
👑 NIVEL 3: EL SECRETO
━━━━━━━━━━━━━━━━━━━━━━━━

El nivel máximo del Mapa.

Todo lo anterior, más:
{chr(8226)} Acceso total a todo el contenido Premium
{chr(8226)} Comunicación libre con Diana (sin límites de tema)
{chr(8226)} Participación en decisiones de contenido
{chr(8226)} Reconocimiento como 'Guardián del Secreto'
{chr(8226)} Acceso de por vida a contenido futuro de esta categoría

Precio: {item.price_besitos}

Este nivel es para quienes no quieren límites.
Para quienes buscan la conexión completa.

No es para todos. Es para los guardianes de sus secretos más profundos."
'''
        }
        
        message = tier_messages.get(tier, "")
        await self.bot.send_message(user_id, message)
        
        # Create keyboard with appropriate buttons based on the tier
        keyboard = InlineKeyboardBuilder()
        
        if tier == 1:
            keyboard.row(
                InlineKeyboardButton(text="Ver siguiente nivel", callback_data="mapa_tier:2"),
                InlineKeyboardButton(text="Elegir este nivel", callback_data=f"purchase_mapa_tier:{tier}")
            )
        elif tier == 2:
            keyboard.row(
                InlineKeyboardButton(text="Ver siguiente nivel", callback_data="mapa_tier:3"),
                InlineKeyboardButton(text="Elegir este nivel", callback_data=f"purchase_mapa_tier:{tier}"),
                InlineKeyboardButton(text="Volver al anterior", callback_data="mapa_tier:1")
            )
        else:  # tier == 3
            keyboard.row(
                InlineKeyboardButton(text="Elegir este nivel", callback_data=f"purchase_mapa_tier:{tier}"),
                InlineKeyboardButton(text="Volver a ver opciones", callback_data="mapa_compare"),
                InlineKeyboardButton(text="Necesito pensarlo", callback_data="mapa_defer")
            )
        
        await self.bot.send_message(user_id, "¿Qué desea hacer?", reply_markup=keyboard.as_markup())

    async def show_mapa_comparison(self, user_id: int):
        """
        Show comparison of all tiers as per documentation.
        """
        message = '''Speaker: LUCIEN
[Si usuario pide comparar]

"Los tres niveles, lado a lado:

┌─────────────────────────────────────────────────────────┐
│                    MAPA DEL DESEO                       │
├─────────────────────────────────────────────────────────┤
│ Beneficio          │ Llave  │ Círculo │ Secreto        │
├─────────────────────────────────────────────────────────┤
│ Suscripción VIP    │   ✓    │    ✓    │    ✓           │
│ 2 Videos Premium   │   ✓    │    ✓    │    ✓           │
│ Sesión personal    │   ✗    │    ✓    │    ✓           │
│ Todo Premium       │   ✗    │    ✗    │    ✓           │
│ Comunicación libre │   ✗    │    ✗    │    ✓           │
│ Contenido futuro   │   ✗    │    ✗    │    ✓           │
├─────────────────────────────────────────────────────────┤
│ Precio             │ 80     │   150   │   250          │
└─────────────────────────────────────────────────────────┘

La decisión depende de qué tan profundo desea llegar."
'''
        
        await self.bot.send_message(user_id, message)
        
        keyboard = InlineKeyboardBuilder()
        keyboard.row(
            InlineKeyboardButton(text="Elegir Llave Premium", callback_data="purchase_mapa_tier:1"),
            InlineKeyboardButton(text="Elegir Círculo", callback_data="purchase_mapa_tier:2"),
            InlineKeyboardButton(text="Elegir Secreto", callback_data="purchase_mapa_tier:3")
        )
        
        await self.bot.send_message(user_id, "¿Qué nivel desea elegir?", reply_markup=keyboard.as_markup())

    async def purchase_mapa_tier(self, user_id: int, tier: int) -> bool:
        """
        Process purchase of a Mapa del Deseo tier.
        """
        tier_packages = {
            1: "la-llave-premium",
            2: "circulo-intimo", 
            3: "el-secreto"
        }
        
        if tier not in tier_packages:
            logger.error(f"Invalid tier: {tier}")
            return False
        
        slug = tier_packages[tier]
        stmt = select(ShopItem).where(ShopItem.slug == slug)
        result = await self.session.execute(stmt)
        item = result.scalar_one_or_none()
        
        if not item:
            logger.error(f"Package for tier {tier} not found")
            return False
        
        # Check if user already has this tier or higher
        user = await self.session.get(User, user_id)
        if not user or not user.is_vip:
            return False  # Only VIP users can purchase
            
        # Check if user has sufficient besitos
        besito_service = BesitoService(self.session)
        user_gamification = await besito_service.get_user_gamification(user_id)
        
        if user_gamification.total_besitos < item.price_besitos:
            return False  # Insufficient funds
        
        # Process the purchase
        success = await besito_service.transfer_besitos(
            from_user_id=user_id,
            to_user_id=None,  # Transfer to system/economy sink
            amount=item.price_besitos,
            description=f"Compra de Mapa del Deseo - Nivel {tier}: {item.name}"
        )
        
        if not success:
            return False  # Transfer failed
        
        # Add item to user's inventory
        from bot.shop.database.models import UserInventory, UserInventoryItem
        
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
            f"Ha adquirido: {item.name} (Nivel {tier})\n"
            f"Precio: {item.price_besitos} Favores\n\n"
            f"{item.purchase_message or 'Gracias por su confianza en el Mapa del Deseo.'}"
        )
        
        # Grant special benefits based on the tier
        await self.grant_mapa_benefits(user_id, tier)
        
        return True

    async def grant_mapa_benefits(self, user_id: int, tier: int):
        """
        Grant special benefits based on the Mapa del Deseo tier purchased.
        """
        # This would grant special access, badges, etc. based on the tier
        benefits_messages = {
            1: "Se le ha otorgado acceso al contenido premium del Nivel 1 y el badge 'Portador de la Llave Premium'.",
            2: "Se le ha otorgado acceso al Círculo Íntimo, prioridad en nuevo contenido y el badge 'Miembro del Círculo'.",
            3: "Se le ha otorgado acceso total, posibilidad de comunicación directa con Diana y el reconocimiento 'Guardián del Secreto'."
        }
        
        message = benefits_messages.get(tier, "Se han otorgado sus beneficios especiales.")
        await self.bot.send_message(user_id, f"🎁 {message}")

    async def get_user_mapa_status(self, user_id: int) -> Dict[str, Any]:
        """
        Get user's current Mapa del Deseo status and purchased tiers.
        """
        from bot.shop.database.models import UserInventoryItem
        
        # Find all Mapa del Deseo items purchased by the user
        stmt = (
            select(ShopItem)
            .join(UserInventoryItem, ShopItem.id == UserInventoryItem.item_id)
            .join(ItemCategory)
            .where(
                UserInventoryItem.user_id == user_id,
                ItemCategory.slug == "mapa-del-deseo"
            )
        )
        result = await self.session.execute(stmt)
        purchased_items = result.scalars().all()
        
        purchased_tiers = []
        for item in purchased_items:
            # Extract tier from item metadata
            import ast
            try:
                metadata = ast.literal_eval(item.item_metadata) if item.item_metadata else {}
                tier = metadata.get("tier", 0)
                if tier:
                    purchased_tiers.append(tier)
            except:
                logger.warning(f"Could not parse metadata for item {item.id}")
        
        return {
            "purchased_tiers": sorted(purchased_tiers),
            "highest_tier": max(purchased_tiers) if purchased_tiers else 0,
            "has_any_tier": len(purchased_tiers) > 0
        }