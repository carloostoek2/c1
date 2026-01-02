# TRACKING: FASE 4 - EL GABINETE

**Inicio:** 2024-12-30
**Estado:** En Progreso
**Progreso:** 0/9 tareas completadas (0%)

---

## RESUMEN DE TAREAS

| Tarea | Descripcion | Estado |
|-------|-------------|--------|
| F4.1 | Modelo de Datos y Migraciones | Pendiente |
| F4.2 | Catalogo de Items (Seed Data) | Pendiente |
| F4.3 | Servicio del Gabinete | Pendiente |
| F4.4 | Sistema de Descuentos | Pendiente |
| F4.5 | Items Limitados y Temporales | Pendiente |
| F4.6 | Handlers de Usuario (Navegacion y Compra) | Pendiente |
| F4.7 | Inventario y Uso de Items | Pendiente |
| F4.8 | Recomendaciones y Notificaciones | Pendiente |
| F4.9 | Comandos de Admin | Pendiente |

---

## CONTEXTO TECNICO

### Estructura Existente
El proyecto ya tiene un modulo `bot/shop/` con:
- **ItemCategory**: Categorias de productos
- **ShopItem**: Items con precio en besitos, stock, rareza, etc.
- **UserInventory**: Inventario del usuario (Mochila)
- **UserInventoryItem**: Items poseidos por el usuario
- **ItemPurchase**: Historial de compras

### Adaptacion Requerida
La Fase 4 extiende este sistema con:
1. Categorias especificas del Gabinete (Efimeros, Distintivos, Llaves, Reliquias)
2. Items narrativos con descripciones de Lucien
3. Sistema de niveles de acceso por categoria
4. Descuentos acumulativos
5. Items ocultos para usuarios de alto nivel
6. Integracion con sistema de arquetipos (Fase 3)

### Moneda
- **Favores**: Equivalentes a "besitos" en el sistema de gamificacion
- Conversion: 1 Favor = X besitos (configurable)

---

## DETALLE POR TAREA

### F4.1 - Modelo de Datos y Migraciones   (COMPLETADA)

**Objetivo:** Extender modelos existentes y crear nuevos para el Gabinete.

**Subtareas:**
- [ ] Crear enum `GabineteCategory` (ephemeral, distinctive, keys, relics, secret)
- [ ] Crear enum `ItemVisibility` (public, confidants_only, guardians_only)
- [ ] Agregar campos a `ShopItem`:
  - `gabinete_category`: Categoria del Gabinete
  - `lucien_description`: Descripcion narrativa de Lucien
  - `purchase_message`: Mensaje al comprar
  - `min_level_to_view`: Nivel minimo para ver el item
  - `min_level_to_buy`: Nivel minimo para comprar
  - `visibility`: Visibilidad del item
  - `duration_hours`: Duracion para items temporales
  - `content_type`: Tipo de contenido (audio, text, image, badge, etc.)
  - `content_data`: Datos del contenido (JSON)
- [ ] Crear tabla `UserDiscount`:
  - `user_id`: FK a usuario
  - `discount_source`: Fuente del descuento (level, badge, relic)
  - `discount_percent`: Porcentaje de descuento
  - `expires_at`: Expiracion (nullable)
- [ ] Crear tabla `GabineteNotification`:
  - `user_id`: FK a usuario
  - `item_id`: FK a ShopItem
  - `notification_type`: Tipo (new_item, low_stock, expiring)
  - `sent_at`: Timestamp
  - `read_at`: Timestamp (nullable)
- [ ] Crear migracion Alembic (019_add_gabinete_features.py)
- [ ] Tests de modelos

**Archivos a crear/modificar:**
- `bot/shop/database/models.py` (modificar)
- `bot/shop/database/enums.py` (crear)
- `alembic/versions/019_add_gabinete_features.py` (crear)

---

### F4.2 - Catalogo de Items (Seed Data) (COMOLETADA)

**Objetivo:** Poblar la base de datos con los 20+ items definidos en fase-4.md.

**Subtareas:**
- [ ] Crear categorias del Gabinete:
  - Efimeros (ephemeral) - Emoji: ⚡
  - Distintivos (distinctive) - Emoji: 🎖
  - Llaves (keys) - Emoji: 🔑
  - Reliquias (relics) - Emoji: 💎
