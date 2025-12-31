# TRACKING: FASE 5 - NARRATIVA Y CONTENIDO
## El Mayordomo del Diván

---

## ESTADO GENERAL: 🟢 SPRINT 1 COMPLETADO

**Sistema Base:** ✅ 100% implementado (modelos extendidos, servicios, handlers)
**Contenido Narrativo:** 🟢 Nivel 1 completo (9 fragmentos, 11 decisiones)
**Features Implementadas:** ✅ SPRINT 1 MVP completo

---

## F5.1: MODELO DE DATOS NARRATIVO

### ✅ LO QUE YA EXISTE:
- [x] NarrativeChapter (modelo base)
- [x] NarrativeFragment (modelo base)
- [x] FragmentDecision (modelo base)
- [x] UserNarrativeProgress (modelo base)
- [x] FragmentRequirement (requisitos avanzados)
- [x] FragmentVariant (variantes por contexto)
- [x] UserDecisionHistory (historial completo)
- [x] Sistema inmersivo completo (visitas, cooldowns, challenges, journal)

### ✅ COMPLETADO EN SPRINT 1:
- [x] **F5.1.1:** Extender NarrativeChapter con campos Fase 5
  - [ ] `level` (int 1-6)
  - [ ] `requires_level` (int)
  - [ ] `requires_chapter_completed` (FK)
  - [ ] `requires_archetype` (str)
  - [ ] `estimated_duration_minutes` (int)
  - [ ] `favor_reward` (float)
  - [ ] `badge_reward` (str)
  - [ ] `item_reward` (str)

- [ ] **F5.1.2:** Extender NarrativeFragment con campos Fase 5
  - [ ] `delay_seconds` (int) - pausa dramática
  - [ ] `is_decision_point` (bool)
  - [ ] `decisions` (JSON array) - legacy field opcional
  - [ ] `next_fragment_id` (FK) - para flujo lineal
  - [ ] `condition_type` (str)
  - [ ] `condition_value` (str)

- [ ] **F5.1.3:** Extender FragmentDecision con campos Fase 5
  - [ ] `subtext` (str) - texto pequeño debajo
  - [ ] `favor_change` (float) - puede ser negativo
  - [ ] `sets_flag` (str) - flag a setear
  - [ ] `requires_flag` (str) - flag requerido

- [ ] **F5.1.4:** Extender UserNarrativeProgress con campos Fase 5
  - [ ] `current_level` (int 1-6)
  - [ ] `chapters_completed` (JSON array)
  - [ ] `fragments_seen` (JSON array)
  - [ ] `decisions_made` (JSON dict)
  - [ ] `narrative_flags` (JSON dict) - NEW: Sistema de flags
  - [ ] `active_mission_id` (str)
  - [ ] `mission_started_at` (datetime)
  - [ ] `mission_data` (JSON)
  - [ ] `level_1_completed_at` ... `level_6_completed_at`

- [ ] **F5.1.5:** Crear migración Alembic
  - [ ] Migración para extender modelos existentes
  - [ ] Backward compatible (campos nullable)

---

## F5.2: NIVEL 1 - BIENVENIDA (Los Kinkys)

**Status:** 🔴 0/12 fragmentos

### Capítulo: L1_WELCOME

- [ ] **F5.2.1:** Crear capítulo L1_WELCOME
  - [ ] level=1, chapter_type=FREE
  - [ ] favor_reward=5
  - [ ] badge_reward="first_step"

- [ ] **F5.2.2:** Fragmentos narrativos (10-12 fragmentos)
  - [ ] L1_01: Primera aparición de Diana
  - [ ] L1_02: Lucien se presenta
  - [ ] L1_03: El primer desafío
  - [ ] L1_03B: Respuesta al desafiante (branch)
  - [ ] L1_04: Esperando reacción (SYSTEM)
  - [ ] L1_05A: Reacción rápida (<2 min) - sets_flag: "first_reaction_fast"
  - [ ] L1_05B: Reacción pausada (>2 min) - sets_flag: "first_reaction_slow"
  - [ ] L1_06: Entrega de recompensas (Diana)
  - [ ] L1_07: Explicación de Lucien + Cierre

- [ ] **F5.2.3:** Integración trigger de reacción
  - [ ] Background task detecta reacción en canal
  - [ ] Mide tiempo de respuesta
  - [ ] Continúa automáticamente a L1_05A o L1_05B
  - [ ] Timeout 24 horas → L1_TIMEOUT

- [ ] **F5.2.4:** Recompensas
  - [ ] Integración con FavorService (+5 favores)
  - [ ] Badge "first_step"
  - [ ] Item "pista_1" (ClueService)

---

## F5.3: NIVEL 2 - OBSERVACIÓN (Los Kinkys)

**Status:** 🔴 0/15 fragmentos

