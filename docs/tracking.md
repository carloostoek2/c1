# 🎮 TRACKING: Implementación Módulo Gamificación

**Inicio:** Diciembre 2024  
**Estado General:** 🟡 En Progreso  
**Progreso Total:** 0/30 tareas (0%)

---

## 📊 PROGRESO POR FASE

### **FASE 1: Base del Sistema (6 tareas)** 🔴 No iniciado
- [ ] G1.1 - Estructura de directorios del módulo
- [ ] G1.2 - Modelos de base de datos (13 modelos)
- [ ] G1.3 - Migraciones Alembic
- [ ] G1.4 - Enums y tipos personalizados
- [ ] G1.5 - Configuración del módulo
- [ ] G1.6 - Tests unitarios modelos

**Estimado:** 1-2 semanas  
**Progreso:** 0/6 (0%)

---

### **FASE 2: Servicios Core (7 tareas)** 🔴 No iniciado
- [ ] G2.1 - ReactionService
- [ ] G2.2 - BesitoService (con atomic updates)
- [ ] G2.3 - LevelService
- [ ] G2.4 - MissionService
- [ ] G2.5 - RewardService
- [ ] G2.6 - UserGamificationService
- [ ] G2.7 - GamificationContainer (DI)

**Estimado:** 2-3 semanas  
**Progreso:** 0/7 (0%)

---

### **FASE 3: Orchestrators y Validación (4 tareas)** 🔴 No iniciado
- [ ] G3.1 - Validadores (criterios, metadata)
- [ ] G3.2 - MissionOrchestrator
- [ ] G3.3 - RewardOrchestrator
- [ ] G3.4 - ConfigurationOrchestrator (coordina)

**Estimado:** 1-2 semanas  
**Progreso:** 0/4 (0%)

---

### **FASE 4: Handlers y FSM (5 tareas)** 🔴 No iniciado
- [ ] G4.1 - Estados FSM (Wizards)
- [ ] G4.2 - Handler menú admin gamification
- [ ] G4.3 - Wizard crear misión
- [ ] G4.4 - Wizard crear recompensa
- [ ] G4.5 - Handlers usuarios (perfil, misiones, leaderboard)

**Estimado:** 2-3 semanas  
**Progreso:** 0/5 (0%)

---

### **FASE 5: Background Jobs y Hooks (3 tareas)** 🔴 No iniciado
- [ ] G5.1 - Background job: auto-progression
- [ ] G5.2 - Background job: expiración rachas
- [ ] G5.3 - Hooks en sistema de reacciones existente

**Estimado:** 1 semana  
**Progreso:** 0/3 (0%)

---

### **FASE 6: Features Avanzadas (3 tareas)** 🔴 No iniciado
- [ ] G6.1 - Sistema de plantillas predefinidas
- [ ] G6.2 - GamificationStatsService
- [ ] G6.3 - Sistema de notificaciones

**Estimado:** 1-2 semanas  
**Progreso:** 0/3 (0%)

---

### **FASE 7: Testing y Documentación (2 tareas)** 🔴 No iniciado
- [ ] G7.1 - Tests E2E (flujos completos)
- [ ] G7.2 - Documentación (GAMIFICATION.md, API.md)

**Estimado:** 1 semana  
**Progreso:** 0/2 (0%)

---

## 🎯 PRÓXIMA TAREA

**Tarea actual:** G1.1 - Estructura de directorios del módulo  
**Prompt generado:** ✅ Listo para ejecutar  
**Bloqueadores:** Ninguno

---

## 📝 NOTAS DE IMPLEMENTACIÓN

### Decisiones Tomadas
- ✅ Módulo separado en `bot/gamification/`
- ✅ Shared container entre módulos
- ✅ Atomic updates para besitos
- ✅ Validadores con dataclasses para JSON
- ✅ Soft-delete para misiones/recompensas

### Pendientes de Decisión
- ⏸️ Timezone para rachas (recomendado: UTC)
- ⏸️ Límite máximo de besitos por usuario
- ⏸️ Roles de admin (GAMIFICATION_ADMIN vs SUPER_ADMIN)

---

## 🐛 ISSUES ENCONTRADOS

_Ninguno por ahora_

---

## 📊 MÉTRICAS

- **Commits realizados:** 0
- **Tests pasando:** 0/0
- **Cobertura de código:** N/A
- **Tiempo invertido:** 0 horas

---

## 🏪 MÓDULO TIENDA (SHOP) - COMPLETADO

### Estado: ✅ Implementado

**Fecha de implementación:** Diciembre 2024

### Componentes Implementados:

#### 1. Base de Datos
- [x] `bot/shop/database/models.py` - 5 modelos SQLAlchemy:
  - `ItemCategory`: Categorías de productos
  - `ShopItem`: Productos de la tienda
  - `UserInventory`: Inventario del usuario (Mochila)
  - `UserInventoryItem`: Items que posee el usuario
  - `ItemPurchase`: Historial de compras

