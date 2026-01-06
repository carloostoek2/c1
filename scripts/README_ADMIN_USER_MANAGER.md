# Admin User Manager Script

Script administrativo para realizar operaciones de mantenimiento y debugging sobre usuarios específicos directamente en la base de datos.

## 🚀 Características

- ✅ Ver información completa del usuario
- ✅ Resetear estado narrativo
- ✅ Gestionar besitos (ver, establecer, agregar, restar)
- ✅ Resetear daily gift claims
- ✅ Resetear streaks de gamificación
- ✅ Ver historial de transacciones de besitos
- ✅ Limpiar progreso completo (reset total)

## 📋 Requisitos

- Python 3.11+
- SQLAlchemy 2.0+
- Base de datos inicializada

## 🔧 Uso

### 1. Ver Información Completa del Usuario

Muestra un resumen completo de toda la información del usuario:

```bash
python scripts/admin_user_manager.py info <user_id>
```

**Ejemplo:**
```bash
python scripts/admin_user_manager.py info 123456789
```

**Output:**
```
======================================================================
👤 INFORMACIÓN DEL USUARIO 123456789
======================================================================

📋 Información Básica:
  • Nombre: Juan Pérez
  • Username: @juanperez
  • Rol: VIP
  • Creado: 2025-01-01 10:30:00

🎮 Gamificación:
  • Total Besitos: 500
  • Besitos Ganados: 750
  • Besitos Gastados: 250
  • Nivel Actual: 3
  • Última Actualización: 2025-01-06 15:20:00

📖 Progreso Narrativo:
  • Capítulo Actual: 2
  • Fragmento Actual: scene_5a
  • Arquetipo: IMPULSIVE (confianza: 75%)
  • Total Decisiones: 12
  • Capítulos Completados: 1
  • Última Interacción: 2025-01-06 14:00:00

🎁 Regalo Diario:
  • Última Reclamación: 2025-01-06 08:00:00
  • Racha Actual: 5 días
  • Récord Racha: 10 días
  • Total Reclamaciones: 30

🔥 Rachas:
  • Racha Actual: 3
  • Récord Racha: 8
  • Última Reacción: 2025-01-06 12:00:00

======================================================================
```

### 2. Resetear Estado Narrativo

Elimina todo el progreso narrativo del usuario, incluyendo:
- Capítulo y fragmento actual
- Arquetipo detectado
- Historial de decisiones
- Capítulos completados

```bash
python scripts/admin_user_manager.py reset-narrative <user_id>
```

**Ejemplo:**
```bash
python scripts/admin_user_manager.py reset-narrative 123456789
```

**Output:**
```
🔄 Reseteando estado narrativo de Juan Pérez...
✅ Estado narrativo reseteado exitosamente.
```

### 3. Establecer Cantidad Exacta de Besitos

Establece el balance de besitos a un valor específico:

```bash
python scripts/admin_user_manager.py set-besitos <user_id> <amount>
```

**Ejemplo:**
```bash
python scripts/admin_user_manager.py set-besitos 123456789 1000
```

**Output:**
```
💰 Estableciendo besitos de Juan Pérez a 1000...
✅ Besitos establecidos a 1000.
```

**Nota:** Esta operación registra una transacción de auditoría en la tabla `besito_transactions` con el tipo `admin_adjustment`.

### 4. Agregar Besitos

Incrementa el balance de besitos del usuario:

```bash
python scripts/admin_user_manager.py add-besitos <user_id> <amount>
```

**Ejemplo:**
```bash
python scripts/admin_user_manager.py add-besitos 123456789 500
```

**Output:**
```
💰 Agregando 500 besitos a Juan Pérez...
✅ Se agregaron 500 besitos.
```

**Nota:** Esta operación registra una transacción con tipo `admin_grant`.

### 5. Restar Besitos

Decrementa el balance de besitos del usuario:

```bash
python scripts/admin_user_manager.py subtract-besitos <user_id> <amount>
```

**Ejemplo:**
```bash
python scripts/admin_user_manager.py subtract-besitos 123456789 200
```

**Output:**
```
💰 Restando 200 besitos a Juan Pérez...
✅ Se restaron 200 besitos.
```

**Nota:**
- Esta operación NO permite besitos negativos (mínimo 0)
- Registra una transacción con tipo `admin_deduction`

### 6. Resetear Daily Gift

Resetea el estado del regalo diario, permitiendo al usuario reclamarlo nuevamente:

```bash
python scripts/admin_user_manager.py reset-daily-gift <user_id>
```

**Ejemplo:**
```bash
python scripts/admin_user_manager.py reset-daily-gift 123456789
```

**Output:**
```
🎁 Reseteando daily gift de Juan Pérez...
✅ Daily gift reseteado exitosamente.
```

**Efectos:**
- Limpia `last_claim_date` (usuario puede reclamar inmediatamente)
- Resetea `current_streak` a 0

### 7. Resetear Streaks

Resetea las rachas de reacciones del usuario:

```bash
python scripts/admin_user_manager.py reset-streaks <user_id>
```

**Ejemplo:**
```bash
python scripts/admin_user_manager.py reset-streaks 123456789
```

**Output:**
```
🔥 Reseteando streaks de Juan Pérez...
✅ Streaks reseteados exitosamente.
```

**Efectos:**
- Resetea `current_streak` a 0
- Limpia `last_reaction_date`

### 8. Ver Historial de Transacciones

Muestra las últimas transacciones de besitos del usuario:

```bash
python scripts/admin_user_manager.py transactions <user_id> [--limit N]
```