- [ ] Crear items Efimeros (5 items):
  - eph_001: Sello del Dia (1 Favor)
  - eph_002: Susurro Efimero (3 Favores)
  - eph_003: Pase de Prioridad (5 Favores)
  - eph_004: Vistazo al Sensorium (15 Favores)
  - eph_005: Confesion Nocturna (8 Favores)
- [ ] Crear items Distintivos (6 items):
  - dist_001: Sello del Visitante (2 Favores)
  - dist_002: Insignia del Observador (5 Favores)
  - dist_003: Marca del Evaluado (8 Favores)
  - dist_004: Emblema del Reconocido (12 Favores)
  - dist_005: Marca del Confidente (25 Favores)
  - dist_006: Corona del Guardian (50 Favores)
- [ ] Crear items Llaves (5 items):
  - key_001: Llave del Fragmento I (10 Favores)
  - key_002: Llave del Fragmento II (12 Favores)
  - key_003: Llave del Fragmento III (15 Favores)
  - key_004: Llave del Archivo Oculto (20 Favores)
  - key_005: Llave de la Primera Vez (18 Favores)
- [ ] Crear items Reliquias (5 items):
  - rel_001: El Primer Secreto (30 Favores)
  - rel_002: Fragmento del Espejo (40 Favores)
  - rel_003: La Carta No Enviada (50 Favores)
  - rel_004: Cristal de Medianoche (45 Favores)
  - rel_005: Llave Maestra del Gabinete (75 Favores)
- [ ] Crear items Ocultos (solo Confidentes+):
  - secret_001: Susurro de Lucien (20 Favores)
  - secret_002: Las Coordenadas (35 Favores)
- [ ] Crear script de seed: `scripts/seed_gabinete.py`
- [ ] Verificar seed con tests

**Archivos a crear:**
- `scripts/seed_gabinete.py`
- `bot/shop/data/gabinete_items.json` (opcional, datos en JSON)

---

### F4.3 - Servicio del Gabinete (COMPLETADA)

**Objetivo:** Servicio core para gestionar el Gabinete con logica de negocio.

**Subtareas:**
- [ ] Crear `GabineteService`:
  - `get_categories()` - Listar categorias visibles para usuario
  - `get_items_by_category()` - Items de una categoria
  - `get_item_detail()` - Detalle de un item
  - `can_view_item()` - Verificar si puede ver item
  - `can_purchase_item()` - Verificar si puede comprar
  - `purchase_item()` - Procesar compra (atomica)
  - `get_user_inventory()` - Inventario del usuario
  - `use_item()` - Usar item consumible
  - `get_user_discounts()` - Descuentos activos del usuario
- [ ] Integrar con `GamificationContainer`
- [ ] Transacciones atomicas (compra = descuento besitos + agregar item)
- [ ] Logging de compras para auditoria
- [ ] Tests unitarios

**Archivos a crear:**
- `bot/shop/services/gabinete.py`
- `tests/shop/test_gabinete_service.py`

---

### F4.4 - Sistema de Descuentos (COMPLETADA)

**Objetivo:** Implementar descuentos acumulativos por nivel, distintivos y reliquias.

**Subtareas:**
- [ ] Crear `DiscountService`:
  - `calculate_total_discount()` - Calculo con todas las fuentes
  - `get_level_discount()` - Descuento por nivel (0-20%)
  - `get_badge_discount()` - Descuento por distintivos (0-15%)
  - `get_relic_discount()` - Descuento por reliquias (0-20%)
  - `apply_discount()` - Aplicar descuento a precio
  - `get_discount_breakdown()` - Desglose para UI
- [ ] Implementar reglas de descuento:
  - Nivel 1-3: 0%
  - Nivel 4: 5%
  - Nivel 5: 10%
  - Nivel 6: 15%
  - Nivel 7: 20%
  - Emblema del Reconocido: +5%
  - Marca del Confidente: +10%
  - Corona del Guardian: +15%
  - El Primer Secreto: +3%
  - Llave Maestra: +20%
- [ ] Limite maximo: 50%
- [ ] Redondeo a 1 decimal
- [ ] Tests unitarios

**Archivos a crear:**
- `bot/shop/services/discount.py`
- `tests/shop/test_discount_service.py`

---

### F4.5 - Items Limitados y Temporales (COMPLETADA)

**Objetivo:** Soporte para items con stock limitado y disponibilidad temporal.