### Capítulo: L2_OBSERVATION

- [ ] **F5.3.1:** Crear capítulo L2_OBSERVATION
  - [ ] level=2, chapter_type=FREE
  - [ ] requires_level=1
  - [ ] favor_reward=8

- [ ] **F5.3.2:** Fragmentos narrativos (12-15 fragmentos)
  - [ ] L2_01: Diana reconoce el regreso
  - [ ] L2_02: Lucien presenta el desafío
  - [ ] L2_03: Inicio de misión (INTERACTIVE)
  - [ ] L2_03B: Hints adicionales (branch)
  - [ ] L2_04: Misión activa (SYSTEM)
  - [ ] L2_05: Reportar hallazgo (INPUT)
  - [ ] L2_06: Pista aceptada (con contador 1/3, 2/3, 3/3)
  - [ ] L2_06B: Pista rechazada (branch)
  - [ ] L2_07: Misión completada (Diana)
  - [ ] L2_08: Entrega de recompensas

- [ ] **F5.3.3:** Misión de observación (3 días)
  - [ ] Crear NarrativeMission model (nueva tabla)
  - [ ] Tipo: OBSERVATION
  - [ ] duration_hours: 72
  - [ ] hints_required: 3
  - [ ] Guardar en UserNarrativeProgress.active_mission_id

- [ ] **F5.3.4:** Validación de hallazgos
  - [ ] Opción A: Lista de palabras clave (simple)
  - [ ] Opción B: Validación por IA (avanzado)
  - [ ] Opción C: Aceptar cualquier respuesta >20 chars (MVP)

- [ ] **F5.3.5:** Recompensas
  - [ ] +8 favores
  - [ ] Badge "keen_eye"
  - [ ] Item "memory_fragment_1"
  - [ ] Item "pista_2"
  - [ ] Unlock shop item "Llave del Fragmento I"

---

## F5.4: NIVEL 3 - PERFIL DE DESEO (Los Kinkys)

**Status:** 🔴 0/20 fragmentos

### Capítulo: L3_DESIRE_PROFILE

- [ ] **F5.4.1:** Crear capítulo L3_DESIRE_PROFILE
  - [ ] level=3, chapter_type=FREE
  - [ ] requires_level=2
  - [ ] favor_reward=10

- [ ] **F5.4.2:** Fragmentos narrativos (15-20 fragmentos)
  - [ ] L3_01: Diana solicita el perfil
  - [ ] L3_02: Lucien explica el proceso
  - [ ] L3_03: Pregunta 1 (4 opciones - setean flags)
  - [ ] L3_04: Pregunta 2 (4 opciones)
  - [ ] L3_05: Pregunta 3 (4 opciones)
  - [ ] L3_06: Pregunta 4 (4 opciones)
  - [ ] L3_07: Pregunta 5 (input texto libre)
  - [ ] L3_08: Análisis (delay 3 segundos)
  - [ ] L3_09_EXPLORER: Respuesta para Exploradores
  - [ ] L3_09_ROMANTIC: Respuesta para Románticos
  - [ ] L3_09_ANALYTICAL: Respuesta para Analíticos
  - [ ] L3_09_DIRECT: Respuesta para Directos
  - [ ] L3_09_PATIENT: Respuesta para Pacientes
  - [ ] L3_09_PERSISTENT: Respuesta para Persistentes
  - [ ] L3_10: La Invitación (Diana)
  - [ ] L3_11: Lucien presenta la Llave del Diván

- [ ] **F5.4.3:** Sistema de flags narrativos
  - [ ] Implementar sets_flag en FragmentDecision
  - [ ] Guardar flags en UserNarrativeProgress.narrative_flags
  - [ ] Flags: curious, attracted, seeking, intuitive, visual, verbal, mystery, personal, depth, surface, cautious, perceptive, pleasure, connection, understanding, open

- [ ] **F5.4.4:** Detección de arquetipo por respuestas
  - [ ] Analizar flags al terminar cuestionario
  - [ ] Determinar arquetipo si no está definido
  - [ ] Usar ArchetypeService.update_archetype()

- [ ] **F5.4.5:** Ramificación por arquetipo
  - [ ] Fragmento L3_09 tiene 6 variantes
  - [ ] Condición: archetype == EXPLORER/ROMANTIC/etc.
  - [ ] Usar FragmentVariant existente

- [ ] **F5.4.6:** Trigger de conversión VIP
  - [ ] Al completar capítulo L3
  - [ ] Enviar notificación a admins
  - [ ] Mostrar "Llave del Diván" en shop
  - [ ] Integración con ConversionService (si existe)

---

## F5.5: NIVELES 4-6 (VIP - El Diván)

**Status:** 🔴 0% (POST-MVP)

### Estructura resumida (implementar después)

