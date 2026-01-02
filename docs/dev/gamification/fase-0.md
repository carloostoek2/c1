# REQUERIMIENTO: FASE 0 - FUNDAMENTOS
## Proyecto: El Mayordomo del Diván
## Bot de Telegram para Señorita Kinky

---

# CONTEXTO DEL PROYECTO

Este bot es "El Mayordomo del Diván" - un bot de Telegram donde el personaje **Lucien** (un mayordomo británico elegante, evaluador y protector de Diana) guía a los usuarios a través de un viaje narrativo gamificado.

**Objetivo del bot:**
- Engagement de usuarios en canal Free (Los Kinkys)
- Conversión Free → VIP (El Diván)
- Upsell VIP → Premium/Mapa del Deseo
- Retención de suscriptores

**Voz del bot:** Todos los mensajes son de Lucien. Tono formal (siempre "usted"), elegante, evaluador, con sarcasmo sutil. Ver archivo `lucien_character_bible.md` en el proyecto para referencia completa de personalidad.

---

# FASE 0: FUNDAMENTOS

## Objetivo
Establecer las bases del sistema de gamificación y preparar la estructura para las fases siguientes.

---

# F0.1: SISTEMA DE ECONOMÍA - "FAVORES"

## Descripción
Reemplazar el sistema actual de "Besitos" por "Favores". Los Favores representan reconocimientos que Diana otorga a usuarios dignos. Cada Favor tiene peso significativo - Diana no regala reconocimiento fácilmente.

## Especificaciones

### Renombrar en todo el sistema
- "Besitos" → "Favores"
- "besitos" → "favores"
- "besito" → "favor"
- Actualizar en: modelos de BD, servicios, handlers, mensajes, UI

### Configuración de valores de ganancia

| Acción | Favores | Frecuencia | Límite |
|--------|---------|------------|--------|
| Reaccionar a publicación del canal | +0.1 | Por reacción | 10/día |
| Primera reacción del día | +0.5 | 1x día | - |
| Completar misión diaria | +1 | 1x día | - |
| Completar misión semanal | +3 | 1x semana | - |
| Completar evaluación de nivel | +5 | Por nivel | - |
| Bonus racha 7 días | +2 | Cada 7 días consecutivos | - |
| Bonus racha 30 días | +10 | Cada 30 días consecutivos | - |
| Encontrar easter egg | +2 a +5 | Variable | - |
| Referir usuario activo | +5 | Por referido que complete onboarding | - |

### Notas de implementación
- El sistema debe soportar **decimales** (0.1, 0.5, etc.)
- Mostrar al usuario con 1 decimal cuando tenga decimales, entero cuando sea exacto
- Ejemplo: "3.5 Favores" o "10 Favores"

### Niveles del Protocolo de Acceso

| Nivel | Nombre | Favores Mínimos | Descripción Interna |
|-------|--------|-----------------|---------------------|
| 1 | Visitante | 0 | Usuario nuevo |
| 2 | Observado | 5 | Lucien ha notado su presencia |
| 3 | Evaluado | 15 | Ha pasado primeras pruebas |
| 4 | Reconocido | 35 | Diana sabe que existe |
| 5 | Admitido | 70 | Tiene derecho a estar |
| 6 | Confidente | 120 | Lucien comparte información |
| 7 | Guardián de Secretos | 200 | Círculo más íntimo |

### Migración de datos existentes
- Si existen usuarios con "Besitos", convertir proporcionalmente
- Fórmula sugerida: `nuevos_favores = besitos_actuales / 50` (ajustar según inflación actual)
- Mantener niveles relativos de los usuarios

---

# F0.2: ARCHIVO DE CONSTANTES DE MENSAJES DE LUCIEN

## Descripción
Crear un archivo centralizado con todos los mensajes del bot en voz de Lucien. Esto permite:
- Consistencia de voz en todo el bot
- Facilidad de edición sin tocar lógica
- Referencia única para el personaje

## Especificación

