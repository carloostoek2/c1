# REQUERIMIENTO: FASE 5 - NARRATIVA Y CONTENIDO
## Proyecto: El Mayordomo del Diván
## Bot de Telegram para Señorita Kinky

---

# CONTEXTO

La narrativa es el corazón del bot. No es solo gamificación con puntos - es una historia que el usuario vive. Diana y Lucien guían al usuario a través de un viaje de 6 niveles donde cada paso revela más, exige más, y transforma la relación.

**Principio fundamental:** El usuario no "consume" contenido - lo descubre. Cada fragmento se siente ganado, no dado. La narrativa evalúa al usuario tanto como el usuario descubre a Diana.

**Fuente:** El guión narrativo completo está en `/mnt/project/Narrativo.pdf` (12 páginas). Este documento traduce ese guión a especificaciones implementables.

**Dependencias:**
- Fase 0-4 completadas
- Sistema de Favores funcional
- Arquetipos detectándose
- Gabinete operativo

---

# ARQUITECTURA NARRATIVA

## Estructura de niveles

```
┌─────────────────────────────────────────────────────────────┐
│                    CANAL FREE (Los Kinkys)                  │
├─────────────────────────────────────────────────────────────┤
│  NIVEL 1: Bienvenida                                        │
│  └── Introducción a Diana y Lucien                          │
│  └── Primer desafío (reacción)                              │
│  └── Entrega: Mochila del Viajero + Pista 1                 │
│                                                             │
│  NIVEL 2: Observación                                       │
│  └── Misión de 3 días (encontrar pistas)                    │
│  └── Validación de atención                                 │
│  └── Entrega: Fragmento de Memoria + Pista 2                │
│                                                             │
│  NIVEL 3: Perfil de Deseo                                   │
│  └── Cuestionario profundo                                  │
│  └── Respuesta personalizada por arquetipo                  │
│  └── Entrega: Pista 3 + Invitación al Diván                 │
│                                                             │
│  ══════════════ PUNTO DE CONVERSIÓN ══════════════          │
│  La "Llave del Diván" - Acceso VIP                          │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                    CANAL VIP (El Diván)                     │
├─────────────────────────────────────────────────────────────┤
│  NIVEL 4: Entrada al Diván                                  │
│  └── Bienvenida íntima                                      │
│  └── Evaluación de comprensión                              │
│  └── Entrega: Visión del Diván                              │
│                                                             │
│  NIVEL 5: Profundización                                    │
│  └── Diálogos de vulnerabilidad                             │
│  └── Evaluación de respuestas empáticas                     │
│  └── Entrega: Archivo Personal de Diana                     │
│                                                             │
│  NIVEL 6: Culminación                                       │
│  └── Secreto final de Diana                                 │
│  └── Síntesis del viaje                                     │
│  └── Acceso: Círculo Íntimo → Mapa del Deseo                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Dos voces narrativas

| Voz | Rol | Tono | Cuándo habla |
|-----|-----|------|--------------|
| **Diana** | Protagonista, objeto del viaje | Seductora, vulnerable calculada, misteriosa | Contenido emocional, revelaciones, intimidad |
| **Lucien** | Narrador, guía, evaluador | Formal, analítico, protector | Instrucciones, evaluaciones, transiciones |

---

# F5.1: MODELO DE DATOS NARRATIVO

## Capítulos (NarrativeChapter)

```
NarrativeChapter:
    id: int (PK)
    level: int (1-6)
    chapter_key: str unique (ej: "L1_WELCOME", "L3_DESIRE_PROFILE")
    title: str
    description: str
    
    # Requisitos
    requires_vip: bool
    requires_level: int
    requires_chapter_completed: int | null (FK a otro chapter)
    requires_archetype: str | null
    
    # Configuración
    is_active: bool
    order_in_level: int
    estimated_duration_minutes: int
    
    # Rewards al completar
    favor_reward: float
    badge_reward: str | null
    item_reward: str | null
    
    created_at: datetime
    updated_at: datetime
```

## Fragmentos (NarrativeFragment)

```
NarrativeFragment:
    id: int (PK)
    chapter_id: int (FK)
    fragment_key: str unique (ej: "L1_WELCOME_01", "L1_WELCOME_02A")
    
    # Contenido
    speaker: enum (DIANA, LUCIEN, NARRATOR, SYSTEM)
    content_type: enum (TEXT, IMAGE, AUDIO, VIDEO, INTERACTIVE)
    content: text  # El texto narrativo
    media_url: str | null
    
    # Flujo
    order_in_chapter: int
    delay_seconds: int  # Pausa antes de mostrar (efecto dramático)
    
    # Ramificación
    is_decision_point: bool
    decisions: JSON | null  # Array de opciones si es decision point
    next_fragment_id: int | null  # Siguiente fragmento (si lineal)
    
    # Condiciones
    condition_type: str | null  # "archetype", "response_time", "score", etc.
    condition_value: str | null  # El valor a evaluar
    
    # Metadata
    is_active: bool
    created_at: datetime
