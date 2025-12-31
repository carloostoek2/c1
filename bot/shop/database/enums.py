"""
Enums y tipos para el módulo de Tienda.
"""

from enum import Enum
from typing import TypedDict, Optional


class ItemType(str, Enum):
    """Tipo de producto en la tienda."""

    NARRATIVE = "narrative"      # Artefactos que desbloquean fragmentos
    DIGITAL = "digital"          # Paquetes de contenido digital
    CONSUMABLE = "consumable"    # Items de uso único (boost, etc.)
    COSMETIC = "cosmetic"        # Items cosméticos (títulos, badges extra)

    def __str__(self) -> str:
        return self.value

    @property
    def emoji(self) -> str:
        """Emoji representativo del tipo."""
        emojis = {
            "narrative": "📜",
            "digital": "💾",
            "consumable": "🧪",
            "cosmetic": "✨",
        }
        return emojis.get(self.value, "📦")

    @property
    def display_name(self) -> str:
        """Nombre para mostrar en UI."""
        names = {
            "narrative": "Artefacto Narrativo",
            "digital": "Contenido Digital",
            "consumable": "Consumible",
            "cosmetic": "Cosmético",
        }
        return names.get(self.value, "Producto")


class ItemRarity(str, Enum):
    """Rareza del producto (afecta visualización)."""

    COMMON = "common"        # Blanco/Gris
    UNCOMMON = "uncommon"    # Verde
    RARE = "rare"            # Azul
    EPIC = "epic"            # Púrpura
    LEGENDARY = "legendary"  # Dorado

    def __str__(self) -> str:
        return self.value

    @property
    def emoji(self) -> str:
        """Emoji representativo de la rareza."""
        emojis = {
            "common": "⚪",
            "uncommon": "🟢",
            "rare": "🔵",
            "epic": "🟣",
            "legendary": "🟡",
        }
        return emojis.get(self.value, "⚪")

    @property
    def display_name(self) -> str:
        """Nombre para mostrar en UI."""
        names = {
            "common": "Común",
            "uncommon": "Poco Común",
            "rare": "Raro",
            "epic": "Épico",
            "legendary": "Legendario",
        }
        return names.get(self.value, "Común")


class PurchaseStatus(str, Enum):
    """Estado de una compra."""

    COMPLETED = "completed"    # Compra exitosa
    REFUNDED = "refunded"      # Compra reembolsada
    CANCELLED = "cancelled"    # Compra cancelada

    def __str__(self) -> str:
        return self.value


# ============================================================
# TYPEDDICTS PARA METADATA
# ============================================================


class NarrativeItemMetadata(TypedDict, total=False):
    """Metadata para items narrativos y pistas.

    Soporta tanto artefactos narrativos como pistas del sistema inmersivo.
    """

    # --- Campos de artefacto narrativo ---
    unlocks_fragment_key: Optional[str]   # Fragment key que desbloquea
    unlocks_chapter_slug: Optional[str]   # Chapter slug que desbloquea
    lore_text: Optional[str]              # Texto de lore del artefacto

    # --- Campos de pista (is_clue=True) ---
    is_clue: bool                         # True = es una pista narrativa
    clue_category: Optional[str]          # "map", "secret", "password", "key"
    clue_hint: Optional[str]              # Pista de cómo encontrarla
    source_fragment_key: Optional[str]    # Fragmento donde se obtiene
    required_for_fragments: list          # Fragment keys que la requieren
    clue_icon: Optional[str]              # Emoji específico de la pista


class ObtainedVia(str, Enum):
    """Modos de obtención de items en el inventario."""

    PURCHASE = "purchase"       # Comprado en tienda
    GIFT = "gift"              # Regalado por otro usuario
    REWARD = "reward"          # Recompensa de misión/sistema
    ADMIN_GRANT = "admin_grant" # Otorgado por admin
    DISCOVERY = "discovery"    # Descubierto en narrativa (pistas)


class DigitalItemMetadata(TypedDict):
    """Metadata para items digitales."""

    content_description: str              # Descripción del contenido
    download_url: Optional[str]           # URL de descarga (si aplica)
    access_key: Optional[str]             # Key de acceso a contenido


class ConsumableItemMetadata(TypedDict):
    """Metadata para items consumibles."""

    effect_type: str                      # Tipo de efecto ("besitos_boost", "xp_boost", etc.)
    effect_value: int                     # Valor del efecto
    duration_hours: Optional[int]         # Duración en horas (None = permanente)


class CosmeticItemMetadata(TypedDict):
    """Metadata para items cosméticos."""

    cosmetic_type: str                    # "title", "badge", "emoji"
    cosmetic_value: str                   # Valor del cosmético
    is_animated: bool                     # Si es animado (para badges)


# ============================================================
# ENUMS DEL GABINETE (FASE 4)
# ============================================================


