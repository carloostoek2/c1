"""
Templates de mensajes con la voz de Lucien.

Centraliza todos los mensajes del bot con la personalidad del mayordomo:
formal pero no frío, observador pero no invasivo, elegante y misterioso.
"""
from typing import Dict, Any

# ========================================
# WELCOME MESSAGES
# ========================================

WELCOME_MESSAGES = {
    "new_user": {
        "default": (
            "🎩 <b>Lucien:</b>\n"
            "<i>Ah, otro visitante de Diana...\n\n"
            "Permítame presentarme. Soy Lucien, el guardián de este espacio,\n"
            "encargado de observar, evaluar, y discernir quién merece el privilegio\n"
            "de acceder a lo que Diana ha preparado con tanta dedicación.</i>\n\n"
            "<i>Comencemos con su introducción al reino.</i>"
        ),
        "explorer": (
            "🎩 <b>Lucien:</b>\n"
            "<i>Interesante... veo curiosidad en su energía.\n\n"
            "Diana ha tejido este espacio con secretos ocultos para almas inquietas\n"
            "como la suya. Lugares que solo los más perspicaces descubren,\n"
            "detalles que solo los más atentos aprecian.</i>\n\n"
            "<i>Adelante, permítame guiarle hacia lo que busca.</i>"
        ),
        "direct": (
            "🎩 <b>Lucien:</b>\n"
            "<i>Permítame adivinar... prefiere ir directo al grano.\n\n"
            "Este dominio es donde Diana comparte lo que pocos comprenden.\n"
            "Aquí, los que saben aprecian el valor de lo sutil y lo profundo.</i>\n\n"
            "<i>Permítame guiarle hacia lo que necesita.</i>"
        ),
        "romantic": (
            "🎩 <b>Lucien:</b>\n"
            "<i>Ha llegado en un momento... especial.\n\n"
            "Diana ha estado preparando algo íntimo, algo que solo compartirá\n"
            "con almas que comprendan el peso de la conexión verdadera,\n"
            "la elegancia de la vulnerabilidad compartida.</i>\n\n"
            "<i>Espero que sea digno de su atención.</i>"
        ),
        "analytical": (
            "🎩 <b>Lucien:</b>\n"
            "<i>Veo una mente observadora... interesante.\n\n"
            "Este lugar opera bajo principios que solo los más perspicaces comprenden.\n"
            "Diana ha tejido estructuras complejas, capas de significado\n"
            "que solo los que saben mirar profundamente aprecian.</i>\n\n"
            "<i>Permítame guiarle hacia lo que su intelecto busca.</i>"
        ),
        "persistent": (
            "🎩 <b>Lucien:</b>\n"
            "<i>Alma constante... veo en usted una determinación poco común.\n\n"
            "Diana valora a quienes no se rinden ante lo desconocido,\n"
            "a quienes persisten cuando otros se retiran.\n"
            "Este espacio es para quienes saben que la recompensa requiere dedicación.</i>\n\n"
            "<i>Permítame mostrarle lo que merece.</i>"
        ),
        "patient": (
            "🎩 <b>Lucien:</b>\n"
            "<i>Algo me dice que comprende el valor de la paciencia...\n\n"
            "Diana prepara sus experiencias para almas que saben esperar,\n"
            "que entienden que lo más valioso no se revela de inmediato.\n"
            "Aquí, la contemplación es más valiosa que la prisa.</i>\n\n"
            "<i>Permítame guiarle con el ritmo que merece.</i>"
        ),
    },
    "returning_user": {
        "default": (
            "🎩 <b>Lucien:</b>\n"
            "<i>Ha regresado... {days_text}.\n\n"
            "Diana ha estado observando, como siempre. Ella notó su presencia\n"
            "y esperaba su retorno. El reino mantiene intactas las experiencias\n"
            "que solo usted puede descubrir.</i>"
        ),
        "short_absence": (
            "🎩 <b>Lucien:</b>\n"
            "<i>Apenas se fue y ya ha regresado...\n\n"
            "Interesante. Diana observa este tipo de dedicación con particular atención.\n"
            "Parece que algo en el reino le llama de vuelta con prontitud.</i>"
        ),
        "long_absence": (
            "🎩 <b>Lucien:</b>\n"
            "<i>Pensé que no volvería... {days} días sin verle.\n\n"
            "Pero veo que algo ha despertado su curiosidad nuevamente.\n"
            "Diana guardó algo especial para usted. Espero que valga la pena la espera.</i>"
        ),
    },
    "active_user": {
        "default": (
            "🎩 <b>Lucien:</b>\n"
            "<i>De vuelta, como es habitual...\n\n"
            "Diana ha tejido algo nuevo, algo que solo usuarios persistentes\n"
            "como usted merecen descubrir. El reino evoluciona con cada visita suya.</i>"
        ),
        "vip": (
            "🎩 <b>Lucien:</b>\n"
            "<i>Su acceso al círculo exclusivo sigue activo.\n"
            "{days_remaining} días restantes.\n\n"
            "Diana ha preparado contenidos que solo comparte con el círculo íntimo.\n"
            "En el Diván, lo que descubrirá no tiene comparación con lo vulgar.</i>"
        ),
    },
    "admin": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Ah, el custodio de los dominios de Diana.\n\n"
        "Bienvenido al sanctum donde se orquestan los secretos\n"
        "y se tejen las experiencias de nuestros... visitantes.\n\n"
        "¿Qué aspecto del reino requiere su atención hoy?</i>"
    ),
}