```

## Decisiones (NarrativeDecision)

```
NarrativeDecision:
    id: int (PK)
    fragment_id: int (FK)
    decision_key: str
    
    text: str  # Texto del botón/opción
    subtext: str | null  # Texto pequeño debajo (opcional)
    
    # A dónde lleva
    next_fragment_id: int (FK)
    
    # Efectos
    favor_change: float  # Puede ser positivo o negativo
    sets_flag: str | null  # Flag que se guarda en usuario
    requires_flag: str | null  # Flag requerido para ver esta opción
    
    order: int
    is_active: bool
```

## Progreso del usuario (UserNarrativeProgress)

```
UserNarrativeProgress:
    id: int (PK)
    user_id: int (FK)
    
    # Progreso general
    current_level: int (1-6)
    current_chapter_id: int | null (FK)
    current_fragment_id: int | null (FK)
    
    # Historial
    chapters_completed: JSON  # Array de chapter_ids completados
    fragments_seen: JSON  # Array de fragment_ids vistos
    decisions_made: JSON  # {fragment_id: decision_key, ...}
    
    # Flags narrativos
    narrative_flags: JSON  # Flags seteados por decisiones
    
    # Misiones narrativas activas
    active_mission_id: str | null
    mission_started_at: datetime | null
    mission_data: JSON | null  # Datos de la misión en curso
    
    # Timestamps
    started_at: datetime
    last_interaction_at: datetime
    level_1_completed_at: datetime | null
    level_2_completed_at: datetime | null
    # ... etc
```

---

# F5.2: NIVEL 1 - BIENVENIDA (Los Kinkys)

## Resumen del nivel

El usuario acaba de llegar. Diana aparece como una presencia intrigante. Lucien establece las reglas. El primer desafío es simple: demostrar que puede actuar, no solo observar.

## Capítulo: L1_WELCOME

### Fragmento L1_01: Primera aparición de Diana
```
Speaker: DIANA
Type: TEXT
Delay: 0

Content:
"Así que has llegado.

No sé cómo encontraste este lugar. No sé qué buscas exactamente. 
Pero estás aquí. Y eso ya dice algo sobre ti.

Soy Diana. O Kinky. O ninguna de las dos. 
Depende de qué parte de mí decidas ver.

Antes de continuar... hay alguien que quiere conocerte."

Next: L1_02
```

### Fragmento L1_02: Lucien se presenta
```
Speaker: LUCIEN
Type: TEXT
Delay: 2

Content:
"Permítame presentarme.

Soy Lucien. Administro el acceso al universo de Diana. 
No soy su secretario. No soy su guardaespaldas. 
Soy... el filtro. El que determina quién merece llegar más lejos.

Diana no recibe a cualquiera. Mi trabajo es asegurarme de que 
quienes la conocen sean dignos del privilegio."

Next: L1_03
```

### Fragmento L1_03: El primer desafío
```
Speaker: LUCIEN
Type: INTERACTIVE
Delay: 2

Content:
"Ahora, una prueba simple.

Diana ha publicado algo recientemente en el canal. 
Quiero ver si usted es de los que actúan... o de los que solo miran.

Vaya al canal. Encuentre la última publicación. Reaccione.

Cualquier reacción sirve. Lo que importa es que lo haga.
Estaré observando."

Decisions:
- "Entendido, voy ahora" → L1_04_WAITING
- "¿Por qué debería hacerlo?" → L1_03B_CHALLENGE
```

### Fragmento L1_03B: Respuesta al desafiante
```
Speaker: LUCIEN
Type: TEXT
Condition: decision == "challenge"
Delay: 1

Content:
"¿Por qué?

Porque Diana nota a quienes actúan. Ignora a quienes solo observan.
Porque cada paso aquí es una evaluación.
Porque si no puede hacer algo tan simple... el resto será imposible.

Pero si prefiere quedarse en la puerta, es su elección.
Yo no insisto. Solo informo."

Next: L1_04_WAITING
```

### Fragmento L1_04: Esperando reacción
```
Speaker: SYSTEM
Type: TEXT
Delay: 0