**Ejemplo:**
```bash
python scripts/admin_user_manager.py transactions 123456789 --limit 10
```

**Output:**
```
==========================================================================================
💸 HISTORIAL DE TRANSACCIONES - Juan Pérez (últimas 10)
==========================================================================================

📝 Transacción #523
  • Monto: +50 besitos
  • Tipo: reaction
  • Descripción: Reacción al mensaje en canal VIP
  • Balance después: 550
  • Fecha: 2025-01-06 14:30:00

📝 Transacción #522
  • Monto: -100 besitos
  • Tipo: shop_purchase
  • Descripción: Compra en la tienda: Item Premium
  • Balance después: 500
  • Fecha: 2025-01-06 12:00:00

...

==========================================================================================
```

**Parámetros:**
- `--limit N`: Cantidad de transacciones a mostrar (default: 20)

### 9. Reset Completo (PELIGROSO)

⚠️ **ADVERTENCIA:** Esta operación elimina TODO el progreso del usuario.

Resetea completamente:
- Estado narrativo completo
- Todos los besitos (balance a 0)
- Daily gift claims
- Streaks de reacciones
- Nivel de gamificación

```bash
python scripts/admin_user_manager.py reset-all <user_id> --confirm
```

**Ejemplo sin confirmación (solo muestra advertencia):**
```bash
python scripts/admin_user_manager.py reset-all 123456789
```

**Output:**
```
⚠️  ¡ADVERTENCIA! Esta acción reseteará TODO el progreso de Juan Pérez:
  • Estado narrativo completo
  • Todos los besitos
  • Daily gift
  • Streaks

Para confirmar, ejecuta el comando con --confirm
```

**Ejemplo con confirmación:**
```bash
python scripts/admin_user_manager.py reset-all 123456789 --confirm
```

**Output:**
```
🔄 Reseteando TODO el progreso de Juan Pérez...
✅ Progreso completo reseteado exitosamente.
```

**Nota:**
- El historial de transacciones se MANTIENE para auditoría
- Se registra una transacción de tipo `admin_reset`

## 📊 Auditoría

Todas las operaciones que modifican besitos registran transacciones en la tabla `besito_transactions` con los siguientes tipos:

| Tipo | Descripción |
|------|-------------|
| `admin_adjustment` | Ajuste manual de balance exacto |
| `admin_grant` | Concesión manual de besitos |
| `admin_deduction` | Deducción manual de besitos |
| `admin_reset` | Reset completo del perfil |

Puedes consultar el historial completo con:
```bash
python scripts/admin_user_manager.py transactions <user_id> --limit 100
```

## 🔒 Seguridad

- ⚠️ Este script tiene acceso DIRECTO a la base de datos
- ⚠️ NO valida permisos de administrador (usa solo en entorno seguro)
- ⚠️ Las operaciones son INMEDIATAS (no hay deshacer)
- ✅ Todas las modificaciones quedan registradas en transacciones

## 🐛 Troubleshooting

### Error: Usuario no encontrado
```bash
❌ Usuario 123456789 no encontrado.
```
**Solución:** Verifica que el `user_id` sea correcto. Puedes verificarlo en la tabla `users`.

### Error: Usuario no tiene perfil de gamificación
```bash
⚠️  Usuario 123456789 no tiene perfil de gamificación.
```
**Solución:** El usuario debe interactuar con el bot al menos una vez para que se cree su perfil de gamificación.

### Error: No se puede conectar a la base de datos
**Solución:**
1. Verifica que el archivo de base de datos exista
2. Revisa la configuración en `bot/config.py`
3. Asegúrate de estar en el directorio raíz del proyecto

## 📝 Ejemplos de Uso Común

### Debugging: Ver información completa de un usuario con problemas
```bash
python scripts/admin_user_manager.py info 123456789
```

### Testing: Resetear un usuario de prueba
```bash
python scripts/admin_user_manager.py reset-all 123456789 --confirm
```

### Recompensa: Dar besitos a un usuario como premio
```bash
python scripts/admin_user_manager.py add-besitos 123456789 500
```

### Corrección: Ajustar besitos después de un bug
```bash
python scripts/admin_user_manager.py set-besitos 123456789 1000
```

### Auditoría: Revisar transacciones de un usuario sospechoso
```bash
python scripts/admin_user_manager.py transactions 123456789 --limit 50
```

### Soporte: Permitir a un usuario reclamar el regalo diario nuevamente
```bash
python scripts/admin_user_manager.py reset-daily-gift 123456789
```

## 🎯 Casos de Uso

1. **Debugging de Usuarios:**
   - Ver estado completo para diagnosticar problemas
   - Verificar balance de besitos y transacciones

2. **Testing:**
   - Resetear usuarios de prueba entre tests
   - Establecer estados específicos para testing

3. **Soporte al Cliente:**
   - Resolver problemas de besitos
   - Resetear daily gifts si hay errores
   - Corregir estados inconsistentes

4. **Moderación:**
   - Ajustar besitos por violaciones
   - Resetear progreso en casos extremos

5. **Eventos Especiales:**
   - Dar recompensas manuales a usuarios
   - Bonificaciones por participación

## 🔗 Referencias

- **Modelos Core:** `bot/database/models.py`
- **Modelos Gamificación:** `bot/gamification/database/models.py`
- **Modelos Narrativa:** `bot/narrative/database/models.py`
- **Engine de BD:** `bot/database/engine.py`

## 📞 Soporte

Para reportar bugs o sugerir mejoras, contacta al equipo de desarrollo.
