#!/usr/bin/env python3
"""
Seed script para el Gabinete de Lucien (Fase 4).

Crea las categorias y los 22+ items definidos en fase-4.md.
Incluye: Efimeros, Distintivos, Llaves, Reliquias y Secretos.

Uso:
    python scripts/seed_gabinete.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from bot.database.engine import get_session
from bot.shop.database.models import ItemCategory, ShopItem
from bot.shop.database.enums import (
    GabineteCategory,
    ItemVisibility,
    GabineteItemType,
    ItemType,
    ItemRarity,
)


# ============================================================
# CATEGORIAS DEL GABINETE
# ============================================================

GABINETE_CATEGORIES = [
    {
        "name": "Efimeros",
        "slug": "ephemeral",
        "description": "Items de un solo uso que expiran o se consumen.",
        "emoji": "⚡",
        "order": 1,
        "gabinete_category": GabineteCategory.EPHEMERAL.value,
        "lucien_description": "Placeres de un solo uso. Intensos pero fugaces. Como ciertos momentos con Diana.",
        "min_level_to_view": 1,
        "min_level_to_buy": 1,
        "is_gabinete": True,
    },
    {
        "name": "Distintivos",
        "slug": "distinctive",
        "description": "Badges permanentes que muestran estatus.",
        "emoji": "🎖️",
        "order": 2,
        "gabinete_category": GabineteCategory.DISTINCTIVE.value,
        "lucien_description": "Marcas visibles de su posicion en este universo. Para quienes valoran el reconocimiento publico.",
        "min_level_to_view": 1,
        "min_level_to_buy": 2,
        "is_gabinete": True,
    },
    {
        "name": "Llaves",
        "slug": "keys",
        "description": "Desbloquean contenido narrativo oculto.",
        "emoji": "🔑",
        "order": 3,
        "gabinete_category": GabineteCategory.KEYS.value,
        "lucien_description": "Abren puertas a contenido que otros no pueden ver. El conocimiento tiene precio.",
        "min_level_to_view": 2,
        "min_level_to_buy": 3,
        "is_gabinete": True,
    },
    {
        "name": "Reliquias",
        "slug": "relics",
        "description": "Items de alto valor, exclusivos y con efectos significativos.",
        "emoji": "💎",
        "order": 4,
        "gabinete_category": GabineteCategory.RELICS.value,
        "lucien_description": "Los objetos mas valiosos del Gabinete. Requieren Favores considerables... y dignidad demostrada.",
        "min_level_to_view": 4,
        "min_level_to_buy": 5,
        "is_gabinete": True,
    },
    {
        "name": "Secretos",
        "slug": "secret",
        "description": "Items ocultos solo para Confidentes y superiores.",
        "emoji": "🤫",
        "order": 5,
        "gabinete_category": GabineteCategory.SECRET.value,
        "lucien_description": "Algunos secretos solo se revelan a quienes han demostrado... discrecion.",
        "min_level_to_view": 6,
        "min_level_to_buy": 6,
        "is_gabinete": True,
    },
]


# ============================================================
# ITEMS DEL GABINETE
# ============================================================

GABINETE_ITEMS = [
    # ========== EFIMEROS ==========
    {
        "category_slug": "ephemeral",
        "name": "Sello del Dia",
        "slug": "eph_001_sello_dia",
        "description": "Una marca temporal que indica actividad reciente.",
        "item_type": ItemType.CONSUMABLE.value,
        "rarity": ItemRarity.COMMON.value,
        "price_besitos": 1,
        "icon": "📛",
        "lucien_description": "Una marca temporal que indica actividad reciente. Valida hasta medianoche. Algunos lo consideran un ritual diario. Otros, una vanidad menor.",
        "purchase_message": "El Sello ha sido aplicado. Por las proximas horas, su presencia sera... marcada. Use este tiempo sabiamente.",
        "post_use_message": "El Sello se ha desvanecido con el nuevo dia.",
        "min_level_to_view": 1,
        "min_level_to_buy": 1,
        "visibility": ItemVisibility.PUBLIC.value,
        "gabinete_item_type": GabineteItemType.BADGE_TEMP.value,
        "duration_hours": 24,
        "order": 1,
    },
    {
        "category_slug": "ephemeral",
        "name": "Susurro Efimero",
        "slug": "eph_002_susurro",
        "description": "Un mensaje de voz exclusivo de Diana.",
        "item_type": ItemType.CONSUMABLE.value,
        "rarity": ItemRarity.UNCOMMON.value,
        "price_besitos": 3,
        "icon": "🎧",
        "lucien_description": "Un mensaje de voz que Diana grabo en un momento de... inspiracion. 15 segundos. Una vez. Luego se desvanece como si nunca hubiera existido.",
        "purchase_message": "El Susurro es suyo. Escuchelo cuando este... preparado. No habra repeticion. Diana no se repite.",
        "post_use_message": "El Susurro se ha desvanecido. Como estaba destinado. Valio la pena? Solo usted lo sabe.",
        "min_level_to_view": 1,
        "min_level_to_buy": 1,
        "visibility": ItemVisibility.PUBLIC.value,
        "gabinete_item_type": GabineteItemType.AUDIO.value,
        "max_per_user": 3,
        "order": 2,
    },
    {
        "category_slug": "ephemeral",
        "name": "Pase de Prioridad",
        "slug": "eph_003_pase_prioridad",
        "description": "Acceso prioritario al proximo contenido limitado.",
        "item_type": ItemType.CONSUMABLE.value,
        "rarity": ItemRarity.RARE.value,
        "price_besitos": 5,
        "icon": "🎫",
        "lucien_description": "Cuando Diana libere contenido de acceso limitado, usted estara primero en la fila. No garantiza acceso - garantiza oportunidad.",
        "purchase_message": "El Pase es suyo. Cuando Diana decida abrir algo exclusivo, usted sera notificado antes que los demas. La ventaja del tiempo... no es poca cosa.",
        "post_use_message": "El Pase de Prioridad ha sido utilizado. Esperemos que haya valido la espera.",
        "min_level_to_view": 1,
        "min_level_to_buy": 2,
        "visibility": ItemVisibility.PUBLIC.value,
        "gabinete_item_type": GabineteItemType.PRIORITY_PASS.value,
        "duration_hours": 720,  # 30 dias
        "max_per_user": 1,
        "order": 3,
    },
    {
        "category_slug": "ephemeral",
        "name": "Vistazo al Sensorium",
        "slug": "eph_004_vistazo_sensorium",
        "description": "Preview de 30 segundos del contenido Sensorium.",
        "item_type": ItemType.CONSUMABLE.value,
        "rarity": ItemRarity.EPIC.value,
        "price_besitos": 15,
        "icon": "👁️",
        "lucien_description": "Una muestra del contenido Sensorium. Treinta segundos disenados para alterar su percepcion sensorial. Diana paso meses estudiando como el cerebro procesa el placer. Este es un fragmento de ese conocimiento.",
        "purchase_message": "El Vistazo esta desbloqueado. Tiene 48 horas. Le sugiero un espacio tranquilo. Auriculares. Sin distracciones. Esto no es contenido convencional.",
        "post_use_message": "El Vistazo ha expirado. Si desea mas... ya sabe donde encontrarlo.",
        "min_level_to_view": 2,
        "min_level_to_buy": 3,
        "visibility": ItemVisibility.PUBLIC.value,
        "gabinete_item_type": GabineteItemType.PREVIEW.value,
        "duration_hours": 48,
        "max_per_user": 1,
        "order": 4,
    },
    {
        "category_slug": "ephemeral",
        "name": "Confesion Nocturna",
        "slug": "eph_005_confesion_nocturna",
        "description": "Un texto intimo que Diana escribio tarde en la noche.",
        "item_type": ItemType.CONSUMABLE.value,
        "rarity": ItemRarity.RARE.value,
        "price_besitos": 8,
        "icon": "🌙",
        "lucien_description": "Un texto que Diana escribio tarde en la noche. Pensamientos que normalmente no comparte. Una confesion entre ella y la oscuridad. Ahora, entre ella y usted.",
        "purchase_message": "La Confesion esta disponible. Diana no sabe que la compro. O quizas si. Nunca se sabe con ella.",
        "post_use_message": "Ha leido la Confesion. Las palabras permanecen, pero el momento fue unico.",
        "min_level_to_view": 1,
        "min_level_to_buy": 2,
        "visibility": ItemVisibility.PUBLIC.value,
        "gabinete_item_type": GabineteItemType.TEXT.value,
        "order": 5,
    },

    # ========== DISTINTIVOS ==========
    {
        "category_slug": "distinctive",
        "name": "Sello del Visitante",
        "slug": "dist_001_sello_visitante",
        "description": "La marca mas basica. Indica existencia oficial.",
        "item_type": ItemType.COSMETIC.value,
        "rarity": ItemRarity.COMMON.value,
        "price_besitos": 2,
        "icon": "👁️",
        "lucien_description": "La marca mas basica. Indica que existe en este universo y decidio hacerlo oficial. No es mucho. Pero es un comienzo.",
        "purchase_message": "El Sello esta grabado. Ahora es oficialmente parte del registro. Diana podra ver esta marca cuando revise... si revisa.",
        "min_level_to_view": 1,
        "min_level_to_buy": 1,
        "visibility": ItemVisibility.PUBLIC.value,
        "gabinete_item_type": GabineteItemType.BADGE_PERM.value,
        "max_per_user": 1,
        "order": 1,
    },
    {
        "category_slug": "distinctive",
        "name": "Insignia del Observador",
        "slug": "dist_002_insignia_observador",
        "description": "Lucien lo ha notado. Esta insignia lo certifica.",
        "item_type": ItemType.COSMETIC.value,
        "rarity": ItemRarity.UNCOMMON.value,
        "price_besitos": 5,
        "icon": "🔍",
        "lucien_description": "Lucien lo ha notado. Esta insignia lo certifica. Significa algo? Para algunos, todo. Para otros, nada. Depende de cuanto valore ser visto.",
        "purchase_message": "La Insignia es suya. A partir de ahora, cuando yo observe el registro, su nombre tendra esta marca. No es poco.",
        "min_level_to_view": 1,
        "min_level_to_buy": 2,
        "visibility": ItemVisibility.PUBLIC.value,
        "gabinete_item_type": GabineteItemType.BADGE_PERM.value,
        "max_per_user": 1,
        "order": 2,
    },
    {
        "category_slug": "distinctive",
        "name": "Marca del Evaluado",
        "slug": "dist_003_marca_evaluado",
        "description": "Ha pasado las primeras pruebas.",
        "item_type": ItemType.COSMETIC.value,
        "rarity": ItemRarity.RARE.value,
        "price_besitos": 8,
        "icon": "✓",
        "lucien_description": "Ha pasado las primeras pruebas. Esta marca lo atestigua. No todas las pruebas. Pero las suficientes para merecer reconocimiento.",
        "purchase_message": "La Marca esta aplicada. Cuando otros vean su perfil, sabran que no es un visitante casual. Es alguien... evaluado.",
        "min_level_to_view": 2,
        "min_level_to_buy": 3,
        "visibility": ItemVisibility.PUBLIC.value,
        "gabinete_item_type": GabineteItemType.BADGE_PERM.value,
        "max_per_user": 1,
        "order": 3,
    },
    {
        "category_slug": "distinctive",
        "name": "Emblema del Reconocido",
        "slug": "dist_004_emblema_reconocido",
        "description": "Diana sabe su nombre. +5% descuento.",
        "item_type": ItemType.COSMETIC.value,
        "rarity": ItemRarity.EPIC.value,
        "price_besitos": 12,
        "icon": "⭐",
        "lucien_description": "Diana sabe su nombre. Este emblema lo confirma publicamente. No es algo que se otorgue facilmente. Usted lo gano.",
        "purchase_message": "El Emblema brilla en su perfil. Diana lo reconoce. Eso conlleva privilegios. Y expectativas.",
        "min_level_to_view": 3,
        "min_level_to_buy": 4,
        "visibility": ItemVisibility.PUBLIC.value,
        "gabinete_item_type": GabineteItemType.BADGE_PERM.value,
        "max_per_user": 1,
        "order": 4,
    },
    {
        "category_slug": "distinctive",
        "name": "Marca del Confidente",
        "slug": "dist_005_marca_confidente",
        "description": "Lucien confia en usted. +10% descuento. Acceso a items secretos.",
        "item_type": ItemType.COSMETIC.value,
        "rarity": ItemRarity.LEGENDARY.value,
        "price_besitos": 25,
        "icon": "🤫",
        "lucien_description": "Pocos llevan esta marca. Indica que Lucien confia en usted. Relativamente, por supuesto. La confianza absoluta no existe. Pero esto es lo mas cercano que ofrezco.",
        "purchase_message": "La Marca del Confidente es suya. Bienvenido al circulo interno. Hay cosas que solo los Confidentes pueden ver en el Gabinete. Explore.",
        "min_level_to_view": 5,
        "min_level_to_buy": 6,
        "visibility": ItemVisibility.PUBLIC.value,
        "gabinete_item_type": GabineteItemType.BADGE_PERM.value,
        "max_per_user": 1,
        "order": 5,
    },
    {
        "category_slug": "distinctive",
        "name": "Corona del Guardian",
        "slug": "dist_006_corona_guardian",
        "description": "El distintivo mas alto. +15% descuento. Acceso total.",
        "item_type": ItemType.COSMETIC.value,
        "rarity": ItemRarity.LEGENDARY.value,
        "price_besitos": 50,
        "icon": "👑",
        "lucien_description": "El distintivo mas alto del Gabinete. Solo los Guardianes de Secretos pueden portarlo. Usted no solo conoce los secretos de Diana. Los protege.",
        "purchase_message": "La Corona es suya, Guardian. No hay distintivo superior a este. Ha alcanzado la cima. Diana fue informada personalmente. Creame, eso no pasa seguido.",
        "min_level_to_view": 6,
        "min_level_to_buy": 7,
        "visibility": ItemVisibility.PUBLIC.value,
        "gabinete_item_type": GabineteItemType.BADGE_PERM.value,
        "max_per_user": 1,
        "order": 6,
    },

    # ========== LLAVES ==========
    {
        "category_slug": "keys",
        "name": "Llave del Fragmento I",
        "slug": "key_001_fragmento_i",
        "description": "Abre el primer secreto oculto.",
        "item_type": ItemType.NARRATIVE.value,
        "rarity": ItemRarity.RARE.value,
        "price_besitos": 10,
        "icon": "🔑",
        "lucien_description": "Abre el primer secreto oculto. Un fragmento de historia que Diana no cuenta publicamente. El comienzo de algo... mas profundo.",
        "purchase_message": "La Llave es suya. El Fragmento I esta desbloqueado. Encuentrelo en su Historia. Esta donde no estaba antes.",
        "post_use_message": "El Fragmento I ha sido revelado. Hay mas... si tiene la voluntad de buscarlo.",
        "min_level_to_view": 2,
        "min_level_to_buy": 3,
        "visibility": ItemVisibility.PUBLIC.value,
        "gabinete_item_type": GabineteItemType.NARRATIVE_KEY.value,
        "max_per_user": 1,
        "order": 1,
    },
    {
        "category_slug": "keys",
        "name": "Llave del Fragmento II",
        "slug": "key_002_fragmento_ii",
        "description": "El segundo secreto. Mas profundo que el primero.",
        "item_type": ItemType.NARRATIVE.value,
        "rarity": ItemRarity.RARE.value,
        "price_besitos": 12,
        "icon": "🔑",
        "lucien_description": "El segundo secreto. Mas profundo que el primero. Aqui Diana muestra algo que preferiria esconder.",
        "purchase_message": "La segunda Llave gira. El Fragmento II emerge. Tenga cuidado con lo que descubre. No todo conocimiento es comodo.",
        "post_use_message": "El Fragmento II ha sido revelado. Continua el descenso?",
        "min_level_to_view": 2,
        "min_level_to_buy": 3,
        "visibility": ItemVisibility.PUBLIC.value,
        "gabinete_item_type": GabineteItemType.NARRATIVE_KEY.value,
        "max_per_user": 1,
        "order": 2,
    },
    {
        "category_slug": "keys",
        "name": "Llave del Fragmento III",
        "slug": "key_003_fragmento_iii",
        "description": "El tercer secreto. Donde las cosas se ponen interesantes.",
        "item_type": ItemType.NARRATIVE.value,
        "rarity": ItemRarity.EPIC.value,
        "price_besitos": 15,
        "icon": "🔑",
        "lucien_description": "El tercer secreto. Aqui las cosas se ponen... interesantes. Diana no aprobo que esto estuviera disponible. Lo hice yo. Ella no sabe. O finge no saber.",
        "purchase_message": "Ha llegado mas lejos de lo que Diana anticipo. El Fragmento III contiene... bueno, descubralo usted mismo. No diga que no le adverti.",
        "post_use_message": "El Fragmento III ha sido revelado. Ahora sabe mas de lo que deberia.",
        "min_level_to_view": 3,
        "min_level_to_buy": 4,
        "visibility": ItemVisibility.PUBLIC.value,
        "gabinete_item_type": GabineteItemType.NARRATIVE_KEY.value,
        "max_per_user": 1,
        "order": 3,
    },
    {
        "category_slug": "keys",
        "name": "Llave del Archivo Oculto",
        "slug": "key_004_archivo_oculto",
        "description": "No un fragmento. Un archivo completo.",
        "item_type": ItemType.NARRATIVE.value,
        "rarity": ItemRarity.EPIC.value,
        "price_besitos": 20,
        "icon": "📁",
        "lucien_description": "No un fragmento. Un archivo completo. Memorias que Diana preferiria olvidar. O quizas no. Con ella nunca se sabe.",
        "purchase_message": "El Archivo se abre. Lo que encontrara son retazos. Pensamientos incompletos. Confesiones a medias. Mas reveladores, quizas, que cualquier narrativa pulida.",
        "post_use_message": "Ha explorado el Archivo. Algunas puertas no deberian abrirse. Pero ya es tarde para eso.",
        "min_level_to_view": 3,
        "min_level_to_buy": 4,
        "visibility": ItemVisibility.PUBLIC.value,
        "gabinete_item_type": GabineteItemType.ARCHIVE.value,
        "max_per_user": 1,
        "order": 4,
    },
    {
        "category_slug": "keys",
        "name": "Llave de la Primera Vez",
        "slug": "key_005_primera_vez",
        "description": "La historia de como Diana se convirtio en Senorita Kinky.",
        "item_type": ItemType.NARRATIVE.value,
        "rarity": ItemRarity.LEGENDARY.value,
        "price_besitos": 18,
        "icon": "✨",
        "lucien_description": "La historia de como Diana se convirtio en Senorita Kinky. El momento exacto. La decision. Lo que sintio. Esto no lo cuenta a nadie. Excepto ahora, a usted.",
        "purchase_message": "Esta es la historia mas personal del Gabinete. Diana antes de Kinky. El momento del cambio. Tratela con respeto.",
        "post_use_message": "Ahora conoce el origen. Use ese conocimiento sabiamente.",
        "min_level_to_view": 4,
        "min_level_to_buy": 5,
        "visibility": ItemVisibility.PUBLIC.value,
        "gabinete_item_type": GabineteItemType.NARRATIVE_KEY.value,
        "max_per_user": 1,
        "order": 5,
    },

    # ========== RELIQUIAS ==========
    {
        "category_slug": "relics",
        "name": "El Primer Secreto",
        "slug": "rel_001_primer_secreto",
        "description": "El primer secreto que Diana confio a Lucien. +3% descuento.",
        "item_type": ItemType.NARRATIVE.value,
        "rarity": ItemRarity.LEGENDARY.value,
        "price_besitos": 30,
        "icon": "🔮",
        "lucien_description": "Un objeto que representa el primer secreto que Diana me confio. No el objeto literal, claro. Pero su esencia. Ahora puede ser suyo. Con todo lo que eso implica.",
        "purchase_message": "El Primer Secreto cambia de manos. Ahora usted es su guardian. Diana fue notificada. Su reaccion fue... interesante.",
        "min_level_to_view": 4,
        "min_level_to_buy": 5,
        "visibility": ItemVisibility.PUBLIC.value,
        "gabinete_item_type": GabineteItemType.COLLECTIBLE.value,
        "max_per_user": 1,
        "order": 1,
    },
    {
        "category_slug": "relics",
        "name": "Fragmento del Espejo",
        "slug": "rel_002_fragmento_espejo",
        "description": "Un pedazo del espejo donde Diana se mira. Behind-the-scenes.",
        "item_type": ItemType.DIGITAL.value,
        "rarity": ItemRarity.LEGENDARY.value,
        "price_besitos": 40,
        "icon": "🪞",
        "lucien_description": "Un pedazo del espejo donde Diana se mira antes de cada sesion. Metaforicamente, por supuesto. O quizas no tan metaforicamente. A traves de el, vera lo que ella ve.",
        "purchase_message": "El Fragmento es suyo. Cuando lo 'use', vera algo diferente. No el resultado final. El proceso. La preparacion. Diana sin el maquillaje de la perfeccion.",
        "min_level_to_view": 4,
        "min_level_to_buy": 5,
        "visibility": ItemVisibility.PUBLIC.value,
        "gabinete_item_type": GabineteItemType.COLLECTIBLE.value,
        "max_per_user": 1,
        "order": 2,
    },
    {
        "category_slug": "relics",
        "name": "La Carta No Enviada",
        "slug": "rel_003_carta_no_enviada",
        "description": "Una carta que Diana escribio pero nunca envio.",
        "item_type": ItemType.NARRATIVE.value,
        "rarity": ItemRarity.LEGENDARY.value,
        "price_besitos": 50,
        "icon": "💌",
        "lucien_description": "Diana escribio esto hace tiempo. A alguien. No se a quien. Nunca lo envio. Las palabras quedaron guardadas. Ahora usted puede leerlas. El destinatario original nunca lo hara.",
        "purchase_message": "La Carta es suya. Leala cuando tenga tiempo para procesar. Lo que Diana escribio aqui... no lo ha compartido con nadie mas. Ni siquiera conmigo, hasta que la encontre.",
        "min_level_to_view": 5,
        "min_level_to_buy": 6,
        "visibility": ItemVisibility.PUBLIC.value,
        "gabinete_item_type": GabineteItemType.TEXT.value,
        "max_per_user": 1,
        "order": 3,
    },
    {
        "category_slug": "relics",
        "name": "Cristal de Medianoche",
        "slug": "rel_004_cristal_medianoche",
        "description": "Desbloquea contenido especial cada noche a medianoche.",
        "item_type": ItemType.DIGITAL.value,
        "rarity": ItemRarity.LEGENDARY.value,
        "price_besitos": 45,
        "icon": "💎",
        "lucien_description": "Un artefacto que activa contenido especial a medianoche. Cada noche, cuando el reloj marca las 00:00, algo se desbloquea. Solo para quienes poseen el Cristal.",
        "purchase_message": "El Cristal brilla a medianoche. Cada noche, algo aparece. Solo usted lo vera. Los demas duermen sin saber lo que se pierden.",
        "min_level_to_view": 4,
        "min_level_to_buy": 5,
        "visibility": ItemVisibility.PUBLIC.value,
        "gabinete_item_type": GabineteItemType.MIDNIGHT_CONTENT.value,
        "max_per_user": 1,
        "order": 4,
    },
    {
        "category_slug": "relics",
        "name": "Llave Maestra del Gabinete",
        "slug": "rel_005_llave_maestra",
        "description": "Abre TODO lo cerrado en el Gabinete. +20% descuento.",
        "item_type": ItemType.NARRATIVE.value,
        "rarity": ItemRarity.LEGENDARY.value,
        "price_besitos": 75,
        "icon": "🗝️",
        "lucien_description": "La unica Llave Maestra. Abre todo lo que esta cerrado en el Gabinete. Todos los fragmentos. Todos los archivos. Todo. Es el objeto mas valioso que poseo. Y el mas peligroso.",
        "purchase_message": "No hay nada mas alla de esto. La Llave Maestra abre cada puerta del Gabinete. Pasadas, presentes y futuras. Use este poder con... bueno, como quiera usarlo. Ya no puedo detenerlo.",
        "min_level_to_view": 6,
        "min_level_to_buy": 7,
        "visibility": ItemVisibility.PUBLIC.value,
        "gabinete_item_type": GabineteItemType.MASTER_KEY.value,
        "max_per_user": 1,
        "order": 5,
    },

    # ========== SECRETOS ==========
    {
        "category_slug": "secret",
        "name": "Susurro de Lucien",
        "slug": "secret_001_susurro_lucien",
        "description": "La perspectiva de Lucien. Lo que observa y no comenta.",
        "item_type": ItemType.NARRATIVE.value,
        "rarity": ItemRarity.LEGENDARY.value,
        "price_besitos": 20,
        "icon": "🎭",
        "lucien_description": "No todo es sobre Diana. A veces, incluso yo tengo algo que decir. Este es mi susurro. Mi perspectiva. Lo que observo y no comento. Hasta ahora.",
        "purchase_message": "Esto es... inusual. Normalmente no hablo de mi mismo. Pero usted ha llegado lejos. Merece escuchar lo que pienso. No se lo cuente a Diana.",
        "min_level_to_view": 6,
        "min_level_to_buy": 6,
        "visibility": ItemVisibility.CONFIDANTS_ONLY.value,
        "gabinete_item_type": GabineteItemType.TEXT.value,
        "max_per_user": 1,
        "order": 1,
    },
    {
        "category_slug": "secret",
        "name": "Las Coordenadas",
        "slug": "secret_002_coordenadas",
        "description": "Numeros. Solo numeros. Quizas nada. Quizas todo.",
        "item_type": ItemType.DIGITAL.value,
        "rarity": ItemRarity.LEGENDARY.value,
        "price_besitos": 35,
        "icon": "📍",
        "lucien_description": "Numeros. Solo numeros. No dire que significan. Quizas nada. Quizas todo. Los exploradores verdaderos encontraran su significado.",
        "purchase_message": "Aqui estan. Que hace con ellas es su decision. No espere ayuda. Este acertijo es suyo solo.",
        "min_level_to_view": 6,
        "min_level_to_buy": 6,
        "visibility": ItemVisibility.CONFIDANTS_ONLY.value,
        "gabinete_item_type": GabineteItemType.EASTER_EGG.value,
        "max_per_user": 1,
        "order": 2,
    },
]


async def seed_gabinete():
    """Seed all Gabinete categories and items."""
    async with get_session() as session:
        print("=" * 60)
        print("SEED: El Gabinete de Lucien")
        print("=" * 60)

        # ========================================
        # 1. Create categories
        # ========================================
        print("\n[1/2] Creando categorias del Gabinete...")
        category_map = {}

        for cat_data in GABINETE_CATEGORIES:
            # Check if exists
            result = await session.execute(
                select(ItemCategory).where(ItemCategory.slug == cat_data["slug"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                print(f"  - {cat_data['emoji']} {cat_data['name']}: Ya existe (id={existing.id})")
                category_map[cat_data["slug"]] = existing.id
            else:
                category = ItemCategory(**cat_data)
                session.add(category)
                await session.flush()
                category_map[cat_data["slug"]] = category.id
                print(f"  + {cat_data['emoji']} {cat_data['name']}: Creada (id={category.id})")

        await session.commit()
        print(f"\n  Total categorias: {len(category_map)}")

        # ========================================
        # 2. Create items
        # ========================================
        print("\n[2/2] Creando items del Gabinete...")
        items_created = 0
        items_existed = 0

        for item_data in GABINETE_ITEMS:
            # Get category_id
            category_slug = item_data.pop("category_slug")
            category_id = category_map.get(category_slug)

            if not category_id:
                print(f"  ! Error: Categoria '{category_slug}' no encontrada para item '{item_data['name']}'")
                continue

            # Check if exists
            result = await session.execute(
                select(ShopItem).where(ShopItem.slug == item_data["slug"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                items_existed += 1
                # Restore category_slug for next iteration reference
                item_data["category_slug"] = category_slug
            else:
                item = ShopItem(
                    category_id=category_id,
                    created_by=0,  # System
                    **item_data
                )
                session.add(item)
                items_created += 1
                print(f"  + {item_data['icon']} {item_data['name']}: Creado ({item_data['price_besitos']} Favores)")
                # Restore category_slug for next iteration reference
                item_data["category_slug"] = category_slug

        await session.commit()

        # ========================================
        # Summary
        # ========================================
        print("\n" + "=" * 60)
        print("RESUMEN")
        print("=" * 60)
        print(f"  Categorias: {len(category_map)}")
        print(f"  Items creados: {items_created}")
        print(f"  Items existentes: {items_existed}")
        print(f"  Total items: {items_created + items_existed}")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(seed_gabinete())
