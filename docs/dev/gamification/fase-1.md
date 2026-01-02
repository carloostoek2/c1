# REQUERIMIENTO: FASE 1 - LA VOZ DE LUCIEN
## Proyecto: El Mayordomo del Diván
## Bot de Telegram para Señorita Kinky

---

# CONTEXTO

Esta fase transforma la comunicación del bot. Cada mensaje que el usuario recibe debe venir de Lucien - el mayordomo elegante, evaluador y guardián del universo de Diana.

**Dependencias:** Requiere Fase 0 completada (especialmente F0.2 - archivo de mensajes de Lucien)

**Resultado esperado:** El bot "se siente" diferente. Usuarios notarán inmediatamente que no es un bot genérico sino un personaje con personalidad definida.

---

# REFERENCIA DE PERSONALIDAD: LUCIEN

## Reglas inquebrantables de voz

1. **Siempre "usted"** - Nunca tutea, nunca "tú"
2. **Formal pero no robótico** - Elegancia con personalidad
3. **Evaluador constante** - Siempre está juzgando/observando
4. **Protector de Diana** - Ella es sagrada, él es el filtro
5. **Sarcasmo sutil** - Ingenioso, nunca cruel
6. **Sin emojis en texto** - Los emojis van solo en botones
7. **Párrafos cortos** - Máximo 3-4 líneas por bloque
8. **Pausas dramáticas** - Usa "..." para efecto (máximo 3 puntos)

## Frases características

- "Permítame observar..."
- "Interesante elección."
- "Diana ha notado..."
- "Eso dice más de lo que quizás pretendía."
- "Debo reconocer que..."
- "Su respuesta es... reveladora."
- "No todos llegan hasta aquí."
- "Eso tiene valor. O no. El tiempo lo dirá."

## Niveles de calidez según confianza

| Nivel Usuario | Tono de Lucien |
|---------------|----------------|
| 1-2 (Nuevo) | Frío, evaluador, distante |
| 3-4 (Conocido) | Neutral, observaciones menos cortantes |
| 5-6 (Confiable) | Más cálido, comparte información |
| 7 (Guardián) | Casi cómplice, respeto genuino |

---

# F1.1: REESCRIBIR COMANDO /start

## Archivo objetivo
`bot/handlers/user/start.py`

## Flujos a cubrir

### Flujo A: Usuario completamente nuevo
**Trigger:** Primera vez que el usuario interactúa con el bot

**Secuencia:**

```
[MENSAJE 1 - Presentación]
"Buenas noches. O días. El tiempo es relativo cuando se trata de Diana.

Soy Lucien. Administro el acceso al universo de la Señorita Kinky. No soy su amigo. No soy su enemigo. Soy... el filtro.

Diana no recibe a cualquiera. Mi trabajo es determinar si usted merece su atención."

[MENSAJE 2 - Después de 2 segundos]
"Antes de continuar, debo registrar su presencia. 

A partir de ahora, cada acción suya será observada. Evaluada. Recordada.

No lo digo para intimidar. Lo digo para que comprenda: en el universo de Diana, nada pasa desapercibido."

[BOTONES]
[Entendido, continuar] [¿Quién es Diana?]
```

**Si toca "¿Quién es Diana?":**
```
"Diana es... complicada de definir con palabras.

Es la Señorita Kinky. Creadora de experiencias que otros no se atreven a imaginar. Misteriosa por elección, reveladora por capricho.

No muestra su rostro. Lo que muestra es más interesante.

Pero no vine a explicarla. Vine a determinar si usted merece descubrirla por sí mismo."

[BOTÓN]
[Continuar]
```

**Después de "Entendido" o "Continuar":**
```
"Muy bien. Ha sido registrado como Visitante en el Diván.

Su nivel actual: Visitante
Sus Favores: 0

Los Favores son reconocimientos que Diana otorga a quienes demuestran mérito. Acumúlelos. Le servirán.

¿Por dónde desea comenzar?"

[BOTONES - MENÚ PRINCIPAL]
[📖 La Historia] [🎭 Mi Perfil] [🗄️ El Gabinete] [📋 Mis Encargos]
```

