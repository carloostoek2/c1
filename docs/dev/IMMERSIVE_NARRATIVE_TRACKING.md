# TRACKING: Sistema Narrativo Inmersivo

**Fecha inicio:** 2025-12-28
**Estado:** EN PROGRESO

---

## RESUMEN DEL SISTEMA

Sistema de narrativa inmersiva con:
- Pistas como items narrativos en la mochila unificada
- Variantes de fragmentos por contexto (primera visita, retorno, con pista, etc.)
- Sistema de cooldowns narrativos
- Diario de viaje para navegación
- Desafíos interactivos (acertijos, input del usuario)
- Mecánicas de slowdown (límites diarios, tiempos de espera)

---

## FASE 1: MODELOS Y MIGRACIONES

### Archivos modificados:
- [x] `bot/shop/database/enums.py` - Extender NarrativeItemMetadata con campos de pista
  - Añadido: is_clue, clue_category, clue_hint, source_fragment_key, required_for_fragments, clue_icon
  - Añadido: clase ObtainedVia con constantes (PURCHASE, GIFT, REWARD, ADMIN_GRANT, DISCOVERY)

- [x] `bot/narrative/database/enums.py` - Nuevos enums
  - Añadido en RequirementType: HAS_CLUE, VISITED, VISIT_COUNT, TIME_SPENT, COOLDOWN_PASSED, TIME_WINDOW, CHAPTER_COMPLETE
  - Nuevo enum: VariantConditionType
  - Nuevo enum: ChallengeType
  - Nuevo enum: CooldownType

### Archivos creados:
- [x] `bot/narrative/database/models_immersive.py` - Nuevos modelos:
  - FragmentVariant: Variantes de contenido por contexto
  - UserFragmentVisit: Tracking de visitas y tiempo
  - NarrativeCooldown: Cooldowns activos del usuario
  - FragmentChallenge: Desafíos/acertijos
  - FragmentTimeWindow: Ventanas de disponibilidad temporal
  - UserChallengeAttempt: Intentos de desafíos
  - ChapterCompletion: Capítulos completados por usuario
  - DailyNarrativeLimit: Límites diarios por usuario

- [x] `alembic/versions/013_add_immersive_narrative_system.py` - Migración (8 tablas)

---

## FASE 2: SERVICIOS CORE ✅ COMPLETADA

### Archivos creados:
- [x] `bot/narrative/services/engagement.py` - EngagementService (370 líneas)
  - record_visit(), get_visit_count(), has_visited()
  - start_reading(), stop_reading(), get_time_spent()
  - complete_chapter(), has_completed_chapter()
  - get_or_create_daily_limit(), check_daily_limit()
  - get_user_stats()

- [x] `bot/narrative/services/clue.py` - ClueService (290 líneas)
  - grant_clue(), grant_clue_from_fragment()
  - has_clue(), has_all_clues()
  - get_clue_by_slug(), get_all_clues()
  - get_user_clues(), get_clues_for_fragment()
  - get_clue_progress()

- [x] `bot/narrative/services/variant.py` - VariantService (350 líneas)
  - resolve_variant(), apply_variant()
  - _evaluate_condition() con 8 tipos de condiciones
  - get_variants_for_fragment(), create_variant()
  - update_variant(), delete_variant(), toggle_variant()
  - build_user_context()

- [x] `bot/narrative/services/cooldown.py` - CooldownService (270 líneas)
  - set_cooldown(), check_cooldown(), get_cooldown()
  - clear_cooldown(), clear_all_cooldowns(), clear_expired_cooldowns()
  - set_fragment_cooldown(), set_chapter_cooldown()
  - set_decision_cooldown(), set_challenge_cooldown()
  - can_take_decision(), can_access_fragment()

- [x] `bot/narrative/services/challenge.py` - ChallengeService (380 líneas)
  - get_challenge_for_fragment(), get_challenge_by_id()
  - validate_answer(), record_attempt()
  - has_completed_challenge(), can_attempt()
  - get_hint(), get_available_hints(), get_next_hint()
  - process_challenge_attempt()
  - create_challenge(), update_challenge(), delete_challenge()
  - get_challenge_stats()

