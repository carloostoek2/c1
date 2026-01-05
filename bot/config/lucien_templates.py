"""
Templates de mensajes con la voz de Lucien.

Centraliza todos los mensajes del bot con la personalidad del mayordomo:
formal pero no frío, observador pero no invasivo, elegantemente sarcástico.
"""
from typing import Dict, Any

# ========================================
# WELCOME MESSAGES
# ========================================

WELCOME_MESSAGES = {
    "new_user": {
        "default": (
            "Bienvenido. Soy Lucien, el guardián de este espacio.\n\n"
            "Mi labor es simple: observar, evaluar, y decidir quién merece "
            "acceso a lo que Diana ha preparado.\n\n"
            "Comencemos."
        ),
        "explorer": (
            "Veo curiosidad en tu mirada. Bien.\n\n"
            "Este lugar tiene muchos secretos, y no todos están a la vista. "
            "Algunos... están esperando ser descubiertos por alguien con tu "
            "disposición a buscar.\n\n"
            "Adelante."
        ),
        "direct": (
            "Seré breve, como seguramente prefieres.\n\n"
            "Este es un espacio donde Diana comparte lo que pocos ven. "
            "Lo que encuentres aquí dependerá de tu disposición a involucrarte.\n\n"
            "Eso es todo."
        ),
        "romantic": (
            "Has llegado en un momento especial.\n\n"
            "Diana ha estado preparando algo íntimo, algo que solo compartirá "
            "con quienes comprendan el peso de la vulnerabilidad.\n\n"
            "Espero que seas uno de ellos."
        ),
    },
    "returning_user": {
        "default": "Has vuelto. {days_text}\n\nDiana preguntó por ti.",
        "short_absence": (
            "Apenas te fuiste y ya regresaste.\n\n"
            "Interesante. Diana notará tu... dedicación."
        ),
        "long_absence": (
            "Pensé que no volverías. {days} días sin verte.\n\n"
            "Diana había guardado algo para ti. Espero que valga la pena la espera."
        ),
    },
    "active_user": {
        "default": "De vuelta, como es habitual.\n\nDiana tiene algo nuevo preparado.",
        "vip": (
            "Tu acceso VIP sigue activo. {days_remaining} días restantes.\n\n"
            "Diana ha dejado contenido exclusivo para ti en El Diván."
        ),
    },
    "admin": (
        "Acceso administrativo reconocido.\n\n"
        "Usa /admin para gestionar el sistema."
    ),
}

# ========================================
# ERROR MESSAGES
# ========================================

ERROR_MESSAGES = {
    "permission_denied": (
        "Este lugar no es para ti. Aún.\n\n"
        "Diana decide quién entra, y yo sigo sus instrucciones."
    ),
    "not_configured": (
        "Aún no he preparado {element}.\n\n"
        "Paciencia. Todo a su tiempo."
    ),
    "invalid_input": (
        "No comprendo lo que intentas decir.\n\n"
        "Sé más claro, o no podré ayudarte."
    ),
    "cooldown_active": (
        "Diana necesita un momento. Vuelve {time_text}.\n\n"
        "No insistas. La espera es parte del proceso."
    ),
    "limit_reached": (
        "Has alcanzado el límite por hoy: {limit_type}.\n\n"
        "Esto no es un buffet. Regresa mañana."
    ),
    "token_invalid": (
        "Este token no es válido. O ya fue usado, o nunca existió.\n\n"
        "No puedo hacer nada con esto."
    ),
    "token_expired": (
        "Este token expiró hace {time_text}.\n\n"
        "Los tokens no son eternos. Deberías haberlo usado antes."
    ),
    "vip_not_configured": (
        "El canal VIP aún no está configurado.\n\n"
        "Habla con quien administra esto. Yo solo observo."
    ),
    "free_not_configured": (
        "El canal Free aún no está configurado.\n\n"
        "Habla con quien administra esto."
    ),
    "already_vip": (
        "Ya tienes acceso VIP. {days_remaining} días restantes.\n\n"
        "¿Qué más quieres?"
    ),
    "challenge_failed": (
        "Fallaste el desafío. {attempts_remaining} intentos restantes.\n\n"
        "Diana esperaba más de ti."
    ),
    "no_attempts_left": (
        "No te quedan intentos.\n\n"
        "Este camino está cerrado para ti. Hay otros."
    ),
}

# ========================================
# CONFIRMATION MESSAGES
# ========================================

CONFIRMATION_MESSAGES = {
    "action_success": "Hecho. {details}",
    "purchase_complete": (
        "Adquirido: {item_name} por {cost} Favores.\n\n"
        "Diana estará complacida con tu elección."
    ),
    "level_up": (
        "He observado tu progreso. Ahora eres {level_name}.\n\n"
        "Diana estará complacida."
    ),
    "reward_granted": (
        "Has recibido: {reward_name}.\n\n"
        "Úsalo con sabiduría."
    ),
    "vip_activated": (
        "Tu suscripción VIP está activa. {duration_days} días de acceso.\n\n"
        "Diana te espera en El Diván."
    ),
    "token_generated": (
        "Token generado: <code>{token}</code>\n\n"
        "Válido por {hours} horas. Compártelo con cuidado."
    ),
    "channel_configured": (
        "{channel_type} configurado exitosamente.\n\n"
        "Canal: {channel_name}"
    ),
    "settings_updated": (
        "Configuración actualizada.\n\n"
        "{details}"
    ),
}