class GabineteCategory(str, Enum):
    """Categorias del Gabinete de Lucien."""

    EPHEMERAL = "ephemeral"      # Efimeros - placeres de un solo uso
    DISTINCTIVE = "distinctive"  # Distintivos - badges permanentes
    KEYS = "keys"                # Llaves - desbloquean contenido narrativo
    RELICS = "relics"            # Reliquias - items de alto valor
    SECRET = "secret"            # Secretos - solo para Confidentes+

    def __str__(self) -> str:
        return self.value

    @property
    def emoji(self) -> str:
        """Emoji representativo de la categoria."""
        emojis = {
            "ephemeral": "⚡",
            "distinctive": "🎖️",
            "keys": "🔑",
            "relics": "💎",
            "secret": "🤫",
        }
        return emojis.get(self.value, "📦")

    @property
    def display_name(self) -> str:
        """Nombre para mostrar en UI."""
        names = {
            "ephemeral": "Efímeros",
            "distinctive": "Distintivos",
            "keys": "Llaves",
            "relics": "Reliquias",
            "secret": "Secretos",
        }
        return names.get(self.value, "Categoría")

    @property
    def lucien_description(self) -> str:
        """Descripcion de Lucien para la categoria."""
        descriptions = {
            "ephemeral": "Placeres de un solo uso. Intensos pero fugaces. Como ciertos momentos con Diana.",
            "distinctive": "Marcas visibles de su posicion en este universo. Para quienes valoran el reconocimiento publico.",
            "keys": "Abren puertas a contenido que otros no pueden ver. El conocimiento tiene precio.",
            "relics": "Los objetos mas valiosos del Gabinete. Requieren Favores considerables... y dignidad demostrada.",
            "secret": "Algunos secretos solo se revelan a quienes han demostrado... discrecion.",
        }
        return descriptions.get(self.value, "")

    @property
    def min_level_to_view(self) -> int:
        """Nivel minimo para ver esta categoria."""
        levels = {
            "ephemeral": 1,
            "distinctive": 1,
            "keys": 2,
            "relics": 4,
            "secret": 6,
        }
        return levels.get(self.value, 1)

    @property
    def min_level_to_buy(self) -> int:
        """Nivel minimo para comprar en esta categoria."""
        levels = {
            "ephemeral": 1,
            "distinctive": 2,
            "keys": 3,
            "relics": 5,
            "secret": 6,
        }
        return levels.get(self.value, 1)


class ItemVisibility(str, Enum):
    """Visibilidad de items en el Gabinete."""

    PUBLIC = "public"                  # Visible para todos
    CONFIDANTS_ONLY = "confidants"     # Solo Marca del Confidente (nivel 6+)
    GUARDIANS_ONLY = "guardians"       # Solo Corona del Guardian (nivel 7)

    def __str__(self) -> str:
        return self.value

    @property
    def min_level(self) -> int:
        """Nivel minimo requerido para ver."""
        levels = {
            "public": 1,
            "confidants": 6,
            "guardians": 7,
        }
        return levels.get(self.value, 1)


class GabineteItemType(str, Enum):
    """Tipos de contenido de items del Gabinete."""

    BADGE_TEMP = "badge_temp"          # Badge temporal (ej: Sello del Dia)
    BADGE_PERM = "badge_perm"          # Badge permanente
    AUDIO = "audio"                    # Contenido de audio
    TEXT = "text"                      # Contenido de texto
    IMAGE = "image"                    # Imagen
    PRIORITY_PASS = "priority_pass"    # Pase de prioridad
    PREVIEW = "preview"                # Preview de contenido
    NARRATIVE_KEY = "narrative_key"    # Llave narrativa
    ARCHIVE = "archive"                # Archivo de multiples contenidos
    COLLECTIBLE = "collectible"        # Coleccionable con bonus
    MIDNIGHT_CONTENT = "midnight"      # Contenido que aparece a medianoche
    MASTER_KEY = "master_key"          # Llave maestra (desbloquea todo)
    EASTER_EGG = "easter_egg"          # Easter egg / coordenadas

    def __str__(self) -> str:
        return self.value


class DiscountSource(str, Enum):
    """Fuente de descuento en el Gabinete."""

    LEVEL = "level"           # Descuento por nivel
    BADGE = "badge"           # Descuento por distintivo
    RELIC = "relic"           # Descuento por reliquia
    PROMO = "promo"           # Promocion temporal

    def __str__(self) -> str:
        return self.value


class NotificationType(str, Enum):
    """Tipos de notificacion del Gabinete."""

    NEW_ITEM = "new_item"              # Item nuevo disponible
    LOW_STOCK = "low_stock"            # Stock bajo
    EXPIRING_SOON = "expiring_soon"    # Item por terminar
    ITEM_BACK = "item_back"            # Item de vuelta en stock
    PROMO_ACTIVE = "promo_active"      # Promocion activa

    def __str__(self) -> str:
        return self.value


# ============================================================
# TYPEDDICTS PARA METADATA DEL GABINETE
# ============================================================


class GabineteItemMetadata(TypedDict, total=False):
    """Metadata para items del Gabinete."""

    # Contenido
    content_file_id: Optional[str]        # File ID de Telegram (audio/imagen)
    content_text: Optional[str]           # Texto del contenido
    content_duration_seconds: Optional[int]  # Duracion del contenido

    # Efectos de badges/distintivos
    badge_emoji: Optional[str]            # Emoji del badge
    badge_display_name: Optional[str]     # Nombre visible del badge
    discount_percent: Optional[int]       # Descuento que otorga (%)

    # Llaves narrativas
    unlocks_fragment_keys: Optional[list] # Fragment keys que desbloquea
    requires_previous_key: Optional[str]  # Slug del item previo requerido

    # Coleccionables
    bonus_effects: Optional[dict]         # Efectos bonus (descuento, etc.)

    # Contenido de medianoche
    midnight_content_pool: Optional[list] # Pool de contenidos para rotar

    # Easter eggs
    easter_egg_value: Optional[str]       # Valor del easter egg
