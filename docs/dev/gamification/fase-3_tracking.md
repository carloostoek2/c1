# TRACKING: FASE 3 - ARQUETIPOS EXPANDIDOS

**Inicio:** 2024-12-30
**Estado:** ✅ Completado
**Progreso:** 9/9 tareas completadas (100%)

---

## RESUMEN DE TAREAS

| Tarea | Descripción | Estado |
|-------|-------------|--------|
| F3.1 | Modelo de Datos | ✅ Completado |
| F3.2 | Servicio de Tracking | ✅ Completado |
| F3.3 | Servicio de Detección | ✅ Completado |
| F3.4 | Palabras Emocionales | ✅ Completado |
| F3.5 | Integración con Handlers | ✅ Completado |
| F3.6 | Notificación de Arquetipo | ✅ Completado |
| F3.7 | Adaptación de Contenido | ✅ Completado |
| F3.8 | Impacto en Conversión | ✅ Completado |
| F3.9 | Comandos de Admin | ✅ Completado |

---

## DETALLE POR TAREA

### F3.1 - Modelo de Datos ✅ COMPLETADO

**Objetivo:** Crear estructuras de datos para tracking y clasificación de arquetipos.

- [x] Enum `ArchetypeType` con 6 arquetipos
- [x] Enum `InteractionType` con 14 tipos de interacción
- [x] Campos de arquetipo en modelo User
- [x] Modelo `UserBehaviorSignals` con 24 métricas
- [x] Modelo `BehaviorInteraction` para log
- [x] Migración Alembic (018)
- [x] Tests E2E

**Archivos creados:**
- `bot/database/enums.py` (ArchetypeType, InteractionType)
- `bot/gamification/database/models.py` (UserBehaviorSignals, BehaviorInteraction)
- `alembic/versions/018_add_archetype_behavior_tracking.py`

---

### F3.2 - Servicio de Tracking ✅ COMPLETADO

**Objetivo:** Registrar interacciones y calcular métricas de comportamiento.

- [x] `track_interaction()` - Registro con metadata
- [x] `update_metrics()` - Recálculo de métricas
- [x] `get_behavior_signals()` - Consulta de señales
- [x] `analyze_text_response()` - Análisis de texto
- [x] `sync_streak_metrics()` - Sincronización con rachas
- [x] Integración con GamificationContainer
- [x] Tests E2E (27 tests pasando)

**Archivos creados:**
- `bot/gamification/services/behavior_tracking.py`
- `tests/test_f3_archetype_behavior.py`

---

### F3.3 - Servicio de Detección ✅ COMPLETADO

**Objetivo:** Algoritmo que determina arquetipo basado en señales.

- [x] Fórmulas de scoring para 6 arquetipos
- [x] Función `normalize()` para valores
- [x] `detect_archetype()` - Detección completa
- [x] `get_archetype()` - Consulta sin recalcular
- [x] `should_reevaluate()` - Cuándo re-evaluar
- [x] `force_reevaluation()` - Re-evaluación forzada
- [x] `get_archetype_insights()` - Info detallada para UI
- [x] `get_archetype_distribution()` - Estadísticas globales
- [x] Umbral mínimo de interacciones (20)
- [x] Umbral mínimo de confianza (0.35)
- [x] Tests E2E (27 tests nuevos, 54 total)

**Archivos creados:**
- `bot/gamification/services/archetype_detection.py`

**Características:**
- Scoring ponderado por arquetipo con fórmulas específicas
- ArchetypeResult dataclass para resultados estructurados
- ArchetypeInsights para visualización en UI
- Re-evaluación automática después de 7 días o 50 interacciones
- Estadísticas de distribución de arquetipos
- Integración con GamificationContainer

---

### F3.4 - Palabras Emocionales ✅ COMPLETADO

**Objetivo:** Detectar contenido emocional en respuestas de texto.

- [x] Lista completa de palabras emocionales (60+)
- [x] Lista de frases emocionales
- [x] Función `has_emotional_content()`
- [x] Función `is_diana_question()`
- [x] Función `get_emotional_intensity()`
- [x] Módulo centralizado

**Archivos creados:**
- `bot/gamification/utils/emotional_words.py`

**Características:**
- 60+ palabras emocionales categorizadas
- Patrones de preguntas sobre Diana
- Cálculo de intensidad emocional
- API modular y reutilizable

---

### F3.5 - Integración con Handlers ✅ COMPLETADO

**Objetivo:** Agregar tracking a handlers principales del bot.

- [x] Middleware `BehaviorTrackingMiddleware`
- [x] Tracking de SESSION_START
- [x] Tracking de RETURN_AFTER_INACTIVITY
- [x] Tracking de BUTTON_CLICK
- [x] Tracking de TEXT_RESPONSE
- [x] Tracking de MENU_NAVIGATION
- [x] Tracking no-bloqueante (asyncio.create_task)

**Archivos creados:**
- `bot/middlewares/behavior_tracking.py`
- `bot/middlewares/__init__.py` (actualizado)

**Características:**
- Middleware automático para todos los handlers
- No bloquea la respuesta al usuario
- Detecta retorno después de inactividad (>24h)
- Análisis automático de respuestas de texto