### Ubicación
`bot/utils/lucien_messages.py`

### Estructura del archivo

```
Clase LucienMessages con constantes organizadas por categoría:

CATEGORÍAS REQUERIDAS:

1. ONBOARDING
   - WELCOME_FIRST: Mensaje de bienvenida para usuario nuevo
   - WELCOME_RETURNING: Mensaje para usuario que regresa (con placeholder {days_away})
   - WELCOME_VIP: Mensaje de bienvenida para usuario VIP
   - FIRST_ACTION_COMPLETE: Después de primera acción

2. FAVORES
   - FAVOR_EARNED: Notificación de ganancia (placeholder {amount})
   - FAVOR_EARNED_MILESTONE: Al llegar a hitos (placeholder {total})
   - FAVOR_SPENT: Al gastar favores
   - FAVOR_INSUFFICIENT: Cuando no tiene suficientes
   - FAVOR_BALANCE: Al consultar balance

3. NIVELES
   - LEVEL_UP_GENERIC: Subida de nivel genérica
   - LEVEL_UP_2 a LEVEL_UP_7: Mensaje específico por cada nivel
   - LEVEL_CHECK: Al consultar nivel actual

4. ERRORES
   - ERROR_GENERIC: Error general
   - ERROR_NOT_FOUND: Recurso no encontrado
   - ERROR_PERMISSION: Sin permisos
   - ERROR_TIMEOUT: Tiempo agotado
   - ERROR_INVALID_INPUT: Entrada inválida

5. CONFIRMACIONES
   - CONFIRM_ACTION: Confirmación genérica
   - CONFIRM_PURCHASE: Compra realizada
   - CONFIRM_MISSION_COMPLETE: Misión completada

6. GABINETE (TIENDA)
   - CABINET_WELCOME: Bienvenida al Gabinete
   - CABINET_CATEGORY_EPHEMERAL: Descripción categoría Efímeros
   - CABINET_CATEGORY_DISTINCTIVE: Descripción categoría Distintivos
   - CABINET_CATEGORY_KEYS: Descripción categoría Llaves
   - CABINET_CATEGORY_RELICS: Descripción categoría Reliquias
   - CABINET_ITEM_PURCHASED: Compra exitosa
   - CABINET_EMPTY: Sin items disponibles

7. MISIONES
   - MISSION_NEW_DAILY: Nueva misión diaria disponible
   - MISSION_NEW_WEEKLY: Nueva misión semanal disponible
   - MISSION_COMPLETE: Misión completada
   - MISSION_FAILED: Misión no completada a tiempo
   - MISSION_PROGRESS: Progreso de misión

8. ARQUETIPOS (para cuando se detecta)
   - ARCHETYPE_EXPLORER: Reconocimiento al Explorador
   - ARCHETYPE_DIRECT: Reconocimiento al Directo
   - ARCHETYPE_ROMANTIC: Reconocimiento al Romántico
   - ARCHETYPE_ANALYTICAL: Reconocimiento al Analítico
   - ARCHETYPE_PERSISTENT: Reconocimiento al Persistente
   - ARCHETYPE_PATIENT: Reconocimiento al Paciente

9. RETENCIÓN
   - INACTIVE_3_DAYS: Usuario inactivo 3 días
   - INACTIVE_7_DAYS: Usuario inactivo 7 días
   - INACTIVE_14_DAYS: Usuario inactivo 14+ días
   - STREAK_BROKEN: Racha perdida
   - STREAK_MILESTONE_7: Racha de 7 días
   - STREAK_MILESTONE_30: Racha de 30 días

10. CONVERSIÓN
    - CONVERSION_TEASER: Mención sutil del VIP
    - CONVERSION_INVITATION: Invitación formal al Diván
    - CONVERSION_KEY_OFFER: Oferta de Llave del Diván
    - CONVERSION_PREMIUM_INTRO: Introducción a contenido Premium
    - CONVERSION_MAP_INTRO: Introducción al Mapa del Deseo
```