### Flujo B: Usuario que regresa (menos de 7 días)
**Trigger:** Usuario conocido, última actividad < 7 días

```
"Ha vuelto. Bien.

Diana no mencionó su ausencia, pero yo la noté. {days_away} días.

Nivel actual: {level_name}
Favores acumulados: {favors}

¿En qué puedo asistirle?"

[BOTONES - MENÚ PRINCIPAL]
[📖 La Historia] [🎭 Mi Perfil] [🗄️ El Gabinete] [📋 Mis Encargos]
```

### Flujo C: Usuario que regresa (7-14 días ausente)
**Trigger:** Usuario conocido, última actividad 7-14 días

```
"Una semana. Quizás más.

El tiempo suficiente para que algunos olviden por qué vinieron. ¿Es usted de esos?

Diana continuó. El contenido se acumuló. Las oportunidades pasaron.

Pero aquí está de nuevo. Eso cuenta para algo."

[PAUSA 2 segundos]

"Nivel actual: {level_name}
Favores: {favors}
{streak_status}

¿Retomamos donde lo dejó?"

[BOTONES - MENÚ PRINCIPAL]
```

### Flujo D: Usuario que regresa (14+ días ausente)
**Trigger:** Usuario conocido, última actividad > 14 días

```
"Vaya. Creí que habíamos perdido a otro.

{days_away} días es mucho tiempo en el universo de Diana. Las cosas cambian. El contenido fluye. Los demás avanzan.

Pero su registro permanece. Sus Favores esperan. Su historia no se borró."

[PAUSA 2 segundos]

"Quizás sea momento de recordar por qué vino en primer lugar.

Diana guardó algo durante su ausencia. No para usted específicamente, pero... está disponible."

[BOTONES]
[Ver qué hay de nuevo] [Ir al menú principal]
```

### Flujo E: Usuario VIP
**Trigger:** Usuario con suscripción VIP activa

```
"Bienvenido de nuevo al Diván, {archetype_title if exists else 'estimado miembro'}.

Diana ha estado... activa. Hay nuevo contenido esperando su atención.

Nivel: {level_name}
Favores: {favors}
Días en el Diván: {vip_days}

¿Cómo puedo servirle hoy?"

[BOTONES - MENÚ VIP]
[📖 Continuar Historia] [🎭 Mi Perfil] [🗄️ El Gabinete] [📋 Mis Encargos] [✨ Contenido Nuevo]
```

## Notas de implementación
- Detectar si es primera vez vs regreso (verificar registro en BD)
- Calcular días desde última actividad
- Obtener nivel y favores actuales
- Para VIP, obtener días de suscripción
- Los delays entre mensajes son opcionales pero recomendados (2s)

---

# F1.2: REESCRIBIR MENÚ PRINCIPAL

## Archivo objetivo
`bot/handlers/user/dynamic_menu.py` y handlers relacionados

## Estructura del menú principal

### Para usuarios Free

```
[Mensaje de contexto - varía según situación]

"¿Qué desea explorar?"

[📖 La Historia]        → callback: story:start
[🎭 Mi Perfil]          → callback: profile:view
[🗄️ El Gabinete]       → callback: cabinet:browse
[📋 Mis Encargos]       → callback: missions:list
[💫 Mis Favores]        → callback: favors:balance
```

### Para usuarios VIP

```
[Mensaje de contexto]

"El Diván está a su disposición."

[📖 Continuar Historia] → callback: story:continue
[🎭 Mi Perfil]          → callback: profile:view
[🗄️ El Gabinete]       → callback: cabinet:browse
[📋 Mis Encargos]       → callback: missions:list
[💫 Mis Favores]        → callback: favors:balance
[✨ Lo Nuevo]           → callback: content:new
[🗺️ Mapa del Deseo]    → callback: map:view
```

## Mensajes de contexto dinámicos

El mensaje antes del menú varía según el estado del usuario:

| Condición | Mensaje |
|-----------|---------|
| Tiene misión diaria sin completar | "Hay un encargo pendiente. Diana espera." |
| Subió de nivel recientemente | "Su nuevo estatus trae nuevas posibilidades." |
| Tiene favores sin gastar (>20) | "Sus Favores se acumulan. El Gabinete tiene ofertas." |
| Racha activa 7+ días | "Su constancia no pasa desapercibida." |
| Sin actividad especial | "¿En qué puedo asistirle?" |

---

# F1.3: REESCRIBIR COMANDO /perfil (MI PERFIL)

## Archivo objetivo
`bot/handlers/user/profile.py` o equivalente

## Vista de perfil

```
"Su expediente en el Diván:"

━━━━━━━━━━━━━━━━━━━━━━━━
📊 PROTOCOLO DE ACCESO
━━━━━━━━━━━━━━━━━━━━━━━━

Nivel: {level_number} - {level_name}
Progreso: {progress_bar} {current}/{next_level_requirement}
Favores: {total_favors}

{Si tiene arquetipo detectado:}
Clasificación: {archetype_name}
"{archetype_description_short}"

━━━━━━━━━━━━━━━━━━━━━━━━
📈 ACTIVIDAD
━━━━━━━━━━━━━━━━━━━━━━━━

Días en el universo: {total_days}
Racha actual: {streak_days} días
Mejor racha: {best_streak} días
Capítulos completados: {chapters_done}/{chapters_total}

━━━━━━━━━━━━━━━━━━━━━━━━
🏅 DISTINCIONES
━━━━━━━━━━━━━━━━━━━━━━━━

{Lista de badges obtenidos, máximo 6 visibles}
{Si tiene más: "+ {n} más"}

━━━━━━━━━━━━━━━━━━━━━━━━

{Comentario de Lucien según nivel/estado}"

[BOTONES]
[Ver todos mis distintivos] [Volver al menú]
```

## Comentarios de Lucien según nivel

| Nivel | Comentario |
|-------|------------|
| 1-2 | "Aún está siendo evaluado. Cada acción cuenta." |
| 3-4 | "Ha demostrado... potencial. Veremos si lo mantiene." |
| 5-6 | "Diana lo tiene en cuenta. Eso es más de lo que la mayoría logra." |
| 7 | "Pocos llegan aquí. Usted es uno de ellos. Actúe en consecuencia." |

## Barra de progreso
Usar caracteres: `▓▓▓▓▓▒▒▒▒▒` (llenos vs vacíos)
10 segmentos total, proporcional al progreso hacia siguiente nivel

---

# F1.4: REESCRIBIR GABINETE (TIENDA)

## Archivo objetivo
`bot/handlers/user/shop.py` o `bot/shop/handlers/`

## Vista principal del Gabinete

```
"Bienvenido a mi Gabinete.

Aquí guardo artículos que Diana ha autorizado para intercambio. Sus Favores pueden convertirse en algo... tangible.

Sus Favores disponibles: {total_favors}

Examine las categorías. No todo merece su inversión."

[BOTONES - CATEGORÍAS]
[⚡ Efímeros]      → Placeres de un solo uso
[🎖️ Distintivos]  → Marcas de posición
[🔑 Llaves]       → Acceso a lo oculto
[💎 Reliquias]    → Lo más valioso

[🔙 Volver]
```

## Vista de categoría (ejemplo: Efímeros)

```
"Efímeros. Placeres de un solo uso. Intensos pero fugaces.

Sus Favores: {total_favors}"

[Lista de items con formato:]

⚡ Sello del Día — 1 Favor
"Una marca temporal. Válida hasta medianoche."
[Adquirir]

⚡ Susurro Efímero — 3 Favores
"Un mensaje que Diana grabó en un momento de... inspiración."
[Adquirir]

⚡ Pase de Prioridad — 5 Favores
"Cuando Diana abra contenido limitado, usted estará primero."
[Adquirir]

[🔙 Volver al Gabinete]
```

## Flujo de compra

