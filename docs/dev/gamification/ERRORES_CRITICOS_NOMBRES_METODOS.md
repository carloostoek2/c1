# ERRORES CRÍTICOS - Nombres de Métodos Incorrectos
## Proyecto: El Mayordomo del Diván

**Fecha de verificación:** 2026-01-01
**Estado:** 4 errores críticos encontrados
**Impacto:** Los handlers fallarán en runtime con AttributeError

---

## RESUMEN EJECUTIVO

Se encontraron **4 métodos llamados que NO EXISTEN** en los servicios de gamificación.
Todos estos métodos causarán fallos en runtime cuando los usuarios intenten usar estas funcionalidades.

---

## ERRORES ENCONTRADOS

### 1. ❌ `get_pending_missions()` - NO EXISTE en MissionService

**Ubicación del error:**
```
bot/handlers/user/start.py:138
```

**Código incorrecto:**
```python
pending_missions = await gamification.mission.get_pending_missions(user_id)
```

**Problema:**
- El método `get_pending_missions()` NO existe en `MissionService`

**Solución:**
```python
# Opción 1: Usar get_available_missions (si existe)
pending_missions = await gamification.mission.get_available_missions(user_id)

# Opción 2: Filtrar get_user_missions por status PENDING
from bot.gamification.database.enums import MissionStatus
pending_missions = await gamification.mission.get_user_missions(
    user_id=user_id,
    status=MissionStatus.PENDING
)
```

**Impacto:**
- CRÍTICO: El menú de contexto dinámico fallará al verificar misiones pendientes
- Afecta: Todos los usuarios al ejecutar `/start`

---

### 2. ❌ `get_mission()` - NO EXISTE en MissionService

**Ubicaciones del error:**
```
bot/gamification/handlers/user/missions.py:262
bot/gamification/handlers/user/missions.py:332
```

**Código incorrecto:**
```python
mission = await gamification.mission.get_mission(mission_id)
```

**Problema:**
- El método `get_mission()` NO existe en `MissionService`
- Existe `get_mission_by_id()` en su lugar

**Solución:**
```python
mission = await gamification.mission.get_mission_by_id(mission_id)
```

**Impacto:**
- CRÍTICO: Handler de misiones fallará al mostrar detalles de misión
- Afecta: Callback `mission:view:*` cuando usuario ve detalles de encargo

---

### 3. ❌ `get_user_mission()` - NO EXISTE en MissionService

**Ubicación del error:**
```
bot/gamification/handlers/user/missions.py:263
```

**Código incorrecto:**
```python
user_mission = await gamification.mission.get_user_mission(user_id, mission_id)
```

**Problema:**
- El método `get_user_mission()` NO existe en `MissionService`

**Solución:**
```python
# Opción 1: Filtrar get_user_missions
user_missions = await gamification.mission.get_user_missions(user_id=user_id)
user_mission = next((m for m in user_missions if m.mission_id == mission_id), None)

# Opción 2: Agregar método get_user_mission_by_id en MissionService (recomendado)
user_mission = await gamification.mission.get_user_mission_by_id(user_id, mission_id)
```

**Impacto:**
- CRÍTICO: Handler de misiones fallará al mostrar detalles de misión del usuario
- Afecta: Callback `mission:view:*` cuando usuario ve su progreso en encargo

---

### 4. ❌ `get_streak_info()` - NO EXISTE en DailyGiftService

**Ubicación del error:**
```
bot/gamification/handlers/user/missions.py:349
```

**Código incorrecto:**
```python
streak_info = await gamification.daily_gift.get_streak_info(user_id)
```

**Problema:**
- El método `get_streak_info()` NO existe en `DailyGiftService`
- Existe `get_daily_gift_status()` que retorna información de racha

**Solución:**
```python
streak_status = await gamification.daily_gift.get_daily_gift_status(user_id)
current_streak = streak_status.get("current_streak", 0)
```

**Impacto:**
- MEDIO: Handler de reclamar recompensa de misión fallará al obtener racha
- Afecta: Callback `mission:claim:*` cuando usuario reclama recompensa de misión de racha

---

## MÉTODOS VERIFICADOS COMO CORRECTOS ✅

Los siguientes servicios tienen TODOS sus métodos correctamente nombrados:

### OnboardingService ✅
- `has_completed_onboarding()` ✅
- `grant_welcome_besitos()` ✅

### SubscriptionService ✅
- `validate_token()` ✅
- `activate_vip_subscription()` ✅
- `create_invite_link()` ✅
- `get_vip_subscriber()` ✅
- `is_vip_active()` ✅

### BesitoService ✅
- `get_balance()` ✅
- `deduct_besitos()` ✅
- `get_transaction_history()` ✅

### InventoryService ✅
- `grant_item()` ✅

### DailyGiftService ✅
- `claim_daily_gift()` ✅
- `get_daily_gift_status()` ✅

---

## PLAN DE CORRECCIÓN RECOMENDADO

### Prioridad 1: Corregir errores CRÍTICOS (bloqueantes)

**Archivos a modificar:**
1. `bot/handlers/user/start.py` - Línea 138
2. `bot/gamification/handlers/user/missions.py` - Líneas 262, 263, 332, 349

**Cambios:**
```python
# start.py línea 138
- pending_missions = await gamification.mission.get_pending_missions(user_id)
+ pending_missions = await gamification.mission.get_available_missions(user_id)

# missions.py línea 262 y 332
- mission = await gamification.mission.get_mission(mission_id)
+ mission = await gamification.mission.get_mission_by_id(mission_id)

# missions.py línea 263
- user_mission = await gamification.mission.get_user_mission(user_id, mission_id)
+ user_missions = await gamification.mission.get_user_missions(user_id=user_id)
+ user_mission = next((m for m in user_missions if m.mission_id == mission_id), None)

# missions.py línea 349
- streak_info = await gamification.daily_gift.get_streak_info(user_id)
+ streak_status = await gamification.daily_gift.get_daily_gift_status(user_id)
+ current_streak = streak_status.get("current_streak", 0)
```

### Prioridad 2: Tests de validación

**Crear tests para verificar:**
1. Método `/start` con misiones pendientes
2. Callback `mission:view:*` con misión válida
3. Callback `mission:claim:*` con racha activa

---

## ESTADÍSTICAS DE VERIFICACIÓN

| Servicio | Métodos Verificados | Errores Encontrados | Tasa de Error |
|----------|---------------------|---------------------|---------------|
| **MissionService** | 6 | 3 | 50% ❌ |
| **DailyGiftService** | 3 | 1 | 33% ❌ |
| **BesitoService** | 3 | 0 | 0% ✅ |
| **OnboardingService** | 2 | 0 | 0% ✅ |
| **SubscriptionService** | 5 | 0 | 0% ✅ |
| **InventoryService** | 1 | 0 | 0% ✅ |
| **TOTAL** | **20** | **4** | **20%** |

---

## PRÓXIMOS PASOS

1. ✅ **Documentar errores** (COMPLETADO)
2. ⏳ **Corregir handlers** (PENDIENTE)
3. ⏳ **Validar con tests** (PENDIENTE)
4. ⏳ **Actualizar documentación de tracking** (PENDIENTE)

---

*Fin del reporte de errores críticos*

**Próxima acción:** Corregir los 4 métodos incorrectos en handlers