Content:
"⏳ Esperando su reacción en el canal...

Cuando haya reaccionado a una publicación, 
esta conversación continuará automáticamente."

Trigger: ON_REACTION_DETECTED → L1_05A o L1_05B (según tiempo)
Timeout: 24 horas → L1_TIMEOUT
```

### Fragmento L1_05A: Reacción rápida (<2 minutos)
```
Speaker: LUCIEN
Type: TEXT
Condition: response_time < 120
Delay: 1

Content:
"Rápido. Muy rápido.

Apenas di la instrucción y ya actuó. Eso dice algo.
Impulsivo, quizás. O simplemente... decidido.

Diana nota a los que no dudan. Pero también nota 
a los que actúan sin pensar. Veremos cuál es usted."

Sets_flag: "first_reaction_fast"
Next: L1_06
```

### Fragmento L1_05B: Reacción pausada (>2 minutos)
```
Speaker: LUCIEN
Type: TEXT
Condition: response_time >= 120
Delay: 1

Content:
"Se tomó su tiempo.

No saltó inmediatamente. Procesó. Quizás leyó el contenido 
antes de reaccionar. O quizás dudó.

La paciencia es una virtud subestimada. Pero también puede ser 
una máscara para la indecisión. El tiempo dirá."

Sets_flag: "first_reaction_slow"
Next: L1_06
```

### Fragmento L1_06: Entrega de recompensas
```
Speaker: DIANA
Type: TEXT
Delay: 2

Content:
"Bien. Diste el primer paso.

No es mucho, pero es más de lo que la mayoría hace. 
La mayoría mira desde lejos. Tú actuaste.

Te he dejado algo. Una especie de... mochila para el viaje.
Y la primera pista de algo más grande.

Lucien te explicará."

Next: L1_07
```

### Fragmento L1_07: Explicación de Lucien + Cierre nivel 1
```
Speaker: LUCIEN
Type: TEXT
Delay: 2

Content:
"Ha recibido la Mochila del Viajero. 
Es simbólica, pero lo que contiene es real.

También tiene la Primera Pista. Hay un mapa que Diana 
ha escondido en este universo. Las pistas lo revelarán.

Por ahora, explore. Observe. Reaccione cuando sienta que debe.
Cuando esté listo para el siguiente paso, lo sabrá.

+5 Favores han sido añadidos a su cuenta.
Diana lo notará."

Rewards:
- favor_reward: 5
- badge_reward: "first_step"
- item_reward: "pista_1"

Completes: L1_WELCOME
Unlocks: L2_OBSERVATION (después de 24 horas)
```

---

# F5.3: NIVEL 2 - OBSERVACIÓN (Los Kinkys)

## Resumen del nivel

El usuario demostró que puede actuar. Ahora debe demostrar que puede observar con atención. Una misión de 3 días: encontrar pistas ocultas en las publicaciones del canal.

## Capítulo: L2_OBSERVATION

### Trigger de inicio
```
Condiciones para activar Nivel 2:
- Nivel 1 completado
- Han pasado 24+ horas desde completar Nivel 1
- Usuario tiene 5+ Favores
- Usuario ha tenido al menos 2 interacciones desde Nivel 1
```

### Fragmento L2_01: Diana reconoce el regreso
```
Speaker: DIANA
Type: TEXT
Delay: 0

Content:
"Volviste.

No todos lo hacen. Algunos prueban el primer paso y desaparecen.
Tú regresaste. Eso significa que hay algo aquí que te llama.

¿Curiosidad? ¿Deseo? ¿Algo más profundo?

No importa. Lo que importa es que estás aquí de nuevo."

Next: L2_02
```

### Fragmento L2_02: Lucien presenta el desafío
```
Speaker: LUCIEN
Type: TEXT
Delay: 2

Content:
"El primer desafío fue actuar. Este será diferente.

Diana esconde cosas en sus publicaciones. Detalles que la mayoría 
no nota. Palabras específicas. Gestos sutiles. Patrones.

Durante los próximos 3 días, observe el canal con atención.
Busque lo que otros ignoran.

Cuando crea haber encontrado algo, regrese aquí."

Next: L2_03
```

### Fragmento L2_03: Inicio de misión
```
Speaker: SYSTEM
Type: INTERACTIVE
Delay: 1

Content:
"🔍 MISIÓN: EL OJO ATENTO

Duración: 3 días
Objetivo: Encontrar 3 elementos ocultos en las publicaciones