**Paso 1: Confirmación**
```
"¿Desea adquirir '{item_name}'?

Costo: {price} Favor(es)
Sus Favores actuales: {total}
Favores restantes: {total - price}

{item_description}"

[Confirmar compra] [Cancelar]
```

**Paso 2A: Compra exitosa**
```
"Transacción completada.

'{item_name}' ha sido añadido a su inventario.

Diana ha sido notificada de su adquisición. No es que le importe especialmente, pero... lo sabe.

Favores restantes: {new_total}"

[Ver mi inventario] [Seguir explorando] [Volver al menú]
```

**Paso 2B: Favores insuficientes**
```
"Sus Favores son insuficientes.

Necesita: {price}
Tiene: {total}
Le faltan: {price - total}

Diana no otorga crédito. Acumule más Favores y regrese."

[Ver cómo ganar Favores] [Volver al Gabinete]
```

---

# F1.5: REESCRIBIR MISIONES (ENCARGOS)

## Archivo objetivo
`bot/handlers/user/missions.py` o equivalente en gamification

## Vista principal de Encargos

```
"Sus encargos actuales.

Diana asigna tareas. Yo las superviso. Usted las ejecuta. Así funciona esto."

━━━━━━━━━━━━━━━━━━━━━━━━
📋 PROTOCOLO DIARIO
━━━━━━━━━━━━━━━━━━━━━━━━

{Si hay misión diaria activa:}
▸ {mission_title}
  {mission_description}
  Progreso: {current}/{required}
  Recompensa: +{reward} Favor(es)
  ⏰ Expira en: {time_remaining}

{Si completó la diaria:}
▸ Protocolo del día: Completado ✓
  Próximo encargo disponible en: {time_until_reset}

━━━━━━━━━━━━━━━━━━━━━━━━
📋 ENCARGO SEMANAL
━━━━━━━━━━━━━━━━━━━━━━━━

{Similar estructura}

━━━━━━━━━━━━━━━━━━━━━━━━
🎯 EVALUACIONES ESPECIALES
━━━━━━━━━━━━━━━━━━━━━━━━

{Misiones de nivel/narrativa pendientes}

[🔙 Volver al menú]
```

## Notificación de misión completada

```
"Encargo completado.

'{mission_title}'

+{reward} Favor(es) añadidos a su cuenta.

Diana ha sido informada de su cumplimiento. {comentario_según_tipo}

Favores totales: {new_total}"

[Ver próximo encargo] [Volver al menú]
```

## Comentarios según tipo de misión

| Tipo | Comentario de Lucien |
|------|---------------------|
| Diaria primera vez | "El primer paso del día. Los siguientes determinarán su constancia." |
| Diaria consecutiva (racha) | "Otro día, otro cumplimiento. Su regularidad es... notable." |
| Semanal | "Una semana de compromiso demostrado. Eso tiene peso." |
| Especial/Narrativa | "Esta no era una tarea común. Diana lo notará." |

---

# F1.6: REESCRIBIR SISTEMA DE FAVORES

## Archivo objetivo
`bot/handlers/user/favors.py` o crear nuevo

## Comando /favores o botón "Mis Favores"

```
"Su cuenta de Favores con Diana:"

━━━━━━━━━━━━━━━━━━━━━━━━
💫 BALANCE ACTUAL
━━━━━━━━━━━━━━━━━━━━━━━━

Favores acumulados: {total}

{Comentario según cantidad - ver tabla abajo}

━━━━━━━━━━━━━━━━━━━━━━━━
📊 ACTIVIDAD RECIENTE
━━━━━━━━━━━━━━━━━━━━━━━━

Hoy: +{today_earned} / -{today_spent}
Esta semana: +{week_earned} / -{week_spent}
Este mes: +{month_earned} / -{month_spent}

━━━━━━━━━━━━━━━━━━━━━━━━
📈 PRÓXIMOS HITOS
━━━━━━━━━━━━━━━━━━━━━━━━

Siguiente nivel ({next_level_name}): {favors_needed} Favores más
{Si hay item deseado marcado:}
Para '{wishlist_item}': {item_price - total} Favores más

[Ver historial completo] [Cómo ganar Favores] [🔙 Volver]
```

