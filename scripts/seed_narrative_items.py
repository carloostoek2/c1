"""
Script para poblar la tienda con items narrativos de ONDA C.

Crea 21 items narrativos organizados en 4 categorías:
- Efímeros (5 items): Consumibles temporales
- Distintivos (6 items): Badges permanentes por nivel
- Llaves (5 items): Desbloqueos de contenido narrativo
- Reliquias (5 items): Items raros y ultra-exclusivos
"""
import asyncio
import logging
from datetime import datetime, UTC

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from bot.shop.database.models import ItemCategory, ShopItem
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Datos de categorías
CATEGORIES = [
    {
        "name": "Efímeros",
        "slug": "efimeros",
        "description": "Experiencias temporales y contenido exclusivo de duración limitada.",
        "emoji": "⏳",
        "order": 1,
    },
    {
        "name": "Distintivos",
        "slug": "distintivos",
        "description": "Badges permanentes que marcan tu progreso y dedicación.",
        "emoji": "🎖️",
        "order": 2,
    },
    {
        "name": "Llaves",
        "slug": "llaves",
        "description": "Desbloqueos narrativos que revelan historias ocultas de Diana.",
        "emoji": "🔑",
        "order": 3,
    },
    {
        "name": "Reliquias",
        "slug": "reliquias",
        "description": "Items ultra-exclusivos y raros con contenido especial.",
        "emoji": "💎",
        "order": 4,
    },
]


