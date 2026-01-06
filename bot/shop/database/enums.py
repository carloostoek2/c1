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
    CONTENT_SET = "content_set"  # Content multimedia (photos, videos, audio)

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
            "content_set": "🎬",
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
            "content_set": "Contenido Multimedia",
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


class NarrativeItemMetadata(TypedDict):
    """Metadata para items narrativos."""

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
# CMS CONTENT SET ENUMS
# ============================================================


class ContentType(str, Enum):
    """Tipo de contenido multimedia en un ContentSet."""

    PHOTO_SET = "photo_set"  # Galería de fotos
    VIDEO = "video"          # Video individual
    AUDIO = "audio"          # Audio individual
    MIXED = "mixed"          # Combinación de tipos

    def __str__(self) -> str:
        return self.value

    @property
    def emoji(self) -> str:
        """Emoji representativo del tipo de contenido."""
        emojis = {
            "photo_set": "🖼️",
            "video": "🎬",
            "audio": "🎵",
            "mixed": "🎭",
        }
        return emojis.get(self.value, "📦")

    @property
    def display_name(self) -> str:
        """Nombre para mostrar en UI."""
        names = {
            "photo_set": "Galería de Fotos",
            "video": "Video",
            "audio": "Audio",
            "mixed": "Contenido Mixto",
        }
        return names.get(self.value, "Contenido")


class ContentTier(str, Enum):
    """Nivel de acceso de un ContentSet."""

    FREE = "free"        # Disponible para todos
    VIP = "vip"          # Solo suscriptores VIP
    PREMIUM = "premium"  # Nivel premium especial
    GIFT = "gift"        # Solo por regalo/recompensa

    def __str__(self) -> str:
        return self.value

    @property
    def emoji(self) -> str:
        """Emoji representativo del tier."""
        emojis = {
            "free": "🆓",
            "vip": "👑",
            "premium": "💎",
            "gift": "🎁",
        }
        return emojis.get(self.value, "📦")

    @property
    def display_name(self) -> str:
        """Nombre para mostrar en UI."""
        names = {
            "free": "Gratuito",
            "vip": "VIP Exclusivo",
            "premium": "Premium",
            "gift": "Regalo",
        }
        return names.get(self.value, "Contenido")