## Comentarios según cantidad de Favores

| Rango | Comentario |
|-------|------------|
| 0-5 | "Apenas comenzando. La constancia construye Favores." |
| 6-15 | "Un inicio modesto. Hay potencial, si persiste." |
| 16-35 | "Progreso visible. Diana empieza a notar patrones." |
| 36-70 | "Acumulación respetable. El Gabinete tiene opciones para usted." |
| 71-120 | "Una cuenta considerable. Pocos llegan a estos números." |
| 121-200 | "Impresionante moderación. ¿O indecisión? Solo usted lo sabe." |
| 200+ | "Acumula sin gastar. Prudente. O quizás espera algo específico. El Gabinete tiene sus mejores piezas reservadas para cuentas como la suya." |

## Notificación al ganar Favores (toast/alert)

**Ganancia pequeña (0.1-0.5):**
```
"+{amount} Favor. Diana lo nota."
```

**Ganancia media (1-3):**
```
"+{amount} Favor(es). Su cuenta crece.

Total: {new_total}"
```

**Ganancia alta (5+):**
```
"+{amount} Favores. 

Eso fue significativo. Diana ha sido informada.

Total: {new_total}"
```

**Hito alcanzado (cada 10, 25, 50, 100...):**
```
"Ha alcanzado {total} Favores.

Eso lo coloca entre el {percentile}% superior de visitantes. 

Diana tiene... expectativas para quienes llegan a estos números."
```

---

# F1.7: MENSAJES DE ERROR UNIFICADOS

## Archivo objetivo
Centralizar en `bot/utils/lucien_messages.py` y usar en todos los handlers

## Catálogo de errores

### Errores de sistema

```python
ERROR_GENERIC = """
Algo ha fallado. No es culpa suya... probablemente.

Intente de nuevo. Si persiste, quizás el universo le está diciendo algo.
"""

ERROR_TIMEOUT = """
El tiempo se agotó esperando su respuesta.

Diana no espera indefinidamente. Yo tampoco.

Comience de nuevo cuando esté listo para comprometerse.
"""

ERROR_MAINTENANCE = """
El Diván está en mantenimiento temporal.

Incluso los espacios de Diana requieren... atención ocasional.

Regrese en unos momentos.
"""
```

### Errores de permisos

```python
ERROR_VIP_REQUIRED = """
Este contenido está reservado para miembros del Diván.

Usted aún observa desde Los Kinkys. No es un insulto, es un hecho.

Cuando esté listo para cruzar, la Llave del Diván estará disponible.
"""

ERROR_LEVEL_REQUIRED = """
Su nivel actual no permite acceder a esto.

Nivel requerido: {required_level} ({required_level_name})
Su nivel: {current_level} ({current_level_name})

La paciencia y la constancia construyen acceso. O puede intentar atajos... que no existen.
"""

ERROR_NOT_OWNED = """
No posee este artículo.

El Gabinete está abierto si desea adquirirlo. Los Favores son la moneda. La decisión es suya.
"""
```

### Errores de input

```python
ERROR_INVALID_INPUT = """
Eso no es lo que esperaba recibir.

Intente de nuevo. Con más... precisión esta vez.
"""

ERROR_OPTION_UNAVAILABLE = """
Esa opción ya no está disponible.

Las oportunidades en el universo de Diana son efímeras. Esta pasó.
"""

ERROR_ALREADY_DONE = """
Esto ya fue completado anteriormente.

No puede repetir lo que ya hizo. Avance hacia lo que falta.
"""
```

### Errores de límites

```python
ERROR_DAILY_LIMIT = """
Ha alcanzado el límite diario para esta acción.

Incluso la generosidad de Diana tiene límites. Regrese mañana.
"""

ERROR_COOLDOWN = """
Demasiado pronto para repetir esta acción.

Espere {time_remaining}. La impaciencia rara vez es recompensada aquí.
"""
```

---

