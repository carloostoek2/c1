"""
Enums para el sistema.

Define enumeraciones usadas en los modelos.
"""
from enum import Enum


class ArchetypeType(str, Enum):
    """
    Tipos de arquetipo de usuario en el sistema de gamificación.

    Los arquetipos son detectados automáticamente por Lucien
    basándose en el comportamiento del usuario. El usuario NO
    elige su arquetipo - es asignado por observación.

    Arquetipos:
        EXPLORER: Curiosidad insaciable, busca ver todo
        DIRECT: Eficiencia, va al grano sin rodeos
        ROMANTIC: Busca conexión emocional genuina
        ANALYTICAL: Necesita entender cómo funciona todo
        PERSISTENT: Determinación, no se rinde
        PATIENT: Entiende que lo valioso toma tiempo
    """

    EXPLORER = "explorer"
    DIRECT = "direct"
    ROMANTIC = "romantic"
    ANALYTICAL = "analytical"
    PERSISTENT = "persistent"
    PATIENT = "patient"

    def __str__(self) -> str:
        """Retorna valor string del enum."""
        return self.value

    @property
    def display_name(self) -> str:
        """Retorna nombre legible del arquetipo."""
        names = {
            ArchetypeType.EXPLORER: "El Explorador",
            ArchetypeType.DIRECT: "El Directo",
            ArchetypeType.ROMANTIC: "El Romántico",
            ArchetypeType.ANALYTICAL: "El Analítico",
            ArchetypeType.PERSISTENT: "El Persistente",
            ArchetypeType.PATIENT: "El Paciente"
        }
        return names[self]

    @property
    def lucien_description(self) -> str:
        """Retorna descripción de Lucien sobre el arquetipo."""
        descriptions = {
            ArchetypeType.EXPLORER: "Insaciablemente curioso",
            ArchetypeType.DIRECT: "Refrescantemente directo",
            ArchetypeType.ROMANTIC: "Peligrosamente sentimental",
            ArchetypeType.ANALYTICAL: "Irritantemente preciso",
            ArchetypeType.PERSISTENT: "Admirablemente terco",
            ArchetypeType.PATIENT: "Inquietantemente paciente"
        }
        return descriptions[self]

    @property
    def keyword(self) -> str:
        """Retorna palabra clave del arquetipo."""
        keywords = {
            ArchetypeType.EXPLORER: "Curiosidad",
            ArchetypeType.DIRECT: "Eficiencia",
            ArchetypeType.ROMANTIC: "Emoción",
            ArchetypeType.ANALYTICAL: "Lógica",
            ArchetypeType.PERSISTENT: "Tenacidad",
            ArchetypeType.PATIENT: "Calma"
        }
        return keywords[self]


class InteractionType(str, Enum):
    """
    Tipos de interacción para tracking de comportamiento.

    Cada interacción del usuario es registrada con uno de estos
    tipos para construir su perfil de comportamiento y determinar
    su arquetipo.
    """

    BUTTON_CLICK = "button_click"
    TEXT_RESPONSE = "text_response"
    CONTENT_VIEW = "content_view"
    CONTENT_COMPLETE = "content_complete"
    QUIZ_ANSWER = "quiz_answer"
    DECISION_MADE = "decision_made"
    MENU_NAVIGATION = "menu_navigation"
    EASTER_EGG_FOUND = "easter_egg_found"
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    RETURN_AFTER_INACTIVITY = "return_after_inactivity"
    RETRY_ACTION = "retry_action"
    SKIP_ACTION = "skip_action"
    QUESTION_ASKED = "question_asked"

    def __str__(self) -> str:
        """Retorna valor string del enum."""
        return self.value


class UserRole(str, Enum):
    """
    Roles de usuario en el sistema.

    Roles:
        FREE: Usuario con acceso al canal Free (default)
        VIP: Usuario con suscripción VIP activa
        ADMIN: Administrador del bot

    Transiciones automáticas:
        - Nuevo usuario → FREE
        - Activar token VIP → VIP
        - Expirar suscripción → FREE
        - Asignación manual → ADMIN
    """

    FREE = "free"
    VIP = "vip"
    ADMIN = "admin"

    def __str__(self) -> str:
        """Retorna valor string del enum."""
        return self.value

    @property
    def display_name(self) -> str:
        """Retorna nombre legible del rol."""
        names = {
            UserRole.FREE: "Usuario Free",
            UserRole.VIP: "Usuario VIP",
            UserRole.ADMIN: "Administrador"
        }
        return names[self]

    @property
    def emoji(self) -> str:
        """Retorna emoji del rol."""
        emojis = {
            UserRole.FREE: "🆓",
            UserRole.VIP: "⭐",
            UserRole.ADMIN: "👑"
        }
        return emojis[self]