# Datos de items
NARRATIVE_ITEMS = [
    # ========================================
    # EFÍMEROS (Consumibles)
    # ========================================
    {
        "category_slug": "efimeros",
        "name": "Sello del Día",
        "slug": "sello-del-dia",
        "description": "Marca especial en tu perfil visible por 24 horas.",
        "long_description": "Un sello distintivo que Diana colocará en tu perfil, visible para todos durante 24 horas. Una pequeña muestra de tu dedicación.",
        "item_type": "consumable",
        "rarity": "common",
        "price": 1,
        "icon": "🏷️",
        "max_per_user": None,
        "requires_vip": False,
        "is_featured": False,
    },
    {
        "category_slug": "efimeros",
        "name": "Susurro Efímero",
        "slug": "susurro-efimero",
        "description": "Audio exclusivo de 15 segundos de Diana, solo para ti.",
        "long_description": "Diana te enviará un mensaje de audio personal de 15 segundos. Un momento íntimo que desaparecerá después de escucharlo 3 veces.",
        "item_type": "consumable",
        "rarity": "uncommon",
        "price": 3,
        "icon": "🎧",
        "max_per_user": 5,
        "requires_vip": False,
        "is_featured": True,
    },
    {
        "category_slug": "efimeros",
        "name": "Pase de Prioridad",
        "slug": "pase-prioridad",
        "description": "Acceso anticipado al próximo contenido narrativo.",
        "long_description": "Salta la cola. Cuando Diana publique nuevo contenido, serás de los primeros en experimentarlo, 24 horas antes que el resto.",
        "item_type": "consumable",
        "rarity": "rare",
        "price": 5,
        "icon": "⚡",
        "max_per_user": 3,
        "requires_vip": False,
        "is_featured": True,
    },
    {
        "category_slug": "efimeros",
        "name": "Vistazo al Sensorium",
        "slug": "vistazo-sensorium",
        "description": "Preview exclusivo de 30 segundos del contenido Premium.",
        "long_description": "Diana abrirá las puertas del Sensorium por 30 segundos. Un adelanto tentador de lo que espera a quienes se atrevan a más.",
        "item_type": "consumable",
        "rarity": "epic",
        "price": 15,
        "icon": "👁️",
        "max_per_user": 2,
        "requires_vip": False,
        "is_featured": True,
    },
    {
        "category_slug": "efimeros",
        "name": "Confesión Nocturna",
        "slug": "confesion-nocturna",
        "description": "Texto exclusivo de Diana revelando un secreto personal.",
        "long_description": "A medianoche, Diana te enviará una confesión. Algo que no comparte con nadie más. Lee con atención.",
        "item_type": "consumable",
        "rarity": "rare",
        "price": 8,
        "icon": "🌙",
        "max_per_user": 10,
        "requires_vip": False,
        "is_featured": False,
    },

    # ========================================
    # DISTINTIVOS (Permanentes por Nivel)
    # ========================================
    {
        "category_slug": "distintivos",
        "name": "Sello del Visitante",
        "slug": "sello-visitante",
        "description": "Badge permanente: Has dado el primer paso.",
        "long_description": "El primer sello de tu colección. Diana reconoce que has cruzado el umbral. Permanente en tu perfil.",
        "item_type": "cosmetic",
        "rarity": "common",
        "price": 2,
        "icon": "🔰",
        "max_per_user": 1,
        "requires_vip": False,
        "is_featured": False,
    },
    {
        "category_slug": "distintivos",
        "name": "Marca del Curioso",
        "slug": "marca-curioso",
        "description": "Badge permanente (Nivel 2): Tu curiosidad ha sido notada.",
        "long_description": "Diana marca a quienes buscan. Este badge prueba que no te conformas con lo superficial.",
        "item_type": "cosmetic",
        "rarity": "uncommon",
        "price": 5,
        "icon": "🔍",
        "max_per_user": 1,
        "requires_vip": False,
        "is_featured": False,
    },
    {
        "category_slug": "distintivos",
        "name": "Emblema del Iniciado",
        "slug": "emblema-iniciado",
        "description": "Badge permanente (Nivel 3): Has sido iniciado en los misterios.",
        "long_description": "Solo quienes alcanzan el Nivel 3 pueden portar este emblema. Diana te considera digno de sus secretos.",
        "item_type": "cosmetic",
        "rarity": "rare",
        "price": 10,
        "icon": "⚜️",
        "max_per_user": 1,
        "requires_vip": False,
        "is_featured": True,
    },
    {
        "category_slug": "distintivos",
        "name": "Sigilo del Confidente",
        "slug": "sigilo-confidente",
        "description": "Badge permanente (Nivel 4): Diana confía en ti.",
        "long_description": "Nivel 4. Pocos llegan aquí. Este sigilo indica que Diana te ha confiado cosas que no comparte con nadie más.",
        "item_type": "cosmetic",
        "rarity": "epic",
        "price": 20,
        "icon": "🤫",
        "max_per_user": 1,
        "requires_vip": True,
        "is_featured": True,
    },
    {
        "category_slug": "distintivos",
        "name": "Insignia del Devoto",
        "slug": "insignia-devoto",
        "description": "Badge permanente (Nivel 5): Tu dedicación es inquebrantable.",
        "long_description": "Nivel 5. Elite. Esta insignia se otorga solo a quienes demuestran devoción genuina al universo de Diana.",
        "item_type": "cosmetic",
        "rarity": "legendary",
        "price": 35,
        "icon": "👑",
        "max_per_user": 1,
        "requires_vip": True,
        "is_featured": True,
    },
    {
        "category_slug": "distintivos",
        "name": "Corona del Guardián",
        "slug": "corona-guardian",
        "description": "Badge permanente (Nivel 6+): Eres guardián de los secretos.",
        "long_description": "Nivel 6+. El nivel más alto. Esta corona te marca como guardián de los secretos más profundos de Diana. Respeto máximo.",
        "item_type": "cosmetic",
        "rarity": "legendary",
        "price": 50,
        "icon": "👸",
        "max_per_user": 1,
        "requires_vip": True,
        "is_featured": True,
    },

    # ========================================
    # LLAVES (Desbloqueos Narrativos)
    # ========================================
    {
        "category_slug": "llaves",
        "name": "Fragmento I",
        "slug": "fragmento-i",
        "description": "Primera parte de la historia oculta de Diana.",
        "long_description": "El primer fragmento de una historia que Diana nunca contó. Desbloquea el capítulo oculto: 'Antes del Diván'.",
        "item_type": "narrative",
        "rarity": "uncommon",
        "price": 10,
        "icon": "📜",
        "max_per_user": 1,
        "requires_vip": False,
        "is_featured": True,
    },
    {
        "category_slug": "llaves",
        "name": "Fragmento II",
        "slug": "fragmento-ii",
        "description": "Segunda parte de la historia oculta.",
        "long_description": "Continuación del Fragmento I. La historia se vuelve más oscura. Desbloquea: 'El Primer Paciente'.",
        "item_type": "narrative",
        "rarity": "rare",
        "price": 12,
        "icon": "📜",
        "max_per_user": 1,
        "requires_vip": False,
        "is_featured": True,
    },
    {
        "category_slug": "llaves",
        "name": "Fragmento III",
        "slug": "fragmento-iii",
        "description": "Última parte de la historia oculta.",
        "long_description": "El desenlace. Todo tiene sentido ahora. Desbloquea: 'La Verdad Sobre Lucien'.",
        "item_type": "narrative",
        "rarity": "epic",
        "price": 15,
        "icon": "📜",
        "max_per_user": 1,
        "requires_vip": True,
        "is_featured": True,
    },
    {
        "category_slug": "llaves",
        "name": "Archivo Oculto",
        "slug": "archivo-oculto",
        "description": "Expediente personal con anotaciones de Lucien.",
        "long_description": "Un archivo que Lucien guardó celosamente. Contiene notas, observaciones y... algo inquietante sobre ti.",
        "item_type": "narrative",
        "rarity": "epic",
        "price": 20,
        "icon": "📁",
        "max_per_user": 1,
        "requires_vip": True,
        "is_featured": True,
    },
    {
        "category_slug": "llaves",
        "name": "Llave de la Primera Vez",
        "slug": "llave-primera-vez",
        "description": "Desbloquea el origen: El primer día de Diana.",
        "long_description": "Diana nunca habló del día en que todo empezó. Con esta llave, lo descubrirás. Advertencia: No hay vuelta atrás.",
        "item_type": "narrative",
        "rarity": "legendary",
        "price": 18,
        "icon": "🔓",
        "max_per_user": 1,
        "requires_vip": True,
        "is_featured": True,
    },

    # ========================================
    # RELIQUIAS (Raras y Ultra-Exclusivas)
    # ========================================
    {
        "category_slug": "reliquias",
        "name": "El Primer Secreto",
        "slug": "primer-secreto",
        "description": "Contenido ultra-exclusivo que Diana nunca publicó.",
        "long_description": "Diana grabó esto y nunca lo publicó. Demasiado íntimo, demasiado real. Solo para quienes demuestren devoción.",
        "item_type": "digital",
        "rarity": "legendary",
        "price": 30,
        "icon": "💌",
        "max_per_user": 1,
        "requires_vip": True,
        "is_featured": True,
    },
    {
        "category_slug": "reliquias",
        "name": "Fragmento del Espejo",
        "slug": "fragmento-espejo",
        "description": "Behind-the-scenes: Cómo Diana crea su contenido.",
        "long_description": "Una mirada al proceso creativo de Diana. Verás cómo piensa, cómo crea, cómo decide qué compartir y qué ocultar.",
        "item_type": "digital",
        "rarity": "epic",
        "price": 40,
        "icon": "🪞",
        "max_per_user": 1,
        "requires_vip": True,
        "is_featured": True,
    },
    {
        "category_slug": "reliquias",
        "name": "La Carta No Enviada",
        "slug": "carta-no-enviada",
        "description": "Carta íntima que Diana escribió pero nunca envió.",
        "long_description": "Diana escribió esta carta para alguien especial. Nunca la envió. Ahora, por alguna razón, ha decidido que tú puedes leerla.",
        "item_type": "narrative",
        "rarity": "legendary",
        "price": 50,
        "icon": "✉️",
        "max_per_user": 1,
        "requires_vip": True,
        "is_featured": True,
    },
    {
        "category_slug": "reliquias",
        "name": "Cristal de Medianoche",
        "slug": "cristal-medianoche",
        "description": "Micro-contenido diario enviado a medianoche durante 7 días.",
        "long_description": "Durante 7 días consecutivos, Diana te enviará algo a medianoche. Puede ser texto, audio, imagen. Siempre diferente. Siempre personal.",
        "item_type": "consumable",
        "rarity": "legendary",
        "price": 45,
        "icon": "🔮",
        "max_per_user": 3,
        "requires_vip": True,
        "is_featured": True,
    },
    {
        "category_slug": "reliquias",
        "name": "Llave Maestra",
        "slug": "llave-maestra",
        "description": "Desbloquea TODO el contenido del Gabinete permanentemente.",
        "long_description": "La Llave Maestra. Desbloquea todos los fragmentos, archivos, reliquias y secretos del Gabinete. Todo. Sin excepciones. Para siempre.",
        "item_type": "narrative",
        "rarity": "legendary",
        "price": 75,
        "icon": "🗝️",
        "max_per_user": 1,
        "requires_vip": True,
        "is_featured": True,
    },
]


