"""
Servicio de mensajes adaptados por arquetipo.

Proporciona variaciones de mensajes según el arquetipo del usuario
para una experiencia personalizada con el tono de Lucien.
"""

from typing import Optional, Dict, Any
from bot.database.enums import ArchetypeType


# ========================================
# MENSAJES BASE Y VARIACIONES
# ========================================

# Formato: {base_key: {archetype: mensaje}}

ARCHETYPE_MESSAGES: Dict[str, Dict[Optional[ArchetypeType], str]] = {
    # ----------------------------------------
    # Misión diaria disponible
    # ----------------------------------------
    "mission_daily_available": {
        None: "Hay un encargo pendiente para hoy.",

        ArchetypeType.EXPLORER: (
            "Hay un encargo pendiente. "
            "Pero quizás encuentre algo más mientras lo completa..."
        ),
        ArchetypeType.DIRECT: (
            "Encargo del día disponible. Una acción, una recompensa."
        ),
        ArchetypeType.ROMANTIC: (
            "Diana ha pensado en algo para usted hoy. "
            "Un pequeño encargo que la haría... sonreír."
        ),
        ArchetypeType.ANALYTICAL: (
            "Protocolo diario activado. "
            "Parámetros: {details}. Recompensa calculada: {reward} Favores."
        ),
        ArchetypeType.PERSISTENT: (
            "Otro día, otra oportunidad de demostrar su constancia. "
            "El encargo espera."
        ),
        ArchetypeType.PATIENT: (
            "El encargo de hoy está disponible. "
            "Como siempre, tómese el tiempo que necesite."
        ),
    },

    # ----------------------------------------
    # Bienvenida de regreso
    # ----------------------------------------
    "welcome_back": {
        None: "Ha vuelto. Bien.",

        ArchetypeType.EXPLORER: (
            "Ha vuelto. Hay nuevos rincones esperando ser descubiertos."
        ),
        ArchetypeType.DIRECT: (
            "De vuelta. ¿Continuamos?"
        ),
        ArchetypeType.ROMANTIC: (
            "Ha vuelto. Diana notó su ausencia... y yo también."
        ),
        ArchetypeType.ANALYTICAL: (
            "Registro de retorno confirmado. "
            "Actividad suspendida por {days} días. Sistemas listos."
        ),
        ArchetypeType.PERSISTENT: (
            "Sabía que volvería. Siempre lo hace. Eso es... admirable."
        ),
        ArchetypeType.PATIENT: (
            "Ha regresado en su propio tiempo. "
            "Como era de esperarse de alguien como usted."
        ),
    },

    # ----------------------------------------
    # Misión completada
    # ----------------------------------------
    "mission_completed": {
        None: "Misión completada. Bien hecho.",

        ArchetypeType.EXPLORER: (
            "Misión completada. Pero seguro vio algo interesante "
            "mientras la realizaba, ¿no es así?"
        ),
        ArchetypeType.DIRECT: (
            "Hecho. {reward} Favores acreditados."
        ),
        ArchetypeType.ROMANTIC: (
            "Misión completada. Diana estaría complacida "
            "de ver su dedicación."
        ),
        ArchetypeType.ANALYTICAL: (
            "Objetivo cumplido. Eficiencia: {efficiency}%. "
            "Recompensa: {reward} Favores."
        ),
        ArchetypeType.PERSISTENT: (
            "Otra victoria para quien no se rinde. "
            "Su persistencia da frutos: {reward} Favores."
        ),
        ArchetypeType.PATIENT: (
            "Completado con la calma que lo caracteriza. "
            "{reward} Favores bien ganados."
        ),
    },

    # ----------------------------------------
    # Racha alcanzada
    # ----------------------------------------
    "streak_milestone": {
        None: "Ha alcanzado una racha de {streak} días.",

        ArchetypeType.EXPLORER: (
            "{streak} días explorando sin parar. "
            "¿Qué más habrá encontrado en el camino?"
        ),
        ArchetypeType.DIRECT: (
            "Racha: {streak} días. Eficiente."
        ),
        ArchetypeType.ROMANTIC: (
            "{streak} días de conexión continua. "
            "Diana siente cada uno de ellos."
        ),
        ArchetypeType.ANALYTICAL: (
            "Racha actual: {streak} días consecutivos. "
            "Probabilidad de continuidad: alta."
        ),
        ArchetypeType.PERSISTENT: (
            "{streak} días seguidos. Su terquedad es... inspiradora."
        ),
        ArchetypeType.PATIENT: (
            "{streak} días de constancia paciente. "
            "El tiempo recompensa a quienes saben esperar."
        ),
    },

    # ----------------------------------------
    # Level up
    # ----------------------------------------
    "level_up": {
        None: "Ha alcanzado un nuevo nivel: {level_name}.",

        ArchetypeType.EXPLORER: (
            "Nuevo nivel desbloqueado: {level_name}. "
            "Nuevos territorios aguardan."
        ),
        ArchetypeType.DIRECT: (
            "Nivel: {level_name}. Siguiente."
        ),
        ArchetypeType.ROMANTIC: (
            "Ha ascendido a {level_name}. "
            "Diana verá su nombre con otros ojos ahora."
        ),
        ArchetypeType.ANALYTICAL: (
            "Progresión confirmada. Nuevo nivel: {level_name}. "
            "Beneficios actualizados."
        ),
        ArchetypeType.PERSISTENT: (
            "Su determinación lo llevó a {level_name}. "
            "La persistencia siempre gana."
        ),
        ArchetypeType.PATIENT: (
            "Finalmente, {level_name}. "
            "Las cosas buenas llegan a quienes esperan."
        ),
    },

    # ----------------------------------------
    # Error o acción no permitida
    # ----------------------------------------
    "action_not_allowed": {
        None: "Eso no está permitido.",

        ArchetypeType.EXPLORER: (
            "Interesante intento, pero ese camino está bloqueado. "
            "Quizás haya otro..."
        ),
        ArchetypeType.DIRECT: (
            "No. Siguiente opción."
        ),
        ArchetypeType.ROMANTIC: (
            "Entiendo el impulso, pero Diana no aprobaría eso."
        ),
        ArchetypeType.ANALYTICAL: (
            "Operación denegada. Parámetros fuera de rango aceptable."
        ),
        ArchetypeType.PERSISTENT: (
            "No esta vez. Pero aprecio que lo intente de nuevo."
        ),
        ArchetypeType.PATIENT: (
            "Todavía no es el momento para eso. Paciencia."
        ),
    },
}


