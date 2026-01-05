# PLAN ACTUALIZADO: EXPANSIÓN GAMIFICACIÓN Y NARRATIVA

> **Fecha:** Enero 2026
> **Estado:** Planificación
> **Versión:** 2.0 (Adaptado a arquitectura actual)

---

## ÍNDICE

1. [Contexto y Motivación](#1-contexto-y-motivación)
2. [Estado Actual de la Arquitectura](#2-estado-actual-de-la-arquitectura)
3. [Mapeo: Plan Original → Arquitectura Actual](#3-mapeo-plan-original--arquitectura-actual)
4. [Plan Adaptado: 4 Ondas de Desarrollo](#4-plan-adaptado-4-ondas-de-desarrollo)
5. [ONDA A: Servicios Inmersivos](#5-onda-a-servicios-inmersivos)
6. [ONDA B: Voz de Lucien + Arquetipos Avanzados](#6-onda-b-voz-de-lucien--arquetipos-avanzados)
7. [ONDA C: El Gabinete + Conversión](#7-onda-c-el-gabinete--conversión)
8. [ONDA D: Retención y Ciclo de Vida](#8-onda-d-retención-y-ciclo-de-vida)
9. [Dependencias y Orden de Ejecución](#9-dependencias-y-orden-de-ejecución)
10. [Filosofía y Principios](#10-filosofía-y-principios)

---

## 1. CONTEXTO Y MOTIVACIÓN

### 1.1 Plan Original (7 Fases)

El plan original definía 7 fases de expansión:

| Fase | Nombre | Objetivo |
|------|--------|----------|
| 1 | La Voz de Lucien | Transformar mensajes genéricos → personalidad del mayordomo |
| 2 | Economía de Besitos | Sistema de puntos, niveles, streaks |
| 3 | Arquetipos Expandidos | Detección de personalidad y personalización |
| 4 | El Gabinete | Tienda premium con ítems narrativos |
| 5 | Narrativa y Contenido | Historia de 6 niveles con evaluación del usuario |
| 6 | Conversión y Upsell | Monetización contextual (Free→VIP→Premium) |
| 7 | Retención y Anti-Churn | Gestión del ciclo de vida del usuario |

### 1.2 Razón de la Actualización

Desde que se aprobó el plan original, se ha desarrollado significativamente la arquitectura del bot:

- **Módulo de Gamificación:** ~19,000 líneas implementadas
- **Módulo de Narrativa:** ~5,143 líneas implementadas
- **Sistema de Shop:** Integrado con gamificación
- **Broadcasting Gamificado:** Custom reactions implementadas

Gran parte de las fases 2, 3, 4 y 5 ya tienen **infraestructura implementada** (modelos, servicios base, handlers). Este plan adapta las fases restantes a lo que existe.

---

## 2. ESTADO ACTUAL DE LA ARQUITECTURA

### 2.1 Módulo de Gamificación

```
bot/gamification/
├── database/
│   ├── models.py          # 13 modelos (UserGamification, Reaction, Level, Mission, etc.)
│   └── enums.py           # MissionType, RewardType, TransactionType, etc.
├── services/
│   ├── container.py       # GamificationContainer (DI + lazy loading)
│   ├── besito.py          # BesitoService ✅
│   ├── reaction.py        # ReactionService ✅
│   ├── custom_reaction.py # CustomReactionService ✅
│   ├── level.py           # LevelService ✅
│   ├── mission.py         # MissionService ✅
│   ├── reward.py          # RewardService ✅
│   ├── user_gamification.py # UserGamificationService ✅
│   ├── stats.py           # StatsService ✅
│   ├── daily_gift.py      # DailyGiftService ✅
│   ├── notifications.py   # NotificationService ✅
│   ├── unified.py         # UnifiedRewardService ✅
│   └── narrative_condition.py # NarrativeConditionService ✅
├── handlers/
│   ├── admin/             # 12 handlers admin (wizards, config, etc.)
│   └── user/              # 15 handlers user (profile, missions, etc.)
└── background/
    ├── auto_progression_checker.py
    ├── streak_expiration_checker.py
    └── reaction_hook.py
```

**Funcionalidades completas:**
- Sistema de besitos (moneda virtual)
- Niveles y progresión
- Misiones (ONE_TIME, DAILY, WEEKLY, STREAK)
- Recompensas (badges, ítems, permisos, títulos)
- Streaks con milestones
- Daily gifts
- Custom reactions en broadcasting
- Notificaciones automáticas
- Background tasks

### 2.2 Módulo de Narrativa

```
bot/narrative/
├── database/
│   ├── models.py           # Chapters, Fragments, Decisions, Progress
│   ├── models_immersive.py # Variants, Visits, Cooldowns, Challenges
│   └── enums.py            # ChapterType, RequirementType, ArchetypeType
├── services/
│   ├── container.py        # NarrativeContainer (DI + lazy loading)
│   ├── chapter.py          # ChapterService ✅
│   ├── fragment.py         # FragmentService ✅
│   ├── progress.py         # ProgressService ✅
│   ├── decision.py         # DecisionService ✅
│   ├── archetype.py        # ArchetypeService ✅ (básico)
│   ├── requirements.py     # RequirementsService ✅
│   ├── validation.py       # NarrativeValidationService ✅
│   ├── clue.py             # ClueService ✅
│   ├── journal.py          # JournalService ✅
│   ├── import_service.py   # JsonImportService ✅
│   ├── orchestrator.py     # NarrativeOrchestrator ✅
│   │
│   │ # SERVICIOS PENDIENTES (en container pero sin implementar)
│   ├── engagement.py       # EngagementService ❌
│   ├── variant.py          # VariantService ❌
│   ├── cooldown.py         # CooldownService ❌
│   └── challenge.py        # ChallengeService ❌
├── config_data/
│   ├── archetypes.py       # Reglas de detección (6 tipos expandidos)
│   └── story_content.py    # Estructura de contenido
└── handlers/
    └── user/
        ├── story.py        # Handler de lectura
        ├── challenge.py    # Handler de retos
        └── journal.py      # Handler de navegación
```

**Funcionalidades completas:**
- Capítulos FREE/VIP
- Fragmentos con decisiones
- Sistema de requerimientos (14 tipos)
- Arquetipos (9 tipos definidos)
- Pistas (clues) integradas con shop
- Diario de viaje (journal)
- Importación JSON
- Validación de integridad

**Pendiente:**
- Servicios inmersivos (engagement, variant, cooldown, challenge)

---

## 3. MAPEO: PLAN ORIGINAL → ARQUITECTURA ACTUAL

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PLAN ORIGINAL (7 FASES)                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  FASE 1: LA VOZ DE LUCIEN                    → 🔴 NO IMPLEMENTADO       │
│  ├── Templates de mensajes centralizados                                │
│  ├── Diferenciación por rol (new/VIP/admin)                             │
│  └── Errores y confirmaciones con personalidad                          │
│                                                                         │
│  FASE 2: ECONOMÍA DE BESITOS                 → 🟢 IMPLEMENTADO (95%)    │
│  ├── BesitoService                           ✅                          │
│  ├── LevelService (7 niveles)                ✅                          │
│  ├── UserStreak                              ✅                          │
│  ├── Notificaciones                          ✅                          │
│  ├── TransactionHistory                      ✅                          │
│  └── Admin Panel (GamificationConfig)        ✅                          │
│                                                                         │
│  FASE 3: ARQUETIPOS EXPANDIDOS               → 🟡 PARCIAL (40%)         │
│  ├── 9 arquetipos definidos                  ✅                          │
│  ├── ArchetypeService básico                 ✅                          │
│  ├── Detección por tiempo de respuesta       ✅                          │
│  ├── Detección avanzada (20+ métricas)       ❌                          │
│  ├── Personalización de contenido            ❌                          │
│  └── Triggers de conversión por arquetipo    ❌                          │
│                                                                         │
│  FASE 4: EL GABINETE                         → 🟡 PARCIAL (50%)         │
│  ├── ShopService básico                      ✅                          │
│  ├── Inventario de usuario                   ✅                          │
│  ├── Ítems narrativos (efímeros/llaves)      ❌ (falta contenido)        │
│  ├── Descuentos por nivel/streaks            ❌                          │
│  ├── Stock limitado/eventos temporales       ❌                          │
│  └── Recomendaciones por arquetipo           ❌                          │
│                                                                         │
│  FASE 5: NARRATIVA Y CONTENIDO               → 🟡 PARCIAL (60%)         │
│  ├── Modelo de capítulos/fragmentos          ✅                          │
│  ├── Sistema de decisiones                   ✅                          │
│  ├── Requerimientos (14 tipos)               ✅                          │
│  ├── Variantes (modelos listos)              ✅ modelos, ❌ servicio      │
│  ├── Cooldowns (modelos listos)              ✅ modelos, ❌ servicio      │
│  ├── Challenges (modelos listos)             ✅ modelos, ❌ servicio      │
│  ├── Contenido de los 6 niveles              ❌                          │
│  └── Integración con conversión              ❌                          │
│                                                                         │
│  FASE 6: CONVERSIÓN Y UPSELL                 → 🟡 PARCIAL (30%)         │
│  ├── Deep links                              ✅                          │
│  ├── Tokens VIP                              ✅                          │
│  ├── Sistema de planes/tarifas               ✅                          │
│  ├── Flujos de conversión contextuales       ❌                          │
│  ├── Triggers por arquetipo                  ❌                          │
│  └── Sistema de descuentos inteligentes      ❌                          │
│                                                                         │
│  FASE 7: RETENCIÓN Y ANTI-CHURN              → 🔴 NO IMPLEMENTADO       │
│  ├── Estados de usuario (lifecycle)          ❌                          │
│  ├── Risk score calculation                  ❌                          │
│  ├── Re-engagement automático                ❌                          │
│  ├── Mensajes dignos (AT_RISK/DORMANT)       ❌                          │
│  └── Preferencias de notificación            ❌                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 4. PLAN ADAPTADO: 4 ONDAS DE DESARROLLO

Reorganizamos las 7 fases en **4 ondas** que aprovechan la arquitectura existente:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PLAN ADAPTADO: 4 ONDAS                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ONDA A: SERVICIOS INMERSIVOS                                           │
│  ─────────────────────────────────────────────────────────────────      │
│  Completa los servicios que tienen modelos pero no implementación.      │
│  Desbloquea toda la capacidad narrativa inmersiva.                      │
│                                                                         │
│  ONDA B: VOZ DE LUCIEN + ARQUETIPOS AVANZADOS                           │
│  ─────────────────────────────────────────────────────────────────      │
│  Personaliza toda la experiencia con la voz del mayordomo.              │
│  Expande la detección de arquetipos con métricas avanzadas.             │
│                                                                         │
│  ONDA C: EL GABINETE + CONVERSIÓN                                       │
│  ─────────────────────────────────────────────────────────────────      │
│  Sistema completo de tienda narrativa con monetización orgánica.        │
│  Flujos de conversión contextuales y dignos.                            │
│                                                                         │
│  ONDA D: RETENCIÓN Y CICLO DE VIDA                                      │
│  ─────────────────────────────────────────────────────────────────      │
│  Gestión completa del lifecycle del usuario.                            │
│  Re-engagement automatizado pero respetuoso.                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 5. ONDA A: SERVICIOS INMERSIVOS

> **Objetivo:** Completar los 4 servicios que tienen modelos de BD pero no implementación.
> **Impacto:** Desbloquea toda la narrativa inmersiva (variantes, cooldowns, retos, engagement).
> **Dependencias:** Ninguna (puede comenzar inmediatamente).

### 5.1 Tareas

#### A1: EngagementService
**Archivo:** `bot/narrative/services/engagement.py`
**Modelos que usa:** `UserFragmentVisit`, `DailyNarrativeLimit`

```python
class EngagementService:
    """Tracking de engagement y visitas de usuario."""

    # Métodos requeridos:
    async def record_visit(user_id, fragment_key) -> UserFragmentVisit
    async def get_visit_count(user_id, fragment_key) -> int
    async def get_total_time_spent(user_id, fragment_key) -> int
    async def get_user_engagement_stats(user_id) -> dict
    async def check_daily_limit(user_id, limit_type) -> Tuple[bool, int]
    async def increment_daily_counter(user_id, limit_type) -> None
    async def reset_daily_limits() -> int  # Background task
```

**Funcionalidades:**
- Registrar cada visita a un fragmento
- Calcular tiempo de lectura (entre visita y siguiente acción)
- Tracking de límites diarios (fragmentos, decisiones, challenges)
- Estadísticas de engagement por usuario
- Reset automático de límites a medianoche

---

#### A2: VariantService
**Archivo:** `bot/narrative/services/variant.py`
**Modelos que usa:** `FragmentVariant`

```python
class VariantService:
    """Selección de variantes de contenido basada en contexto."""

    # Métodos requeridos:
    async def get_applicable_variant(fragment_key, user_context) -> Optional[FragmentVariant]
    async def evaluate_condition(variant, user_context) -> bool
    async def create_variant(fragment_key, variant_key, condition_type, ...) -> FragmentVariant
    async def get_variants_for_fragment(fragment_key) -> List[FragmentVariant]
    async def build_user_context(user_id) -> dict  # Helper
```

**Tipos de condición soportados:**
- `archetype`: Mostrar variante si usuario tiene arquetipo X
- `has_clue`: Mostrar si usuario posee pista específica
- `decision_made`: Mostrar si usuario tomó decisión Y
- `visit_count`: Mostrar si visitó fragmento Z veces
- `time_of_day`: Mostrar según hora (mañana/tarde/noche)
- `vip_status`: Mostrar solo a VIPs
- `level_reached`: Mostrar si alcanzó nivel N

**Prioridad de variantes:**
- Variantes con condiciones más específicas tienen prioridad
- Si múltiples aplican, usar `priority` field
- Fallback al contenido original del fragmento

---

#### A3: CooldownService
**Archivo:** `bot/narrative/services/cooldown.py`
**Modelos que usa:** `NarrativeCooldown`, `FragmentTimeWindow`

```python
class CooldownService:
    """Gestión de cooldowns y ventanas de tiempo."""

    # Métodos requeridos:
    async def check_cooldown(user_id, cooldown_type, target_key) -> Tuple[bool, Optional[datetime], Optional[str]]
    async def set_cooldown(user_id, cooldown_type, target_key, duration_seconds, message) -> NarrativeCooldown
    async def clear_cooldown(user_id, cooldown_type, target_key) -> bool
    async def check_time_window(fragment_key) -> Tuple[bool, Optional[str]]
    async def get_active_cooldowns(user_id) -> List[NarrativeCooldown]
    async def cleanup_expired_cooldowns() -> int  # Background task
```

**Tipos de cooldown:**
- `FRAGMENT`: No puede ver fragmento X por N segundos
- `CHAPTER`: No puede avanzar en capítulo por N segundos
- `DECISION`: No puede tomar decisiones por N segundos
- `CHALLENGE`: No puede reintentar challenge por N segundos

**Ventanas de tiempo:**
- `available_hours`: Lista de horas disponibles (ej: [22, 23, 0, 1])
- `available_days`: Días de la semana (ej: ["friday", "saturday"])
- `special_dates`: Fechas específicas (ej: ["2026-02-14"])
- `unavailable_message`: Mensaje narrativo cuando no está disponible

---

#### A4: ChallengeService
**Archivo:** `bot/narrative/services/challenge.py`
**Modelos que usa:** `FragmentChallenge`, `UserChallengeAttempt`

```python
class ChallengeService:
    """Gestión de desafíos interactivos."""

    # Métodos requeridos:
    async def get_challenge(fragment_key) -> Optional[FragmentChallenge]
    async def validate_answer(challenge_id, user_answer) -> Tuple[bool, str]
    async def record_attempt(user_id, challenge_id, answer, is_correct, hints_used) -> UserChallengeAttempt
    async def get_remaining_attempts(user_id, challenge_id) -> int
    async def get_available_hints(user_id, challenge_id) -> List[str]
    async def use_hint(user_id, challenge_id) -> Tuple[bool, Optional[str]]
    async def create_challenge(fragment_key, challenge_type, question, ...) -> FragmentChallenge
```

**Tipos de challenge:**
- `TEXT_INPUT`: Usuario escribe respuesta libre
- `CHOICE_SEQUENCE`: Seleccionar opciones en orden correcto
- `TIMED_RESPONSE`: Responder antes de timeout
- `MEMORY_RECALL`: Recordar información de fragmentos anteriores
- `OBSERVATION`: Encontrar detalles en contenido

**Sistema de hints:**
- Cada challenge puede tener 0-3 hints
- Usar hint reduce recompensa en besitos
- Hints se revelan uno a uno

---

### 5.2 Handlers a Actualizar

Una vez implementados los servicios, actualizar:

```
bot/narrative/handlers/user/
├── story.py      # Integrar variants y cooldowns en display_fragment()
├── challenge.py  # Completar flujo con ChallengeService
└── journal.py    # Mostrar cooldowns activos y tiempo restante
```

### 5.3 Background Tasks

Agregar a `bot/narrative/background/`:

```python
# tasks.py
async def reset_daily_narrative_limits():
    """Ejecutar a medianoche: reset límites diarios."""

async def cleanup_expired_cooldowns():
    """Ejecutar cada hora: limpiar cooldowns expirados."""
```

### 5.4 Tests

```
tests/narrative/
├── test_engagement_service.py
├── test_variant_service.py
├── test_cooldown_service.py
├── test_challenge_service.py
└── test_immersive_integration.py
```

### 5.5 Entregables ONDA A

| Entregable | Archivo | Líneas Est. |
|------------|---------|-------------|
| EngagementService | `services/engagement.py` | ~250 |
| VariantService | `services/variant.py` | ~300 |
| CooldownService | `services/cooldown.py` | ~280 |
| ChallengeService | `services/challenge.py` | ~350 |
| Background tasks | `background/tasks.py` | ~100 |
| Tests | `tests/narrative/test_*.py` | ~400 |
| **Total** | | **~1,680** |

---

## 6. ONDA B: VOZ DE LUCIEN + ARQUETIPOS AVANZADOS

> **Objetivo:** Personalizar toda la experiencia con la voz del mayordomo y expandir la detección de arquetipos.
> **Impacto:** Cada interacción se siente única y observada.
> **Dependencias:** ONDA A (EngagementService para métricas de arquetipo).

### 6.1 Tareas

#### B1: LucienVoiceService
**Archivo:** `bot/services/lucien_voice.py`
**Nuevo servicio en container principal**

```python
class LucienVoiceService:
    """Centraliza la voz y personalidad de Lucien."""

    # Templates por categoría
    TEMPLATES = {
        "welcome": {...},
        "error": {...},
        "confirmation": {...},
        "notification": {...},
        "conversion": {...},
        "retention": {...}
    }

    # Métodos requeridos:
    async def get_message(category, key, context) -> str
    async def format_error(error_type, details) -> str
    async def format_confirmation(action_type, details) -> str
    async def get_welcome_message(user_type, user_context) -> str
    async def get_notification(notification_type, data) -> str
```

**Categorías de mensajes:**

1. **Welcome (diferenciado por tipo de usuario):**
   - `new_user`: Primera vez
   - `returning_user`: Regresa después de inactividad
   - `active_user`: Usuario activo
   - `vip_user`: Usuario VIP
   - `admin`: Administrador

2. **Errors (con personalidad):**
   - `permission_denied`
   - `not_configured`
   - `invalid_input`
   - `cooldown_active`
   - `limit_reached`

3. **Confirmations:**
   - `action_success`
   - `purchase_complete`
   - `level_up`
   - `reward_granted`

4. **Contextual (por arquetipo):**
   - Mensajes alternativos para cada arquetipo
   - Tono adaptado a personalidad detectada

---

#### B2: AdvancedArchetypeService
**Archivo:** `bot/narrative/services/archetype_advanced.py`
**Extiende ArchetypeService existente**

```python
class AdvancedArchetypeService:
    """Detección avanzada de arquetipos con 20+ métricas."""

    # Métricas a trackear:
    METRICS = {
        "exploration": [...],   # Exploración de contenido
        "timing": [...],        # Patrones de tiempo
        "emotional": [...],     # Respuestas emocionales
        "persistence": [...],   # Persistencia y reintentos
        "social": [...],        # Interacción social
    }

    # Métodos requeridos:
    async def calculate_archetype_scores(user_id) -> Dict[ArchetypeType, float]
    async def get_dominant_archetype(user_id) -> Tuple[ArchetypeType, float]
    async def track_metric(user_id, metric_type, value) -> None
    async def get_archetype_profile(user_id) -> dict  # Perfil completo
    async def should_recalculate(user_id) -> bool
```

**Métricas de detección (20+):**

| Métrica | Arquetipo Indicado | Peso |
|---------|-------------------|------|
| % contenido explorado | EXPLORER | 0.15 |
| Easter eggs encontrados | EXPLORER | 0.10 |
| Tiempo promedio por fragmento | CONTEMPLATIVE/DIRECT | 0.12 |
| Velocidad de decisiones | IMPULSIVE/ANALYTICAL | 0.10 |
| Revisitas a contenido emocional | ROMANTIC | 0.08 |
| Uso de palabras emocionales | ROMANTIC | 0.08 |
| Reintentos de challenges | PERSISTENT | 0.10 |
| Abandono de misiones | PERSISTENT (inverso) | 0.07 |
| Duración de sesiones | PATIENT | 0.08 |
| Frecuencia de retorno | PATIENT | 0.07 |
| Patrones de horario | PATIENT | 0.05 |

---

#### B3: PersonalizationService
**Archivo:** `bot/services/personalization.py`

```python
class PersonalizationService:
    """Personalización de contenido basada en arquetipo."""

    async def get_personalized_content(user_id, content_key) -> str
    async def get_conversion_trigger(user_id) -> Optional[dict]
    async def get_recommended_items(user_id, limit) -> List[ShopItem]
    async def should_show_offer(user_id, offer_type) -> bool
```

---

#### B4: Actualización de Handlers

Modificar handlers existentes para usar LucienVoiceService:

```python
# Antes:
await message.answer("Error: canal no configurado")

# Después:
msg = await lucien_voice.format_error("not_configured", {"element": "canal VIP"})
await message.answer(msg)
```

**Handlers a actualizar:**
- `bot/handlers/user/start.py`
- `bot/handlers/admin/main.py`
- `bot/handlers/admin/vip.py`
- `bot/handlers/admin/free.py`
- `bot/gamification/handlers/user/profile.py`
- `bot/gamification/handlers/user/missions.py`
- `bot/narrative/handlers/user/story.py`

### 6.2 Templates de Lucien

**Ejemplo de estructura:**

```python
LUCIEN_TEMPLATES = {
    "welcome": {
        "new_user": {
            "default": "Bienvenido. Soy Lucien, el guardián de este espacio...",
            "EXPLORER": "Veo curiosidad en tu mirada. Bien. Este lugar tiene muchos secretos...",
            "DIRECT": "Seré breve. Esto es lo que necesitas saber...",
            "ROMANTIC": "Has llegado en un momento especial. Diana ha estado esperando...",
        },
        "returning_user": {
            "default": "Has vuelto. {days} días sin verte...",
            "short_absence": "Apenas te fuiste y ya regresaste. Interesante...",
            "long_absence": "Pensé que no volverías. Diana preguntó por ti...",
        }
    },
    "error": {
        "not_configured": "Aún no he preparado {element}. Paciencia.",
        "permission_denied": "Este lugar no es para ti. Aún.",
        "cooldown_active": "Diana necesita un momento. Vuelve en {time}.",
    },
    "notification": {
        "level_up": "He observado tu progreso. Ahora eres {level}. Diana estará complacida.",
        "streak_milestone": "{days} días consecutivos. Tu dedicación no pasa desapercibida.",
    }
}
```

### 6.3 Entregables ONDA B

| Entregable | Archivo | Líneas Est. |
|------------|---------|-------------|
| LucienVoiceService | `services/lucien_voice.py` | ~400 |
| Templates | `config/lucien_templates.py` | ~500 |
| AdvancedArchetypeService | `narrative/services/archetype_advanced.py` | ~350 |
| PersonalizationService | `services/personalization.py` | ~250 |
| Actualización handlers | varios | ~300 |
| Tests | `tests/test_lucien_*.py` | ~350 |
| **Total** | | **~2,150** |

---

## 7. ONDA C: EL GABINETE + CONVERSIÓN

> **Objetivo:** Sistema completo de tienda narrativa con monetización orgánica.
> **Impacto:** Monetización que se siente ganada, no forzada.
> **Dependencias:** ONDA B (arquetipos para personalización de ofertas).

### 7.1 Tareas

#### C1: Ítems Narrativos en Shop

Crear los ítems definidos en el plan original:

**Efímeros (consumibles):**
| Ítem | Costo | Efecto |
|------|-------|--------|
| Sello del Día | 1 Favor | Marca especial en perfil por 24h |
| Susurro Efímero | 3 Favores | Audio exclusivo de 15 segundos |
| Pase de Prioridad | 5 Favores | Acceso anticipado a contenido |
| Vistazo al Sensorium | 15 Favores | Preview de 30 segundos |
| Confesión Nocturna | 8 Favores | Texto exclusivo |

**Distintivos (permanentes):**
| Ítem | Costo | Requisito |
|------|-------|-----------|
| Sello del Visitante | 2 Favores | Nivel 1 |
| Marca del Curioso | 5 Favores | Nivel 2 |
| Emblema del Iniciado | 10 Favores | Nivel 3 |
| Sigilo del Confidente | 20 Favores | Nivel 4 |
| Insignia del Devoto | 35 Favores | Nivel 5 |
| Corona del Guardián | 50 Favores | Nivel 6+ |

**Llaves (desbloqueos narrativos):**
| Ítem | Costo | Desbloquea |
|------|-------|------------|
| Fragmento I | 10 Favores | Historia oculta parte 1 |
| Fragmento II | 12 Favores | Historia oculta parte 2 |
| Fragmento III | 15 Favores | Historia oculta parte 3 |
| Archivo Oculto | 20 Favores | Archivo personal |
| Llave de la Primera Vez | 18 Favores | Origen de Diana |

**Reliquias (raras):**
| Ítem | Costo | Efecto |
|------|-------|--------|
| El Primer Secreto | 30 Favores | Contenido ultra-exclusivo |
| Fragmento del Espejo | 40 Favores | Behind-the-scenes |
| La Carta No Enviada | 50 Favores | Carta íntima de Diana |
| Cristal de Medianoche | 45 Favores | Micro-contenido diario a medianoche |
| Llave Maestra | 75 Favores | Desbloquea todo el Gabinete |

---

#### C2: DiscountService
**Archivo:** `bot/services/discount.py`

```python
class DiscountService:
    """Sistema de descuentos inteligentes."""

    async def calculate_discount(user_id, item_id) -> Tuple[float, List[str]]
    async def get_applicable_discounts(user_id) -> List[Discount]
    async def apply_level_discount(user_level) -> float  # 0-15%
    async def apply_streak_discount(streak_days) -> float  # 0-10%
    async def apply_archetype_discount(archetype, item_category) -> float  # 0-5%
    async def apply_first_purchase_discount() -> float  # 10%
    async def apply_limited_time_discount(event_id) -> float  # Variable
```

**Tabla de descuentos por nivel:**
| Nivel | Descuento Base |
|-------|---------------|
| 1-2 | 0% |
| 3 | 5% |
| 4 | 8% |
| 5 | 10% |
| 6+ | 15% |

**Descuentos por streak:**
| Días | Descuento |
|------|-----------|
| 7+ | 3% |
| 14+ | 5% |
| 30+ | 7% |
| 60+ | 10% |

---

#### C3: ConversionService
**Archivo:** `bot/services/conversion.py`

```python
class ConversionService:
    """Gestión de flujos de conversión."""

    async def check_conversion_triggers(user_id) -> List[ConversionTrigger]
    async def get_offer_for_user(user_id, offer_type) -> Optional[ConversionOffer]
    async def record_conversion_event(user_id, event_type, details) -> None
    async def get_conversion_stats(user_id) -> dict
    async def should_show_offer(user_id, offer_type) -> bool  # Rate limiting
```

**Triggers de conversión:**

| Trigger | Condición | Oferta |
|---------|-----------|--------|
| `narrative_level_3_complete` | Completó nivel 3 FREE | Invitación a VIP |
| `high_engagement` | 5+ días activo, 20+ decisiones | Descuento VIP 15% |
| `archetype_romantic` | Arquetipo ROMANTIC detectado | Llaves narrativas |
| `archetype_explorer` | Arquetipo EXPLORER detectado | Reliquias |
| `streak_milestone` | Streak de 14+ días | Distintivo exclusivo |
| `vip_expiring` | VIP expira en 3 días | Renovación con descuento |

**Flujos de conversión:**

```
FREE → VIP:
├── Trigger: Completar Nivel 3 narrativo
├── Mensaje: Lucien presenta "La Llave del Diván"
├── Descuento: Basado en nivel + streaks + arquetipo
├── Post-compra: 15 Favores bonus + Nivel 4 unlock
└── Respeto: Si rechaza, no insistir por 7 días

VIP → Premium Individual:
├── Trigger: Nivel 4+ completo o nuevo contenido
├── Mensaje: Personalizado por arquetipo
├── Descuento: Loyalty discount por días VIP
└── Respeto: Máximo 1 oferta por semana

VIP → Mapa del Deseo (Packs):
├── Tier 1: VIP + 2 premium videos
├── Tier 2: Tier 1 + sesión personalizada
├── Tier 3: Todo + comunicación ilimitada
└── Trigger: Nivel 5+ o 30+ días VIP
```

---

#### C4: StockLimitedService
**Archivo:** `bot/shop/services/stock.py`

```python
class StockLimitedService:
    """Gestión de ítems con stock limitado."""

    async def create_limited_item(item_id, stock_quantity, end_date) -> LimitedStock
    async def check_availability(item_id) -> Tuple[bool, int]  # available, remaining
    async def reserve_item(user_id, item_id) -> bool
    async def complete_purchase(user_id, item_id) -> bool
    async def release_reservation(user_id, item_id) -> None
    async def get_limited_items() -> List[ShopItem]
```

### 7.2 Modelos Nuevos

```python
# bot/database/models.py

class ConversionEvent(Base):
    """Registro de eventos de conversión."""
    __tablename__ = "conversion_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    event_type: Mapped[str]  # offer_shown, offer_accepted, offer_declined
    offer_type: Mapped[str]  # free_to_vip, vip_to_premium, etc.
    offer_details: Mapped[dict] = mapped_column(JSON)
    discount_applied: Mapped[float] = mapped_column(default=0.0)
    created_at: Mapped[datetime]

class LimitedStock(Base):
    """Ítems con stock limitado."""
    __tablename__ = "limited_stock"

    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("shop_items.id"))
    initial_quantity: Mapped[int]
    remaining_quantity: Mapped[int]
    start_date: Mapped[datetime]
    end_date: Mapped[Optional[datetime]]
```

### 7.3 Entregables ONDA C

| Entregable | Archivo | Líneas Est. |
|------------|---------|-------------|
| Seed de ítems narrativos | `scripts/seed_narrative_items.py` | ~200 |
| DiscountService | `services/discount.py` | ~300 |
| ConversionService | `services/conversion.py` | ~400 |
| StockLimitedService | `shop/services/stock.py` | ~250 |
| Modelos nuevos | `database/models.py` | ~100 |
| Handlers conversión | `handlers/user/conversion.py` | ~300 |
| Tests | `tests/test_conversion_*.py` | ~400 |
| **Total** | | **~1,950** |

---

## 8. ONDA D: RETENCIÓN Y CICLO DE VIDA

> **Objetivo:** Gestión completa del lifecycle del usuario con re-engagement digno.
> **Impacto:** Retención sostenible sin spam ni manipulación.
> **Dependencias:** ONDA B (voz de Lucien para mensajes), ONDA C (ofertas de re-engagement).

### 8.1 Tareas

#### D1: UserLifecycleService
**Archivo:** `bot/services/user_lifecycle.py`

```python
class UserLifecycleService:
    """Gestión del ciclo de vida del usuario."""

    # Estados del lifecycle
    class LifecycleState(Enum):
        NEW = "new"           # 0-7 días desde registro
        ACTIVE = "active"     # Actividad en últimos 3 días
        AT_RISK = "at_risk"   # 4-7 días sin actividad
        DORMANT = "dormant"   # 8-30 días sin actividad
        LOST = "lost"         # 30+ días sin actividad

    async def get_user_state(user_id) -> LifecycleState
    async def update_user_activity(user_id) -> None
    async def get_users_by_state(state) -> List[User]
    async def calculate_days_inactive(user_id) -> int
    async def transition_state(user_id, new_state) -> None
```

---

#### D2: RiskScoreService
**Archivo:** `bot/services/risk_score.py`

```python
class RiskScoreService:
    """Cálculo de riesgo de abandono."""

    async def calculate_risk_score(user_id) -> int  # 0-100
    async def get_risk_factors(user_id) -> List[RiskFactor]
    async def get_high_risk_users(threshold=70) -> List[User]
```

**Factores de riesgo:**

| Factor | Peso | Cálculo |
|--------|------|---------|
| Días inactivo | 25% | days_inactive * 2.5 (max 25) |
| Streak roto | 15% | 15 si streak > 7 días roto |
| Misiones abandonadas | 15% | abandoned_missions * 5 (max 15) |
| Declive de actividad | 15% | % reducción vs. semana anterior |
| VIP por expirar | 15% | 15 si expira en < 5 días |
| Onboarding incompleto | 10% | 10 si no completó nivel 1 |
| Sin compras | 5% | 5 si nunca compró nada |

---

#### D3: ReengagementService
**Archivo:** `bot/services/reengagement.py`

```python
class ReengagementService:
    """Re-engagement automatizado y digno."""

    async def get_reengagement_message(user_id, state) -> Optional[str]
    async def should_send_message(user_id) -> bool  # Rate limiting
    async def record_message_sent(user_id, message_type) -> None
    async def get_return_bonus(user_id) -> int  # Besitos por volver
    async def process_user_return(user_id) -> dict  # Bonus + mensaje
```

**Mensajes por estado:**

| Estado | Día | Mensaje |
|--------|-----|---------|
| AT_RISK | 4-5 | "He notado tu ausencia. Diana preguntó por ti..." |
| DORMANT | 8-10 | "Han pasado {days} días. Hay cosas que quiero mostrarte..." |
| DORMANT | 15-17 | "Este será mi último mensaje. Si decides volver..." |
| LOST | 30+ | "Adiós. Si algún día vuelves, aquí estaré." (luego silencio) |

**Reglas de dignidad:**
- Máximo 2-3 mensajes por usuario en estado inactivo
- Nunca más de 1 mensaje por semana
- Si usuario responde "no molestar", respetar permanentemente
- Sin culpa ni manipulación emocional

---

#### D4: NotificationPreferencesService
**Archivo:** `bot/services/notification_preferences.py`

```python
class NotificationPreferencesService:
    """Gestión de preferencias de notificación del usuario."""

    async def get_preferences(user_id) -> NotificationPreferences
    async def update_preferences(user_id, preferences) -> None
    async def should_notify(user_id, notification_type) -> bool
    async def get_quiet_hours(user_id) -> Tuple[int, int]  # start, end hour
    async def is_in_quiet_hours(user_id) -> bool
```

**Preferencias configurables:**
- `content_notifications`: Nuevo contenido
- `streak_reminders`: Recordatorios de streak
- `offer_notifications`: Ofertas y descuentos
- `reengagement_messages`: Mensajes de re-engagement
- `quiet_hours_start`: Hora inicio silencio (default: 22)
- `quiet_hours_end`: Hora fin silencio (default: 8)
- `max_messages_per_day`: Máximo por día (default: 3)
- `timezone`: Zona horaria del usuario

---

#### D5: Background Tasks de Lifecycle

```python
# bot/background/lifecycle_tasks.py

async def update_user_lifecycle_states():
    """Ejecutar cada hora: actualizar estados de usuarios."""

async def send_reengagement_messages():
    """Ejecutar cada 6 horas: enviar mensajes de re-engagement."""

async def calculate_risk_scores():
    """Ejecutar diariamente: recalcular risk scores."""

async def archive_lost_users():
    """Ejecutar semanalmente: archivar usuarios perdidos."""
```

### 8.2 Modelos Nuevos

```python
# bot/database/models.py

class UserLifecycle(Base):
    """Estado del ciclo de vida del usuario."""
    __tablename__ = "user_lifecycle"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    current_state: Mapped[str]  # new, active, at_risk, dormant, lost
    last_activity: Mapped[datetime]
    risk_score: Mapped[int] = mapped_column(default=0)
    messages_sent_count: Mapped[int] = mapped_column(default=0)
    last_message_sent: Mapped[Optional[datetime]]
    do_not_disturb: Mapped[bool] = mapped_column(default=False)
    state_changed_at: Mapped[datetime]

class NotificationPreferences(Base):
    """Preferencias de notificación del usuario."""
    __tablename__ = "notification_preferences"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    content_notifications: Mapped[bool] = mapped_column(default=True)
    streak_reminders: Mapped[bool] = mapped_column(default=True)
    offer_notifications: Mapped[bool] = mapped_column(default=True)
    reengagement_messages: Mapped[bool] = mapped_column(default=True)
    quiet_hours_start: Mapped[int] = mapped_column(default=22)
    quiet_hours_end: Mapped[int] = mapped_column(default=8)
    max_messages_per_day: Mapped[int] = mapped_column(default=3)
    timezone: Mapped[str] = mapped_column(default="America/Mexico_City")

class ReengagementLog(Base):
    """Log de mensajes de re-engagement enviados."""
    __tablename__ = "reengagement_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    message_type: Mapped[str]  # at_risk_1, dormant_1, dormant_2, lost_farewell
    sent_at: Mapped[datetime]
    user_responded: Mapped[bool] = mapped_column(default=False)
    response_at: Mapped[Optional[datetime]]
```

### 8.3 Handler de Preferencias

```
bot/handlers/user/
└── preferences.py  # /preferences - Configurar notificaciones
```

### 8.4 Entregables ONDA D

| Entregable | Archivo | Líneas Est. |
|------------|---------|-------------|
| UserLifecycleService | `services/user_lifecycle.py` | ~300 |
| RiskScoreService | `services/risk_score.py` | ~250 |
| ReengagementService | `services/reengagement.py` | ~350 |
| NotificationPreferencesService | `services/notification_preferences.py` | ~200 |
| Modelos nuevos | `database/models.py` | ~150 |
| Background tasks | `background/lifecycle_tasks.py` | ~200 |
| Handler preferences | `handlers/user/preferences.py` | ~150 |
| Tests | `tests/test_lifecycle_*.py` | ~400 |
| **Total** | | **~2,000** |

---

## 9. DEPENDENCIAS Y ORDEN DE EJECUCIÓN

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    GRAFO DE DEPENDENCIAS                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                        ┌─────────┐                                      │
│                        │ ONDA A  │ ← Puede comenzar inmediatamente      │
│                        │Inmersivo│                                      │
│                        └────┬────┘                                      │
│                             │                                           │
│                             ▼                                           │
│                        ┌─────────┐                                      │
│                        │ ONDA B  │ ← Requiere EngagementService (A1)    │
│                        │ Lucien  │                                      │
│                        └────┬────┘                                      │
│                             │                                           │
│              ┌──────────────┴──────────────┐                            │
│              ▼                             ▼                            │
│         ┌─────────┐                   ┌─────────┐                       │
│         │ ONDA C  │                   │ ONDA D  │                       │
│         │Gabinete │                   │Retención│                       │
│         └─────────┘                   └─────────┘                       │
│              │                             │                            │
│              │    Requiere PersonalizationService (B3)                  │
│              │    Requiere LucienVoiceService (B1)                      │
│              │                             │                            │
│              └──────────────┬──────────────┘                            │
│                             ▼                                           │
│                     ┌──────────────┐                                    │
│                     │  INTEGRACIÓN │                                    │
│                     │    FINAL     │                                    │
│                     └──────────────┘                                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Orden Recomendado

| Orden | Onda | Razón |
|-------|------|-------|
| 1 | **ONDA A** | Sin dependencias, desbloquea narrativa inmersiva |
| 2 | **ONDA B** | Requiere A para métricas de arquetipo |
| 3 | **ONDA C** | Requiere B para personalización de ofertas |
| 3 | **ONDA D** | Requiere B para voz de Lucien en mensajes |
| 4 | **Integración** | Pruebas E2E completas |

> **Nota:** ONDA C y ONDA D pueden desarrollarse en paralelo después de ONDA B.

---

## 10. FILOSOFÍA Y PRINCIPIOS

### 10.1 Principios Fundamentales

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PRINCIPIOS GUÍA                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. DIGNIDAD                                                            │
│     • Nunca spam                                                        │
│     • Nunca manipulación emocional                                      │
│     • Nunca culpa por inactividad                                       │
│     • Respetar "no" como respuesta final                                │
│                                                                         │
│  2. OBSERVACIÓN GENUINA                                                 │
│     • Lucien "ve" al usuario (no solo trackea)                          │
│     • La personalización se siente natural                              │
│     • Los arquetipos son reconocimiento, no etiquetas                   │
│                                                                         │
│  3. PROGRESIÓN SIGNIFICATIVA                                            │
│     • Cada avance se siente ganado                                      │
│     • Las recompensas tienen peso narrativo                             │
│     • El tiempo invertido tiene valor                                   │
│                                                                         │
│  4. MONETIZACIÓN ORGÁNICA                                               │
│     • Las ofertas llegan cuando se merecen                              │
│     • Los precios son justos y transparentes                            │
│     • El valor precede al pedido de dinero                              │
│                                                                         │
│  5. RETENCIÓN POR VALOR                                                 │
│     • El usuario regresa porque quiere                                  │
│     • El contenido justifica la atención                                │
│     • La experiencia mejora con el tiempo                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 10.2 Anti-Patrones a Evitar

| Anti-Patrón | Por Qué Evitarlo |
|-------------|------------------|
| Dark patterns | Destruyen confianza |
| FOMO artificial | Manipulación barata |
| Notificaciones excesivas | Irritan al usuario |
| Culpar por inactividad | Genera resentimiento |
| Ofertas constantes | Devalúan el producto |
| Métricas vanidosas | No reflejan valor real |

### 10.3 Voz de Lucien: Guía de Estilo

**Lucien ES:**
- Formal pero no frío
- Observador pero no invasivo
- Protector de Diana
- Elegantemente sarcástico cuando corresponde
- Respetuoso siempre

**Lucien NO ES:**
- Servil ni adulador
- Agresivo ni insistente
- Vendedor ni promotor
- Casual ni coloquial
- Robótico ni genérico

**Ejemplos:**

```
❌ MAL: "¡Hey! ¡Tenemos ofertas increíbles para ti! 🎉🎉🎉"
✅ BIEN: "He preparado algo que podría interesarte. Si decides verlo."

❌ MAL: "¡Te extrañamos! Vuelve pronto 😢"
✅ BIEN: "Han pasado días desde tu última visita. Diana preguntó por ti."

❌ MAL: "¡Felicidades! ¡Subiste de nivel! 🎊"
✅ BIEN: "He observado tu progreso. Ahora eres Iniciado. Diana estará complacida."
```

---

## RESUMEN EJECUTIVO

| Onda | Objetivo | Entregables | Líneas Est. |
|------|----------|-------------|-------------|
| **A** | Servicios Inmersivos | 4 servicios + tests | ~1,680 |
| **B** | Lucien + Arquetipos | 4 servicios + handlers | ~2,150 |
| **C** | Gabinete + Conversión | 4 servicios + ítems | ~1,950 |
| **D** | Retención + Lifecycle | 4 servicios + tasks | ~2,000 |
| **Total** | | | **~7,780** |

### Próximos Pasos

1. **Revisar y aprobar** este plan adaptado
2. **Priorizar** ondas según necesidades del negocio
3. **Comenzar ONDA A** (sin dependencias)
4. **Iterar** según feedback y resultados

---

*Documento generado: Enero 2026*
*Basado en: Plan Original (7 Fases) + Arquitectura Actual*