### Contenido de mensajes clave (ejemplos para referencia de tono)

**WELCOME_FIRST:**
"Buenas noches. O días. El tiempo es relativo cuando se trata de Diana.

Soy Lucien. Administro el acceso al universo de la Señorita Kinky. No soy su amigo. No soy su enemigo. Soy... el filtro.

Diana no recibe a cualquiera. Mi trabajo es determinar si usted merece su atención. Comencemos."

**ERROR_INSUFFICIENT_FAVORS:**
"Sus Favores son insuficientes para esto.

Diana no otorga crédito. Acumule más Favores y regrese."

**LEVEL_UP_4 (Reconocido):**
"Interesante. Diana ha mencionado su nombre. No pregunte qué dijo exactamente - eso sería una indiscreción por mi parte.

Pero sepa que ahora es... Reconocido. Eso conlleva privilegios. Y expectativas."

**CABINET_WELCOME:**
"Bienvenido a mi Gabinete. Aquí guardo ciertos... artículos que Diana ha autorizado para intercambio.

Los Favores que ha acumulado pueden convertirse en algo más tangible. Examine con cuidado. No todo lo que brilla merece su inversión."

**ARCHETYPE_PATIENT:**
"He observado algo en usted. Toma su tiempo. Procesa. No reacciona por impulso.

Eso es raro. Diana nota a quienes no se apresuran por agradar. Usted no busca aprobación inmediata. Eso tiene valor."

**INACTIVE_7_DAYS:**
"Una semana. El tiempo suficiente para que algunos olviden por qué vinieron aquí.

¿Es usted de esos? ¿O hay algo que lo retiene?"

### Reglas de estilo para todos los mensajes
1. Lucien siempre usa "usted", nunca tutea
2. Tono formal pero no robótico
3. Puntos suspensivos para pausas dramáticas (máximo 3 puntos)
4. Sarcasmo sutil, nunca agresivo
5. Referencias a Diana en tercera persona con reverencia
6. Evaluación constante del usuario (implícita o explícita)
7. Nunca usa emojis en el texto (pueden ir en botones)
8. Párrafos cortos, máximo 3-4 líneas por bloque

---

# F0.3: SISTEMA DE ARQUETIPOS EXPANDIDO

## Descripción
Expandir el sistema actual de 3 arquetipos básicos a 6 arquetipos del universo narrativo.

## Arquetipos actuales (a deprecar gradualmente)
- IMPULSIVE
- CONTEMPLATIVE  
- SILENT

## Nuevos arquetipos

| Arquetipo | Enum Value | Descripción |
|-----------|------------|-------------|
| Explorador | EXPLORER | Busca cada detalle, revisa todo |
| Directo | DIRECT | Va al grano, respuestas concisas |
| Romántico | ROMANTIC | Poético, busca conexión emocional |
| Analítico | ANALYTICAL | Reflexivo, busca comprensión |
| Persistente | PERSISTENT | No se rinde, múltiples intentos |
| Paciente | PATIENT | Toma tiempo, procesa profundamente |

## Reglas de detección

### EXPLORER (Explorador)
Condiciones (cumplir 2+ de 3):
- Ha visto >80% del contenido disponible para su nivel
- Ha encontrado al menos 1 easter egg
- Tiempo promedio en contenido >30 segundos

### DIRECT (Directo)
Condiciones (cumplir 2+ de 3):
- Respuestas promedio <15 palabras
- Tiempo de decisión promedio <5 segundos
- Usa botones/acciones rápidas >80% del tiempo vs texto libre

### ROMANTIC (Romántico)
Condiciones (cumplir 2+ de 3):
- Respuestas contienen palabras emocionales (definir lista: amor, sentir, corazón, alma, etc.)
- Respuestas promedio >30 palabras
- Interactúa más con contenido etiquetado como "emocional"

### ANALYTICAL (Analítico)
Condiciones (cumplir 2+ de 3):
- Score >80% en evaluaciones/cuestionarios
- Hace preguntas al bot
- Respuestas estructuradas (usa puntos, enumera, etc.)