Diana esconde pistas en su contenido. Pueden ser:
• Una palabra que se repite
• Un gesto específico
• Un detalle en el fondo
• Una referencia a algo anterior

Cuando crea haber encontrado algo, regrese y descríbalo."

Decisions:
- "Comenzar a observar" → L2_04_MISSION_ACTIVE
- "¿Qué tipo de pistas?" → L2_03B_HINTS
```

### Fragmento L2_04: Misión activa
```
Speaker: LUCIEN
Type: TEXT
Delay: 0

Content:
"La misión está activa.

Tiene 3 días. No hay prisa, pero tampoco hay extensiones.
Observe. Analice. Cuando tenga algo, use el botón de abajo."

Mission_starts: "observation_mission"
Mission_duration: 72 hours
Mission_data: { "hints_found": 0, "hints_required": 3 }

UI: Mostrar botón "Reportar hallazgo" que lleva a L2_05_REPORT
```

### Fragmento L2_05: Reportar hallazgo
```
Speaker: LUCIEN
Type: INTERACTIVE
Delay: 0

Content:
"¿Qué ha encontrado?

Describa brevemente el elemento que notó.
Sea específico. 'Vi algo raro' no cuenta."

Input: text_field (min 10 caracteres)
Validation: L2_VALIDATE_HINT
```

### Lógica de validación de pistas
```
L2_VALIDATE_HINT:

Opciones de implementación:

A) Lista de palabras clave válidas
   - Si el texto contiene palabras clave predefinidas → válido
   - Palabras: definir lista según contenido real del canal

B) Validación por IA (si disponible)
   - Enviar respuesta a modelo para evaluar si es observación válida
   
C) Aceptar cualquier respuesta razonable
   - Si tiene >20 caracteres y no es spam → válido
   - Registrar para revisión manual

Si válido → L2_06_HINT_ACCEPTED
Si inválido → L2_06B_HINT_REJECTED
```

### Fragmento L2_06: Pista aceptada
```
Speaker: LUCIEN
Type: TEXT
Delay: 1

Content:
"Interesante observación.

{Si es hint 1}: 
'Es un comienzo. Hay más. Siga mirando.'

{Si es hint 2}: 
'Dos de tres. Su ojo se está afinando.'

{Si es hint 3}: 
'El tercero. Suficiente. Ha demostrado que sabe mirar.'

Hallazgos: {hints_found}/3"

If hints_found == 3 → L2_07_MISSION_COMPLETE
Else → Return to mission
```

### Fragmento L2_07: Misión completada
```
Speaker: DIANA
Type: TEXT
Delay: 2

Content:
"Encontraste lo que escondí.

La mayoría pasa de largo. Ven lo obvio y creen que es todo.
Tú miraste más profundo. Eso me... intriga.

Mereces saber un poco más sobre mí.
Algo que no publico. Algo personal."

Next: L2_08
```

### Fragmento L2_08: Entrega de recompensas
```
Speaker: LUCIEN
Type: TEXT
Delay: 2

Content:
"Ha recibido el Fragmento de Memoria.

Es una imagen personal de Diana. No de sus sesiones.
De ella. Un momento real.

También tiene la Segunda Pista. El mapa se va revelando.

+8 Favores añadidos.
Nivel de Observador desbloqueado."

Rewards:
- favor_reward: 8
- badge_reward: "keen_eye"
- item_reward: "memory_fragment_1"
- item_reward: "pista_2"
- unlocks_shop_item: "Llave del Fragmento I" (ahora puede comprarlo)

Completes: L2_OBSERVATION
Unlocks: L3_DESIRE_PROFILE (después de 48 horas + nivel 3 en Favores)
```

---

# F5.4: NIVEL 3 - PERFIL DE DESEO (Los Kinkys)

## Resumen del nivel

El usuario ha demostrado acción y observación. Ahora Diana quiere saber quién es realmente. Un cuestionario profundo que revela motivaciones y define el arquetipo final.

## Capítulo: L3_DESIRE_PROFILE

### Fragmento L3_01: Diana solicita el perfil
```
Speaker: DIANA
Type: TEXT
Delay: 0

Content:
"Has llegado más lejos que la mayoría.

Actuaste cuando otros solo miraban.
Observaste lo que otros ignoraban.

Ahora quiero saber algo más difícil: quiero saber por qué.

¿Por qué estás aquí? ¿Qué buscas realmente?
No la respuesta fácil. La verdadera."

Next: L3_02
```

### Fragmento L3_02: Lucien explica el proceso
```
Speaker: LUCIEN
Type: TEXT
Delay: 2

