# Validación y Tracking - Módulo de Gamificación
## Proyecto: El Mayordomo del Diván

**Fecha de creación:** 2025-12-31
**Última actualización:** 2026-01-01
**Estado:** ✅ Validación completada - ❌ 4 errores críticos de nombres de métodos encontrados
**Objetivo:** Validar implementación vs especificaciones y mapear comandos para integración de menús

---

## ⚠️ ERRORES CRÍTICOS ENCONTRADOS (2026-01-01)

**Ver documento completo:** `docs/dev/gamification/ERRORES_CRITICOS_NOMBRES_METODOS.md`

### Resumen de Errores:
1. ❌ `gamification.mission.get_pending_missions()` - NO EXISTE (debe ser `get_available_missions`)
2. ❌ `gamification.mission.get_mission()` - NO EXISTE (debe ser `get_mission_by_id`)
3. ❌ `gamification.mission.get_user_mission()` - NO EXISTE (debe usar `get_user_missions` + filtro)
4. ❌ `gamification.daily_gift.get_streak_info()` - NO EXISTE (debe ser `get_daily_gift_status`)

**Impacto:** Los handlers fallarán en runtime al llamar estos métodos.
**Acción requerida:** Corregir nombres de métodos en handlers (ver documento de errores)

---

# ÍNDICE

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Mapeo de Fases vs Implementación](#mapeo-de-fases-vs-implementación)
3. [Comandos Disponibles](#comandos-disponibles)
4. [Gaps de Integración](#gaps-de-integración)
5. [Acciones Recomendadas](#acciones-recomendadas)

---

# RESUMEN EJECUTIVO

## Estado General del Módulo de Gamificación (ACTUALIZADO 2026-01-01)

| Componente | Estado | Cobertura | Notas |
|------------|--------|-----------|-------|
| **Base de Datos** | ✅ Completo | 100% | 16+ modelos implementados |
| **Servicios** | ⚠️ Completo con errores | 95% | 30+ servicios, 4 métodos con nombres incorrectos |
| **Handlers Admin** | ✅ Completo | 90% | 20+ handlers funcionales |
| **Handlers User** | ✅ Completo | 95% | Onboarding integrado, misiones completas, /start completo |
| **Mensajes Lucien** | ✅ Completo | 100% | Archivo `lucien_messages.py` con todas las categorías |
| **Conversión** | ✅ Implementado | 90% | Fase 6 completa |
| **Arquetipos** | ✅ Implementado | 95% | Detección funcional |
| **Tienda/Gabinete** | ✅ Completo | 100% | Backend + Frontend + 16 items cargados |
| **Onboarding** | ✅ Integrado | 100% | Conectado a /start correctamente |
| **Callbacks Menú** | ✅ Completo | 100% | Todos los callbacks conectados |

**Conclusión (ACTUALIZADO):**
- ✅ Backend COMPLETO (servicios, BD, handlers)
- ✅ Frontend COMPLETO (todos los handlers user implementados)
- ✅ Onboarding integrado con /start
- ✅ Inventario del Gabinete cargado (16 items, 4 categorías)
- ✅ Todos los callbacks del menú conectados
- ❌ **4 ERRORES CRÍTICOS de nombres de métodos** que causan fallos en runtime

**Áreas que requieren corrección inmediata:**
1. **Corregir nombres de métodos** en MissionService (3 errores)
2. **Corregir nombre de método** en DailyGiftService (1 error)
3. **Tests de validación** para prevenir regresiones

---

# MAPEO DE FASES VS IMPLEMENTACIÓN

## FASE 0: Fundamentos

### F0.1: Economía de Favores

| Especificación | Implementación | Estado | Archivos |
|----------------|----------------|--------|----------|
| Backend usa "besitos", UI muestra "Favores" | ✅ Implementado | ✅ Completo | `formatters.py:format_currency()` |
| Soporte decimales (0.1, 0.5) | ⚠️ Requiere migración | ⚠️ Pendiente | `total_besitos` es Integer |
| Configuración de valores editable | ✅ Implementado | ✅ Completo | `EconomyConfigService` |
| Tabla de ganancia (FAVOR_REWARDS) | ✅ Implementado | ✅ Completo | `formatters.py` |
| 7 niveles de Protocolo | ✅ Implementado | ✅ Completo | `PROTOCOL_LEVELS` |

**NOTA:** Decisión de arquitectura correcta - backend mantiene "besitos" por estabilidad, UI muestra "Favores".

### F0.2: Mensajes de Lucien

| Categoría | Implementado | Archivo |
|-----------|--------------|---------|
| ONBOARDING (5 flujos) | ✅ Completo | `lucien_messages.py` líneas 37-195 |
| FAVORES (12 mensajes) | ✅ Completo | `lucien_messages.py` líneas 197-318 |
| NIVELES (10 mensajes) | ✅ Completo | `lucien_messages.py` líneas 320-371 |
| ERRORES (12 mensajes) | ✅ Completo | `lucien_messages.py` líneas 373-453 |
| CONFIRMACIONES (14 mensajes) | ✅ Completo | `lucien_messages.py` líneas 455-561 |
| GABINETE (10 mensajes) | ✅ Completo | `lucien_messages.py` líneas 563-632 |
| MISIONES (9 mensajes) | ✅ Completo | `lucien_messages.py` líneas 634-703 |
| ARQUETIPOS (6 mensajes) | ✅ Completo | `lucien_messages.py` líneas 705-746 |
| RETENCIÓN (6 mensajes) | ✅ Completo | `lucien_messages.py` líneas 748-787 |
| CONVERSIÓN (5 mensajes) | ✅ Completo | `lucien_messages.py` líneas 789-824 |

**Archivo:** `bot/utils/lucien_messages.py` - 870 líneas, TODAS las categorías completas ✅

### F0.3: Arquetipos Expandidos

| Arquetipo | Enum | Detección | Mensajes |
|-----------|------|-----------|----------|
| EXPLORER | ✅ | ✅ | ✅ |
| DIRECT | ✅ | ✅ | ✅ |
| ROMANTIC | ✅ | ✅ | ✅ |
| ANALYTICAL | ✅ | ✅ | ✅ |
| PERSISTENT | ✅ | ✅ | ✅ |
| PATIENT | ✅ | ✅ | ✅ |

**Archivos:**
- `enums.py`: ArchetypeType enum ✅
- `services/archetype_detection.py`: Detección basada en comportamiento ✅
- `services/archetype_messages.py`: Mensajes por arquetipo ✅
- `lucien_messages.py`: Líneas 705-746 ✅

### F0.4: Inventario del Gabinete (✅ ACTUALIZADO 2026-01-01)

| Categoría | Items Especificados | Items Cargados | Estado |
|-----------|---------------------|----------------|--------|
| Efímeros | 4 | 4 | ✅ Completo |
| Distintivos | 5 | 5 | ✅ Completo |
| Llaves | 4 | 4 | ✅ Completo |
| Reliquias | 3 | 3 | ✅ Completo |
| **TOTAL** | **16** | **16** | ✅ **100%** |

**✅ COMPLETADO:** Script `scripts/seed_cabinet_items.py` ejecutado correctamente.
**Verificación BD:** 16 items activos, 4 categorías cargadas.
**Handlers:** Frontend del Gabinete implementado en `bot/handlers/user/start.py:1208-1463`

### F0.5: Estructura Narrativa

| Componente | Estado | Archivos |
|------------|--------|----------|
| NarrativeChapter | ✅ | `narrative/database/models.py` |
| NarrativeFragment | ✅ | `narrative/database/models.py` |
| NarrativeDecision | ✅ | `narrative/database/models.py` |
| UserNarrativeProgress | ✅ | `narrative/database/models.py` |
| Seeds niveles 1-6 | ✅ | `seed_level_*.py` |

---

## FASE 1: La Voz de Lucien

### F1.1: Comando /start

| Flujo | Especificación | Implementación | Estado | Archivo |
|-------|----------------|----------------|--------|---------|
| Usuario nuevo | 2+ mensajes, voz Lucien | ⚠️ Requiere integración | ⚠️ Pendiente | `start.py` existe |
| Usuario regresa (<7 días) | Mensaje personalizado | ✅ Mensaje existe | ⚠️ Pendiente integrar | `lucien_messages.py:75` |
| Usuario inactivo (7-14 días) | Mensaje retención | ✅ Mensaje existe | ⚠️ Pendiente integrar | `lucien_messages.py:84` |
| Usuario muy inactivo (14+días) | Mensaje re-engagement | ✅ Mensaje existe | ⚠️ Pendiente integrar | `lucien_messages.py:100` |
| Usuario VIP | Flujo diferenciado | ✅ Mensaje existe | ⚠️ Pendiente integrar | `lucien_messages.py:114` |

**NOTA IMPORTANTE:** Existe onboarding obligatorio de 5 pasos (`onboarding.py`) que debe integrarse con /start.

**Acción requerida:** Reescribir `bot/handlers/user/start.py` para:
1. Integrar los 5 flujos diferenciados
2. Conectar con onboarding obligatorio
3. Usar mensajes desde `lucien_messages.py`

### F1.2: Menú Principal

| Componente | Especificación | Implementación | Estado |
|------------|----------------|----------------|--------|
| Menú Free | 5 botones, contexto dinámico | ⚠️ Existe básico | Necesita expansión |
| Menú VIP | 6 botones + extras | ⚠️ Existe básico | Necesita expansión |
| Contextos dinámicos | 5 tipos de mensajes | ✅ Mensajes listos | ⚠️ Pendiente usar |

**Archivo:** `bot/handlers/user/dynamic_menu.py` - Existe, necesita usar `Lucien.MENU_CONTEXT_*`

### F1.3: Perfil (/perfil)

| Componente | Especificación | Implementación | Estado |
|------------|----------------|----------------|--------|
| Vista completa | Nivel, favores, arquetipo, badges | ⚠️ Parcial | `profile.py` básico |
| Comentario Lucien por nivel | ✅ Mensajes listos | ⚠️ Pendiente usar | `lucien_messages.py:153-171` |

### F1.4: Gabinete (Tienda) (✅ ACTUALIZADO 2026-01-01)

| Componente | Especificación | Implementación | Estado | Archivo |
|------------|----------------|----------------|--------|---------| | Vista principal | ✅ Mensajes listos | ✅ Implementado | ✅ Completo | `start.py:1209-1271` |
| Vista de categoría | ✅ Mensajes listos | ✅ Implementado | ✅ Completo | `start.py:1273-1335` |
| Vista de item | ✅ Mensajes listos | ✅ Implementado | ✅ Completo | `start.py:1337-1388` |
| Flujo de compra | ✅ Mensajes listos | ✅ Implementado | ✅ Completo | `start.py:1390-1464` |
| Callbacks | shop:browse, shop:category:*, shop:item:*, shop:buy:* | ✅ Implementado | ✅ Completo | Todos conectados |

**✅ COMPLETADO:** Handler del Gabinete totalmente funcional con:
- Vista de categorías con items
- Navegación por categorías
- Vista de detalles de items
- Flujo completo de compra (verificación de favores + deducción + grant item)
- Integración con Mochila (backpack)
- Uso completo de mensajes de Lucien

### F1.5: Encargos (Misiones)

| Componente | Especificación | Implementación | Estado | Archivo |
|------------|----------------|----------------|--------|---------|
| Vista de misiones | Protocolo diario, semanal, especiales | ✅ Completo | ✅ | `missions.py` |
| Notificación completado | ✅ Mensaje Lucien | ✅ Usa `Lucien.MISSION_COMPLETE_*` | ✅ | `missions.py:77` |
| Comentarios por tipo | ✅ 4 mensajes | ✅ Implementado | ✅ | `lucien_messages.py:671-685` |

**Estado:** ✅ COMPLETO - Handler implementado con voz de Lucien.

### F1.6: Sistema de Favores (✅ ACTUALIZADO 2026-01-01)

| Componente | Especificación | Implementación | Estado | Archivo |
|------------|----------------|----------------|--------|---------| | Vista balance | ✅ Mensajes listos | ✅ Implementado | ✅ Completo | `start.py:1106-1167` |
| Historial | ✅ Mensajes listos | ✅ Implementado | ✅ Completo | `start.py:1174-1198` |
| Cómo ganar | ✅ Mensajes listos | ✅ Implementado | ✅ Completo | `start.py:1200-1202` |
| Callbacks | start:favors, favors:history, favors:how_to_earn | ✅ Implementado | ✅ Completo | Todos conectados |

**✅ COMPLETADO:** Handler de Favores totalmente funcional con:
- Vista de balance con comentarios de Lucien según cantidad
- Historial de transacciones (últimas 10)
- Guía de cómo ganar Favores
- Integración completa con menú principal

---

## FASE 2: Economía de Favores

### F2.1: Decimales

| Requerimiento | Estado | Notas |
|---------------|--------|-------|
| Campo total_besitos Float/Decimal | ⚠️ Pendiente | Actualmente Integer |
| Migración a DECIMAL(10,2) | ⚠️ Pendiente | Necesario para 0.1, 0.5 |

### F2.2 - F2.10: Economía

| Componente | Estado | Archivos |
|------------|--------|----------|
| Configuración editable | ✅ | `economy_config.py` |
| Rachas con bonus | ✅ | `services/streak.py` |
| Level-up automático | ✅ | `services/level.py` |
| Límites diarios | ✅ | `services/reaction.py` |
| Admin commands | ✅ | `handlers/admin/economy_admin.py` |
| Prevención de exploits | ✅ | Múltiples capas |

---

## FASE 3: Arquetipos Expandidos

| Componente | Estado | Archivos |
|------------|--------|----------|
| 6 arquetipos definidos | ✅ | `enums.py` |
| Detección por comportamiento | ✅ | `archetype_detection.py` |
| Mensajes por arquetipo | ✅ | `lucien_messages.py:705-746` |
| Notificaciones personalizadas | ✅ | `archetype_notification.py` |

---

## FASE 4: El Gabinete

| Componente | Estado | Notas |
|------------|--------|-------|
| Backend (modelos, servicios) | ✅ | Completo |
| Inventario (17 items) | ❌ | **CRÍTICO: Vacío** |
| Handler admin | ✅ | `admin/shop.py` |
| Handler user | ⚠️ | Falta usar voz Lucien |
| Mensajes de Lucien | ✅ | `lucien_messages.py:563-632` |

**Acción prioritaria:** Crear seed script para cargar items del Gabinete.

---

## FASE 5: Narrativa y Contenido

| Componente | Estado | Archivos |
|------------|--------|----------|
| Modelos narrativos | ✅ | `narrative/database/models.py` |
| Servicios narrativos | ✅ | `narrative/services/` |
| Seeds 6 niveles | ✅ | `seed_level_*.py` |
| Easter eggs (6) | ✅ | Implementados |
| Onboarding (5 pasos) | ✅ | `onboarding.py` |

---

## FASE 6: Conversión y Upsell

| Componente | Estado | Archivos |
|------------|--------|----------|
| Flujo Free → VIP | ✅ | `handlers/user/conversion.py` |
| Servicios de conversión | ✅ | 8 servicios implementados |
| Mensajes de Lucien | ✅ | `messages.py`, `lucien_messages.py:789-824` |
| Handlers /vip, /premium, /mapa | ✅ | `conversion.py` |

---

# COMANDOS DISPONIBLES

## Comandos de Usuario (ACTUALIZADO 2026-01-01)

| Comando | Handler | Voz Lucien | Integrado en Menú | Estado |
|---------|---------|------------|-------------------|--------|
| /start | `user/start.py` | ✅ Completo | ✅ Raíz | ✅ Completo |
| /perfil | `gamification/user/profile.py` | ✅ Completo | ✅ Callback: user:profile | ✅ Completo |
| /misiones | `gamification/user/missions.py` | ✅ Completo | ✅ Callback: user:missions | ✅ Completo |
| /daily_gift | `gamification/user/daily_gift.py` | ✅ Completo | ✅ Callback: user:daily_gift | ✅ Completo |
| /leaderboard | `gamification/user/leaderboard.py` | ⚠️ Parcial | ❌ | ✅ Funcional |
| /vip | `handlers/user/start.py` | ✅ Completo | ✅ Callback: vip:info | ✅ Completo |
| /premium | `handlers/user/start.py` | ✅ Completo | ✅ Callback: premium:info | ✅ Completo |
| /mapa | `handlers/user/start.py` | ✅ Completo | ✅ Callback: mapa:info | ✅ Completo |
| /historia | `narrative/user/story.py` | ⚠️ Parcial | ✅ Callbacks: narr:start, story:continue | ✅ Funcional |
| **Favores (callback)** | `user/start.py:1105-1206` | ✅ Completo | ✅ Callback: start:favors | ✅ Completo |
| **Tienda (callback)** | `user/start.py:1208-1463` | ✅ Completo | ✅ Callback: shop:browse | ✅ Completo |
| **Mochila (callback)** | `shop/user/backpack.py` | ✅ Completo | ✅ Callback: backpack:main | ✅ Completo |

## Comandos de Administración

| Comando | Handler | Estado |
|---------|---------|--------|
| /gamif | `gamification/admin/main.py` | ✅ |
| /g_config | `gamification/admin/config.py` | ✅ |
| /g_missions | `gamification/admin/mission_config.py` | ✅ |
| /g_rewards | `gamification/admin/reward_config.py` | ✅ |
| /g_levels | `gamification/admin/level_config.py` | ✅ |
| /g_economy | `gamification/admin/economy_admin.py` | ✅ |
| /g_wizard_* | `gamification/admin/*_wizard.py` | ✅ |
| /admin:narrative | `narrative/admin/main.py` | ✅ |

---

# GAPS DE INTEGRACIÓN

## Handlers que NO usan voz de Lucien

| Handler | Archivo | Acción |
|---------|---------|--------|
| /start | `user/start.py` | Reescribir con 5 flujos + onboarding |
| /perfil | `gamification/user/profile.py` | Usar `Lucien.PROFILE_*` |
| /daily_gift | `gamification/user/daily_gift.py` | Usar `Lucien.FAVOR_EARNED_*` |
| /leaderboard | `gamification/user/leaderboard.py` | Agregar intro de Lucien |
| /vip, /premium, /mapa | `user/conversion.py` | Usar `Lucien.CONVERSION_*` |

## Handlers FALTANTES

| Comando | Archivo a crear | Mensajes disponibles |
|---------|-----------------|---------------------|
| /favores | `gamification/user/favors.py` | `Lucien.FAVORS_*` (12 mensajes) |
| /tienda | `gamification/user/shop.py` | `Lucien.CABINET_*` (10 mensajes) |

## Inventario Vacío

**CRÍTICO:** El Gabinete tiene 0 items cargados de 17 especificados.

| Categoría | Items | Código |
|-----------|-------|-------|
| Efímeros | 5 | eph_001 a eph_005 |
| Distintivos | 5 | dist_001 a dist_005 |
| Llaves | 4 | key_001 a key_004 |
| Reliquias | 3 | rel_001 a rel_003 |

**Acción:** Crear `scripts/seed_cabinet_items.py`

---

# ACCIONES RECOMENDADAS (ACTUALIZADO 2026-01-01)

## ✅ COMPLETADAS - Acciones Anteriores

Todas las acciones de prioridad ALTA documentadas anteriormente han sido completadas:

| Acción | Estado Anterior | Estado Actual |
|--------|-----------------|---------------|
| 1. Reescribir /start con onboarding | ⏳ Pendiente | ✅ Completado |
| 2. Cargar inventario del Gabinete | ⏳ Pendiente | ✅ Completado (16 items) |
| 3. Crear handler /favores | ⏳ Pendiente | ✅ Completado |
| 4. Crear handler /tienda | ⏳ Pendiente | ✅ Completado |
| 5. Integrar comandos en menús | ⏳ Pendiente | ✅ Completado |

---

## 🔴 PRIORIDAD CRÍTICA - Corregir Nombres de Métodos

**Ver documento completo:** `docs/dev/gamification/ERRORES_CRITICOS_NOMBRES_METODOS.md`

### 1. Corregir `bot/handlers/user/start.py` (Línea 138)

**Error:**
```python
pending_missions = await gamification.mission.get_pending_missions(user_id)
```

**Corrección:**
```python
pending_missions = await gamification.mission.get_available_missions(user_id)
```

---

### 2. Corregir `bot/gamification/handlers/user/missions.py` (Líneas 262, 332)

**Error:**
```python
mission = await gamification.mission.get_mission(mission_id)
```

**Corrección:**
```python
mission = await gamification.mission.get_mission_by_id(mission_id)
```

---

### 3. Corregir `bot/gamification/handlers/user/missions.py` (Línea 263)

**Error:**
```python
user_mission = await gamification.mission.get_user_mission(user_id, mission_id)
```

**Corrección:**
```python
user_missions = await gamification.mission.get_user_missions(user_id=user_id)
user_mission = next((m for m in user_missions if m.mission_id == mission_id), None)
```

---

### 4. Corregir `bot/gamification/handlers/user/missions.py` (Línea 349)

**Error:**
```python
streak_info = await gamification.daily_gift.get_streak_info(user_id)
```

**Corrección:**
```python
streak_status = await gamification.daily_gift.get_daily_gift_status(user_id)
current_streak = streak_status.get("current_streak", 0)
```

## Prioridad MEDIA

### 6. Actualizar /perfil
**Archivo:** `bot/gamification/handlers/user/profile.py`
**Cambios:** Usar `Lucien.PROFILE_COMMENT_LEVEL_*`

### 7. Migración a decimales (opcional)
**Nota:** Solo si se necesitan valores como 0.1, 0.5
**Archivo:** Alembic migration

## Prioridad BAJA

### 8. Actualizar otros handlers con voz Lucien
- `/daily_gift`: Usar `Lucien.FAVOR_NOTIFICATION_*`
- `/leaderboard`: Agregar intro de Lucien

---

# MÉTRICAS DE VALIDACIÓN

## Porcentaje de Implementación por Fase

| Fase | Especificación | Implementación | Gap |
|------|---------------|----------------|-----|
| F0 - Fundamentos | 100% | 85% | 15% |
| F1 - Voz Lucien | 100% | 70% | 30% |
| F2 - Economía | 100% | 90% | 10% |
| F3 - Arquetipos | 100% | 100% | 0% |
| F4 - Gabinete | 100% | 75% | 25% |
| F5 - Narrativa | 100% | 95% | 5% |
| F6 - Conversión | 100% | 95% | 5% |
| **TOTAL** | **100%** | **87%** | **13%** |

## Porcentaje por Capa

| Capa | Implementación | Notas |
|------|----------------|-------|
| Database (Modelos) | 100% | Completo |
| Services (Lógica) | 95% | Muy completo |
| Handlers Admin | 90% | Bastante completo |
| Handlers User | 70% | **Área de trabajo principal** |
| Messages (Lucien) | 100% | ✅ **COMPLETO** |
| Menús/Integración | 40% | **Área de trabajo principal** |

---

# ESTRUCTURA DE MENÚS PROPUESTA

## Menú Principal (Free)

```
┌─────────────────────────────────────┐
│ [Contexto dinámico de Lucien]      │
│ ¿En qué puedo asistirle?           │
├─────────────────────────────────────┤
│ [📖 La Historia]   story:start     │
│ [🎭 Mi Perfil]     profile:view     │
│ [🗄️ El Gabinete]   cabinet:browse   │
│ [📋 Mis Encargos]  user:missions    │
│ [💫 Mis Favores]   favors:view       │
│ [🔑 La Llave]      conversion:vip   │
└─────────────────────────────────────┘
```

## Menú Principal (VIP)

```
┌─────────────────────────────────────┐
│ El Diván está a su disposición.    │
├─────────────────────────────────────┤
│ [📖 Continuar]     story:continue   │
│ [🎭 Mi Perfil]     profile:view     │
│ [🗄️ El Gabinete]   cabinet:browse   │
│ [📋 Mis Encargos]  user:missions    │
│ [💫 Mis Favores]   favors:view       │
│ [💎 Premium]       conversion:premium│
│ [🗺️ Mapa del Deseo] conversion:mapa │
└─────────────────────────────────────┘
```

---

# NOTAS ADICIONALES

## Sobre el Backend

El backend está **excepcionalmente bien implementado**:
- 30+ servicios con DI + Lazy Loading
- 16+ modelos de BD bien relacionados
- Enums completos
- Orquestadores para flujos complejos

## Sobre los Mensajes de Lucien

**✅ COMPLETO** - El archivo `bot/utils/lucien_messages.py` tiene 870 líneas con:
- 10 categorías de mensajes
- 80+ mensajes individuales
- Todos los placeholders definidos
- Método `format()` para uso fácil
- Alias `Lucien` para acceso corto

## Sobre el Onboarding

Existe onboarding obligatorio de 5 pasos (`onboarding.py`):
- Detección de arquetipo integrada
- 30 besitos de bienvenida
- Tutorial de mecánicas del sistema
- Debe integrarse con /start

---

*Fin del documento de validación*

**Próxima actualización:** Después de implementar acciones de prioridad ALTA