async def seed_narrative_items():
    """Poblar la tienda con items narrativos."""
    # Crear engine
    engine = create_async_engine(
        Config.DATABASE_URL,
        echo=False
    )

    # Crear sesión
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        try:
            logger.info("🌱 Iniciando seed de items narrativos...")

            # 1. Crear categorías
            logger.info("📁 Creando categorías...")
            category_map = {}

            for cat_data in CATEGORIES:
                category = ItemCategory(
                    name=cat_data["name"],
                    slug=cat_data["slug"],
                    description=cat_data["description"],
                    emoji=cat_data["emoji"],
                    order=cat_data["order"],
                    is_active=True,
                )
                session.add(category)
                category_map[cat_data["slug"]] = category

                logger.info(f"  ✅ {cat_data['emoji']} {cat_data['name']}")

            await session.flush()  # Para obtener IDs

            # 2. Crear items
            logger.info("\n🎁 Creando items narrativos...")
            items_created = 0

            for item_data in NARRATIVE_ITEMS:
                category = category_map[item_data["category_slug"]]

                shop_item = ShopItem(
                    category_id=category.id,
                    name=item_data["name"],
                    slug=item_data["slug"],
                    description=item_data["description"],
                    long_description=item_data["long_description"],
                    item_type=item_data["item_type"],
                    rarity=item_data["rarity"],
                    price_besitos=item_data["price"],
                    icon=item_data["icon"],
                    max_per_user=item_data["max_per_user"],
                    requires_vip=item_data["requires_vip"],
                    is_featured=item_data["is_featured"],
                    is_active=True,
                    order=items_created,
                    created_by=1,  # System
                )
                session.add(shop_item)
                items_created += 1

                vip_mark = " [VIP]" if item_data["requires_vip"] else ""
                logger.info(
                    f"  {item_data['icon']} {item_data['name']} "
                    f"({item_data['price']} Favores){vip_mark}"
                )

            # Commit todo
            await session.commit()

            logger.info(f"\n✅ Seed completado exitosamente!")
            logger.info(f"   Categorías creadas: {len(CATEGORIES)}")
            logger.info(f"   Items creados: {items_created}")

        except Exception as e:
            logger.error(f"❌ Error durante seed: {e}", exc_info=True)
            await session.rollback()
            raise

        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_narrative_items())
