# TRACKING: FASE 3 - ARQUETIPOS EXPANDIDOS

**Inicio:** 2024-12-30
**Estado:** 🟡 En Progreso
**Progreso:** 3/9 tareas completadas (33%)

---

## RESUMEN DE TAREAS

| Tarea | Descripción | Estado |
|-------|-------------|--------|
| F3.1 | Modelo de Datos | ✅ Completado |
| F3.2 | Servicio de Tracking | ✅ Completado |
| F3.3 | Servicio de Detección | ✅ Completado |
| F3.4 | Palabras Emocionales | 🟡 Parcial |
| F3.5 | Integración con Handlers | 🔴 Pendiente |
| F3.6 | Notificación de Arquetipo | 🔴 Pendiente |
| F3.7 | Adaptación de Contenido | 🔴 Pendiente |
| F3.8 | Impacto en Conversión | 🔴 Pendiente |
| F3.9 | Comandos de Admin | 🔴 Pendiente |

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

### F3.4 - Palabras Emocionales 🟡 PARCIAL

**Objetivo:** Detectar contenido emocional en respuestas de texto.

- [x] Lista básica de palabras emocionales (implementada en F3.2)
- [ ] Lista completa de palabras (60+)
- [ ] Lista de frases emocionales
- [ ] Función `has_emotional_content()` mejorada
- [ ] Tests

---

### F3.5 - Integración con Handlers 🔴 PENDIENTE

**Objetivo:** Agregar tracking a handlers principales del bot.

- [ ] start.py - SESSION_START, RETURN_AFTER_INACTIVITY
- [ ] dynamic_menu.py - MENU_NAVIGATION, BUTTON_CLICK
- [ ] story.py - CONTENT_VIEW, DECISION_MADE
- [ ] decisions.py - DECISION_MADE con tiempo
- [ ] shop.py - BUTTON_CLICK
- [ ] missions.py - CONTENT_VIEW
- [ ] Middleware de tracking (opcional)
- [ ] Tests de integración

---

### F3.6 - Notificación de Arquetipo 🔴 PENDIENTE

**Objetivo:** Notificar al usuario cuando se detecta su arquetipo.

- [ ] Mensajes de Lucien para cada arquetipo (6)
- [ ] Badge de arquetipo (6 badges)
- [ ] Lógica de cuándo notificar
- [ ] NO notificar en re-evaluaciones iguales
- [ ] Tests

---

### F3.7 - Adaptación de Contenido 🔴 PENDIENTE

**Objetivo:** Variar mensajes según arquetipo del usuario.

- [ ] Helper `get_adapted_message()`
- [ ] Variaciones de mensaje de misión diaria (6)
- [ ] Variaciones de bienvenida de regreso
- [ ] Al menos 5 mensajes con variaciones
- [ ] Tests

---

### F3.8 - Impacto en Conversión 🔴 PENDIENTE

**Objetivo:** Triggers y mensajes de conversión personalizados.

- [ ] Triggers de conversión por arquetipo (6)
- [ ] Mensajes de conversión personalizados (6)
- [ ] Timing óptimo por arquetipo
- [ ] Tests

---

### F3.9 - Comandos de Admin 🔴 PENDIENTE

**Objetivo:** Herramientas de administración para arquetipos.

- [ ] `/admin_archetype <user_id>` - Ver arquetipo
- [ ] `/admin_archetype_stats` - Estadísticas globales
- [ ] `/admin_archetype_refresh <user_id>` - Forzar re-evaluación
- [ ] Tests

---

## COMMITS REALIZADOS

1. `99add94` - feat(F3.1, F3.2): Sistema de Arquetipos y Tracking de Comportamiento
2. `b089f0a` - feat(F3.3): ArchetypeDetectionService con algoritmo de scoring

---

## PRÓXIMOS PASOS

1. **F3.4** - Completar lista de palabras emocionales
2. **F3.5** - Integrar tracking en handlers principales
3. **F3.6** - Notificación de arquetipo detectado

---

## NOTAS

- El tracking debe ser no-bloqueante (fire-and-forget)
- No guardar contenido de mensajes, solo métricas
- Umbral recomendado: 20 interacciones mínimas para detectar

---

**Última actualización:** 2025-12-30