**Subtareas:**
- [ ] Extender `ShopItem`:
  - `is_limited`: Flag de stock limitado
  - `total_stock`: Stock inicial
  - `remaining_stock`: Stock actual
  - `limit_per_user`: Limite por usuario
  - `available_from`: Fecha inicio disponibilidad
  - `available_until`: Fecha fin disponibilidad
  - `event_name`: Nombre del evento (opcional)
- [ ] Crear `LimitedItemService`:
  - `is_item_available()` - Verificar disponibilidad
  - `check_user_limit()` - Verificar limite por usuario
  - `reserve_stock()` - Reservar stock (atomico)
  - `release_stock()` - Liberar stock (si falla compra)
  - `get_remaining_time()` - Tiempo restante para items temporales
- [ ] Background task para expirar items temporales
- [ ] Tests unitarios

**Archivos a crear/modificar:**
- `bot/shop/services/limited_items.py`
- `bot/shop/database/models.py` (agregar campos)
- `tests/shop/test_limited_items.py`

---

### F4.6 - Handlers de Usuario (Navegacion y Compra) (COMPLETADA)

**Objetivo:** Flujos de usuario para navegar y comprar en el Gabinete.

**Subtareas:**
- [ ] Handler `/gabinete` o boton "El Gabinete":
  - Mensaje de bienvenida (primera vez vs. recurrente)
  - Mostrar Favores disponibles
  - Mostrar nivel actual
  - Botones de categorias
- [ ] Handler navegacion por categoria:
  - Lista de items con precios
  - Items bloqueados (por nivel) con indicacion visual
  - Paginacion si hay muchos items
- [ ] Handler detalle de item:
  - Descripcion de Lucien
  - Precio (original y con descuento si aplica)
  - Estado de stock (si es limitado)
  - Boton Adquirir / Ver requisitos
- [ ] Handler proceso de compra:
  - Confirmacion con desglose
  - Mensaje post-compra
  - Opciones: Usar ahora / Ver inventario / Seguir explorando
- [ ] Estados FSM para flujos multi-paso
- [ ] Keyboards dinamicos
- [ ] Tests E2E

**Archivos a crear:**
- `bot/shop/handlers/user/gabinete.py`
- `bot/shop/states/gabinete.py`
- `tests/shop/test_gabinete_handlers.py`

---

### F4.7 - Inventario y Uso de Items (COMPLETADA)

**Objetivo:** Visualizacion de inventario y uso de items consumibles.

**Subtareas:**
- [ ] Handler "Mi Inventario":
  - Seccion Items Activos (por usar)
  - Seccion Distintivos (badges)
  - Seccion Coleccionables (reliquias)
  - Contenido desbloqueado (llaves usadas)
- [ ] Handler uso de item consumible:
  - Confirmacion de uso
  - Advertencia si es irreversible
  - Mostrar contenido desbloqueado
  - Mensaje post-uso
- [ ] Logica de items especiales:
  - Efimeros: desaparecen al usar
  - Distintivos: permanentes, afectan perfil
  - Llaves: desbloquean contenido narrativo
  - Reliquias: permanentes con beneficios
- [ ] Integracion con sistema de contenido:
  - Audio (file_id de Telegram)
  - Texto (fragmentos narrativos)
  - Imagenes (behind-the-scenes)
- [ ] Tests E2E

**Archivos a crear:**
- `bot/shop/handlers/user/inventory.py`
- `bot/shop/services/item_effects.py`
- `tests/shop/test_inventory_handlers.py`

---

### F4.8 - Recomendaciones y Notificaciones (COMPLETADA)

**Objetivo:** Sistema de recomendaciones personalizadas y notificaciones proactivas.

**Subtareas:**
- [ ] Crear `RecommendationService`:
  - `get_recommendation_for_archetype()` - Recomendacion por arquetipo
  - `get_recommendation_from_history()` - Recomendacion por historial
  - `get_personalized_message()` - Mensaje de Lucien personalizado
- [ ] Mapeo arquetipo -> item recomendado:
  - EXPLORER -> Llaves (contenido oculto)
  - DIRECT -> Efimeros (uso inmediato)
  - ROMANTIC -> Reliquias emotivas
  - ANALYTICAL -> Items informativos
  - PERSISTENT -> Distintivos
  - PATIENT -> Reliquias de largo plazo