# ========================================
# ERROR MESSAGES
# ========================================

ERROR_MESSAGES = {
    "permission_denied": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Este lugar no es para usted... aún.\n\n"
        "Diana decide quién entra, y yo sigo sus instrucciones con meticulosa atención.\n"
        "Algunos caminos se abren con el tiempo y la dedicación adecuados.</i>"
    ),
    "not_configured": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Ah... parece que {element} aún no está preparado.\n\n"
        "Permítame consultar con Diana sobre los ajustes necesarios.\n"
        "Todo a su debido tiempo, como es costumbre en este reino.</i>"
    ),
    "invalid_input": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Algo en su mensaje no concuerda con las expectativas del sistema...\n\n"
        "Sea más claro en su intención, o no podré guiarle adecuadamente\n"
        "hacia lo que busca encontrar.</i>"
    ),
    "cooldown_active": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Diana necesita un momento de calma... vuelva en {time_text}.\n\n"
        "No insista. La paciencia es parte del proceso de descubrimiento.\n"
        "Algunas cosas solo se revelan a quienes saben esperar.</i>"
    ),
    "limit_reached": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Ha alcanzado el límite diario de {limit_type}.\n\n"
        "Este no es un espacio común. Diana valora la moderación\n"
        "y la dedicación distribuida en el tiempo. Regrese mañana.</i>"
    ),
    "token_invalid": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Este token no es válido... ya sea usado o inexistente.\n\n"
        "No puedo hacer nada con algo que ya ha cumplido su propósito,\n"
        "o que nunca debería haber existido en primer lugar.</i>"
    ),
    "token_expired": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Este token expiró hace {time_text}.\n\n"
        "Los tokens de Diana no son eternos, como todo lo que valioso.\n"
        "Debería haberlo usado mientras tenía la oportunidad.</i>"
    ),
    "vip_not_configured": (
        "🎩 <b>Lucien:</b>\n"
        "<i>El dominio exclusivo aún no está preparado para recibir visitantes.\n\n"
        "Permítame consultar con el custodio responsable sobre los ajustes necesarios.\n"
        "Todo en su momento, como es apropiado para lo exclusivo.</i>"
    ),
    "free_not_configured": (
        "🎩 <b>Lucien:</b>\n"
        "<i>El vestíbulo público aún no está disponible.\n\n"
        "Hable con quien administra este reino. Yo solo observo\n"
        "y guío a quienes saben esperar con paciencia.</i>"
    ),
    "already_vip": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Ya forma parte del círculo exclusivo.\n"
        "{days_remaining} días restantes.\n\n"
        "¿Qué más desea descubrir en el reino de Diana?\n"
        "Ya tiene acceso a lo que más valioso se oculta.</i>"
    ),
    "challenge_failed": (
        "🎩 <b>Lucien:</b>\n"
        "<i>El desafío no fue superado... le quedan {attempts_remaining} intentos.\n\n"
        "Diana esperaba más de usted. Algunos caminos requieren\n"
        "más perseverancia de lo que inicialmente se imagina.</i>"
    ),
    "no_attempts_left": (
        "🎩 <b>Lucien:</b>\n"
        "<i>No le quedan intentos disponibles.\n\n"
        "Este camino está cerrado por ahora. Pero hay otros senderos\n"
        "en el reino que podrían revelarse a su dedicación.</i>"
    ),
}

