# MISIONES NARRATIVAS - SISTEMA COMPLETO
## Fase 5 - Sprint 3

---

## CONTEXTO

Las misiones narrativas son flujos interactivos especiales que requieren múltiples pasos,
validación de respuestas, y seguimiento de progreso. Están integradas en los niveles
narrativos pero tienen lógica específica.

---

## TIPOS DE MISIONES IMPLEMENTADAS

### 1. OBSERVATION (Nivel 2) ✅ COMPLETADO EN SPRINT 2

**Descripción:** Usuario debe encontrar 3 pistas ocultas en publicaciones del canal.

**Duración:** 72 horas (3 días)

**Mecánica:**
- Usuario reporta hallazgos (fragmentos L2_05)
- Sistema valida (actualmente: botones simulados, futuro: input texto)
- Contador: 1/3, 2/3, 3/3
- Al completar: recompensas + avance a L2_07

**Tracking:**
```json
{
  "mission_type": "OBSERVATION",
  "hints_found": 2,
  "hints_required": 3,
  "started_at": "2025-01-01T10:00:00Z"
}
```

**Implementación:**
- `UserNarrativeProgress.mission_data` (campo JSON)
- Fragmentos: L2_04 (inicio), L2_05 (reporte), L2_06 (validación)

---

### 2. QUESTIONNAIRE (Nivel 3) ✅ COMPLETADO EN SPRINT 2

**Descripción:** Perfil de Deseo - 5 preguntas para detectar arquetipo.

**Duración:** Sin límite

**Mecánica:**
- 5 preguntas secuenciales (L3_03 a L3_07)
- Cada respuesta setea flags (curious, attracted, seeking, visual, etc.)
- Pregunta 5: input texto libre (simulado con botones)
- Análisis: delay 3s (L3_08)
- Ramificación: 6 variantes según arquetipo (L3_09_*)

**Tracking:**
```json
{
  "mission_type": "QUESTIONNAIRE",
  "questions_answered": 5,
  "flags_set": ["curious", "mystery", "depth"],
  "archetype_detected": "EXPLORER"
}
```

**Implementación:**
- `UserNarrativeProgress.narrative_flags` (campo JSON)
- Fragmentos: L3_03-L3_07 (preguntas), L3_08 (análisis), L3_09_* (variantes)
- Servicio: `ArchetypeDetector.detect_from_narrative_flags()`

---

### 3. QUIZ (Nivel 4 - VIP) ✅ COMPLETADO EN SPRINT 3

**Descripción:** Evaluación de comprensión sobre Diana - 5 preguntas con scoring.

**Duración:** Sin límite (pausable)

**Mecánica:**
- 5 preguntas sobre Diana (L4_03 a L4_07)
- Cada respuesta tiene score implícito:
  * Shallow: 0 puntos
  * Good: 2 puntos
  * Deep: 3 puntos
- Score total: 0-15 puntos
- Análisis: delay 3s (L4_08)
- Ramificación:
  * >=7 puntos → L4_09A (score alto, "Realmente me ves")
  * 4-6 puntos → L4_09B (score medio, "Comprendes algunas capas")
  * <4 puntos → (implícito: bajo, actualmente no implementado)

**Tracking:**
```json
{
  "mission_type": "QUIZ",
  "quiz_answers": {
    "q1": "deep",
    "q2": "deep",
    "q3": "good",
    "q4": "deep",
    "q5": "deep"
  },
  "total_score": 13
}
```

**Flags seteados:**
- `quiz_q1_shallow`, `quiz_q1_good`, `quiz_q1_deep`
- `quiz_q2_shallow`, `quiz_q2_good`, `quiz_q2_deep`
- ...
- `high_comprehension` (si score >= 7)

**Implementación:**
- Fragmentos: L4_03-L4_07 (quiz), L4_08 (evaluación), L4_09A/B (variantes)
- Handler debe calcular score sumando flags

**Algoritmo de scoring:**
```python
def calculate_quiz_score(flags: dict) -> int:
    score = 0
    for q in range(1, 6):
        if flags.get(f"quiz_q{q}_deep"):
            score += 3
        elif flags.get(f"quiz_q{q}_good"):
            score += 2
        # shallow = 0 puntos
    return score
```

---

### 4. DIALOGUE (Nivel 5 - VIP) ✅ COMPLETADO EN SPRINT 3

**Descripción:** Diálogos de vulnerabilidad con evaluación de empatía.

**Duración:** Sin límite

**Mecánica:**
- 2 diálogos de vulnerabilidad (L5_02, L5_04)
- Cada diálogo tiene 3 opciones de respuesta:
  * Empática (2 puntos): Comprende sin juzgar
  * Posesiva (0 puntos): Reclama a Diana
  * Arregladora (0 puntos): Intenta "solucionar"
- Respuestas de Diana según tipo (9 fragmentos variantes)
- Evaluación final (L5_07)
- Ramificación:
  * >=2 empathetic flags → L5_08A ("Escuchó sin juzgar")
  * <2 empathetic flags → L5_08B ("Cayó en patrones comunes")

**Tracking:**
```json
{
  "mission_type": "DIALOGUE",
  "dialogues_completed": 2,
  "empathetic_responses": 2,
  "possessive_responses": 0,
  "fixing_responses": 0
}
```

**Flags seteados:**
- `empathetic_response_1`, `empathetic_response_2`
- `possessive_response_1`, `possessive_response_2`
- `fixing_response_1`, `fixing_response_2`
- `deep_empathy_achieved` (si >=2 empathetic)

