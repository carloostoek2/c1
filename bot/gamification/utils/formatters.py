"""Formateadores de gamificación.

Funciones de formateo para la capa de presentación del sistema de gamificación.
Centraliza el manejo de nombres de moneda y formateo de cantidades.

NOTA: El sistema interno usa "besitos" pero al usuario se muestra como "Favores".
"""

from typing import Union

# ============================================================
# CONSTANTES DE MONEDA
# ============================================================

# Nombre de la moneda en la UI (singular y plural)
CURRENCY_NAME = "Favor"
CURRENCY_NAME_PLURAL = "Favores"

# Emoji de la moneda
CURRENCY_EMOJI = "✨"  # Emoji elegante para Favores de Diana


# ============================================================
# FUNCIONES DE FORMATEO
# ============================================================


def format_currency(amount: Union[int, float], with_emoji: bool = False) -> str:
    """Formatea una cantidad de moneda para mostrar al usuario.

    Maneja decimales inteligentemente:
    - Si es entero exacto: "10 Favores"
    - Si tiene decimales: "3.5 Favores"
    - Singular cuando es 1: "1 Favor"

    Args:
        amount: Cantidad de moneda (puede ser int o float)
        with_emoji: Si incluir emoji antes de la cantidad

    Returns:
        String formateado (ej: "10 Favores", "1 Favor", "3.5 Favores")

    Examples:
        >>> format_currency(10)
        '10 Favores'
        >>> format_currency(1)
        '1 Favor'
        >>> format_currency(3.5)
        '3.5 Favores'
        >>> format_currency(10, with_emoji=True)
        '✨ 10 Favores'
    """
    # Determinar si mostrar como entero o decimal
    if isinstance(amount, float):
        # Si el float es un entero exacto (ej: 10.0), mostrar como entero
        if amount == int(amount):
            display_amount = str(int(amount))
        else:
            # Mostrar con 1 decimal
            display_amount = f"{amount:.1f}"
    else:
        display_amount = str(amount)

    # Determinar singular o plural
    # Usamos el valor numérico real para decidir
    numeric_value = float(amount) if isinstance(amount, (int, float)) else 0
    currency_word = CURRENCY_NAME if numeric_value == 1 else CURRENCY_NAME_PLURAL

    # Construir resultado
    if with_emoji:
        return f"{CURRENCY_EMOJI} {display_amount} {currency_word}"
    return f"{display_amount} {currency_word}"


def format_currency_short(amount: Union[int, float]) -> str:
    """Formatea moneda en versión corta (solo número y emoji).

    Args:
        amount: Cantidad de moneda

    Returns:
        String corto (ej: "✨10", "✨3.5")

    Examples:
        >>> format_currency_short(10)
        '✨10'
        >>> format_currency_short(3.5)
        '✨3.5'
    """
    if isinstance(amount, float) and amount != int(amount):
        return f"{CURRENCY_EMOJI}{amount:.1f}"
    return f"{CURRENCY_EMOJI}{int(amount)}"


def format_currency_change(amount: Union[int, float], is_gain: bool = True) -> str:
    """Formatea un cambio de moneda (+/-).

    Args:
        amount: Cantidad de cambio (siempre positivo)
        is_gain: True si es ganancia, False si es gasto

    Returns:
        String con signo (ej: "+10 Favores", "-5 Favores")

    Examples:
        >>> format_currency_change(10)
        '+10 Favores'
        >>> format_currency_change(5, is_gain=False)
        '-5 Favores'
    """
    sign = "+" if is_gain else "-"
    formatted = format_currency(abs(amount))
    return f"{sign}{formatted}"


def currency_name(amount: Union[int, float] = 2) -> str:
    """Retorna el nombre de la moneda (singular o plural).

    Args:
        amount: Cantidad para determinar singular/plural (default: 2 para plural)

    Returns:
        "Favor" o "Favores"

    Examples:
        >>> currency_name(1)
        'Favor'
        >>> currency_name(2)
        'Favores'
        >>> currency_name()
        'Favores'
    """
    return CURRENCY_NAME if amount == 1 else CURRENCY_NAME_PLURAL


# ============================================================
# FUNCIONES DE FORMATEO DE NIVELES
# ============================================================

# Nombres de los niveles del Protocolo de Acceso
PROTOCOL_LEVELS = {
    1: "Visitante",
    2: "Observado",
    3: "Evaluado",
    4: "Reconocido",
    5: "Admitido",
    6: "Confidente",
    7: "Guardián de Secretos",
}


def format_level_name(level_number: int) -> str:
    """Formatea el nombre del nivel del Protocolo de Acceso.

    Args:
        level_number: Número de nivel (1-7)

    Returns:
        Nombre del nivel

    Examples:
        >>> format_level_name(1)
        'Visitante'
        >>> format_level_name(7)
        'Guardián de Secretos'
    """
    return PROTOCOL_LEVELS.get(level_number, f"Nivel {level_number}")


def format_level_with_number(level_number: int) -> str:
    """Formatea nivel con número y nombre.

    Args:
        level_number: Número de nivel

    Returns:
        String formateado (ej: "Nivel 3: Evaluado")

    Examples:
        >>> format_level_with_number(3)
        'Nivel 3: Evaluado'
    """
    name = format_level_name(level_number)
    return f"Nivel {level_number}: {name}"


# ============================================================
# CONFIGURACIÓN DE VALORES DE GANANCIA DE FAVORES
# ============================================================
# Estos valores definen la economía del sistema de gamificación.
# Los Favores representan reconocimientos que Diana otorga.
# Cada Favor tiene peso significativo - Diana no regala reconocimiento fácilmente.

FAVOR_REWARDS = {
    # Reacciones a publicaciones del canal
    "reaction_base": 0.1,           # Por cada reacción
    "reaction_first_daily": 0.5,    # Bonus por primera reacción del día
    "reaction_daily_limit": 10,     # Máximo de reacciones que dan Favores por día

    # Misiones
    "mission_daily": 1.0,           # Completar misión diaria
    "mission_weekly": 3.0,          # Completar misión semanal
    "level_evaluation": 5.0,        # Completar evaluación de nivel

    # Rachas
    "streak_7_days": 2.0,           # Bonus racha 7 días consecutivos
    "streak_30_days": 10.0,         # Bonus racha 30 días consecutivos

    # Easter eggs
    "easter_egg_min": 2.0,          # Mínimo por encontrar easter egg
    "easter_egg_max": 5.0,          # Máximo por encontrar easter egg

    # Referidos
    "referral_active": 5.0,         # Por referido que complete onboarding
}

# Alias para compatibilidad con el sistema interno (que usa "besitos")
BESITO_REWARDS = FAVOR_REWARDS


def get_favor_reward(action: str) -> float:
    """Obtiene el valor de Favores para una acción.

    Args:
        action: Clave de la acción (ej: "reaction_base", "mission_daily")

    Returns:
        Cantidad de Favores para esa acción

    Examples:
        >>> get_favor_reward("reaction_base")
        0.1
        >>> get_favor_reward("mission_daily")
        1.0
    """
    return FAVOR_REWARDS.get(action, 0)