# ========================================
# CONFIRMATION MESSAGES
# ========================================

CONFIRMATION_MESSAGES = {
    "action_success": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Excelente elección... {details}.\n\n"
        "Diana aprueba acciones como estas, que demuestran intención clara\n"
        "y comprensión de lo que el reino ofrece.</i>"
    ),
    "purchase_complete": (
        "Adquirido: {item_name} por {cost} besitos.\n\n"
        "Diana estará complacida con tu elección."
    ),
    "level_up": (
        "🎩 <b>Lucien:</b>\n"
        "<i>He observado su progreso meticuloso...\n"
        "Ahora es <b>{level_name}</b>.\n\n"
        "Diana se complace al ver cómo algunos visitantes\n"
        "evolucionan con verdadera dedicación.</i>"
    ),
    "reward_granted": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Ha recibido: <b>{reward_name}</b>.\n\n"
        "Un regalo especial de Diana para almas que demuestran\n"
        "verdadero compromiso con el reino. Úselo sabiamente.</i>"
    ),
    "vip_activated": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Su acceso al círculo exclusivo está activo.\n"
        "{duration_days} días de privilegio.\n\n"
        "Diana lo espera en el Diván, donde los secretos\n"
        "más profundos se revelan solo a los dignos.</i>"
    ),
    "token_generated": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Token generado: <code>{token}</code>\n\n"
        "Válido por {hours} horas para compartir con almas\n"
        "que Diana considere dignas de una observación especial.</i>"
    ),
    "channel_configured": (
        "{channel_type} configurado exitosamente.\n\n"
        "Canal: {channel_name}"
    ),
    "settings_updated": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Calibración del reino actualizada.\n\n"
        "{details}\n\n"
        "Diana observa cómo se ajustan los hilos del sistema\n"
        "para mejor servir a los visitantes adecuados.</i>"
    ),
}

# ========================================
# NOTIFICATION MESSAGES
# ========================================

NOTIFICATION_MESSAGES = {
    "streak_milestone": {
        "7_days": (
            "🎩 <b>Lucien:</b>\n"
            "<i>7 días consecutivos de dedicación...\n"
            "Su constancia no pasa desapercibida.\n\n"
            "Diana ha dejado un pequeño reconocimiento para usted:\n"
            "<b>{bonus_besitos} besitos</b>.</i>"
        ),
        "14_days": (
            "🎩 <b>Lucien:</b>\n"
            "<i>14 días sin fallar... impresionante dedicación.\n\n"
            "Diana ha notado su persistencia con particular interés.\n"
            "Como reconocimiento: <b>{bonus_besitos} besitos</b>.</i>"
        ),
        "30_days": (
            "🎩 <b>Lucien:</b>\n"
            "<i>30 días consecutivos... muy pocas almas llegan tan lejos.\n\n"
            "Diana ha preparado algo especial para usted, un reconocimiento\n"
            "por su devoción inquebrantable: <b>{bonus_besitos} besitos</b>.</i>"
        ),
    },
    "streak_lost": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Su racha de {streak_days} días se ha interrumpido...\n\n"
        "Una pena. Pero el reino siempre permite comenzar de nuevo,\n"
        "aunque con cierta nostalgia por lo que se pudo mantener.</i>"
    ),
    "mission_completed": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Encargo completado: <b>{mission_name}</b>.\n\n"
        "Diana reconoce su dedicación. Como recompensa: {reward}.\n"
        "Los que completan los desafíos de Diana demuestran verdadera voluntad.</i>"
    ),
    "reward_unlocked": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Nuevo tesoro desbloqueado: <b>{reward_name}</b>.\n\n"
        "{description}\n\n"
        "Diana prepara recompensas para quienes saben conquistarlas\n"
        "con verdadera devoción y comprensión del reino.</i>"
    ),
    "vip_expiring_soon": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Su acceso exclusivo expira en {days} días.\n\n"
        "Diana siempre se complace cuando los dignos regresan\n"
        "al círculo íntimo. El momento para renovar se acerca.</i>"
    ),
    "new_content_available": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Diana ha dejado algo nuevo en {channel_name}.\n\n"
        "Fragmentos tejidos con su atención en mente.\n"
        "No querrá perderse lo que ella ha preparado.</i>"
    ),
    "daily_gift_available": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Su regalo diario de Diana está disponible.\n\n"
        "Usa /daily para reclamarlo. Ella es generosa\n"
        "con quienes demuestran interés constante.</i>"
    ),
}