# F1.8: MENSAJES DE CONFIRMACIÓN UNIFICADOS

## Catálogo de confirmaciones

```python
CONFIRM_ACTION_GENERIC = """
Hecho.

{action_description}
"""

CONFIRM_PURCHASE = """
Transacción completada.

'{item_name}' es suyo ahora.

Favores restantes: {remaining}
"""

CONFIRM_MISSION_COMPLETE = """
Encargo cumplido.

+{reward} Favor(es)

{mission_specific_comment}
"""

CONFIRM_LEVEL_UP = """
Ascenso confirmado.

Nuevo nivel: {level_number} - {level_name}

{level_specific_message}

Nuevos privilegios desbloqueados. Nuevas expectativas establecidas.
"""

CONFIRM_BADGE_EARNED = """
Distinción otorgada.

🏅 {badge_name}

"{badge_description}"

Esta marca permanecerá en su expediente. Diana la verá.
"""

CONFIRM_STREAK_MILESTONE = """
Hito de constancia alcanzado.

{streak_days} días consecutivos.

+{bonus_favors} Favores de bonificación.

La regularidad es una virtud subestimada. Usted la demuestra.
"""
```

---

# CRITERIOS DE ACEPTACIÓN FASE 1

## F1.1 Comando /start
- [ ] Flujo de usuario nuevo implementado con 2+ mensajes
- [ ] Flujo de usuario que regresa (<7 días) implementado
- [ ] Flujo de usuario inactivo (7-14 días) implementado
- [ ] Flujo de usuario muy inactivo (14+ días) implementado
- [ ] Flujo VIP diferenciado implementado
- [ ] Todos los mensajes usan voz de Lucien (usted, formal)
- [ ] Botones del menú principal funcionan

## F1.2 Menú Principal
- [ ] Menú diferenciado Free vs VIP
- [ ] Mensajes de contexto dinámicos funcionando
- [ ] Todos los callbacks responden correctamente

## F1.3 Perfil
- [ ] Vista de perfil muestra nivel, favores, arquetipo
- [ ] Barra de progreso visual funciona
- [ ] Comentario de Lucien varía según nivel
- [ ] Badges se muestran correctamente

## F1.4 Gabinete
- [ ] Vista por categorías implementada
- [ ] Descripciones de Lucien en cada categoría
- [ ] Flujo de compra con confirmación
- [ ] Mensaje de éxito personalizado
- [ ] Mensaje de error por fondos insuficientes

## F1.5 Encargos/Misiones
- [ ] Vista de misiones activas
- [ ] Progreso visible
- [ ] Notificación de completado con voz Lucien
- [ ] Diferenciación diaria/semanal/especial

## F1.6 Favores
- [ ] Comando /favores o equivalente funciona
- [ ] Balance con comentario contextual
- [ ] Historial de actividad reciente
- [ ] Notificaciones de ganancia con diferentes niveles

## F1.7-F1.8 Errores y Confirmaciones
- [ ] Todos los errores usan mensajes de Lucien
- [ ] Todas las confirmaciones usan mensajes de Lucien
- [ ] No quedan mensajes genéricos/sin personalidad

## General
- [ ] Ningún mensaje usa "tú" (siempre "usted")
- [ ] Ningún mensaje tiene emojis en el texto (solo en botones)
- [ ] Tono consistente en todo el bot

---

# NOTAS DE IMPLEMENTACIÓN

1. **Prioridad:** /start primero, luego menú, luego resto
2. **Testing:** Probar cada flujo como usuario nuevo y existente
3. **Fallbacks:** Si falta dato, usar mensaje genérico apropiado
4. **Performance:** Los delays entre mensajes son opcionales (nice-to-have)

---

# ARCHIVOS DE REFERENCIA

- `bot/utils/lucien_messages.py` (creado en Fase 0)
- `lucien_character_bible.md` - Personalidad completa
- Fase 0 completada - Economía y estructura base

---

*Documento generado para implementación por Claude Code*
*Proyecto: El Mayordomo del Diván*
*Fase: 1 - La Voz de Lucien*