- [x] `bot/narrative/services/container.py` - Actualizado
  - 5 nuevos properties: engagement, clue, variant, cooldown, challenge
  - get_loaded_services() actualizado
  - clear_cache() actualizado

---

## FASE 3: MOCHILA UNIFICADA ✅ COMPLETADA

### Archivos modificados:
- [x] `bot/shop/database/enums.py` - ObtainedVia class añadida (PURCHASE, GIFT, REWARD, ADMIN_GRANT, DISCOVERY)

- [x] `bot/shop/handlers/user/backpack.py` - Extendido (~250 líneas nuevas)
  - Nuevo filtro: "🔍 Pistas" con contador
  - Nuevo filtro: "🎁 Recompensas" con contador
  - Vista especial para pistas con metadata completa
  - Helper _is_clue_item() y _get_clue_metadata()
  - Handler callback_filter_clues() con paginación
  - Handler callback_clue_detail() con:
    - Categoría, descripción, lore
    - Fragmento origen con botón "Ver fragmento origen"
    - Lista de fragmentos que desbloquea
    - Pista/hint asociada
  - Handler callback_filter_rewards() con paginación
  - Keyboard principal actualizado con conteo de especiales

---

## FASE 4: SISTEMA DE VARIANTES

### Archivos por modificar:
- [ ] `bot/narrative/services/fragment.py`
  - Integrar VariantService en get_fragment()
  - Resolver variante activa antes de retornar contenido

- [ ] `bot/narrative/handlers/user/story.py`
  - Mostrar contenido de variante activa
  - Registrar visita en EngagementService

---

## FASE 5: DIARIO DE VIAJE

### Archivos por crear:
- [ ] `bot/narrative/handlers/user/journal.py`
  - cmd_journal: Comando /diario o /journal
  - show_chapter_progress: Vista de progreso por capítulo
  - show_fragment_list: Lista de fragmentos visitados/bloqueados
  - show_clues_summary: Resumen de pistas
  - quick_navigate: Navegación rápida a fragmentos

- [ ] `bot/narrative/services/journal.py` - JournalService
  - get_chapter_progress()
  - get_fragment_status() - visited/locked/available
  - get_accessible_fragments()
  - get_blocked_fragments_with_reasons()

---

## FASE 6: COOLDOWNS Y SLOWDOWN

### Archivos por crear/modificar:
- [ ] `bot/narrative/handlers/user/story.py`
  - Verificar cooldowns antes de mostrar fragmento
  - Mostrar tiempo restante si hay cooldown activo
  - Aplicar cooldown después de fragmentos intensos

- [ ] `bot/narrative/config.py` (nuevo)
  - DAILY_FRAGMENT_LIMIT: int = 10
  - DECISION_COOLDOWN_SECONDS: int = 30
  - INTENSE_FRAGMENT_COOLDOWN: int = 300

---

## FASE 7: DESAFIOS INTERACTIVOS

### Archivos por crear:
- [ ] `bot/narrative/handlers/user/challenge.py`
  - show_challenge: Mostrar desafío
  - handle_text_input: Procesar respuesta de texto
  - handle_timeout: Manejar timeout
  - show_result: Mostrar resultado (éxito/fallo)

- [ ] `bot/narrative/states/challenge.py`
  - ChallengeStates: FSM para flujo de desafíos

---

## NOTAS TÉCNICAS

### Integración con sistema existente:
- Las pistas son ShopItems con item_type=NARRATIVE y metadata.is_clue=True
- Se obtienen via obtained_via="discovery" cuando se encuentran en narrativa
- RequirementType.ITEM ya soporta validar posesión de items (incluidas pistas)
- El sistema de variantes es un layer sobre FragmentService, no reemplaza

### Dependencias:
- InventoryService para gestionar pistas
- RequirementsService para validar acceso
- ProgressService para tracking de posición
- DecisionService para historial de decisiones

---

## COMMITS REALIZADOS

(Se actualizará con cada commit)

---

## SIGUIENTE PASO

Crear `bot/narrative/database/models_immersive.py` con los nuevos modelos.