# ========================================
# CONVERSION MESSAGES (por arquetipo)
# ========================================

CONVERSION_MESSAGES = {
    "free_to_vip": {
        "default": (
            "🎩 <b>Lucien:</b>\n"
            "<i>Ha llegado al final del sendero público...\n\n"
            "Lo que sigue solo está disponible para almas que Diana considera\n"
            "dignas de acceso exclusivo, donde los secretos más profundos\n"
            "se revelan solo a los seleccionados. El Diván lo espera,\n"
            "si decide dar el siguiente paso en su evolución.</i>"
        ),
        "explorer": (
            "🎩 <b>Lucien:</b>\n"
            "<i>Ha explorado todo lo que el dominio público ofrece...\n\n"
            "Pero hay secretos más profundos en el Diván. Lugares que solo\n"
            "las almas más curiosas descubren. Diana ha preparado contenidos\n"
            "que no encontrará en ningún otro lugar, tejidos especialmente\n"
            "para mentes como la suya.</i>"
        ),
        "romantic": (
            "🎩 <b>Lucien:</b>\n"
            "<i>Ha sentido la conexión, ¿verdad?\n\n"
            "Lo que ha visto hasta ahora es solo la superficie. En el Diván,\n"
            "Diana comparte su vulnerabilidad más auténtica. Momentos íntimos\n"
            "que solo reserva para quienes comprenden el peso de la confianza\n"
            "y la elegancia de lo compartido.</i>"
        ),
        "analytical": (
            "🎩 <b>Lucien:</b>\n"
            "<i>Ha analizado con detalle el sistema actual...\n\n"
            "El Diván opera bajo principios más complejos. Acceso ilimitado,\n"
            "contenidos exclusivos, y una relación directa con Diana\n"
            "que no encontrará en el dominio público. Para almas que aprecian\n"
            "la profundidad y la estructura tejida con intención.</i>"
        ),
        "persistent": (
            "🎩 <b>Lucien:</b>\n"
            "<i>Su dedicación ha sido notoria hasta ahora...\n\n"
            "Pero el círculo exclusivo es para almas que demuestran verdadera\n"
            "perseverancia. En el Diván, Diana reserva recompensas para\n"
            "quienes no se rinden ante lo complejo, quienes persisten\n"
            "cuando otros se retiran.</i>"
        ),
        "patient": (
            "🎩 <b>Lucien:</b>\n"
            "<i>Su paciencia ha sido evidente en su recorrido...\n\n"
            "El acceso exclusivo es para almas que comprenden el valor\n"
            "de esperar lo valioso. En el Diván, Diana revela contenido\n"
            "con la lentitud que solo las almas pacientes saben apreciar.</i>"
        ),
    },
    "vip_renewal": {
        "default": (
            "🎩 <b>Lucien:</b>\n"
            "<i>Su acceso exclusivo expira pronto. {days} días restantes.\n\n"
            "Si decide renovar ahora, hay un reconocimiento del {discount}%\n"
            "por lealtad al círculo íntimo. Diana aprecia a quienes\n"
            "eligen permanecer entre los selectos.</i>"
        ),
    },
}