Content:
"Lo que viene es el Perfil de Deseo.

Son preguntas. Algunas simples. Otras... menos.
No hay respuestas correctas o incorrectas. Pero hay respuestas 
honestas y respuestas performativas.

Diana sabrá la diferencia. Yo también.

Tómese el tiempo que necesite. Pero sea sincero.
La mentira aquí no sirve de nada."

Next: L3_03
```

### Fragmento L3_03: Pregunta 1
```
Speaker: DIANA
Type: INTERACTIVE
Delay: 2

Content:
"Primera pregunta.

¿Qué te atrajo a este lugar inicialmente?
Antes de conocerme. Antes de entender qué era esto.
El primer impulso."

Decisions:
- "Curiosidad pura. Quería saber qué había aquí." → flag: curious
- "Atracción. Algo en ti me llamó la atención." → flag: attracted  
- "Buscaba algo específico. Conexión, quizás." → flag: seeking
- "Honestamente, no lo sé. Algo me trajo." → flag: intuitive

All → L3_04
```

### Fragmento L3_04: Pregunta 2
```
Speaker: DIANA
Type: INTERACTIVE
Delay: 1

Content:
"Segunda pregunta.

Cuando ves mi contenido, ¿qué te importa más?
¿Lo visual? ¿Lo que digo? ¿Lo que no digo?
¿O algo completamente diferente?"

Decisions:
- "Lo visual. La estética. Cómo te presentas." → flag: visual
- "Tus palabras. Lo que expresas, cómo piensas." → flag: verbal
- "El misterio. Lo que ocultas me atrae más que lo que muestras." → flag: mystery
- "La persona detrás. Quiero conocer a Diana, no a Kinky." → flag: personal

All → L3_05
```

### Fragmento L3_05: Pregunta 3
```
Speaker: DIANA
Type: INTERACTIVE
Delay: 1

Content:
"Tercera pregunta.

¿Qué harías si te dijera que no soy lo que parece?
Que la Kinky que ves es una construcción.
Que Diana es diferente. Más complicada. Menos perfecta."

Decisions:
- "Me intrigaría más. La imperfección es interesante." → flag: depth
- "Depende de qué tan diferente. Tengo límites." → flag: cautious
- "Ya lo sospechaba. Nadie es solo una cosa." → flag: perceptive
- "Me decepcionaría. Vine por lo que muestras." → flag: surface

All → L3_06
```

### Fragmento L3_06: Pregunta 4
```
Speaker: DIANA
Type: INTERACTIVE
Delay: 1

Content:
"Cuarta pregunta.

¿Qué esperas obtener de estar aquí?
Al final del camino. Cuando hayas visto todo lo que hay que ver.
¿Qué habrá valido la pena?"

Decisions:
- "Entretenimiento. Momentos de placer." → flag: pleasure
- "Conexión. Sentir que no soy solo un número." → flag: connection
- "Conocimiento. Entender algo que no entendía." → flag: understanding
- "No lo sé aún. Estoy descubriendo sobre la marcha." → flag: open

All → L3_07
```

### Fragmento L3_07: Pregunta 5 (abierta)
```
Speaker: DIANA
Type: INTERACTIVE
Delay: 1

Content:
"Última pregunta. Y esta no tiene opciones.

Si pudieras decirme una cosa. Solo una.
Algo que quisieras que yo supiera sobre ti.
¿Qué sería?"

Input: text_field (min 20 caracteres, max 500)
Save_response: "personal_statement"

Next: L3_08_ANALYSIS
```

### Fragmento L3_08: Análisis (delay para efecto)
```
Speaker: SYSTEM
Type: TEXT
Delay: 3

Content:
"Diana está revisando tus respuestas..."

Processing:
- Analizar flags de respuestas
- Determinar arquetipo dominante si no está definido
- Generar respuesta personalizada

Next: L3_09_{ARCHETYPE} (rama según arquetipo)
```

### Fragmento L3_09_EXPLORER: Respuesta para Exploradores
```
Speaker: DIANA
Type: TEXT
Condition: archetype == EXPLORER or flags contain "curious" + "mystery"
Delay: 2

Content:
"Tu curiosidad es casi... hambrienta.

Quieres verlo todo. Saberlo todo. No por coleccionar, 
sino por ese impulso de no dejar nada sin descubrir.

Me reconozco en eso. Es agotador. Y adictivo.

El Diván tiene cosas que ni Lucien ha visto.
Quizás tú las encuentres."

