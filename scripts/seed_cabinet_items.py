#!/usr/bin/env python3
"""
Script para poblar el inventario del Gabinete con los items iniciales.

Basado en las especificaciones de FASE 0 - F0.4: INVENTARIO INICIAL DEL GABINETE

Categorías:
- Efímeros (ephemeral): 4 items
- Distintivos (distinctive): 5 items
- Llaves (keys): 4 items
- Reliquias (relics): 3 items

Total: 16 items iniciales
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, UTC
from sqlalchemy import select
from bot.database import get_session, init_db, close_db
from bot.shop.database.models import ItemCategory, ShopItem


# ============================================================
# DATOS DE LAS CATEGORÍAS DEL GABINETE
# ============================================================

CABINET_CATEGORIES = [
    {
        "name": "Efímeros",
        "slug": "efimeros",
        "gabinete_category": "ephemeral",
        "description": "Placeres de un solo uso. Intensos pero fugaces.",
        "lucien_description": (
            "Placeres de un solo uso. Intensos pero fugaces. "
            "Como los momentos que Diana prefiere olvidar."
        ),
        "emoji": "✨",
        "order": 1,
        "min_level_to_view": 1,
        "min_level_to_buy": 1,
    },
    {
        "name": "Distintivos",
        "slug": "distintivos",
        "gabinete_category": "distinctive",
        "description": "Marcas visibles de su posición. Para quienes valoran el reconocimiento.",
        "lucien_description": (
            "Marcas visibles de su posición. Para quienes valoran el reconocimiento. "
            "Diana observa quienes llevan estas marcas."
        ),
        "emoji": "🏅",
        "order": 2,
        "min_level_to_view": 1,
        "min_level_to_buy": 1,
    },
    {
        "name": "Llaves",
        "slug": "llaves",
        "gabinete_category": "keys",
        "description": "Abren puertas a contenido que otros no pueden ver.",
        "lucien_description": (
            "Abren puertas a contenido que otros no pueden ver. "
            "Cada llave revela un secreto que Diana guarda celosamente."
        ),
        "emoji": "🔑",
        "order": 3,
        "min_level_to_view": 2,
        "min_level_to_buy": 2,
    },
    {
        "name": "Reliquias",
        "slug": "reliquias",
        "gabinete_category": "relics",
        "description": "Los objetos más valiosos del Gabinete. Requieren Favores... y dignidad.",
        "lucien_description": (
            "Los objetos más valiosos del Gabinete. Requieren Favores... y dignidad. "
            "Solo aquellos en el círculo íntimo pueden posesionarse de estas rarezas."
        ),
        "emoji": "💎",
        "order": 4,
        "min_level_to_view": 4,
        "min_level_to_buy": 4,
    },
]


# ============================================================
# DATOS DE LOS ITEMS DEL GABINETE
# ============================================================

CABINET_ITEMS = [
    # ============================================================
    # CATEGORÍA: EFÍMEROS (ephemeral)
    # ============================================================
    {
        "slug": "sello-del-dia",
        "name": "Sello del Día",
        "category_slug": "efimeros",
        "description": "Una marca temporal. Válida hasta medianoche.",
        "lucien_description": (
            "Un sello efímero que marca su presencia por un día. "
            "Cuando el reloj marque las doce, desaparecerá. Como todos los momentos."
        ),
        "price": 1,
        "icon": "🔖",
        "item_type": "consumable",
        "rarity": "common",
        "gabinete_item_type": "badge_temporary",
        "duration_hours": 24,
        "stock": None,  # Ilimitado
        "is_limited": False,
        "max_per_user": None,
        "min_level_to_view": 1,
        "min_level_to_buy": 1,
        "visibility": "public",
        "order": 1,
    },
    {
        "slug": "susurro-efimero",
        "name": "Susurro Efímero",
        "category_slug": "efimeros",
        "description": "Un mensaje que Diana grabó en un momento de... inspiración.",
        "lucien_description": (
            "Un audio de 15 segundos que Diana grabó en un momento de... "
            "inspiración. No estoy seguro de qué era exactamente, "
            "pero su voz contiene algo que prefiero no analizar."
        ),
        "price": 3,
        "icon": "🎤",
        "item_type": "digital",
        "rarity": "uncommon",
        "gabinete_item_type": "audio_exclusive",
        "duration_hours": None,  # Permanente
        "stock": None,
        "is_limited": False,
        "max_per_user": 3,
        "min_level_to_view": 1,
        "min_level_to_buy": 1,
        "visibility": "public",
        "order": 2,
    },
    {
        "slug": "pase-prioridad",
        "name": "Pase de Prioridad",
        "category_slug": "efimeros",
        "description": "Cuando Diana abra contenido limitado, usted estará primero.",
        "lucien_description": (
            "Un pase que lo coloca al frente de la fila. "
            "Cuando Diana decida liberar contenido limitado, "
            "usted será de los primeros en saberlo. "
            "La anticipación tiene sus ventajas."
        ),
        "price": 5,
        "icon": "🎫",
        "item_type": "consumable",
        "rarity": "rare",
        "gabinete_item_type": "priority_flag",
        "duration_hours": None,  # Permanente hasta uso
        "stock": 50,
        "is_limited": True,
        "total_stock": 50,
        "max_per_user": 1,
        "min_level_to_view": 1,
        "min_level_to_buy": 1,
        "visibility": "public",
        "order": 3,
    },
    {
        "slug": "vistazo-sensorium",
        "name": "Vistazo al Sensorium",
        "category_slug": "efimeros",
        "description": "Una muestra del contenido Sensorium. Treinta segundos que alterarán sus sentidos.",
        "lucien_description": (
            "Treinta segundos del contenido Sensorium. "
            "He visto efectos en quienes lo experimentan. "
            "No voy a detallarlos, pero digamos que... "
            "alteran la percepción de forma permanente. "
            "Solo ligeramente. Espero."
        ),
        "price": 15,
        "icon": "👁️",
        "item_type": "narrative",
        "rarity": "epic",
        "gabinete_item_type": "content_preview",
        "duration_hours": None,
        "stock": None,
        "is_limited": False,
        "max_per_user": 1,
        "min_level_to_view": 2,
        "min_level_to_buy": 2,
        "visibility": "public",
        "requires_vip": False,
        "order": 4,
    },

    # ============================================================
    # CATEGORÍA: DISTINTIVOS (distinctive)
    # ============================================================
    {
        "slug": "sello-visitante",
        "name": "Sello del Visitante",
        "category_slug": "distintivos",
        "description": "La marca más básica. Indica que existe en este universo.",
        "lucien_description": (
            "La marca más básica. Indica que existe en este universo. "
            "No es mucho, pero es un comienzo. "
            "Todos empezamos somewhere."
        ),
        "price": 2,
        "icon": "🏷️",
        "item_type": "cosmetic",
        "rarity": "common",
        "gabinete_item_type": "badge_permanent",
        "duration_hours": None,
        "stock": None,
        "is_limited": False,
        "max_per_user": 1,
        "min_level_to_view": 1,
        "min_level_to_buy": 1,
        "visibility": "public",
        "order": 1,
    },
    {
        "slug": "insignia-observador",
        "name": "Insignia del Observador",
        "category_slug": "distintivos",
        "description": "Lucien lo ha notado. Eso significa algo... o nada.",
        "lucien_description": (
            "Lucien lo ha notado. Eso significa algo... o nada. "
            "Yo noto a todos. Pero no a todos les otorgo una insignia. "
            "Considérelo un reconocimiento... condicional."
        ),
        "price": 5,
        "icon": "👁️‍🗨️",
        "item_type": "cosmetic",
        "rarity": "uncommon",
        "gabinete_item_type": "badge_permanent",
        "duration_hours": None,
        "stock": None,
        "is_limited": False,
        "max_per_user": 1,
        "min_level_to_view": 2,
        "min_level_to_buy": 2,
        "visibility": "public",
        "order": 2,
    },
    {
        "slug": "marca-evaluado",
        "name": "Marca del Evaluado",
        "category_slug": "distintivos",
        "description": "Ha pasado las primeras pruebas. No todas, pero algunas.",
        "lucien_description": (
            "Ha pasado las primeras pruebas. No todas, pero algunas. "
            "Diana evalúa constantemente. Esta marca indica "
            "que ha sobrevivido al primer filtro. "
            "El segundo es... menos indulgente."
        ),
        "price": 8,
        "icon": "✅",
        "item_type": "cosmetic",
        "rarity": "rare",
        "gabinete_item_type": "badge_permanent",
        "duration_hours": None,
        "stock": None,
        "is_limited": False,
        "max_per_user": 1,
        "min_level_to_view": 3,
        "min_level_to_buy": 3,
        "visibility": "public",
        "order": 3,
    },
    {
        "slug": "emblema-reconocido",
        "name": "Emblema del Reconocido",
        "category_slug": "distintivos",
        "description": "Diana sabe su nombre. No es poco.",
        "lucien_description": (
            "Diana sabe su nombre. No es poco. "
            "En este universo, ser conocido por ella es un privilegio "
            "que pocos pueden reclamar. Este emblema lo prueba."
        ),
        "price": 12,
        "icon": "⭐",
        "item_type": "cosmetic",
        "rarity": "epic",
        "gabinete_item_type": "badge_permanent",
        "duration_hours": None,
        "stock": None,
        "is_limited": False,
        "max_per_user": 1,
        "min_level_to_view": 4,
        "min_level_to_buy": 4,
        "visibility": "confidants",
        "requires_vip": True,
        "order": 4,
    },
    {
        "slug": "marca-confidente",
        "name": "Marca del Confidente",
        "category_slug": "distintivos",
        "description": "Pocos llevan esta marca. Indica que Lucien confía en usted. Relativamente.",
        "lucien_description": (
            "Pocos llevan esta marca. Indica que Lucien confía en usted. "
            "Relativamente. Mi confianza es... matizada. "
            "Pero esta marca es lo más cercano a una aprobación "
            "que algún usuario recibirá de mí."
        ),
        "price": 25,
        "icon": "👑",
        "item_type": "cosmetic",
        "rarity": "legendary",
        "gabinete_item_type": "badge_permanent",
        "duration_hours": None,
        "stock": None,
        "is_limited": False,
        "max_per_user": 1,
        "min_level_to_view": 5,
        "min_level_to_buy": 5,
        "visibility": "confidants",
        "requires_vip": True,
        "order": 5,
    },

    # ============================================================
    # CATEGORÍA: LLAVES (keys)
    # ============================================================
    {
        "slug": "llave-fragmento-i",
        "name": "Llave del Fragmento I",
        "category_slug": "llaves",
        "description": "Abre el primer secreto oculto. Lo que Diana no cuenta en público.",
        "lucien_description": (
            "Abre el primer secreto oculto. Lo que Diana no cuenta en público. "
            "Todos tienen secretos. Diana solo tiene... "
            "aquellos que prefieren no mencionarse en compañía."
        ),
        "price": 10,
        "icon": "🗝️",
        "item_type": "narrative",
        "rarity": "rare",
        "gabinete_item_type": "content_unlock",
        "duration_hours": None,
        "stock": None,
        "is_limited": False,
        "max_per_user": 1,
        "min_level_to_view": 2,
        "min_level_to_buy": 2,
        "visibility": "public",
        "order": 1,
    },
    {
        "slug": "llave-fragmento-ii",
        "name": "Llave del Fragmento II",
        "category_slug": "llaves",
        "description": "El segundo secreto. Más profundo que el primero.",
        "lucien_description": (
            "El segundo secreto. Más profundo que el primero. "
            "Aquellos que adquieren esta llave suelen... "
            "reaccionar de forma inesperada. "
            "No puedo predecir cómo reaccionará usted."
        ),
        "price": 12,
        "icon": "🗝️",
        "item_type": "narrative",
        "rarity": "rare",
        "gabinete_item_type": "content_unlock",
        "duration_hours": None,
        "stock": None,
        "is_limited": False,
        "max_per_user": 1,
        "min_level_to_view": 2,
        "min_level_to_buy": 2,
        "visibility": "public",
        "order": 2,
    },
    {
        "slug": "llave-fragmento-iii",
        "name": "Llave del Fragmento III",
        "category_slug": "llaves",
        "description": "El tercer secreto. Aquí las cosas se ponen... interesantes.",
        "lucien_description": (
            "El tercer secreto. Aquí las cosas se ponen... interesantes. "
            '"Interesante" es mi eufemismo para '
            '"aquello que desafía explicación racional". '
            "Proceda bajo su propia responsabilidad."
        ),
        "price": 15,
        "icon": "🗝️",
        "item_type": "narrative",
        "rarity": "epic",
        "gabinete_item_type": "content_unlock",
        "duration_hours": None,
        "stock": None,
        "is_limited": False,
        "max_per_user": 1,
        "min_level_to_view": 3,
        "min_level_to_buy": 3,
        "visibility": "confidants",
        "requires_vip": True,
        "order": 3,
    },
    {
        "slug": "llave-archivo-oculto",
        "name": "Llave del Archivo Oculto",
        "category_slug": "llaves",
        "description": "Acceso a memorias que Diana preferiría olvidar. O quizás no.",
        "lucien_description": (
            "Acceso a memorias que Diana preferiría olvidar. O quizás no. "
            "El archivo contiene fragmentos que no fueron "
            "destinados al consumo público. "
            "Usted ha sido advertido."
        ),
        "price": 20,
        "icon": "🗝️",
        "item_type": "narrative",
        "rarity": "epic",
        "gabinete_item_type": "content_unlock_set",
        "duration_hours": None,
        "stock": None,
        "is_limited": False,
        "max_per_user": 1,
        "min_level_to_view": 4,
        "min_level_to_buy": 4,
        "visibility": "confidants",
        "requires_vip": True,
        "order": 4,
    },

    # ============================================================
    # CATEGORÍA: RELIQUIAS (relics)
    # ============================================================
    {
        "slug": "primer-secreto",
        "name": "El Primer Secreto",
        "category_slug": "reliquias",
        "description": "Un objeto que representa el primer secreto que Diana compartió conmigo.",
        "lucien_description": (
            "Un objeto que representa el primer secreto que Diana "
            "compartió conmigo. Ahora puede ser suyo. "
            "No voy a describirlo. Su valor es precisamente "
            "en lo que representa... no en lo que es."
        ),
        "price": 30,
        "icon": "🏺",
        "item_type": "collectible",
        "rarity": "legendary",
        "gabinete_item_type": "relic_unique",
        "duration_hours": None,
        "stock": 1,
        "is_limited": True,
        "total_stock": 1,
        "max_per_user": 1,
        "min_level_to_view": 4,
        "min_level_to_buy": 4,
        "visibility": "guardians",
        "requires_vip": True,
        "order": 1,
    },
    {
        "slug": "fragmento-espejo",
        "name": "Fragmento del Espejo",
        "category_slug": "reliquias",
        "description": "Un pedazo del espejo donde Diana se mira antes de cada sesión. Metafóricamente, claro.",
        "lucien_description": (
            "Un pedazo del espejo donde Diana se mira antes de cada sesión. "
            "Metafóricamente, claro. No esperaba que "
            "creyera que tengo fragmentos literales de espejo "
            "esparcidos por el Gabinete. O tal vez sí."
        ),
        "price": 40,
        "icon": "🪞",
        "item_type": "collectible",
        "rarity": "legendary",
        "gabinete_item_type": "relic_collectible",
        "duration_hours": None,
        "stock": 3,
        "is_limited": True,
        "total_stock": 3,
        "max_per_user": 1,
        "min_level_to_view": 5,
        "min_level_to_buy": 5,
        "visibility": "guardians",
        "requires_vip": True,
        "order": 2,
    },
    {
        "slug": "carta-no-enviada",
        "name": "La Carta No Enviada",
        "category_slug": "reliquias",
        "description": "Diana escribió esto hace tiempo. Nunca lo envió. Ahora usted puede leerlo.",
        "lucien_description": (
            "Diana escribió esto hace tiempo. Nunca lo envió. "
            "Ahora usted puede leerlo. Contiene palabras "
            "que probablemente deberían haber permanecido "
            "en el cajón de los 'nunca para ser leídos'. "
            "Pero la curiosidad... vence a la discreción."
        ),
        "price": 50,
        "icon": "📜",
        "item_type": "narrative",
        "rarity": "legendary",
        "gabinete_item_type": "relic_narrative",
        "duration_hours": None,
        "stock": 1,
        "is_limited": True,
        "total_stock": 1,
        "max_per_user": 1,
        "min_level_to_view": 6,
        "min_level_to_buy": 6,
        "visibility": "guardians",
        "requires_vip": True,
        "order": 3,
    },
]


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

async def seed_cabinet_items():
    """Puebla el inventario del Gabinete con los items iniciales."""

    print("🗝️ Poblando el Gabinete de Lucien...")
    print("=" * 60)

    # Inicializar BD
    print("\n🔧 Inicializando base de datos...")
    await init_db()
    print("✅ Base de datos inicializada")

    async with get_session() as session:
        # Crear categorías
        print("\n📁 Creando categorías...")
        category_map = {}

        for cat_data in CABINET_CATEGORIES:
            # Verificar si ya existe
            result = await session.execute(
                select(ItemCategory).where(ItemCategory.slug == cat_data["slug"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                print(f"  ⏭️  Categoría ya existe: {cat_data['name']}")
                category_map[cat_data["slug"]] = existing
            else:
                category = ItemCategory(
                    name=cat_data["name"],
                    slug=cat_data["slug"],
                    description=cat_data["description"],
                    emoji=cat_data["emoji"],
                    order=cat_data["order"],
                    is_active=True,
                    # Campos del Gabinete
                    gabinete_category=cat_data["gabinete_category"],
                    lucien_description=cat_data["lucien_description"],
                    min_level_to_view=cat_data["min_level_to_view"],
                    min_level_to_buy=cat_data["min_level_to_buy"],
                    is_gabinete=True,
                )
                session.add(category)
                await session.flush()
                category_map[cat_data["slug"]] = category
                print(f"  ✅ Categoría creada: {cat_data['name']}")

        # Crear items
        print("\n🎁 Creando items del Gabinete...")
        items_created = 0
        items_skipped = 0

        for item_data in CABINET_ITEMS:
            # Verificar si ya existe
            result = await session.execute(
                select(ShopItem).where(ShopItem.slug == item_data["slug"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                print(f"  ⏭️  Item ya existe: {item_data['name']}")
                items_skipped += 1
                continue

            # Obtener categoría
            category = category_map.get(item_data["category_slug"])
            if not category:
                print(f"  ❌ Categoría no encontrada: {item_data['category_slug']}")
                continue

            # Crear item
            item = ShopItem(
                category_id=category.id,
                name=item_data["name"],
                slug=item_data["slug"],
                description=item_data["description"],
                # Campos del Gabinete
                lucien_description=item_data["lucien_description"],
                icon=item_data["icon"],
                price_besitos=item_data["price"],
                item_type=item_data["item_type"],
                rarity=item_data["rarity"],
                gabinete_item_type=item_data.get("gabinete_item_type"),
                duration_hours=item_data.get("duration_hours"),
                stock=item_data.get("stock"),
                is_limited=item_data.get("is_limited", False),
                total_stock=item_data.get("total_stock"),
                max_per_user=item_data.get("max_per_user"),
                min_level_to_view=item_data.get("min_level_to_view", 1),
                min_level_to_buy=item_data.get("min_level_to_buy", 1),
                visibility=item_data.get("visibility", "public"),
                requires_vip=item_data.get("requires_vip", False),
                order=item_data.get("order", 0),
                is_active=True,
                is_featured=False,
                created_by=1,  # System admin
            )
            session.add(item)
            items_created += 1
            print(f"  ✅ Item creado: {item_data['name']} ({item_data['price']} Favores)")

        # Commit cambios
        await session.commit()

        print("\n" + "=" * 60)
        print(f"✅ Gabinete poblado exitosamente!")
        print(f"   Items creados: {items_created}")
        print(f"   Items saltados (ya existían): {items_skipped}")
        print(f"   Total items en datos: {len(CABINET_ITEMS)}")
        print("=" * 60)

    # Cerrar BD
    await close_db()
    print("\n🔌 Conexión a BD cerrada")


if __name__ == "__main__":
    asyncio.run(seed_cabinet_items())