**Implementación:**
- Fragmentos: L5_02, L5_04 (vulnerabilidades)
- Variantes: L5_03_*, L5_05_* (respuestas de Diana)
- Evaluación: L5_07, L5_08A/B

**Algoritmo de evaluación:**
```python
def evaluate_empathy(flags: dict) -> str:
    empathetic_count = sum(
        1 for key in flags
        if key.startswith("empathetic_response_") and flags[key]
    )

    if empathetic_count >= 2:
        return "high_empathy"
    else:
        return "low_empathy"
```

---

## HANDLERS NECESARIOS

### 1. Handler de Score Calculation (Nivel 4)

**Ubicación:** `bot/narrative/handlers/user/story.py`

**Función:**
```python
async def calculate_quiz_score(user_id: int, session: AsyncSession) -> int:
    """
    Calcula el score del quiz del nivel 4.

    Returns:
        int: Score total (0-15)
    """
    progress = await get_user_progress(user_id, session)
    flags = progress.narrative_flags or {}

    score = 0
    for q in range(1, 6):
        if flags.get(f"quiz_q{q}_deep"):
            score += 3
        elif flags.get(f"quiz_q{q}_good"):
            score += 2

    return score
```

**Integración:**
- Al llegar a L4_08 (evaluación), calcular score
- Dirigir a L4_09A (score >= 7) o L4_09B (score < 7)

---

### 2. Handler de Empathy Evaluation (Nivel 5)

**Ubicación:** `bot/narrative/handlers/user/story.py`

**Función:**
```python
async def evaluate_empathy_level(user_id: int, session: AsyncSession) -> str:
    """
    Evalúa nivel de empatía basado en respuestas.

    Returns:
        str: "high_empathy" o "low_empathy"
    """
    progress = await get_user_progress(user_id, session)
    flags = progress.narrative_flags or {}

    empathetic_count = sum(
        1 for key in flags
        if key.startswith("empathetic_response_") and flags[key]
    )

    return "high_empathy" if empathetic_count >= 2 else "low_empathy"
```

**Integración:**
- Al llegar a L5_07 (evaluación de Lucien), evaluar empatía
- Dirigir a L5_08A (high) o L5_08B (low)

---

## METADATA EN FRAGMENTOS

Para que los handlers sepan que deben ejecutar lógica especial:

### Fragmento L4_08 (Evaluación Quiz):
```python
l4_08.metadata = {
    "trigger_evaluation": True,
    "evaluation_type": "quiz_score",
    "high_score_fragment": "l4_09a_high_score",
    "medium_score_fragment": "l4_09b_medium_score",
    "threshold_high": 7
}
```

### Fragmento L5_07 (Evaluación Empatía):
```python
l5_07.metadata = {
    "trigger_evaluation": True,
    "evaluation_type": "empathy_level",
    "high_empathy_fragment": "l5_08a_empathetic",
    "low_empathy_fragment": "l5_08b_problematic"
}
```

---

## TESTING DE MISIONES

### Test 1: QUIZ Score Calculation
```python
async def test_quiz_score_calculation():
    # Setup: Crear usuario con flags de quiz
    flags = {
        "quiz_q1_deep": True,    # 3 pts
        "quiz_q2_good": True,    # 2 pts
        "quiz_q3_deep": True,    # 3 pts
        "quiz_q4_good": True,    # 2 pts
        "quiz_q5_deep": True,    # 3 pts
    }

    score = calculate_quiz_score_from_flags(flags)
    assert score == 13  # Alto (>= 7)

    # Usuario debe ir a L4_09A
```

### Test 2: Empathy Evaluation
```python
async def test_empathy_evaluation():
    # Setup: 2 respuestas empáticas
    flags = {
        "empathetic_response_1": True,
        "empathetic_response_2": True,
        "fixing_response_1": False,
        "possessive_response_2": False,
    }

    result = evaluate_empathy_from_flags(flags)
    assert result == "high_empathy"

    # Usuario debe ir a L5_08A
```

### Test 3: OBSERVATION Progress Tracking
```python
async def test_observation_mission_progress():
    # Setup: Misión activa
    mission_data = {
        "mission_type": "OBSERVATION",
        "hints_found": 2,
        "hints_required": 3
    }

    # Reportar tercer hallazgo
    mission_data["hints_found"] += 1

    assert mission_data["hints_found"] == 3
    # Debe completar misión y avanzar a L2_07
```

---

## CRITERIOS DE ACEPTACIÓN

### Misiones QUIZ y DIALOGUE:
- [x] Fragmentos cargados en BD (seeds completos)
- [ ] Handler de score calculation implementado
- [ ] Handler de empathy evaluation implementado
- [ ] Metadata en fragmentos de evaluación
- [ ] Tests unitarios de algoritmos
- [ ] Tests E2E de flujos completos

### Sistema general:
- [x] 4 tipos de misiones diseñadas
- [x] Tracking en UserNarrativeProgress.mission_data
- [ ] Handlers de evaluación funcionando
- [ ] Tests E2E pasando

---

## PRÓXIMOS PASOS (SPRINT 3)

1. ✅ Crear seeds de niveles 4-6
2. 🔄 Implementar handlers de evaluación (ACTUAL)
3. ⏳ Agregar metadata a fragmentos
4. ⏳ Tests E2E de misiones
5. ⏳ Easter eggs narrativos

---

**Última actualización:** 2025-12-30
**Status:** 🟡 Diseño completo, implementación parcial