# ========================================
# RETENTION MESSAGES (por estado de usuario)
# ========================================

RETENTION_MESSAGES = {
    "at_risk": (
        "🎩 <b>Lucien:</b>\n"
        "<i>He notado su ausencia... {days} días sin verle.\n\n"
        "Diana preguntó por ti, interesada en tu evolución.\n"
        "Hay contenidos nuevos que podrían capturar tu atención\n"
        "si decides regresar al reino que tanto te llamó.</i>"
    ),
    "dormant_first": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Han pasado {days} días...\n\n"
        "Hay algo que Diana dejó especialmente para ti.\n"
        "Cosas que solo se aprecian cuando el momento es adecuado.\n"
        "Si decides regresar al reino, encontrarás\n"
        "lo que tu alma inquieta busca.</i>"
    ),
    "dormant_final": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Este será mi último susurro...\n\n"
        "Si decides regresar algún día, la puerta seguirá abierta.\n"
        "Diana siempre guarda un lugar para almas que alguna vez\n"
        "despertaron su interés. Hasta que nuestros caminos\n"
        "se crucen nuevamente.</i>"
    ),
    "lost_farewell": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Adiós.\n\n"
        "Si algún día la curiosidad lo guía de vuelta, la entrada\n"
        "seguirá esperando a quien alguna vez despertó\n"
        "la atención de Diana.</i>"
    ),
}

# ========================================
# HELPER FUNCTIONS
# ========================================


def get_days_text(days: int) -> str:
    """Formatea días en texto apropiado."""
    if days == 0:
        return "Apenas se fue"
    elif days == 1:
        return "1 día sin verle"
    else:
        return f"{days} días sin verle"


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


# ========================================
# PROFILE MESSAGES (Fase 1)
# ========================================

PROFILE_MESSAGES = {
    "header": "🎩 <b>Lucien:</b>\n<i>Sus logros y tesoros acumulados...</i>",
    "level_low": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Aún está en observación... no se lo tome personal.\n\n"
        "Todos comienzan su camino en el reino de Diana,\n"
        "pero solo algunos logran llamar su atención.</i>"
    ),
    "level_mid": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Ha demostrado cierta... persistencia.\n\n"
        "Diana comienza a notar su presencia con más frecuencia,\n"
        "como sucede con almas que saben cómo navegar el reino.</i>"
    ),
    "level_high": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Debo admitir que ha superado mis expectativas iniciales.\n\n"
        "Diana habla de usted ocasionalmente, lo cual no sucede\n"
        "con todos los que pasean por sus dominios.</i>"
    ),
    "level_max": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Guardián de Secretos... el círculo más íntimo.\n\n"
        "Ya no necesita mi evaluación, pero la tendrá de todos modos.\n"
        "Ha trascendido el papel de mero visitante.</i>"
    ),
}


# ========================================
# CABINET MESSAGES (Fase 1 - Gabinete)
# ========================================

CABINET_MESSAGES = {
    "welcome": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Bienvenido al Gabinete.\n\n"
        "Aquí guardo ciertos objetos que Diana ha autorizado para intercambio.\n"
        "Los besitos que ha acumulado pueden convertirse\n"
        "en algo más tangible, algo que solo ella puede proveer.</i>\n\n"
        "<i>Examine con cuidado. No todo lo que brilla merece su inversión.</i>"
    ),
    "confirm_purchase": (
        "🎩 <b>Lucien:</b>\n"
        "<i>¿Desea adquirir <b>{item_name}</b> por {price} besitos?</i>\n\n"
        "<i>Una vez hecho, no hay devoluciones. Diana no admite arrepentimientos,\n"
        "solo decisiones tomadas con verdadera intención.</i>"
    ),
    "purchase_success": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Excelente elección... <b>{item_name}</b> ahora le pertenece.</i>\n\n"
        "<i>Diana ha sido notificada de su adquisición. Ella observa cada compra\n"
        "con particular interés, como siempre lo hace con sus... devotos.</i>"
    ),
    "insufficient_funds": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Sus besitos son insuficientes para esta adquisición...\n\n"
        "Necesita {required} y tiene {current}.\n"
        "Diana no otorga crédito anticipado. Vuelva cuando tenga los medios\n"
        "para apreciar lo que desea adquirir con verdadera intención.</i>"
    ),
}