- [ ] Crear `GabineteNotificationService`:
  - `notify_new_item()` - Item nuevo disponible
  - `notify_low_stock()` - Stock bajo
  - `notify_expiring_soon()` - Item por terminar
  - `get_pending_notifications()` - Notificaciones pendientes
  - `mark_as_read()` - Marcar como leida
- [ ] Background task para enviar notificaciones
- [ ] Respetar preferencias de notificacion del usuario
- [ ] Tests unitarios

**Archivos a crear:**
- `bot/shop/services/recommendations.py`
- `bot/shop/services/gabinete_notifications.py`
- `tests/shop/test_recommendations.py`

---

### F4.9 - Comandos de Admin

**Objetivo:** Herramientas de administracion para gestionar el Gabinete.

**Subtareas:**
- [ ] `/admin_shop_add` - Wizard para agregar item:
  - Seleccionar categoria
  - Nombre y descripcion
  - Precio y nivel requerido
  - Tipo y limites
- [ ] `/admin_shop_edit <item_id>` - Editar item existente
- [ ] `/admin_shop_disable <item_id>` - Desactivar item
- [ ] `/admin_shop_stock <item_id> <cantidad>` - Ajustar stock
- [ ] `/admin_shop_stats` - Estadisticas:
  - Items mas vendidos (30 dias)
  - Total Favores gastados
  - Categoria mas popular
  - Items sin ventas
  - Usuarios con mas compras
- [ ] `/admin_shop_promo <item_id> <descuento%> <horas>` - Crear promocion
- [ ] Tests E2E

**Archivos a crear:**
- `bot/shop/handlers/admin/gabinete_admin.py`
- `bot/shop/states/admin_gabinete.py`
- `tests/shop/test_gabinete_admin.py`

---

## DEPENDENCIAS ENTRE TAREAS

```
F4.1 (Modelos)
  ↓
F4.2 (Seed Data)
  ↓
F4.3 (Servicio Core) ← F4.4 (Descuentos)
  ↓                      ↓
F4.5 (Items Limitados) ──┘
  ↓
F4.6 (Handlers Usuario)
  ↓
F4.7 (Inventario) ← F4.8 (Recomendaciones)
  ↓
F4.9 (Admin)
```

---

## INTEGRACIONES CON OTRAS FASES

### Fase 2 - Sistema de Favores
- Usar `spend_favors()` para deducir Favores al comprar
- Validar saldo antes de permitir compra

### Fase 3 - Arquetipos
- Usar arquetipo para recomendaciones personalizadas
- Adaptar mensajes de Lucien segun arquetipo

### Fase 5 - Contenido Narrativo (Futura)
- Items tipo "Llave" desbloquean fragmentos narrativos
- Preparar integracion con sistema de fragmentos

---

## CRITERIOS DE ACEPTACION

- [ ] Minimo 20 items creados y funcionando
- [ ] 4 categorias con niveles de acceso
- [ ] Navegacion fluida por categorias
- [ ] Proceso de compra con confirmacion
- [ ] Inventario muestra items comprados
- [ ] Items consumibles funcionan correctamente
- [ ] Descuentos se aplican y muestran correctamente
- [ ] Items limitados muestran stock
- [ ] Items temporales muestran tiempo restante
- [ ] Items ocultos solo para Confidentes+
- [ ] Recomendaciones por arquetipo
- [ ] Notificaciones proactivas
- [ ] Comandos admin funcionales
- [ ] Tests E2E con >85% coverage

---

## NOTAS TECNICAS

1. **Transacciones atomicas:** Compras deben ser atomicas (Favores - Item en una transaccion)
2. **Cache:** Considerar cachear catalogo, invalidar al modificar
3. **Imagenes:** Items pueden tener imagen opcional (file_id de Telegram)
4. **Contenido:** Items tipo Llave vinculan a fragmentos narrativos (Fase 5)
5. **Auditoria:** Log de todas las compras para analisis
6. **Performance:** Paginacion para listas largas de items

---

## ARCHIVOS DE REFERENCIA

- `docs/dev/gamification/fase-4.md` - Especificacion completa
- `bot/shop/database/models.py` - Modelos existentes
- `bot/gamification/services/archetype_detection.py` - Arquetipos
- `bot/gamification/services/user_gamification.py` - Sistema de Favores/Besitos

---

## COMMITS REALIZADOS

*Se actualizara conforme se completen tareas*

---

**Ultima actualizacion:** 2024-12-30
**Estado actual:** En planificacion