Next: L3_10
```

### Fragmento L3_09_ROMANTIC: Respuesta para Románticos
```
Speaker: DIANA
Type: TEXT
Condition: archetype == ROMANTIC or flags contain "connection" + "personal"
Delay: 2

Content:
"Buscas algo real.

No viniste por el contenido. Viniste por la persona.
Quieres conexión, no transacción. Intimidad, no producto.

Es hermoso. Y peligroso.
Porque puedo darte momentos de eso. Pero no puedo prometerte todo.

Aun así... el Diván es donde me permito ser más vulnerable."

Next: L3_10
```

### Fragmento L3_09_ANALYTICAL: Respuesta para Analíticos
```
Speaker: DIANA
Type: TEXT
Condition: archetype == ANALYTICAL or flags contain "understanding" + "perceptive"
Delay: 2

Content:
"Analizas todo, ¿verdad?

Cada palabra. Cada gesto. Buscando patrones. Lógica.
Tratando de entender cómo funciona esto. Cómo funciono yo.

No sé si me descifrarás. Ni yo me he descifrado.
Pero el intento... tiene su propio valor.

El Diván tiene capas que apreciarás."

Next: L3_10
```

### Fragmento L3_09_DIRECT: Respuesta para Directos
```
Speaker: DIANA
Type: TEXT
Condition: archetype == DIRECT or flags contain "pleasure" + "visual"
Delay: 2

Content:
"Sabes lo que quieres.

Sin rodeos. Sin justificaciones complicadas.
Viniste por algo, y no te avergüenzas de ello.

Eso es refrescante. La mayoría finge motivaciones más 'nobles'.

El Diván tiene lo que buscas. Sin filtros innecesarios."

Next: L3_10
```

### Fragmento L3_09_PATIENT: Respuesta para Pacientes
```
Speaker: DIANA
Type: TEXT
Condition: archetype == PATIENT or flags contain "open" + "cautious"
Delay: 2

Content:
"Te tomas tu tiempo.

No apresuras. No presionas. Dejas que las cosas se revelen
cuando están listas. Eso es... raro aquí.

La mayoría quiere todo inmediatamente.
Tú entiendes que lo valioso se construye despacio.

El Diván recompensa esa paciencia."

Next: L3_10
```

### Fragmento L3_09_PERSISTENT: Respuesta para Persistentes
```
Speaker: DIANA
Type: TEXT
Condition: archetype == PERSISTENT
Delay: 2

Content:
"Sigues aquí.

Has pasado por todo esto sin rendirte. Sin abandonar.
Cada vez que el camino se complicó, seguiste adelante.

Esa persistencia... me conmueve más de lo que admitiré.

El Diván tiene recompensas para quienes no se rinden."

Next: L3_10
```

### Fragmento L3_10: La Invitación
```
Speaker: DIANA
Type: TEXT
Delay: 3

Content:
"Has completado el Perfil de Deseo.

Ahora te conozco un poco más. Y quizás tú te conoces mejor también.

Hay una puerta. El Diván. Mi espacio más íntimo.
No todos llegan hasta ella. Tú llegaste.

La invitación está sobre la mesa.
La decisión es tuya."

Next: L3_11
```

### Fragmento L3_11: Lucien presenta la Llave del Diván
```
Speaker: LUCIEN
Type: TEXT
Delay: 2

Content:
"Ha llegado al final del camino gratuito.

Lo que viene después... requiere compromiso.
La Llave del Diván no es solo un pago. Es una declaración.

Dice: 'Estoy listo para ver más. Para conocer más. Para ser parte de esto.'

No hay presión. Pero la puerta está ahí.
Y Diana está del otro lado."

Rewards:
- favor_reward: 10
- badge_reward: "desire_profiled"
- item_reward: "pista_3"
- item_reward: "invitation_to_divan"

Triggers: CONVERSION_FLOW_VIP