- [ ] **F5.5.1:** NIVEL 4: Entrada al Diván
  - [ ] Capítulo L4_DIVAN_ENTRY
  - [ ] Evaluación de comprensión (quiz)
  - [ ] Respuesta según score (alto/medio)

- [ ] **F5.5.2:** NIVEL 5: Profundización
  - [ ] Capítulo L5_DEEPENING
  - [ ] Diálogos de vulnerabilidad
  - [ ] Evaluación de empatía

- [ ] **F5.5.3:** NIVEL 6: Culminación
  - [ ] Capítulo L6_CULMINATION
  - [ ] Secreto final de Diana
  - [ ] Acceso a Círculo Íntimo

---

## F5.6: MISIONES NARRATIVAS

**Status:** 🔴 0/4 tipos

- [ ] **F5.6.1:** Modelo NarrativeMission
  - [ ] Tabla nueva o usar campo JSON en UserNarrativeProgress
  - [ ] Campos: type, duration_hours, requirements, validation, rewards

- [ ] **F5.6.2:** Misión OBSERVATION (Nivel 2)
  - [ ] Ya cubierto en F5.3.3

- [ ] **F5.6.3:** Misión QUESTIONNAIRE (Nivel 3)
  - [ ] Ya cubierto en F5.4.2 (cuestionario)

- [ ] **F5.6.4:** Misión QUIZ (Nivel 4 - VIP)
  - [ ] POST-MVP

- [ ] **F5.6.5:** Misión DIALOGUE (Nivel 5 - VIP)
  - [ ] POST-MVP

---

## F5.7: SISTEMA DE FLAGS

**Status:** 🔴 0%

- [ ] **F5.7.1:** Implementar campo narrative_flags en UserNarrativeProgress
  - [ ] Tipo: JSON dict
  - [ ] Métodos en ProgressService:
    - [ ] `set_flag(user_id, flag_key, value)`
    - [ ] `get_flag(user_id, flag_key)`
    - [ ] `has_flag(user_id, flag_key)`
    - [ ] `get_all_flags(user_id)`

- [ ] **F5.7.2:** Integrar flags en DecisionService
  - [ ] Al procesar decisión, leer sets_flag
  - [ ] Guardar en narrative_flags
  - [ ] Validar requires_flag antes de mostrar decisión

- [ ] **F5.7.3:** Condiciones basadas en flags
  - [ ] FragmentRequirement con type=FLAG
  - [ ] RequirementsService.check_flag()

---

## F5.8: INTEGRACIÓN CON OTROS SISTEMAS

**Status:** 🟡 50% (ya existe integración básica)

### ✅ Ya integrado:
- [x] FavorService (via NarrativeOrchestrator)
- [x] ArchetypeService (via ProgressService)
- [x] ShopService (items como rewards)
- [x] VIP status (ChapterType.VIP)

### 🔴 Falta integrar:
- [ ] **F5.8.1:** ConversionService
  - [ ] trigger_vip_invitation(user_id) al completar L3
  - [ ] present_desire_map(user_id) al completar L6

- [ ] **F5.8.2:** NotificationService
  - [ ] Notificar admins al completar niveles clave
  - [ ] Alertas de conversión potencial

---

## F5.9: COMANDOS Y HANDLERS

**Status:** 🟡 50% (handler básico existe)

### ✅ Ya existe:
- [x] /historia (handler básico)
- [x] show_fragment() con variantes
- [x] process_decision() completo
- [x] Tracking de visitas y progreso

### 🔴 Falta implementar:
- [ ] **F5.9.1:** Extender /historia con info de misiones
  - [ ] Mostrar misión activa
  - [ ] Tiempo restante
  - [ ] Progreso (ej: "Pistas encontradas: 2/3")

- [ ] **F5.9.2:** Implementar delays entre fragmentos
  - [ ] Leer fragment.delay_seconds
  - [ ] asyncio.sleep() antes de enviar
  - [ ] Mensaje "Diana está escribiendo..." opcional

- [ ] **F5.9.3:** Handler de reportar hallazgo
  - [ ] Estado FSM para input texto libre
  - [ ] Validación según lógica de misión
  - [ ] Feedback inmediato

- [ ] **F5.9.4:** Handler de cuestionario
  - [ ] Ya funciona con decisiones normales
  - [ ] Agregar guardado de respuesta texto libre (L3_07)

---

## F5.10: SEED DATA - CONTENIDO INICIAL

**Status:** 🔴 0%

- [ ] **F5.10.1:** Script de carga completo
  - [ ] Extender scripts/seed_narrative.py
  - [ ] Cargar niveles 1-3 completos

- [ ] **F5.10.2:** Contenido Nivel 1 (10-12 fragmentos)
  - [ ] Textos finales con voz de Diana/Lucien
  - [ ] Decisiones configuradas
  - [ ] Flags seteados correctamente