- [x] `bot/shop/database/enums.py` - Enums y TypedDicts:
  - `ItemType`: narrative, digital, consumable, cosmetic
  - `ItemRarity`: common, uncommon, rare, epic, legendary
  - `PurchaseStatus`: completed, refunded, cancelled
  - TypedDicts para metadata por tipo

- [x] `alembic/versions/011_add_shop_module.py` - Migración completa

#### 2. Servicios
- [x] `bot/shop/services/shop.py` - ShopService:
  - CRUD de categorías y productos
  - Validación de compras
  - Procesamiento de transacciones
  - Estadísticas de ventas

- [x] `bot/shop/services/inventory.py` - InventoryService:
  - Gestión del inventario personal
  - Verificación de posesión de items
  - Uso de items consumibles
  - Equipar/desequipar cosméticos

- [x] `bot/shop/services/container.py` - ShopContainer (DI)

#### 3. Handlers
- [x] `bot/shop/handlers/user/shop.py`:
  - /tienda, /shop, /store commands
  - Navegación por categorías
  - Detalle de productos
  - Flujo de compra

- [x] `bot/shop/handlers/user/backpack.py`:
  - /mochila, /backpack, /inventory commands
  - Ver items por tipo
  - Usar consumibles
  - Equipar/desequipar cosméticos

- [x] `bot/shop/handlers/admin/shop_config.py`:
  - Gestionar categorías
  - CRUD de productos
  - Estadísticas de ventas
  - Otorgar items a usuarios

#### 4. Estados FSM
- [x] `bot/shop/states/admin.py`:
  - CategoryCreationStates
  - CategoryEditStates
  - ItemCreationStates
  - ItemEditStates
  - NarrativeItemConfigStates

#### 5. Integración con Narrativa
- [x] `RequirementType.ITEM` agregado a enums de narrativa
- [x] `_check_item_ownership()` en RequirementsService
- [x] Desbloqueo automático de fragmentos al poseer items

#### 6. Tests E2E
- [x] `tests/shop/test_shop_e2e.py` - 25+ tests:
  - Tests de categorías
  - Tests de productos
  - Tests de compra
  - Tests de inventario
  - Tests de consumibles
  - Tests de cosméticos
  - Tests de estadísticas
  - Tests de reembolso
  - Tests de stock limitado

### Flujo de Usuario:
```
1. Usuario gana besitos (gamificación)
2. Ve fragmento bloqueado → mensaje "Necesitas artefacto X"
3. Accede a /tienda → ve productos
4. Compra con besitos → item en mochila
5. Regresa a fragmento → acceso desbloqueado
```

### Funcionalidades:
- Catálogo de productos por categorías
- 4 tipos de items: narrativos, digitales, consumibles, cosméticos
- 5 niveles de rareza con indicadores visuales
- Stock limitado y máximo por usuario
- Requisito VIP para items exclusivos
- Productos destacados
- Uso de consumibles con efectos
- Equipar/desequipar cosméticos
- Item favorito para perfil
- Historial de compras
- Reembolsos
- Otorgamiento de items por admin
- Estadísticas de ventas

---

## 🎭 FASE 0 - FUNDAMENTOS NARRATIVOS

### Estado: 🟡 En Progreso

### F0.1 Sistema de Economía "Favores" ✅
- [x] Modelo de BD actualizado: "besitos" → "favores" (soporte decimal)
- [x] Tabla de configuración con valores de ganancia
- [x] Migración de datos existentes
- [x] Tests de cálculo de favores

### F0.2 Mensajes de Lucien ✅
- [x] Archivo `bot/utils/lucien_messages.py` creado
- [x] 50+ mensajes definidos con placeholders
- [x] Todos los mensajes usan "usted" formal
- [x] Sin emojis en texto (solo en botones)
- [x] Categorías: Onboarding, Favores, Niveles, Errores, Gabinete, Misiones, Arquetipos, Retención, Conversión

### F0.3 Sistema de Arquetipos Expandido ✅
- [x] Enum `ArchetypeType` con 6 arquetipos: EXPLORER, DIRECT, ROMANTIC, ANALYTICAL, PERSISTENT, PATIENT
- [x] Modelo de usuario con campos de arquetipo
- [x] Arquetipos legacy (IMPULSIVE, CONTEMPLATIVE, SILENT) mantenidos por compatibilidad

### F0.4 Gabinete (Tienda) ✅
- [x] Ver sección "MÓDULO TIENDA (SHOP) - COMPLETADO"

