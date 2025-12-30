"""Utilidades para gamificación."""

from .validators import (
    validate_json_structure,
    validate_mission_criteria,
    validate_reward_metadata,
    validate_unlock_conditions,
    is_valid_emoji,
    validate_mission_progress,
)

from .templates import (
    SYSTEM_TEMPLATES,
    apply_template,
    get_template_info,
    list_templates,
)

from .formatters import (
    # Constantes de moneda
    CURRENCY_NAME,
    CURRENCY_NAME_PLURAL,
    CURRENCY_EMOJI,
    # Funciones de formateo de moneda
    format_currency,
    format_currency_short,
    format_currency_change,
    currency_name,
    # Constantes y funciones de niveles
    PROTOCOL_LEVELS,
    format_level_name,
    format_level_with_number,
    # Configuración de recompensas
    FAVOR_REWARDS,
    BESITO_REWARDS,
    get_favor_reward,
)

from .emotional_words import (
    EMOTIONAL_WORDS,
    EMOTIONAL_PHRASES,
    DIANA_QUESTION_PATTERNS,
    has_emotional_content,
    is_diana_question,
    get_emotional_intensity,
)

__all__ = [
    # Validators
    "validate_json_structure",
    "validate_mission_criteria",
    "validate_reward_metadata",
    "validate_unlock_conditions",
    "is_valid_emoji",
    "validate_mission_progress",
    # Templates
    "SYSTEM_TEMPLATES",
    "apply_template",
    "get_template_info",
    "list_templates",
    # Currency formatters
    "CURRENCY_NAME",
    "CURRENCY_NAME_PLURAL",
    "CURRENCY_EMOJI",
    "format_currency",
    "format_currency_short",
    "format_currency_change",
    "currency_name",
    # Level formatters
    "PROTOCOL_LEVELS",
    "format_level_name",
    "format_level_with_number",
    # Reward configuration
    "FAVOR_REWARDS",
    "BESITO_REWARDS",
    "get_favor_reward",
    # Emotional words
    "EMOTIONAL_WORDS",
    "EMOTIONAL_PHRASES",
    "DIANA_QUESTION_PATTERNS",
    "has_emotional_content",
    "is_diana_question",
    "get_emotional_intensity",
]