- [ ] **F5.10.3:** Contenido Nivel 2 (12-15 fragmentos)
  - [ ] Textos finales
  - [ ] Misión configurada
  - [ ] Validaciones de hallazgos

- [ ] **F5.10.4:** Contenido Nivel 3 (15-20 fragmentos)
  - [ ] Cuestionario completo
  - [ ] 6 variantes por arquetipo
  - [ ] Flags y condiciones

- [ ] **F5.10.5:** Items narrativos
  - [ ] Pista 1, 2, 3
  - [ ] Fragmento de Memoria
  - [ ] Invitación al Diván
  - [ ] Llave del Diván (shop item)

---

## CRITERIOS DE ACEPTACIÓN FASE 5 (MVP)

### Modelos
- [ ] Todos los campos Fase 5 agregados a modelos existentes
- [ ] Migración Alembic ejecutada sin errores
- [ ] Sistema de flags funcionando

### Contenido
- [ ] Nivel 1 completo (10+ fragmentos)
- [ ] Nivel 2 completo (12+ fragmentos)
- [ ] Nivel 3 completo (15+ fragmentos)
- [ ] Variaciones por arquetipo en nivel 3
- [ ] Misión de observación funcionando

### Flujos
- [ ] Usuario puede iniciar narrativa desde /historia
- [ ] Fragmentos se muestran en secuencia
- [ ] Decisiones guardan flags correctamente
- [ ] Delays funcionan (opcional: desactivables)
- [ ] Misiones se activan, validan y completan

### Integraciones
- [ ] Favores se otorgan al completar capítulos
- [ ] Items se agregan al inventario (ClueService)
- [ ] Arquetipos se detectan en nivel 3
- [ ] Conversión VIP se activa al completar nivel 3

### UX
- [ ] /historia muestra progreso y misiones activas
- [ ] Usuario puede continuar donde dejó
- [ ] Mensajes personalizados por arquetipo
- [ ] Delays opcionales (config)

---

## TESTING

- [ ] **Tests unitarios servicios:**
  - [ ] ProgressService.set_flag()
  - [ ] ProgressService.get_flag()
  - [ ] Validación de flags en DecisionService

- [ ] **Tests integración:**
  - [ ] Flujo completo Nivel 1
  - [ ] Flujo completo Nivel 2 (con misión)
  - [ ] Flujo completo Nivel 3 (con cuestionario)
  - [ ] Detección de arquetipo

- [ ] **Tests E2E:**
  - [ ] Usuario completa niveles 1-3 sin errores
  - [ ] Conversión VIP se activa correctamente
  - [ ] Flags persisten entre sesiones

---

## PRIORIDADES

### 🔴 SPRINT 1 (MVP Funcional):
1. F5.1.1-F5.1.5: Extender modelos + migración
2. F5.7.1-F5.7.2: Sistema de flags
3. F5.9.2: Delays entre fragmentos
4. F5.2.1-F5.2.4: Nivel 1 completo
5. Tests básicos

### 🟡 SPRINT 2 (Contenido Principal):
6. F5.3.1-F5.3.5: Nivel 2 + misión observación
7. F5.4.1-F5.4.6: Nivel 3 + cuestionario + arquetipos
8. F5.8.1: Integración conversión VIP
9. F5.9.1, F5.9.3-F5.9.4: Handlers extendidos
10. Tests integración

### 🟢 SPRINT 3 (VIP Content - POST-MVP):
11. F5.5.1-F5.5.3: Niveles 4-6 VIP
12. F5.6.4-F5.6.5: Misiones avanzadas
13. Easter eggs narrativos
14. Tests E2E completos

---

## NOTAS TÉCNICAS

**Archivos principales a modificar:**
- `bot/narrative/database/models.py` - Extender modelos
- `bot/narrative/database/models_immersive.py` - Posible nueva tabla NarrativeMission
- `bot/narrative/services/progress.py` - Métodos de flags
- `bot/narrative/services/decision.py` - Procesar sets_flag
- `bot/narrative/handlers/user/story.py` - Delays, misiones, reportes
- `scripts/seed_narrative.py` - Cargar contenido completo
- `alembic/versions/` - Nueva migración

**Reutilizar directamente:**
- FragmentVariant (variantes por arquetipo)
- EngagementService (tracking visitas)
- CooldownService (delays entre decisiones)
- ChallengeService (validación de respuestas)
- NarrativeOrchestrator (recompensas gamificación)

**NO duplicar:**
- Sistema de modelos base (extender, no crear nuevos)
- ProgressService (agregar métodos, no reescribir)
- Handler de historia (extender show_fragment, no reemplazar)

---

**Última actualización:** 2025-12-30
**Status global:** 🟡 Sistema base 70% completo - Falta contenido y features Fase 5