### F0.5 Estructura de Contenido Narrativo ✅ **COMPLETADO HOY**
- [x] Enums `SpeakerType` y `MediaType` agregados a narrativa
- [x] Script `scripts/seed_chapters_1_3.py` creado
- [x] **Capítulo 1: Bienvenida** (5 fragmentos)
  - 1.1 Bienvenida de Diana (entry point)
  - 1.2 Lucien y el Primer Desafío
  - 1.3A Respuesta Impulsiva (rama arquetipo)
  - 1.3B Respuesta Contemplativa (rama arquetipo)
  - 1.4 La Primera Pista (ending)
- [x] **Capítulo 2: Observación** (4 fragmentos)
  - 2.1 El Regreso Observado
  - 2.2 Desafío de Observación
  - 2.3 Progreso de Observación
  - 2.4 Reconocimiento de Diana
- [x] **Capítulo 3: Perfil de Deseo** (4 fragmentos)
  - 3.1 La Prueba Final
  - 3.2 La Evaluación Mutua
  - 3.3 Evaluación de Diana
  - 3.4 La Invitación - Llave del Diván (conversion point)
- [x] Decisiones con efectos de arquetipo configuradas
- [x] Requisitos de progresión por capítulo (CHAPTER_COMPLETE)
- [x] Metadata de rewards (pistas, items, niveles)
- [x] Seed ejecutado y validado en BD

**Componentes Creados F0.5:**
- `bot/narrative/database/enums.py` → SpeakerType, MediaType
- `bot/narrative/services/fragment.py` → extra_metadata param
- `scripts/seed_chapters_1_3.py` → 13 fragmentos narrativos

---

## 🎭 FASE 1 - LA VOZ DE LUCIEN

### Estado: 🟡 En Progreso

### F1.1 Reescribir Comando /start ✅ **COMPLETADO**
- [x] Campo `last_activity` agregado al modelo User
- [x] Campo `is_new_user` para detectar usuarios nuevos
- [x] Migración 015_add_user_activity_tracking.py creada
- [x] Nuevos mensajes de Lucien para onboarding agregados
- [x] **Flujo A: Usuario nuevo** (2 mensajes + delay dramático)
  - Presentación de Lucien
  - Advertencia de observación
  - Botones: "Entendido, continuar" / "¿Quién es Diana?"
  - Respuesta a "¿Quién es Diana?"
  - Registro completado con status inicial
- [x] **Flujo B: Usuario que regresa (< 7 días)**
  - Bienvenida corta con días de ausencia
  - Menú principal
- [x] **Flujo C: Usuario que regresa (7-14 días)**
  - Drama sobre la ausencia
  - Status con racha
  - Menú principal
- [x] **Flujo D: Usuario que regresa (> 14 días)**
  - Drama intenso
  - Oferta de contenido nuevo
  - Botones: "Ver qué hay de nuevo" / "Menú principal"
- [x] **Flujo E: Usuario VIP**
  - Bienvenida con arquetipo
  - Status VIP (días en el Diván)
  - Menú VIP con "Contenido Nuevo"
- [x] Deep link para tokens VIP funcional
- [x] Menú de Lucien sin emojis en texto (solo en botones)

**Componentes Modificados F1.1:**
- `bot/database/models.py` → User.last_activity, User.is_new_user
- `bot/utils/lucien_messages.py` → 10 nuevos mensajes de onboarding
- `bot/handlers/user/start.py` → Reescritura completa con 5 flujos
- `alembic/versions/015_add_user_activity_tracking.py` → Nueva migración

### F1.2 Reescribir Menú Principal ✅ **COMPLETADO**
- [x] Menú diferenciado Free/VIP
- [x] Callbacks actualizados:
  - `story:start` / `story:continue`
  - `profile:view`
  - `cabinet:browse`
  - `missions:list`
  - `favors:balance`
  - `content:new` (VIP)
  - `map:view` (VIP)
- [x] Mensajes de contexto dinámicos según estado:
  - Misión diaria pendiente
  - Favores acumulados (>20)
  - Racha activa 7+ días
  - Default

### F1.3 Reescribir Vista de Perfil ✅ **COMPLETADO**
- [x] Vista de perfil con secciones:
  - PROTOCOLO DE ACCESO (nivel, progreso, favores)
  - Clasificación de arquetipo con descripción
  - ACTIVIDAD (días, racha, capítulos)
  - DISTINCIONES (badges)
- [x] Barra de progreso visual: `▓▓▓▓▓▒▒▒▒▒`
- [x] Comentarios de Lucien según nivel:
  - 1-2: "Aún está siendo evaluado..."
  - 3-4: "Ha demostrado... potencial..."
  - 5-6: "Diana lo tiene en cuenta..."
  - 7: "Pocos llegan aquí..."
- [x] Botones: "Ver todos mis distintivos" / "Volver al menú"