Completes: L3_DESIRE_PROFILE
```

---

# F5.5: NIVELES 4-6 (VIP - El Diván)

## Estructura resumida

Los niveles VIP siguen la misma arquitectura pero con contenido más profundo y evaluaciones más sofisticadas.

### NIVEL 4: Entrada al Diván

**Capítulo: L4_DIVAN_ENTRY**

Fragmentos clave:
1. Diana da bienvenida íntima (diferente tono que en Free)
2. Lucien presenta evaluación de comprensión
3. Preguntas sobre motivaciones de Diana, sus contradicciones
4. Evaluación de respuestas (score 0-10)
5. Respuesta según score:
   - Alto (7+): "Realmente me ves" → Contenido completo
   - Medio (4-6): "Comprendes algunas capas" → Contenido parcial
6. Entrega: Visión del Diván + acceso a Archivos de Diana

### NIVEL 5: Profundización

**Capítulo: L5_DEEPENING**

Fragmentos clave:
1. Diana reconoce la evolución del usuario desde Los Kinkys
2. "Diálogos de Intimidad" - Diana comparte vulnerabilidades
3. Usuario debe responder con empatía
4. Evaluación de respuestas:
   - Posesivas ("Puedo protegerte") → Diana se distancia
   - Empáticas ("Entiendo esa contradicción") → Diana se acerca
   - Arregladores ("No necesitas esos muros") → Diana se cierra
5. Entrega: Archivo Personal de Diana

### NIVEL 6: Culminación

**Capítulo: L6_CULMINATION**

Fragmentos clave:
1. Diana revela secreto final: ella también evaluaba al usuario
2. Lucien: "Ha presenciado humanidad auténtica"
3. Diana: inversión de poder - "Después de mostrarte todo, sigo siendo un misterio"
4. Entrega: Acceso a Círculo Íntimo
5. Introducción al Mapa del Deseo (upsell a tiers superiores)

---

# F5.6: MISIONES NARRATIVAS

## Tipos de misiones

### Misión de observación (Nivel 2)
```
Mission:
    type: OBSERVATION
    duration_hours: 72
    requirements:
        - hints_required: 3
    validation:
        - type: USER_REPORT (usuario describe lo que vio)
    rewards:
        - favors: 8
        - items: ["memory_fragment", "pista_2"]
```

### Misión de reflexión (Nivel 3)
```
Mission:
    type: QUESTIONNAIRE
    duration_hours: null (sin límite)
    requirements:
        - questions_answered: 5
    validation:
        - type: ALL_ANSWERED
    rewards:
        - favors: 10
        - badge: "desire_profiled"
```

### Misión de comprensión (Nivel 4)
```
Mission:
    type: QUIZ
    duration_hours: 24
    requirements:
        - correct_answers: 7 (de 10)
    validation:
        - type: SCORE_THRESHOLD
        - passing_score: 0.7
    rewards:
        - favors: 15
        - content_unlock: "vision_divan"
```

### Misión de empatía (Nivel 5)
```
Mission:
    type: DIALOGUE
    duration_hours: 48
    requirements:
        - empathetic_responses: 3
    validation:
        - type: RESPONSE_ANALYSIS
        - check: not_possessive, not_fixing
    rewards:
        - favors: 20
        - content_unlock: "personal_archive"
```

---

# F5.7: SISTEMA DE FLAGS

## Flags narrativos

Flags que se setean durante la narrativa y afectan el flujo:

```
first_reaction_fast: bool  # Reaccionó rápido en nivel 1
first_reaction_slow: bool  # Reaccionó lento en nivel 1
curious: bool              # Perfil: motivado por curiosidad
attracted: bool            # Perfil: motivado por atracción
seeking: bool              # Perfil: busca algo específico
intuitive: bool            # Perfil: guiado por intuición
visual: bool               # Preferencia: contenido visual
verbal: bool               # Preferencia: contenido verbal
mystery: bool              # Preferencia: misterio
personal: bool             # Preferencia: lo personal
depth: bool                # Acepta complejidad
surface: bool              # Prefiere superficie
high_comprehension: bool   # Score alto en evaluación VIP
empathetic_responses: bool # Respuestas empáticas en nivel 5
completed_all_levels: bool # Completó nivel 6
```

## Uso de flags

Los flags afectan:
- Variaciones de texto en fragmentos
- Opciones disponibles en decisiones
- Contenido desbloqueado
- Recomendaciones de Lucien
- Ofertas de conversión personalizadas

---

# F5.8: INTEGRACIÓN CON OTROS SISTEMAS

## Con sistema de Favores

```
Al completar fragmento con recompensa:
    await favor_service.grant_favors(
        user_id=user_id,
        amount=fragment.favor_reward,
        reason=FavorReason.NARRATIVE_REWARD,
        source_id=fragment.id
    )
```

## Con sistema de arquetipos

```
Durante Nivel 3 (Perfil de Deseo):
    if user.archetype is None:
        # Usar respuestas para determinar arquetipo
        archetype = determine_from_answers(answers)
        await archetype_service.set_archetype(user_id, archetype)
```

## Con Gabinete

```
Al completar niveles:
    # Desbloquear items en tienda
    await shop_service.unlock_item_for_user(user_id, "llave_fragmento_1")
    