### PERSISTENT (Persistente)
Condiciones (cumplir 2+ de 3):
- Ha retornado después de 3+ días de inactividad, al menos 2 veces
- Múltiples intentos en desafíos/evaluaciones
- Reintenta acciones fallidas

### PATIENT (Paciente)
Condiciones (cumplir 2+ de 3):
- Tiempo de respuesta promedio >30 segundos
- No usa opciones de "skip" o "saltar"
- Racha activa de 7+ días

## Lógica de asignación
1. Evaluar todas las condiciones del usuario
2. Calcular porcentaje de cumplimiento por arquetipo
3. Si un arquetipo tiene >60% de cumplimiento → asignar
4. Si múltiples >60% → asignar el de mayor porcentaje
5. Si ninguno >60% → mantener sin arquetipo (campo null)
6. Re-evaluar cada 7 días o después de 10 interacciones significativas

## Modelo de datos
Agregar a modelo de usuario:
- `archetype`: Enum nullable con los 6 valores
- `archetype_confidence`: Float 0-1 indicando confianza de la detección
- `archetype_detected_at`: DateTime de última detección
- `archetype_signals`: JSON con las señales detectadas

---

# F0.4: INVENTARIO INICIAL DEL GABINETE

## Descripción
Definir los items iniciales de la tienda (Gabinete de Lucien).

## Categorías

| Categoría BD | Nombre Display | Descripción de Lucien |
|--------------|----------------|----------------------|
| ephemeral | Efímeros | "Placeres de un solo uso. Intensos pero fugaces." |
| distinctive | Distintivos | "Marcas visibles de su posición. Para quienes valoran el reconocimiento." |
| keys | Llaves | "Abren puertas a contenido que otros no pueden ver." |
| relics | Reliquias | "Los objetos más valiosos del Gabinete. Requieren Favores... y dignidad." |

## Items iniciales

### Categoría: Efímeros (ephemeral)

| ID | Nombre | Precio (Favores) | Descripción | Efecto Técnico |
|----|--------|------------------|-------------|----------------|
| eph_001 | Sello del Día | 1 | "Una marca temporal. Válida hasta medianoche." | Badge temporal 24h |
| eph_002 | Susurro Efímero | 3 | "Un mensaje que Diana grabó en un momento de... inspiración." | Acceso a audio exclusivo de 15s |
| eph_003 | Pase de Prioridad | 5 | "Cuando Diana abra contenido limitado, usted estará primero." | Flag de prioridad para próximo contenido limitado |
| eph_004 | Vistazo al Sensorium | 15 | "Una muestra del contenido Sensorium. Treinta segundos que alterarán sus sentidos." | Acceso a preview de Sensorium |

### Categoría: Distintivos (distinctive)

| ID | Nombre | Precio (Favores) | Descripción | Efecto Técnico |
|----|--------|------------------|-------------|----------------|
| dist_001 | Sello del Visitante | 2 | "La marca más básica. Indica que existe en este universo." | Badge permanente nivel 1 |
| dist_002 | Insignia del Observador | 5 | "Lucien lo ha notado. Eso significa algo... o nada." | Badge permanente nivel 2 |
| dist_003 | Marca del Evaluado | 8 | "Ha pasado las primeras pruebas. No todas, pero algunas." | Badge permanente nivel 3 |
| dist_004 | Emblema del Reconocido | 12 | "Diana sabe su nombre. No es poco." | Badge permanente nivel 4 |
| dist_005 | Marca del Confidente | 25 | "Pocos llevan esta marca. Indica que Lucien confía en usted. Relativamente." | Badge permanente nivel 5 |

### Categoría: Llaves (keys)

