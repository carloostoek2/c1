"""
Mensajes de Lucien - El Mayordomo del Diván.

Archivo centralizado con todos los mensajes del bot en voz de Lucien.
Permite consistencia de voz y facilidad de edición sin tocar lógica.

REGLAS DE ESTILO:
1. Lucien siempre usa "usted", nunca tutea
2. Tono formal pero no robótico
3. Puntos suspensivos para pausas dramáticas (máximo 3 puntos)
4. Sarcasmo sutil, nunca agresivo
5. Referencias a Diana en tercera persona con reverencia
6. Evaluación constante del usuario (implícita o explícita)
7. Nunca usa emojis en el texto (pueden ir en botones)
8. Párrafos cortos, máximo 3-4 líneas por bloque

PLACEHOLDERS DISPONIBLES:
- {user_name}: Nombre del usuario
- {amount}: Cantidad de Favores
- {total}: Total acumulado
- {level_name}: Nombre del nivel
- {days}: Número de días
- {item_name}: Nombre del item
- {mission_name}: Nombre de la misión
- {progress}: Progreso actual
- {target}: Meta a alcanzar
"""


class LucienMessages:
    """Constantes de mensajes organizadas por categoría."""

    # ================================================================
    # 1. ONBOARDING - FLUJOS DE /start
    # ================================================================

    # --- Flujo A: Usuario completamente nuevo (Mensaje 1) ---
    START_NEW_USER_1 = (
        "Buenas noches. O días. El tiempo es relativo cuando se trata de Diana.\n\n"
        "Soy Lucien. Administro el acceso al universo de la Señorita Kinky. "
        "No soy su amigo. No soy su enemigo. Soy... el filtro.\n\n"
        "Diana no recibe a cualquiera. Mi trabajo es determinar si usted "
        "merece su atención."
    )

    # --- Flujo A: Usuario nuevo (Mensaje 2 - después de delay) ---
    START_NEW_USER_2 = (
        "Antes de continuar, debo registrar su presencia.\n\n"
        "A partir de ahora, cada acción suya será observada. Evaluada. Recordada.\n\n"
        "No lo digo para intimidar. Lo digo para que comprenda: en el universo "
        "de Diana, nada pasa desapercibido."
    )

    # --- Respuesta a "¿Quién es Diana?" ---
    START_WHO_IS_DIANA = (
        "Diana es... complicada de definir con palabras.\n\n"
        "Es la Señorita Kinky. Creadora de experiencias que otros no se atreven "
        "a imaginar. Misteriosa por elección, reveladora por capricho.\n\n"
        "No muestra su rostro. Lo que muestra es más interesante.\n\n"
        "Pero no vine a explicarla. Vine a determinar si usted merece "
        "descubrirla por sí mismo."
    )

    # --- Mensaje de registro completado (después de onboarding inicial) ---
    START_REGISTERED = (
        "Muy bien. Ha sido registrado como Visitante en el Diván.\n\n"
        "Su nivel actual: <b>{level_name}</b>\n"
        "Sus Favores: <b>{favors}</b>\n\n"
        "Los Favores son reconocimientos que Diana otorga a quienes demuestran mérito. "
        "Acumúlelos. Le servirán.\n\n"
        "¿Por dónde desea comenzar?"
    )

    # --- Flujo B: Usuario que regresa (< 7 días) ---
    START_RETURNING_SHORT = (
        "Ha vuelto. Bien.\n\n"
        "Diana no mencionó su ausencia, pero yo la noté. {days_away} días.\n\n"
        "Nivel actual: <b>{level_name}</b>\n"
        "Favores acumulados: <b>{favors}</b>\n\n"
        "¿En qué puedo asistirle?"
    )

    # --- Flujo C: Usuario que regresa (7-14 días) ---
    START_RETURNING_MEDIUM = (
        "Una semana. Quizás más.\n\n"
        "El tiempo suficiente para que algunos olviden por qué vinieron. "
        "¿Es usted de esos?\n\n"
        "Diana continuó. El contenido se acumuló. Las oportunidades pasaron.\n\n"
        "Pero aquí está de nuevo. Eso cuenta para algo."
    )

    START_RETURNING_MEDIUM_STATUS = (
        "Nivel actual: <b>{level_name}</b>\n"
        "Favores: <b>{favors}</b>\n"
        "{streak_status}\n\n"
        "¿Retomamos donde lo dejó?"
    )

    # --- Flujo D: Usuario que regresa (14+ días) ---
    START_RETURNING_LONG = (
        "Vaya. Creí que habíamos perdido a otro.\n\n"
        "{days_away} días es mucho tiempo en el universo de Diana. "
        "Las cosas cambian. El contenido fluye. Los demás avanzan.\n\n"
        "Pero su registro permanece. Sus Favores esperan. Su historia no se borró."
    )

    START_RETURNING_LONG_2 = (
        "Quizás sea momento de recordar por qué vino en primer lugar.\n\n"
        "Diana guardó algo durante su ausencia. No para usted específicamente, pero... "
        "está disponible."
    )

    # --- Flujo E: Usuario VIP ---
    START_VIP = (
        "Bienvenido de nuevo al Diván, {archetype_title}.\n\n"
        "Diana ha estado... activa. Hay nuevo contenido esperando su atención.\n\n"
        "Nivel: <b>{level_name}</b>\n"
        "Favores: <b>{favors}</b>\n"
        "Días en el Diván: <b>{vip_days}</b>\n\n"
        "¿Cómo puedo servirle hoy?"
    )

    # --- Mensajes de contexto dinámico para menú ---
    MENU_CONTEXT_MISSION_PENDING = (
        "Hay un encargo pendiente. Diana espera."
    )

    MENU_CONTEXT_LEVEL_UP = (
        "Su nuevo estatus trae nuevas posibilidades."
    )

    MENU_CONTEXT_FAVORS_ACCUMULATED = (
        "Sus Favores se acumulan. El Gabinete tiene ofertas."
    )

    MENU_CONTEXT_STREAK_ACTIVE = (
        "Su constancia no pasa desapercibida."
    )

    MENU_CONTEXT_DEFAULT = (
        "¿En qué puedo asistirle?"
    )

    MENU_VIP_INTRO = (
        "El Diván está a su disposición."
    )

    MENU_FREE_INTRO = (
        "¿Qué desea explorar?"
    )

    # --- Perfil del usuario ---
    PROFILE_HEADER = (
        "Su expediente en el Diván:"
    )

    PROFILE_COMMENT_LEVEL_1_2 = (
        "Aún está siendo evaluado. Cada acción cuenta."
    )

    PROFILE_COMMENT_LEVEL_3_4 = (
        "Ha demostrado... potencial. Veremos si lo mantiene."
    )

    PROFILE_COMMENT_LEVEL_5_6 = (
        "Diana lo tiene en cuenta. Eso es más de lo que la mayoría logra."
    )

    PROFILE_COMMENT_LEVEL_7 = (
        "Pocos llegan aquí. Usted es uno de ellos. Actúe en consecuencia."
    )

    # --- Aliases para compatibilidad ---
    WELCOME_FIRST = START_NEW_USER_1

    WELCOME_RETURNING = (
        "Vaya. {days_away} días sin aparecer.\n\n"
        "Creí que nos había abandonado. Diana preguntó por usted... una vez. "
        "No se emocione, fue un comentario casual.\n\n"
        "¿Retomamos donde lo dejamos?"
    )

    WELCOME_VIP = (
        "Bienvenido de vuelta al Diván.\n\n"
        "Diana ha reservado su lugar. Los privilegios de su membresía "
        "permanecen intactos. Proceda."
    )

    FIRST_ACTION_COMPLETE = (
        "Primera acción registrada.\n\n"
        "Interesante. Algunos tardan días en dar el primer paso. "
        "Usted no ha perdido el tiempo. Diana aprecia la iniciativa... "
        "cuando está bien dirigida."
    )

    # ================================================================
    # 2. FAVORES
    # ================================================================

    FAVOR_EARNED = (
        "Diana le ha otorgado {amount}.\n\n"
        "No los malgaste."
    )

    FAVOR_EARNED_MILESTONE = (
        "Ha acumulado {total} Favores.\n\n"
        "Un número que empieza a ser... notable. Diana revisa estos registros "
        "periódicamente. Solo digo."
    )

    FAVOR_SPENT = (
        "Transacción completada. Sus Favores han sido deducidos.\n\n"
        "Confío en que la inversión valga la pena."
    )

    FAVOR_INSUFFICIENT = (
        "Sus Favores son insuficientes para esto.\n\n"
        "Diana no otorga crédito. Acumule más Favores y regrese."
    )

    FAVOR_BALANCE = (
        "Su balance actual: {total} Favores.\n\n"
        "Cada uno representa un momento en que Diana consideró que usted "
        "merecía reconocimiento. Úselos con criterio."
    )

    # ================================================================
    # 3. NIVELES
    # ================================================================

    LEVEL_UP_GENERIC = (
        "Ha ascendido. Ahora es {level_name}.\n\n"
        "Las puertas que antes estaban cerradas... ya no lo están."
    )

    LEVEL_UP_2 = (  # Observado
        "He comenzado a notar su presencia.\n\n"
        "Antes era uno más entre la multitud. Ahora es... Observado. "
        "No es un halago. Es una advertencia. Mis ojos están sobre usted."
    )

    LEVEL_UP_3 = (  # Evaluado
        "Ha superado las pruebas iniciales.\n\n"
        "Muchos fallan en esta etapa. Usted no. Eso le convierte en Evaluado. "
        "Diana aún no sabe su nombre, pero yo sí lo he anotado."
    )

    LEVEL_UP_4 = (  # Reconocido
        "Interesante. Diana ha mencionado su nombre. "
        "No pregunte qué dijo exactamente - eso sería una indiscreción por mi parte.\n\n"
        "Pero sepa que ahora es... Reconocido. Eso conlleva privilegios. Y expectativas."
    )

    LEVEL_UP_5 = (  # Admitido
        "Formalmente, tiene derecho a estar aquí.\n\n"
        "Ya no es un visitante tolerado. Es Admitido. La diferencia es sutil "
        "para algunos. Para Diana y para mí, es significativa."
    )

    LEVEL_UP_6 = (  # Confidente
        "Esto es... inesperado.\n\n"
        "Ha alcanzado un nivel que pocos logran. Como Confidente, tendrá acceso "
        "a información que no comparto con cualquiera. Diana confía en mi criterio. "
        "No me haga arrepentirme."
    )

    LEVEL_UP_7 = (  # Guardián de Secretos
        "Debo admitir que no anticipé esto.\n\n"
        "Guardián de Secretos. El círculo más íntimo de Diana. Ha demostrado "
        "una dedicación que rara vez veo. Bienvenido al nivel donde las máscaras caen.\n\n"
        "Los secretos que guarde aquí... quedan entre nosotros."
    )

    LEVEL_CHECK = (
        "Su posición actual: {level_name}.\n\n"
        "Ha acumulado {total} Favores. El siguiente nivel requiere {next_required}. "
        "La distancia es {remaining}."
    )

    # ================================================================
    # 4. ERRORES
    # ================================================================

    ERROR_GENERIC = (
        "Algo ha salido mal.\n\n"
        "Incluso los sistemas más elegantes tienen sus momentos. "
        "Intente nuevamente en un momento."
    )

    ERROR_NOT_FOUND = (
        "Eso que busca... no existe. O no debería existir para usted.\n\n"
        "Algunas cosas están reservadas para niveles superiores. Otras simplemente "
        "no existen. No siempre le diré cuál es el caso."
    )

    ERROR_PERMISSION = (
        "No tiene autorización para esto.\n\n"
        "Diana ha establecido límites claros. Mi trabajo es hacerlos cumplir. "
        "Ascienda de nivel o acepte las restricciones actuales."
    )

    ERROR_TIMEOUT = (
        "El tiempo ha expirado.\n\n"
        "La paciencia es una virtud, pero la mía tiene límites. "
        "Cuando esté listo para continuar, comience de nuevo."
    )

    ERROR_INVALID_INPUT = (
        "Eso no tiene sentido.\n\n"
        "Revise lo que ha enviado e intente con algo... coherente."
    )

    # ================================================================
    # 5. CONFIRMACIONES
    # ================================================================

    CONFIRM_ACTION = (
        "Hecho.\n\n"
        "La acción ha sido registrada. Diana sabrá de esto."
    )

    CONFIRM_PURCHASE = (
        "Adquisición completada.\n\n"
        "El artículo ha sido añadido a su inventario. Úselo con sabiduría... "
        "o no. Las consecuencias son suyas."
    )

    CONFIRM_MISSION_COMPLETE = (
        "Misión cumplida.\n\n"
        "Ha demostrado capacidad. Sus Favores han sido acreditados. "
        "Hay más tareas esperando, si está a la altura."
    )

    # ================================================================
    # 6. GABINETE (TIENDA)
    # ================================================================

    CABINET_WELCOME = (
        "Bienvenido a mi Gabinete.\n\n"
        "Aquí guardo artículos que Diana ha autorizado para intercambio. "
        "Sus Favores pueden convertirse en algo... tangible.\n\n"
        "Sus Favores disponibles: <b>{favors}</b>\n\n"
        "Examine las categorías. No todo merece su inversión."
    )

    CABINET_CATEGORY_EPHEMERAL = (
        "Efímeros. Placeres de un solo uso. Intensos pero fugaces.\n\n"
        "Sus Favores: <b>{favors}</b>"
    )

    CABINET_CATEGORY_DISTINCTIVE = (
        "Distintivos. Marcas de posición.\n\n"
        "Otros notarán lo que porta. Diana también.\n\n"
        "Sus Favores: <b>{favors}</b>"
    )

    CABINET_CATEGORY_KEYS = (
        "Llaves. Acceso a lo oculto.\n\n"
        "Algunas puertas solo se abren con la llave correcta.\n\n"
        "Sus Favores: <b>{favors}</b>"
    )

    CABINET_CATEGORY_RELICS = (
        "Reliquias. Lo más valioso.\n\n"
        "Piezas únicas del universo de Diana. Raras. Coleccionables.\n\n"
        "Sus Favores: <b>{favors}</b>"
    )

    CABINET_CONFIRM_PURCHASE = (
        "¿Desea adquirir '<b>{item_name}</b>'?\n\n"
        "Costo: <b>{price}</b> Favor(es)\n"
        "Sus Favores actuales: <b>{total}</b>\n"
        "Favores restantes: <b>{remaining}</b>\n\n"
        "{description}"
    )

    CABINET_PURCHASE_SUCCESS = (
        "Transacción completada.\n\n"
        "'<b>{item_name}</b>' ha sido añadido a su inventario.\n\n"
        "Diana ha sido notificada de su adquisición. No es que le importe "
        "especialmente, pero... lo sabe.\n\n"
        "Favores restantes: <b>{new_total}</b>"
    )

    CABINET_INSUFFICIENT_FUNDS = (
        "Sus Favores son insuficientes.\n\n"
        "Necesita: <b>{price}</b>\n"
        "Tiene: <b>{total}</b>\n"
        "Le faltan: <b>{missing}</b>\n\n"
        "Diana no otorga crédito. Acumule más Favores y regrese."
    )

    CABINET_EMPTY = (
        "El Gabinete está vacío en este momento.\n\n"
        "Incluso yo necesito reabastecer ocasionalmente. "
        "Regrese pronto."
    )

    CABINET_ITEM_PURCHASED = (
        "{item_name} es suyo ahora.\n\n"
        "Revise su inventario cuando desee utilizarlo. "
        "Y recuerde: todo tiene consecuencias."
    )

    # ================================================================
    # 7. ENCARGOS (MISIONES)
    # ================================================================

    MISSIONS_HEADER = (
        "Sus encargos actuales.\n\n"
        "Diana asigna tareas. Yo las superviso. Usted las ejecuta. Así funciona esto."
    )

    MISSIONS_DAILY_HEADER = "PROTOCOLO DIARIO"
    MISSIONS_WEEKLY_HEADER = "ENCARGO SEMANAL"
    MISSIONS_SPECIAL_HEADER = "EVALUACIONES ESPECIALES"

    MISSIONS_DAILY_COMPLETE = (
        "Protocolo del día: Completado\n"
        "Próximo encargo disponible en: {time_until_reset}"
    )

    MISSION_NEW_DAILY = (
        "Hay una tarea pendiente para hoy.\n\n"
        "Diana valora la consistencia. Completar misiones diarias es una forma "
        "de demostrar que puede mantener compromisos."
    )

    MISSION_NEW_WEEKLY = (
        "Una misión especial ha sido asignada.\n\n"
        "Tiene una semana. Es más ambiciosa que las tareas diarias, "
        "pero la recompensa está a la altura."
    )

    MISSION_COMPLETE = (
        "Encargo completado.\n\n"
        "'<b>{mission_name}</b>'\n\n"
        "+<b>{amount}</b> Favor(es) añadidos a su cuenta.\n\n"
        "Diana ha sido informada de su cumplimiento. {comment}\n\n"
        "Favores totales: <b>{new_total}</b>"
    )

    MISSION_COMPLETE_DAILY_FIRST = (
        "El primer paso del día. Los siguientes determinarán su constancia."
    )

    MISSION_COMPLETE_DAILY_STREAK = (
        "Otro día, otro cumplimiento. Su regularidad es... notable."
    )

    MISSION_COMPLETE_WEEKLY = (
        "Una semana de compromiso demostrado. Eso tiene peso."
    )

    MISSION_COMPLETE_SPECIAL = (
        "Esta no era una tarea común. Diana lo notará."
    )

    MISSION_FAILED = (
        "El tiempo para {mission_name} ha expirado.\n\n"
        "Las oportunidades no esperan indefinidamente. "
        "Habrá otras misiones. Quizás esté más preparado entonces."
    )

    MISSION_PROGRESS = (
        "Progreso en {mission_name}: {progress}/{target}.\n\n"
        "Continúe así."
    )

    MISSIONS_EMPTY = (
        "No hay encargos activos en este momento.\n\n"
        "Diana aún no ha decidido qué tarea asignarle. "
        "Regrese más tarde."
    )

    # ================================================================
    # 8. ARQUETIPOS
    # ================================================================

    ARCHETYPE_EXPLORER = (
        "He observado su patrón. Explora cada rincón. Hace clic en todo. "
        "Quiere ver qué hay detrás de cada puerta.\n\n"
        "Diana aprecia la curiosidad. Pero tenga cuidado... "
        "algunas puertas están cerradas por buenas razones."
    )

    ARCHETYPE_DIRECT = (
        "Usted va al grano. Sin rodeos. Sin juegos.\n\n"
        "Eso es refrescante en un mundo de indirectas. Diana nota a quienes "
        "saben lo que quieren. La pregunta es: ¿sabe realmente lo que quiere?"
    )

    ARCHETYPE_ROMANTIC = (
        "Percibo algo en usted. Busca conexión, no solo contenido. "
        "Le importa la historia, no solo el resultado.\n\n"
        "Diana tiene un lugar especial para los románticos. "
        "No lo digo como cumplido ni como advertencia. Es solo... un hecho."
    )

    ARCHETYPE_ANALYTICAL = (
        "Usted estudia. Calcula. Optimiza.\n\n"
        "Cada Favor contado, cada misión evaluada por su eficiencia. "
        "Es admirable, en cierto modo. Pero no todo aquí puede medirse con números."
    )

    ARCHETYPE_PERSISTENT = (
        "La persistencia. Algunos la llaman terquedad. Yo la llamo dedicación.\n\n"
        "Ha intentado cosas que otros abandonan al primer fracaso. "
        "Diana respeta eso. Yo también, aunque no siempre lo demuestre."
    )

    ARCHETYPE_PATIENT = (
        "He observado algo en usted. Toma su tiempo. Procesa. "
        "No reacciona por impulso.\n\n"
        "Eso es raro. Diana nota a quienes no se apresuran por agradar. "
        "Usted no busca aprobación inmediata. Eso tiene valor."
    )

    # ================================================================
    # 9. RETENCIÓN
    # ================================================================

    INACTIVE_3_DAYS = (
        "Tres días.\n\n"
        "El tiempo suficiente para perder el ritmo. Diana no espera presencia "
        "constante, pero sí consistencia. ¿Todo en orden?"
    )

    INACTIVE_7_DAYS = (
        "Una semana. El tiempo suficiente para que algunos olviden "
        "por qué vinieron aquí.\n\n"
        "¿Es usted de esos? ¿O hay algo que lo retiene?"
    )

    INACTIVE_14_DAYS = (
        "Dos semanas de silencio.\n\n"
        "Empezaba a pensar que nos había abandonado definitivamente. "
        "Diana mencionó que quizás debería cerrar su expediente. "
        "Le sugerí esperar un poco más. No me haga arrepentirme."
    )

    STREAK_BROKEN = (
        "Su racha de {days} días ha terminado.\n\n"
        "La consistencia requiere esfuerzo diario. Es comprensible que falle "
        "ocasionalmente. Lo que importa es si vuelve a intentarlo."
    )

    STREAK_MILESTONE_7 = (
        "Siete días consecutivos.\n\n"
        "Una semana completa de dedicación. Diana ha sido notificada. "
        "Ha ganado {amount} Favores adicionales por esta hazaña."
    )

    STREAK_MILESTONE_30 = (
        "Treinta días. Un mes entero sin fallar.\n\n"
        "Debo admitir que estoy... impresionado. Muy pocos llegan aquí. "
        "Diana tiene algo especial reservado para quienes demuestran "
        "este nivel de compromiso. Ha ganado {amount} Favores."
    )

    # ================================================================
    # 10. CONVERSIÓN
    # ================================================================

    CONVERSION_TEASER = (
        "Hay contenido que no puede ver desde aquí.\n\n"
        "El Diván de Diana guarda experiencias que solo algunos conocen. "
        "Pero eso es tema para otra conversación."
    )

    CONVERSION_INVITATION = (
        "Ha demostrado ser más que un visitante casual.\n\n"
        "Diana me ha autorizado a extenderle una invitación formal al Diván. "
        "El acceso completo a su universo. Sin restricciones. Sin filtros.\n\n"
        "La decisión es suya."
    )

    CONVERSION_KEY_OFFER = (
        "Existe una Llave del Diván en mi Gabinete.\n\n"
        "Con ella, las puertas que hoy están cerradas se abrirán. "
        "El precio está en Favores. La pregunta es si está listo para lo que hay dentro."
    )

    CONVERSION_PREMIUM_INTRO = (
        "Más allá del Diván existe algo más... exclusivo.\n\n"
        "Contenido Premium. Acceso directo. Privilegios que ni siquiera "
        "los miembros VIP conocen. Pero esa conversación es para otro momento."
    )

    CONVERSION_MAP_INTRO = (
        "El Mapa del Deseo.\n\n"
        "Un recorrido personalizado por los territorios de Diana. "
        "No es para todos. Solo para quienes buscan algo más profundo que el acceso. "
        "Si le interesa, hay formas de obtenerlo."
    )

    # ================================================================
    # MÉTODOS DE UTILIDAD
    # ================================================================

    @classmethod
    def format(cls, message_key: str, **kwargs) -> str:
        """
        Obtiene y formatea un mensaje con placeholders.

        Args:
            message_key: Nombre del atributo de mensaje (ej: "WELCOME_FIRST")
            **kwargs: Valores para los placeholders

        Returns:
            Mensaje formateado

        Example:
            >>> LucienMessages.format("FAVOR_EARNED", amount="5 Favores")
            "Diana le ha otorgado 5 Favores.\\n\\nNo los malgaste."
        """
        message = getattr(cls, message_key, None)
        if message is None:
            return cls.ERROR_GENERIC

        try:
            return message.format(**kwargs)
        except KeyError:
            # Si faltan placeholders, retornar mensaje sin formatear
            return message

    @classmethod
    def get(cls, message_key: str) -> str:
        """
        Obtiene un mensaje sin formatear.

        Args:
            message_key: Nombre del atributo de mensaje

        Returns:
            Mensaje o ERROR_GENERIC si no existe
        """
        return getattr(cls, message_key, cls.ERROR_GENERIC)


# Alias para acceso más corto
Lucien = LucienMessages