**Componentes Modificados F1.2/F1.3:**
- `bot/handlers/user/start.py` → Callbacks de menú + vista de perfil
- `bot/utils/lucien_messages.py` → Mensajes de contexto y perfil

### F1.4 Reescribir Gabinete (Tienda) ✅ **COMPLETADO**
- [x] Vista principal con categorías de Lucien:
  - Efímeros (consumibles)
  - Distintivos (cosméticos)
  - Llaves (artefactos narrativos)
  - Reliquias (contenido digital)
- [x] Vista de categoría con lista de items
- [x] Detalle de item con descripción de Lucien
- [x] Flujo de compra con confirmación:
  - Paso 1: Confirmación de compra
  - Paso 2A: Compra exitosa
  - Paso 2B: Favores insuficientes
- [x] Mensajes actualizados:
  - CABINET_WELCOME, CABINET_CATEGORY_*, CABINET_CONFIRM_PURCHASE
  - CABINET_PURCHASE_SUCCESS, CABINET_INSUFFICIENT_FUNDS

### F1.5 Reescribir Misiones (Encargos) ✅ **COMPLETADO**
- [x] Vista principal con secciones:
  - PROTOCOLO DIARIO (misiones diarias)
  - ENCARGO SEMANAL (misiones semanales)
  - EVALUACIONES ESPECIALES (narrativas)
- [x] Formato de progreso: `▸ Nombre\n  Descripción\n  Progreso: X/Y`
- [x] Tiempo restante formateado (Xh Xm)
- [x] Reclamar recompensa con comentario de Lucien:
  - Diaria primera vez: "El primer paso del día..."
  - Diaria racha: "Otro día, otro cumplimiento..."
  - Semanal: "Una semana de compromiso..."
  - Especial: "Esta no era una tarea común..."
- [x] Mensajes actualizados:
  - MISSIONS_HEADER, MISSIONS_*_HEADER
  - MISSION_COMPLETE con placeholder {comment}

**Componentes Modificados F1.4/F1.5:**
- `bot/shop/handlers/user/shop.py` → Reescritura completa (390 líneas)
- `bot/gamification/handlers/user/missions.py` → Reescritura completa (388 líneas)
- `bot/utils/lucien_messages.py` → +25 mensajes Gabinete y Encargos

### F1.6 Reescribir Sistema de Favores ✅ **COMPLETADO**
- [x] Nuevo handler `bot/handlers/user/favors.py`:
  - Comando `/favores` para ver balance completo
  - Callback `start:favors` para botón "Mis Favores"
  - Estadísticas de actividad (hoy/semana/mes)
  - Próximos hitos de nivel
  - Historial de transacciones (últimas 10)
  - Información de cómo ganar Favores
- [x] Comentarios según cantidad de Favores (7 rangos):
  - 0-5: "Apenas comenzando..."
  - 6-15: "Un inicio modesto..."
  - 16-35: "Progreso visible..."
  - 36-70: "Acumulación respetable..."
  - 71-120: "Una cuenta considerable..."
  - 121-200: "Impresionante moderación..."
  - 200+: "Acumula sin gastar..."
- [x] Notificaciones de ganancia:
  - Pequeña (0.1-0.5): "+X Favor. Diana lo nota."
  - Media (1-3): Con total nuevo
  - Alta (5+): "Significativo. Diana informada."
  - Hito: Con percentil de posición
- [x] Router registrado en `bot/handlers/__init__.py`

### F1.7 Mensajes de Error Unificados ✅ **COMPLETADO**
- [x] Catálogo centralizado en `bot/utils/lucien_messages.py`
- [x] Errores de sistema:
  - ERROR_GENERIC (mejorado)
  - ERROR_TIMEOUT (mejorado)
  - ERROR_MAINTENANCE (nuevo)
- [x] Errores de permisos:
  - ERROR_VIP_REQUIRED (nuevo)
  - ERROR_LEVEL_REQUIRED (nuevo, con placeholders nivel)
  - ERROR_NOT_OWNED (nuevo)
- [x] Errores de input:
  - ERROR_INVALID_INPUT (mejorado)
  - ERROR_OPTION_UNAVAILABLE (nuevo)
  - ERROR_ALREADY_DONE (nuevo)
- [x] Errores de límites:
  - ERROR_DAILY_LIMIT (nuevo)
  - ERROR_COOLDOWN (nuevo, con placeholder tiempo)

**Componentes F1.6/F1.7:**
- `bot/handlers/user/favors.py` → Nuevo (390 líneas)
- `bot/utils/lucien_messages.py` → +90 líneas (mensajes Favores + Errores)
- `bot/handlers/__init__.py` → Registro de favors_router
- `bot/handlers/user/__init__.py` → Export de favors_router

---

**Última actualización:** 2024-12-29