| ID | Nombre | Precio (Favores) | Descripción | Efecto Técnico |
|----|--------|------------------|-------------|----------------|
| key_001 | Llave del Fragmento I | 10 | "Abre el primer secreto oculto. Lo que Diana no cuenta en público." | Desbloquea fragmento narrativo secreto #1 |
| key_002 | Llave del Fragmento II | 12 | "El segundo secreto. Más profundo que el primero." | Desbloquea fragmento narrativo secreto #2 |
| key_003 | Llave del Fragmento III | 15 | "El tercer secreto. Aquí las cosas se ponen... interesantes." | Desbloquea fragmento narrativo secreto #3 |
| key_004 | Llave del Archivo Oculto | 20 | "Acceso a memorias que Diana preferiría olvidar. O quizás no." | Desbloquea conjunto de fragmentos especiales |

### Categoría: Reliquias (relics)

| ID | Nombre | Precio (Favores) | Descripción | Efecto Técnico |
|----|--------|------------------|-------------|----------------|
| rel_001 | El Primer Secreto | 30 | "Un objeto que representa el primer secreto que Diana compartió conmigo. Ahora puede ser suyo." | Item coleccionable único + badge especial |
| rel_002 | Fragmento del Espejo | 40 | "Un pedazo del espejo donde Diana se mira antes de cada sesión. Metafóricamente, claro." | Item coleccionable + desbloquea contenido |
| rel_003 | La Carta No Enviada | 50 | "Diana escribió esto hace tiempo. Nunca lo envió. Ahora usted puede leerlo." | Item coleccionable + fragmento narrativo exclusivo |

## Notas de implementación
- Los items deben tener campo `is_limited` para ediciones limitadas futuras
- Los items deben tener campo `stock` (null = ilimitado)
- Los efímeros deben tener campo `duration_hours` para expiración
- Las llaves deben tener campo `unlocks_content_id` para vincular con narrativa

---

# F0.5: ESTRUCTURA DE CONTENIDO NARRATIVO

## Descripción
Definir la estructura para cargar el contenido narrativo del guión.

## Estructura de capítulos

### Canal Free (Los Kinkys) - Niveles 1-3

**Capítulo 1: Bienvenida**
- Tipo: INTRO
- Requisito: Ninguno (automático al entrar)
- Fragmentos:
  - 1.1: Bienvenida de Diana (intro visual + texto)
  - 1.2: Lucien presenta el primer desafío
  - 1.3A: Respuesta para usuario impulsivo (<5s respuesta)
  - 1.3B: Respuesta para usuario paciente (>30s respuesta)
  - 1.4: Primera pista + entrega de Mochila del Viajero

**Capítulo 2: Observación**
- Tipo: MAIN
- Requisito: Completar Capítulo 1 + Nivel 2 (Observado)
- Fragmentos:
  - 2.1: Diana nota el regreso del usuario
  - 2.2: Misión de observación (encontrar pistas en 3 días)
  - 2.3A-F: Respuestas por arquetipo
  - 2.4: Reconocimiento + Pista 2 + Fragmento de Memoria

**Capítulo 3: Perfil de Deseo**
- Tipo: MAIN
- Requisito: Completar Capítulo 2 + Nivel 3 (Evaluado)
- Fragmentos:
  - 3.1: Diana presenta la prueba final del nivel Free
  - 3.2: Cuestionario de Perfil de Deseo (5-7 preguntas)
  - 3.3A-F: Evaluación personalizada por arquetipo
  - 3.4: La Invitación - "Llave del Diván" (punto de conversión)

### Canal VIP (El Diván) - Niveles 4-6

**Capítulo 4: Entrada al Diván**
- Tipo: VIP
- Requisito: Ser VIP + Completar Capítulo 3
- Fragmentos:
  - 4.1: Bienvenida íntima de Diana
  - 4.2: Lucien presenta el desafío de comprensión
  - 4.3A: Respuesta alta comprensión (7+ correctas)
  - 4.3B: Respuesta comprensión media (4-6 correctas)
  - 4.4: Entrega Visión del Diván + Pista complementaria

