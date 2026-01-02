# Flujo del Usuario - Mapeo y Tracking
## Proyecto: El Mayordomo del Diván

**Fecha:** 2025-12-31
**Objetivo:** Mapear el flujo completo del usuario, identificar gaps y corregir para producción

---

# ÍNDICE

1. [Estado Actual del Flujo](#estado-actual-del-flujo)
2. [Diagrama de Flujo Completo](#diagrama-de-flujo-completo)
3. [Componentes y su Estado](#componentes-y-su-estado)
4. [Gaps Identificados](#gaps-identificados)
5. [Plan de Corrección](#plan-de-corrección)

---

# ESTADO ACTUAL DEL FLUJO

## Resumen Ejecutivo

| Componente | Estado | Voz Lucien | Integrado | Notas |
|------------|--------|------------|-----------|-------|
| **/start** | ✅ Completo | ✅ | ⚠️ Parcial | 5 flujos, NO conecta a onboarding |
| **Onboarding** | ✅ Completo | ✅ | ❌ Separado | Módulo narrative independiente |
| **Menú Free** | ⚠️ Doble | ✅ | ⚠️ Parcial | 2 sistemas en paralelo |
| **Menú VIP** | ⚠️ Doble | ✅ | ⚠️ Parcial | 2 sistemas en paralelo |
| **/perfil** | ✅ Completo | ✅ | ✅ | Barra progreso + comentarios |
| **/favores** | ✅ Completo | ✅ | ⚠️ Parcial | Comando existe, NO en menú start.py |
| **/misiones** | ✅ Completo | ✅ | ⚠️ Parcial | Handler existe, parcial en menú |
| **/tienda** | ❌ Falta | ✅ mensajes | ❌ | NO existe handler user |
| **/vip** | ✅ Completo | ⚠️ Parcial | ⚠️ | Existe pero NO en menú |
| **/premium** | ✅ Completo | ⚠️ Parcial | ⚠️ | Existe pero NO en menú |
| **/mapa** | ✅ Completo | ⚠️ Parcial | ⚠️ | Existe pero NO en menú |
| **/historia** | ✅ Completo | ⚠️ Parcial | ⚠️ | Existe pero parcial en menú |

**Conclusión:** Los handlers existen en su mayoría pero están **desconectados** entre sí. Hay dos sistemas de menús en paralelo.

---

# DIAGRAMA DE FLUJO COMPLETO

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FLUJO DEL USUARIO COMPLETO                         │
└─────────────────────────────────────────────────────────────────────────────┘

   USUARIO NUEVO
       │
       ▼
   ┌─────────┐
   │ /start  │
   └────┬────┘
        │
        ├─────────────────────────────────────────────────────────┐
        │                                                         │
        ▼ (Usuario completamente nuevo)                          ▼
   ┌─────────────────┐                                    ┌─────────────────┐
   │ start.py        │                                    │ [FALTA]         │
   │ _flow_new_user()│                                    │ Onboarding      │
   │                 │                                    │ Narrative       │
   │ Mensaje 1:      │                                    │ (5 pasos)       │
   │ Lucien intro    │                                    │                 │
   │                 │                                    │ - Detección     │
   │ Mensaje 2:      │                                    │   arquetipo     │
   │ Advertencia     │                                    │ - 30 besitos    │
   │                 │                                    │ - Tutorial     │
   │ Botones:        │                                    │   sistema       │
   │ - Continuar     │                                    │                 │
   │ - ¿Quién Diana? │                                    └────────┬────────┘
   └────────┬────────┘                                             │
            │                                                      │
            ▼                                                      │
   ┌─────────────────┐                                             │
   │ callback_       │                                             │
   │ continue_onboard│                                             │
   │ ing             │                                             │
   │                 │                                             │
   │ Marca is_new_   │                                             │
   │ user = False    │                                             │
   │                 │                                             │
   │ Muestra menú    │◄────────────────────────────────────────────┘
   │ principal       │
   └────────┬────────┘
            │
            ▼
   ╔═══════════════════════════════════════════════════════════════════╗
   ║                    MENÚ PRINCIPAL                                ║
   ╠═══════════════════════════════════════════════════════════════════╣
   ║                                                                   ║
   ║  FREE:                        VIP:                               ║
   ║  ┌─────────────────────┐     ┌─────────────────────────┐        ║
   ║  │ 📖 La Historia       │     │ 📖 Continuar Historia   │        ║
   ║  │ 🎭 Mi Perfil         │     │ 🎭 Mi Perfil             │        ║
   ║  │ 🗄️ El Gabinete       │     │ 🗄️ El Gabinete           │        ║
   ║  │ 📋 Mis Encargos      │     │ 📋 Mis Encargos          │        ║
   ║  │ 💫 Mis Favores      │     │ 💫 Mis Favores           │        ║
   ║  │ [FALTA: 🔑 Llave]   │     │ 💎 Premium               │        ║
   ║  │                      │     │ 🗺️ Mapa del Deseo        │        ║
   ║  │                      │     │ 🎁 Lo Nuevo              │        ║
   ║  └─────────────────────┘     └─────────────────────────┘        ║
   ╚═══════════════════════════════════════════════════════════════════╝
            │
            ├─── 📖 La Historia ──────────────────────────┐
            │                                             │
            ▼                                             ▼
     ┌──────────────┐                          ┌─────────────────┐
     │story:start    │                          │story:continue   │
     │(narrative/    │                          │(narrative/      │
     │ story.py)     │                          │ story.py)       │
     └──────────────┘                          └─────────────────┘
            │                                             │
            ▼                                             ▼
     ┌─────────────────┐                        ┌─────────────────┐
     │ Narrative       │                        │ Narrative       │
     │ Container      │                        │ Container      │
     │                 │                        │                 │
     │ - Verificar     │                        │ - Continuar     │
     │   onboarding   │                        │   último        │
     │   completado?  │                        │   fragmento     │
     │                 │                        │                 │
     │ ┌─────────────┐ │                        │                 │
     │ │ NO →        │ │                        │                 │
     │ │ Redirigir   │ │                        │                 │
     │ │ a           │ │                        │                 │
     │ │ onboarding? │ │                        │                 │
     │ └─────────────┘ │                        │                 │
     └─────────────────┘                        └─────────────────┘


            ├─── 🎭 Mi Perfil ───────────────────────────┐
            │                                             │
            ▼                                             ▼
     ┌─────────────────┐                        ┌─────────────────┐
     │profile:view     │                        │ Barra de        │
     │(start.py)       │                        │ progreso visual │
     │                 │                        │                 │
     │ - Nivel         │                        │ ▓▓▓▓▓▒▒▒▒▒      │
     │ - Favores       │                        │ 50/100          │
     │ - Arquetipo     │                        │                 │
     │ - Días totales  │                        │ Comentario      │
     │ - Racha         │                        │ Lucien por nivel│
     │ - Capítulos     │                        │                 │
     │ - Badges        │                        │ Botones:        │
     │                 │                        │ - Ver badges    │
     │ Botones:        │                        │ - Volver        │
     │ - Ver badges    │                        │                 │
     │ - Volver        │                        │                 │
     └─────────────────┘                        └─────────────────┘


            ├─── 🗄️ El Gabinete ──────────────────────────┐
            │                                             │
            ▼                                             ▼
     ┌─────────────────┐                        ┌─────────────────┐
     │cabinet:browse   │                        │ [FALTA]         │
     │(start.py)       │                        │ Handler user    │
     │                 │                        │ /tienda         │
     │ Mensaje básico  │                        │                 │
     │ (sin voz Lucien │                        │ Debe usar:      │
     │ completa)      │                        │ Lucien.CABINET_*│
     │                 │                        │                 │
     │ Botón:          │                        │ - Categorías    │
     │ "Ver artículos" │                        │ - Items         │
     │ (shop:browse)   │                        │ - Confirmación  │
     │                 │                        │ - Purchase      │
     │ [PROBLEMA]      │                        │   success/error  │
     │ No hay handler  │                        │                 |
     │ shop:browse     │                        │                 │
     └─────────────────┘                        └─────────────────┘


            ├─── 📋 Mis Encargos ─────────────────────────┐
            │                                             │
            ▼                                             ▼
     ┌─────────────────┐                        ┌─────────────────┐
     │missions:list    │                        │user:missions    │
     │(start.py)       │                        │(gamification/   │
     │                 │                        │ handlers/user/  │
     │ Mensaje intro   │                        │ missions.py)    │
     │ básico          │                        │                 │
     │                 │                        │ ✅ Voz Lucien    │
     │ Botón:          │                        │ ✅ Secciones     │
     │ "Ver encargos"  │                        │ ✅ Comentarios   │
     │                 │                        │ ✅ Formato       │
     │ ▼               │                        │                 │
     │ user:missions   │                        │ - PROTOCOLO     │
     │ (handler gamif) │                        │   DIARIO        │
     │                 │                        │ - ENCARGO       │
     │ ✅ COMPLETO     │                        │   SEMANAL       │
     │ ✅ Voz Lucien   │                        │ - EVALUACIONES  │
     │ ✅ Secciones   │                        │   ESPECIALES    │
     │ ✅ Comentarios  │                        │                 │
     └─────────────────┘                        └─────────────────┘


            ├─── 💫 Mis Favores ────────────────────────────┐
            │                                             │
            ▼                                             ▼
     ┌─────────────────┐                        ┌─────────────────┐
     │favors:balance   │                        │/favores         │
     │(start.py)       │                        │(favors.py)      │
     │                 │                        │                 │
     │ Mensaje básico  │                        │ ✅ Voz Lucien   │
     │ (sin stats)     │                        │ ✅ Balance      │
     │                 │                        │ ✅ Actividad    │
     │ [PROBLEMA]      │                        │ ✅ Hitos        │
     │ No conecta a    │                        │ ✅ Historial    │
     │ handler completo│                        │ ✅ Cómo ganar   │
     │                 │                        │                 │
     │ ▼               │                        │ Callbacks:      │
     │ [NADA]          │                        │ - favors:history│
     │                 │                        │ - favors:how_   │
     │                 │                        │   to_earn       │
     └─────────────────┘                        └─────────────────┘


            ├─── 💎 Premium ────────────────────────────────┐
            │                                             │
            ▼                                             ▼
     ┌─────────────────┐                        ┌─────────────────┐
     │[FALTA callback] │                        │/premium         │
     │en menú VIP      │                        │(conversion.py)  │
     │                 │                        │                 │
     │                 │                        │ ✅ Handler existe│
     │                 │                        │ ⚠️ No en menú    │
     │                 │                        │                 │
     └─────────────────┘                        └─────────────────┘


            ├─── 🗺️ Mapa del Deseo ──────────────────────────┐
            │                                             │
            ▼                                             ▼
     ┌─────────────────┐                        ┌─────────────────┐
     │map:view         │                        │/mapa            │
     │(start.py)       │                        │(conversion.py)  │
     │                 │                        │                 │
     │ Mensaje intro   │                        │ ✅ Handler existe│
     │ básico          │                        │ ⚠️ No en menú    │
     │                 │                        │                 │
     │ [PROBLEMA]      │                        │                 │
     │ No conecta a    │                        │                 │
     │ handler completo│                        │                 │
     └─────────────────┘                        └─────────────────┘


            └─── 🔑 La Llave (VIP) ─────────────────────────┐
            │                                             │
            ▼                                             ▼
     ┌─────────────────┐                        ┌─────────────────┐
     │[FALTA callback] │                        │/vip             │
     │en menú Free     │                        │(conversion.py)  │
     │                 │                        │                 │
     │                 │                        │ ✅ Flujo Free→VIP│
     │                 │                        │ ✅ Voz Lucien   │
     │                 │                        │ ✅ Mensajes     │
     │                 │                        │ ✅ Proceso pago │
     │                 │                        │                 │
     └─────────────────┘                        └─────────────────┘
```

---

# COMPONENTES Y SU ESTADO

## 1. /start - Handler Principal

**Archivo:** `bot/handlers/user/start.py`

**Estado:** ✅ Completo pero desconectado de onboarding

### Flujos Implementados

| Flujo | Trigger | Implementación | Voz Lucien | Notas |
|-------|---------|----------------|------------|-------|
| **New User** | `is_new=True` | ✅ | ✅ | START_NEW_USER_1/2 |
| **Returning < 7d** | `days_away < 7` | ✅ | ✅ | START_RETURNING_SHORT |
| **Returning 7-14d** | `7 <= days < 14` | ✅ | ✅ | START_RETURNING_MEDIUM |
| **Returning > 14d** | `days >= 14` | ✅ | ✅ | START_RETURNING_LONG |
| **VIP** | `is_vip=True` | ✅ | ✅ | START_VIP |

### Keyboards

```python
def lucien_main_menu_keyboard(is_vip: bool = False)
```

**Versión Free:**
- La Historia (story:start)
- Mi Perfil (profile:view)
- El Gabinete (cabinet:browse)
- Mis Encargos (missions:list)
- Mis Favores (favors:balance)

**Versión VIP:**
- Continuar Historia (story:continue)
- Mi Perfil (profile:view)
- El Gabinete (cabinet:browse)
- Mis Encargos (missions:list)
- Mis Favores (favors:balance)
- Lo Nuevo (content:new)
- Mapa del Deseo (map:view)

### Gap Crítico

**❌ Onboarding NO está conectado:**
- El onboarding de narrative (`onboarding.py`) es un flujo independiente
- Se llama desde `approve_ready_free_requests()` DESPUÉS de aprobación Free
- Un usuario nuevo en `/start` NO pasa por onboarding de 5 pasos

**Flujo actual:**
```
Usuario nuevo → /start → Mensajes Lucien → Marca is_new_user=False → Menú
                                                     ↓
                                             (SIN onboarding)
```

**Flujo deseado:**
```
Usuario nuevo → /start → Onboarding 5 pasos → Menú completo
                               ↓
                        - Detección arquetipo
                        - 30 besitos regalo
                        - Tutorial sistema
```

---

## 2. Onboarding - Narrative

**Archivo:** `bot/handlers/user/narrative/onboarding.py`

**Estado:** ✅ Completo pero NO conectado a /start

### Características

| Característica | Estado | Descripción |
|----------------|--------|-------------|
| 5 pasos | ✅ | Tutorial completo del sistema |
| Detección arquetipo | ✅ | Basada en decisiones del usuario |
| 30 besitos regalo | ✅ | `grant_welcome_besitos(user_id, 30)` |
| Voz narrativa | ✅ | Fragmentos con instrucciones |
| Verificación completado | ✅ | `has_completed_onboarding(user_id)` |

### Problema

El onboarding se llama actualmente desde:
- `approve_ready_free_requests()` en el servicio de subscription
- O sea, DESPUÉS de que el usuario es aprobado en el canal Free

**NO se llama desde /start para usuarios nuevos.**

---

## 3. Menús - Sistema Dual

### Sistema 1: start.py (Hardcoded)

**Ubicación:** `bot/handlers/user/start.py`

**Keyboards:**
- `lucien_main_menu_keyboard(is_vip)`
- Keyboards hardcoded en el código

### Sistema 2: dynamic_menu.py (BD)

**Ubicación:** `bot/handlers/user/dynamic_menu.py`

**Keyboards:**
- `dynamic_user_menu_keyboard(session, role)`
- Configurables por admin en BD

### Sistema 3: menu_helpers.py (Híbrido)

**Ubicación:** `bot/utils/menu_helpers.py`

**Funciones:**
- `build_start_menu()` - Usa sistema 2
- `build_profile_menu()` - Usa gamificación + sistema 2

### Problema

**Tres sistemas de menús en paralelo sin un punto de verdad único.**

---

# GAPS IDENTIFICADOS

## Gap 1: Onboarding Desconectado

**Severidad:** 🔴 CRÍTICA

**Descripción:**
- El onboarding de 5 pasos NO se ejecuta desde `/start`
- Usuario nuevo en `/start` solo ve 2 mensajes de Lucien
- No recibe los 30 besitos de bienvenida
- No se le detecta el arquetipo
- No aprende el sistema

**Solución:**
Integrar onboarding narrative en el flujo `/start` para usuarios nuevos.

## Gap 2: Callbacks de Menú Faltantes

**Severidad:** 🟡 ALTA

**Callbacks en menú start.py SIN handler:**

| Callback | Estado | Handler Existente | Acción |
|----------|--------|-------------------|--------|
| `cabinet:browse` | ❌ Parcial | NO (user) | Crear handler /tienda |
| `missions:list` | ⚠️ Parcial | ✅ `user:missions` | Conectar |
| `favors:balance` | ⚠️ Parcial | ✅ `/favores` | Conectar |
| `map:view` | ❌ Parcial | ✅ `/mapa` | Conectar |
| `premium:view` | ❌ Falta | ✅ `/premium` | Agregar callback |
| `vip:view` | ❌ Falta | ✅ `/vip` | Agregar callback |

## Gap 3: Sistema de Menús Desunificado

**Severidad:** 🟡 ALTA

**Descripción:**
- 3 sistemas de menús en paralelo
- No hay un punto de verdad único
- Difícil mantener

**Solución:**
Unificar en un solo sistema con un source of truth.

## Gap 4: Handler /tienda Falta

**Severidad:** 🟡 ALTA

**Descripción:**
- NO existe handler user para /tienda
- Mensajes de Lucien listos (`Lucien.CABINET_*`)
- Inventario del Gabinete vacío (0 items)

**Solución:**
1. Crear `bot/gamification/handlers/user/shop.py`
2. Usar mensajes `Lucien.CABINET_*`
3. Conectar callback `cabinet:browse`

---

# PLAN DE CORRECCIÓN

## Fase 1: Conectar Onboarding a /start

**Archivos a modificar:**
- `bot/handlers/user/start.py`
- `bot/handlers/user/narrative/onboarding.py`

**Cambios:**

1. **Modificar `_flow_new_user()`:**
   ```python
   async def _flow_new_user(message: Message, session: AsyncSession, user):
       # Verificar si ya completó onboarding
       narrative = NarrativeContainer(session)
       if not await narrative.onboarding.has_completed_onboarding(user_id):
           # Redirigir a onboarding
           await send_onboarding_welcome(bot, user_id, session)
       else:
           # Flujo normal actual
           await message.answer(Lucien.START_NEW_USER_1, ...)
   ```

2. **Importar onboarding:**
   ```python
   from bot.handlers.user.narrative.onboarding import send_onboarding_welcome
   from bot.narrative.services.container import NarrativeContainer
   ```

## Fase 2: Crear Handler /tienda

**Archivo a crear:**
- `bot/gamification/handlers/user/shop.py`

**Contenido:**
- Handler comando `/tienda`
- Callback `cabinet:browse`
- Callbacks por categoría
- Mensajes `Lucien.CABINET_*`

## Fase 3: Conectar Callbacks Existentes

**Archivo a modificar:**
- `bot/handlers/user/start.py`

**Cambios:**

1. **Conectar `missions:list`:**
   ```python
   @user_router.callback_query(F.data == "missions:list")
   async def callback_missions_redirect(callback: CallbackQuery):
       # Redirigir a handler de gamification
       # O integrar directamente
   ```

2. **Conectar `favors:balance`:**
   ```python
   @user_router.callback_query(F.data == "favors:balance")
   async def callback_favors_redirect(callback: CallbackQuery):
       # Redirigir a /favores handler
   ```

## Fase 4: Unificar Sistema de Menús

**Estrategia:**
- Mantener `lucien_main_menu_keyboard()` como source of truth
- Actualizar `dynamic_menu.py` para usar misma estructura
- O reemplazar completamente por sistema único

**Decisión pendiente:** ¿Mantener ambos o unificar?

---

*Fin del documento de mapeo*

**Próximo paso:** Implementar correcciones en orden de prioridad