# ========================================
# NOTIFICATION MESSAGES
# ========================================

NOTIFICATION_MESSAGES = {
    "streak_milestone": {
        "7_days": (
            "7 días consecutivos. Tu dedicación no pasa desapercibida.\n\n"
            "Bonus: {bonus_besitos} Favores."
        ),
        "14_days": (
            "14 días sin fallar. Impresionante.\n\n"
            "Diana ha notado tu constancia. Bonus: {bonus_besitos} Favores."
        ),
        "30_days": (
            "30 días. Pocas personas llegan aquí.\n\n"
            "Diana tiene algo especial preparado para ti. "
            "Bonus: {bonus_besitos} Favores."
        ),
    },
    "streak_lost": (
        "Tu racha se rompió. {streak_days} días perdidos.\n\n"
        "Una pena. Tendrás que empezar de nuevo."
    ),
    "mission_completed": (
        "Misión completada: {mission_name}.\n\n"
        "Recompensa: {reward}."
    ),
    "reward_unlocked": (
        "Nuevo item desbloqueado: {reward_name}.\n\n"
        "{description}"
    ),
    "vip_expiring_soon": (
        "Tu acceso VIP expira en {days} días.\n\n"
        "Si deseas renovar, este es el momento."
    ),
    "new_content_available": (
        "Diana ha dejado algo nuevo en {channel_name}.\n\n"
        "No querrás perdértelo."
    ),
    "daily_gift_available": (
        "Tu regalo diario está disponible.\n\n"
        "Usa /daily para reclamarlo."
    ),
}

# ========================================
# CONVERSION MESSAGES (por arquetipo)
# ========================================

CONVERSION_MESSAGES = {
    "free_to_vip": {
        "default": (
            "Has llegado al final del camino gratuito.\n\n"
            "Lo que sigue... solo está disponible para quienes Diana considera dignos de "
            "acceso exclusivo. El Diván te espera, si decides dar el siguiente paso.\n\n"
            "La decisión es tuya."
        ),
        "explorer": (
            "Has explorado todo lo que Los Kinkys ofrecen.\n\n"
            "Pero hay secretos más profundos en El Diván. Lugares que solo los más curiosos "
            "descubren. Diana ha preparado contenido que no encontrarás en ningún otro lugar.\n\n"
            "¿Te atreves?"
        ),
        "romantic": (
            "Has sentido la conexión, ¿verdad?\n\n"
            "Lo que has visto hasta ahora es solo la superficie. En El Diván, Diana comparte "
            "su vulnerabilidad real. Momentos íntimos que solo reserva para quienes comprenden "
            "el peso de la confianza.\n\n"
            "Si buscas profundidad, este es el camino."
        ),
        "analytical": (
            "Has analizado el sistema. Ahora comprendes la estructura.\n\n"
            "El Diván opera bajo reglas distintas. Acceso ilimitado, contenido exclusivo, "
            "y una relación directa con Diana que no encontrarás en el canal gratuito.\n\n"
            "Los números hablan por sí mismos."
        ),
    },
    "vip_renewal": {
        "default": (
            "Tu acceso VIP expira pronto. {days} días restantes.\n\n"
            "Si decides renovar ahora, tienes {discount}% de descuento por lealtad.\n\n"
            "Diana aprecia a quienes se quedan."
        ),
    },
}

# ========================================
# RETENTION MESSAGES (por estado de usuario)
# ========================================

RETENTION_MESSAGES = {
    "at_risk": (
        "He notado tu ausencia. {days} días sin verte.\n\n"
        "Diana preguntó por ti. Hay contenido nuevo esperando."
    ),
    "dormant_first": (
        "Han pasado {days} días.\n\n"
        "Hay cosas que quiero mostrarte. Diana ha dejado algo que creo que apreciarías.\n\n"
        "Si decides volver."
    ),
    "dormant_final": (
        "Este será mi último mensaje.\n\n"
        "Si decides volver algún día, aquí estaré. Diana también.\n\n"
        "Hasta entonces."
    ),
    "lost_farewell": (
        "Adiós.\n\n"
        "Si algún día vuelves, la puerta seguirá abierta."
    ),
}

# ========================================
# HELPER FUNCTIONS
# ========================================


def get_days_text(days: int) -> str:
    """Formatea días en texto apropiado."""
    if days == 0:
        return "Apenas te fuiste"
    elif days == 1:
        return "1 día sin verte"
    else:
        return f"{days} días sin verte"


def get_time_text(seconds: int) -> str:
    """Formatea segundos en texto legible."""
    if seconds < 60:
        return f"{seconds} segundos"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minuto{'s' if minutes != 1 else ''}"
    else:
        hours = seconds // 3600
        return f"{hours} hora{'s' if hours != 1 else ''}"


def get_remaining_days_text(days: int) -> str:
    """Formatea días restantes."""
    if days == 0:
        return "Expira hoy"
    elif days == 1:
        return "1 día restante"
    else:
        return f"{days} días restantes"