def get_adapted_message(
    base_message_key: str,
    user_archetype: Optional[ArchetypeType] = None,
    **format_args: Any
) -> str:
    """
    Obtiene mensaje adaptado al arquetipo del usuario.

    Si no hay arquetipo o no hay variación, usa mensaje base.

    Args:
        base_message_key: Clave del mensaje base
        user_archetype: Arquetipo del usuario (opcional)
        **format_args: Argumentos para formatear el mensaje

    Returns:
        Mensaje formateado adaptado al arquetipo

    Examples:
        >>> get_adapted_message(
        ...     "mission_daily_available",
        ...     ArchetypeType.DIRECT
        ... )
        "Encargo del día disponible. Una acción, una recompensa."

        >>> get_adapted_message(
        ...     "streak_milestone",
        ...     ArchetypeType.ROMANTIC,
        ...     streak=7
        ... )
        "7 días de conexión continua. Diana siente cada uno de ellos."
    """
    messages = ARCHETYPE_MESSAGES.get(base_message_key)

    if messages is None:
        return f"[Missing message: {base_message_key}]"

    # Buscar mensaje para el arquetipo
    message = messages.get(user_archetype)

    # Si no hay variación para este arquetipo, usar base
    if message is None:
        message = messages.get(None, "")

    # Formatear con argumentos
    try:
        return message.format(**format_args)
    except KeyError:
        # Si faltan argumentos, retornar sin formatear
        return message


def has_archetype_variation(base_message_key: str) -> bool:
    """
    Verifica si un mensaje tiene variaciones por arquetipo.

    Args:
        base_message_key: Clave del mensaje

    Returns:
        True si tiene variaciones
    """
    messages = ARCHETYPE_MESSAGES.get(base_message_key, {})
    # Tiene variaciones si hay más de solo el None (base)
    return len(messages) > 1


def get_available_message_keys() -> list:
    """Retorna lista de claves de mensajes disponibles."""
    return list(ARCHETYPE_MESSAGES.keys())


def add_custom_message(
    base_message_key: str,
    messages: Dict[Optional[ArchetypeType], str]
) -> None:
    """
    Agrega un nuevo conjunto de mensajes adaptados.

    Args:
        base_message_key: Clave del mensaje
        messages: Dict con mensaje por arquetipo (None = base)
    """
    ARCHETYPE_MESSAGES[base_message_key] = messages