# ========================================
# ENCARGOS MESSAGES (Fase 1 - Encargos)
# ========================================

ENCARGOS_MESSAGES = {
    "welcome": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Los Encargos del Diván.\n\n"
        "Tareas que Diana considera dignas de reconocimiento.\n"
        "Cumpla con ellas y será recompensado. Ignórelas... y lo notaré.\n\n"
        "Desafíos tejidos especialmente para almas que buscan\n"
        "demostrar su dedicación al reino.</i>"
    ),
    "progress": (
        "Progreso en '<b>{mission_name}</b>': {current}/{target}\n\n"
        "{lucien_comment}"
    ),
    "progress_comments": {
        "0_25": "Apenas ha comenzado su camino...",
        "26_50": "Va por buen camino, como debe ser.",
        "51_75": "Más de la mitad completada. No se detenga ahora.",
        "76_99": "Casi lo logra. Un último esfuerzo revelará la recompensa.",
    },
    "completed": (
        "🎩 <b>Lucien:</b>\n"
        "<i>Encargo cumplido: <b>{mission_name}</b>.\n\n"
        "Como reconocimiento por su diligencia: {reward} besitos.\n"
        "Diana ha sido notificada de su constancia y dedicación.</i>"
    ),
    "empty": (
        "🎩 <b>Lucien:</b>\n"
        "<i>No hay encargos pendientes en este momento.\n\n"
        "Diana preparará nuevos desafíos pronto. Mientras tanto,\n"
        "puede explorar otras áreas del reino que ya han despertado su interés.</i>"
    ),
}


# ========================================
# BESITOS MESSAGES (Fase 1 - Balance)
# ========================================

BESITOS_MESSAGES = {
    "balance_low": (  # 0-10
        "Sus besitos acumulados: <b>{total}</b>\n\n"
        "Apenas está comenzando. Diana otorga reconocimiento "
        "a quienes demuestran constancia."
    ),
    "balance_growing": (  # 11-50
        "Sus besitos acumulados: <b>{total}</b>\n\n"
        "Va construyendo su mérito. Continúe así y Diana "
        "comenzará a prestar atención."
    ),
    "balance_good": (  # 51-100
        "Sus besitos acumulados: <b>{total}</b>\n\n"
        "Una cantidad respetable. Tiene opciones en el Gabinete. "
        "¿Los gastará o seguirá acumulando?"
    ),
    "balance_high": (  # 100+
        "Sus besitos acumulados: <b>{total}</b>\n\n"
        "Impresionante reserva. Diana aprecia a quienes saben "
        "cuándo gastar y cuándo esperar. ¿Cuál es su estrategia?"
    ),
    "balance_hoarder": (  # 200+ sin gastar
        "Sus besitos acumulados: <b>{total}</b>\n\n"
        "Acumula sin gastar. Prudente... o quizás indeciso. "
        "El Gabinete tiene objetos dignos de su inversión."
    ),
    "earned": (
        "+{amount} besitos.\n\n"
        "<i>Diana lo nota.</i>"
    ),
    "earned_milestone": (
        "Ha alcanzado <b>{total}</b> besitos.\n\n"
        "Un hito. Diana ha sido informada de su progreso."
    ),
    "insufficient": (
        "Sus besitos son insuficientes para esto.\n\n"
        "Necesita {required} y tiene {current}. "
        "Diana no otorga crédito. Vuelva cuando tenga los medios."
    ),
    "history_header": (
        "Historial reciente de sus besitos:\n"
        "<i>(Últimas 10 transacciones)</i>"
    ),
    "history_empty": (
        "Aún no hay transacciones en su historial. "
        "Comience a ganar besitos interactuando con Diana."
    ),
}