**Capítulo 5: Profundización**
- Tipo: VIP
- Requisito: Completar Capítulo 4 + Nivel 5 (Admitido)
- Fragmentos:
  - 5.1: Diana reconoce la evolución del usuario
  - 5.2: Diálogos de vulnerabilidad (confesiones de Diana)
  - 5.3: Evaluación de respuestas empáticas vs posesivas
  - 5.4: Archivo Personal de Diana (recompensa)

**Capítulo 6: Culminación**
- Tipo: CLIMAX
- Requisito: Completar Capítulo 5 + Nivel 6 (Confidente)
- Fragmentos:
  - 6.1: Diana revela el secreto final
  - 6.2: Lucien reconoce la transformación
  - 6.3: Síntesis completa + introducción al Mapa del Deseo
  - 6.4: Acceso a Círculo Íntimo (punto de upsell máximo)

## Campos requeridos por fragmento

```
NarrativeFragment:
  - id: int
  - chapter_id: int (FK)
  - fragment_key: string (ej: "1.3A")
  - title: string
  - content: text (el texto narrativo)
  - speaker: enum (DIANA, LUCIEN, NARRATOR)
  - media_type: enum (TEXT, IMAGE, AUDIO, VIDEO) nullable
  - media_url: string nullable
  - order: int
  - requires_archetype: enum nullable (si solo aplica a un arquetipo)
  - requires_response_time: string nullable ("fast", "slow")
  - next_fragment_id: int nullable (para flujo lineal)
  - decisions: JSON (array de opciones si hay bifurcación)
  - rewards: JSON (favores, items, badges a otorgar)
```

## Seed data inicial
- Crear script que cargue los capítulos 1-3 completos para Free
- Los capítulos 4-6 pueden ser placeholder inicialmente
- Priorizar que el flujo Free esté completo para testing

---

# CRITERIOS DE ACEPTACIÓN FASE 0

## F0.1 Economía
- [ ] Modelo de BD actualizado: "besitos" → "favores"
- [ ] Soporte para decimales en favores
- [ ] Tabla de configuración con valores de ganancia
- [ ] Migración de datos existentes ejecutada
- [ ] Tests de cálculo de favores pasan

## F0.2 Mensajes de Lucien
- [ ] Archivo `lucien_messages.py` creado con todas las categorías
- [ ] Mínimo 50 mensajes definidos
- [ ] Todos los mensajes usan "usted"
- [ ] Ningún mensaje tiene emojis en el texto

## F0.3 Arquetipos
- [ ] Enum actualizado con 6 arquetipos
- [ ] Modelo de usuario con campos de arquetipo
- [ ] Servicio de detección con reglas implementadas
- [ ] Migración ejecutada

## F0.4 Gabinete
- [ ] Categorías creadas en BD
- [ ] Mínimo 15 items cargados
- [ ] Precios en nueva escala de Favores
- [ ] Descripciones de Lucien para cada item

## F0.5 Estructura Narrativa
- [ ] Modelo de capítulos y fragmentos listo
- [ ] Capítulos 1-3 definidos (pueden ser placeholder de contenido)
- [ ] Relaciones entre fragmentos configuradas
- [ ] Sistema de requisitos funcionando

---

# NOTAS PARA IMPLEMENTACIÓN

1. **Prioridad de migración:** Primero BD, luego servicios, luego handlers, luego UI
2. **Backward compatibility:** Mantener funcionalidad existente mientras se migra
3. **Testing:** Cada cambio debe tener test correspondiente
4. **Documentación:** Actualizar docs/ con cambios realizados

---

# ARCHIVOS DE REFERENCIA

- `/mnt/project/brief.md` - Identidad de marca Señorita Kinky
- `/mnt/project/Narrativo.pdf` - Guión narrativo completo (extraer texto de pages 1-12)
- `lucien_character_bible.md` - Personalidad completa de Lucien
- `docs/narrativa/` - Documentación del módulo narrativo existente
- `bot/gamification/` - Módulo de gamificación existente

---

*Documento generado para implementación por Claude Code*
*Proyecto: El Mayordomo del Diván*
*Fase: 0 - Fundamentos*