---

### F3.6 - Notificación de Arquetipo ✅ COMPLETADO

**Objetivo:** Notificar al usuario cuando se detecta su arquetipo.

- [x] Mensajes de Lucien para cada arquetipo (6)
- [x] Badge de arquetipo (6 badges)
- [x] Servicio `ArchetypeNotificationService`
- [x] `notify_archetype_detected()` - Enviar notificación
- [x] `_grant_archetype_badge()` - Otorgar badge
- [x] NO notificar en re-evaluaciones iguales

**Archivos creados:**
- `bot/gamification/services/archetype_notification.py`
- `bot/gamification/services/container.py` (actualizado)

**Mensajes implementados:**
- EXPLORER: "Su curiosidad es... insaciable"
- DIRECT: "Su claridad es... refrescante"
- ROMANTIC: "Busca conexión... peligrosamente hermoso"
- ANALYTICAL: "Es irritante... pero respetable"
- PERSISTENT: "Algo casi... conmovedor en esa tenacidad"
- PATIENT: "La paciencia es la virtud más subestimada"

---

### F3.7 - Adaptación de Contenido ✅ COMPLETADO

**Objetivo:** Variar mensajes según arquetipo del usuario.

- [x] Helper `get_adapted_message()`
- [x] Variaciones de misión diaria (6)
- [x] Variaciones de bienvenida de regreso (6)
- [x] Variaciones de misión completada (6)
- [x] Variaciones de racha alcanzada (6)
- [x] Variaciones de level up (6)
- [x] Variaciones de acción no permitida (6)

**Archivos creados:**
- `bot/gamification/services/archetype_messages.py`

**Mensajes implementados:**
- `mission_daily_available`
- `welcome_back`
- `mission_completed`
- `streak_milestone`
- `level_up`
- `action_not_allowed`

---

### F3.8 - Impacto en Conversión ✅ COMPLETADO

**Objetivo:** Triggers y mensajes de conversión personalizados.

- [x] ConversionTrigger dataclass
- [x] ConversionOffer dataclass
- [x] Triggers de conversión por arquetipo (6)
- [x] Mensajes de conversión personalizados (6)
- [x] `ArchetypeConversionService`
- [x] `get_trigger()` - Obtener trigger por arquetipo
- [x] `get_conversion_message()` - Mensaje personalizado
- [x] `should_show_offer()` - Timing óptimo
- [x] `get_optimal_timing()` - Descripción del momento

**Archivos creados:**
- `bot/gamification/services/archetype_conversion.py`

**Triggers implementados:**
- EXPLORER: `easter_egg_requires_vip`
- DIRECT: `action_completed`
- ROMANTIC: `emotional_fragment_viewed`
- ANALYTICAL: `quiz_high_score`
- PERSISTENT: `return_after_inactivity`
- PATIENT: `streak_7_days`

---

### F3.9 - Comandos de Admin ✅ COMPLETADO

**Objetivo:** Herramientas de administración para arquetipos.

- [x] `/admin_archetype <user_id>` - Ver arquetipo de usuario
- [x] `/admin_archetype_stats` - Estadísticas globales
- [x] `/admin_archetype_refresh <user_id>` - Forzar re-evaluación
- [x] Barras visuales de progreso
- [x] Información de señales principales

**Archivos creados:**
- `bot/handlers/admin/archetype.py`
- `bot/handlers/admin/__init__.py` (actualizado)

**Características:**
- Vista completa de arquetipo con scores y confianza
- Distribución global de arquetipos
- Re-evaluación forzada para debugging
- Visualización de comportamientos clave

---

## COMMITS REALIZADOS

1. `99add94` - feat(F3.1, F3.2): Sistema de Arquetipos y Tracking de Comportamiento
2. `b089f0a` - feat(F3.3): ArchetypeDetectionService con algoritmo de scoring
3. (pendiente) - feat(F3.4-F3.9): Sistema completo de arquetipos

---

## ARCHIVOS FASE 3

**Servicios:**
- `bot/gamification/services/archetype_detection.py` - Detección de arquetipos
- `bot/gamification/services/archetype_notification.py` - Notificaciones
- `bot/gamification/services/archetype_messages.py` - Mensajes adaptados
- `bot/gamification/services/archetype_conversion.py` - Triggers de conversión
- `bot/gamification/services/behavior_tracking.py` - Tracking de comportamiento
- `bot/gamification/services/container.py` - Container actualizado

**Utilidades:**
- `bot/gamification/utils/emotional_words.py` - Palabras emocionales

**Middlewares:**
- `bot/middlewares/behavior_tracking.py` - Tracking automático

**Handlers:**
- `bot/handlers/admin/archetype.py` - Comandos admin

**Total archivos nuevos:** 6
**Total archivos modificados:** 4

---

## NOTAS

- El tracking es no-bloqueante (asyncio.create_task)
- No se guarda contenido de mensajes, solo métricas
- Umbral de detección: 20 interacciones mínimas
- Umbral de confianza: 0.35 mínimo
- Re-evaluación: cada 7 días o 50 interacciones

---

**Última actualización:** 2025-12-30
**Estado final:** ✅ FASE 3 COMPLETADA