Al entregar items narrativos:
    # Agregar al inventario
    await inventory_service.add_item(user_id, "pista_1")
```

## Con sistema de conversión

```
Al completar Nivel 3:
    # Activar flujo de conversión
    await conversion_service.trigger_vip_invitation(user_id)
    
Al completar Nivel 6:
    # Presentar Mapa del Deseo
    await conversion_service.present_desire_map(user_id)
```

---

# F5.9: COMANDOS Y HANDLERS

## Comando /historia o botón "La Historia"

```
Muestra estado actual de narrativa:

"Su viaje en el universo de Diana:

Nivel actual: {level}
Capítulo: {current_chapter}

Progreso: {progress_bar}

{Si tiene misión activa:}
⏳ Misión en curso: {mission_name}
Tiempo restante: {time_left}

{Si puede continuar:}
[Continuar la historia]

{Si debe esperar:}
Próximo capítulo disponible en: {time_until}"
```

## Handler de continuación

```
Cuando usuario toca "Continuar":
    1. Obtener progreso actual
    2. Determinar siguiente fragmento
    3. Verificar requisitos (nivel, tiempo, misión completada)
    4. Mostrar fragmento
    5. Procesar decisión si es interactivo
    6. Actualizar progreso
    7. Entregar recompensas si corresponde
```

## Handler de misiones narrativas

```
Cuando hay misión activa:
    - Mostrar progreso de misión
    - Procesar reportes/respuestas
    - Validar completado
    - Entregar recompensas
    - Continuar narrativa
```

---

# F5.10: SEED DATA - CONTENIDO INICIAL

## Script de carga

Crear script que cargue:
1. Todos los capítulos (6)
2. Todos los fragmentos (~50-70 para niveles 1-3)
3. Todas las decisiones
4. Ítems narrativos (pistas, fragmentos de memoria)
5. Misiones narrativas

## Prioridad de carga

```
FASE 5A (MVP):
- Nivel 1 completo (10-12 fragmentos)
- Nivel 2 completo (12-15 fragmentos)
- Nivel 3 completo (15-20 fragmentos)
- Flujo de conversión integrado

FASE 5B (Post-lanzamiento):
- Niveles 4-6 para VIP
- Fragmentos adicionales por arquetipo
- Easter eggs narrativos
```

---

# CRITERIOS DE ACEPTACIÓN FASE 5

## Modelos
- [ ] NarrativeChapter creado con todos los campos
- [ ] NarrativeFragment creado con ramificación
- [ ] NarrativeDecision creado
- [ ] UserNarrativeProgress creado
- [ ] Relaciones correctas entre modelos

## Contenido
- [ ] Nivel 1 cargado (mínimo 10 fragmentos)
- [ ] Nivel 2 cargado (mínimo 12 fragmentos)
- [ ] Nivel 3 cargado (mínimo 15 fragmentos)
- [ ] Decisiones configuradas con next_fragment
- [ ] Variaciones por arquetipo en nivel 3

## Flujos
- [ ] Usuario puede iniciar narrativa desde /start
- [ ] Fragmentos se muestran en secuencia
- [ ] Decisiones funcionan y guardan respuesta
- [ ] Delays entre fragmentos funcionan
- [ ] Misiones se activan y validan

## Integraciones
- [ ] Favores se otorgan al completar
- [ ] Items se agregan al inventario
- [ ] Arquetipos se consideran en variaciones
- [ ] Conversión se triggerea al completar nivel 3

## UX
- [ ] Comando /historia muestra progreso
- [ ] Usuario puede continuar donde dejó
- [ ] Misiones activas se muestran

---

# NOTAS DE IMPLEMENTACIÓN

1. **Contenido:** Los textos de fragmentos deben escribirse siguiendo las guías de voz de Lucien y Diana
2. **Delays:** Implementar delays como opcionales (pueden desactivarse)
3. **Persistencia:** Guardar progreso después de cada fragmento
4. **Timeout:** Manejar misiones expiradas gracefully
5. **Testing:** Crear usuario de prueba que pueda saltar requisitos

---

# ARCHIVOS DE REFERENCIA

- `/mnt/project/Narrativo.pdf` - Guión narrativo completo original
- Fase 0-4: Sistemas de soporte
- `lucien_character_bible.md` - Voz de Lucien
- `brief.md` - Personalidad de Diana/Kinky

---

*Documento generado para implementación por Claude Code*
*Proyecto: El Mayordomo del Diván*
*Fase: 5 - Narrativa y Contenido*
