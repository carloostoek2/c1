# REQUERIMIENTO: FASE 2 - ECONOMÍA DE FAVORES (ACTUALIZADO)
## Proyecto: El Mayordomo del Diván
## Bot de Telegram para Señorita Kinky

---

# ⚠️ NOTA IMPORTANTE

Este documento ha sido actualizado para reflejar el estado actual del proyecto.
El sistema de gamificación ya tiene implementada la mayor parte de la infraestructura.

**Convención clave:** 
- El backend usa "besitos" internamente
- La UI muestra "Favores" al usuario
- Ya existe un helper de conversión en `bot/gamification/utils/formatters.py`

**NO recrear lo que ya existe.** Solo verificar, extender o conectar según se indica.

---

# ESTADO ACTUAL DEL PROYECTO

## ✅ YA IMPLEMENTADO (NO TOCAR)

| Componente | Ubicación | Estado |
|------------|-----------|--------|
| BesitoService | `bot/gamification/services/besito.py` | ✅ Completo |
| grant_besitos() | BesitoService | ✅ Con transacciones atómicas |
| deduct_besitos() | BesitoService | ✅ Con validación de saldo |
| get_balance() | BesitoService | ✅ Funciona |
| BesitoTransaction | `bot/gamification/database/models.py` | ✅ Modelo de auditoría |
| TransactionType | `bot/gamification/database/enums.py` | ✅ 8 tipos definidos |
| format_currency() | `bot/gamification/utils/formatters.py` | ✅ Convierte a "Favores" |
| FAVOR_REWARDS | `bot/gamification/utils/formatters.py` | ✅ Valores definidos |
| PROTOCOL_LEVELS | `bot/gamification/utils/formatters.py` | ✅ 7 niveles con nombres |
| LevelService | `bot/gamification/services/` | ✅ Existe |
| ReactionService | `bot/gamification/services/` | ✅ Existe |
| StreakService | `bot/gamification/services/` | ✅ Existe (confirmar) |
| GamificationContainer | `bot/gamification/services/container.py` | ✅ Inyección de dependencias |

---

# TAREAS DE ESTA FASE

## F2.1: VERIFICAR SOPORTE DE DECIMALES

### Contexto
El sistema de Favores usa valores decimales (0.1, 0.5, etc.) pero el campo `total_besitos` podría ser Integer.

### Tarea
1. Verificar el tipo de dato de `total_besitos` en `UserGamification`
2. Si es Integer → crear migración para convertir a Float/Decimal
3. Si ya es Float/Decimal → no hacer nada

### Verificación
```python
# En bot/gamification/database/models.py buscar:
class UserGamification:
    total_besitos: Mapped[???]  # ¿int o float?
    besitos_earned: Mapped[???]
    besitos_spent: Mapped[???]
```

### Si necesita migración
```sql
-- Migración Alembic
ALTER TABLE user_gamification 
    ALTER COLUMN total_besitos TYPE DECIMAL(10,2);
ALTER TABLE user_gamification 
    ALTER COLUMN besitos_earned TYPE DECIMAL(10,2);
ALTER TABLE user_gamification 
    ALTER COLUMN besitos_spent TYPE DECIMAL(10,2);
```

### Actualizar BesitoService si es necesario
Si el campo ahora es Decimal, verificar que `grant_besitos` y `deduct_besitos` manejen floats correctamente en los parámetros y operaciones.

---

## F2.2: VERIFICAR TABLA DE CONFIGURACIÓN

### Contexto
Debe existir una forma de configurar valores de la economía sin cambiar código.

### Verificar si existe
Buscar en el proyecto:
- `GamificationConfig` model
- Alguna tabla de configuración key-value

### Si existe GamificationConfig
Verificar que tenga estos campos o agregarlos:

```python
class GamificationConfig:
    # Ya debería tener:
    besitos_per_reaction: int
    max_besitos_per_day: int
    streak_reset_hours: int
    
    # Agregar si no existen:
    earn_reaction_base: float = 0.1
    earn_first_reaction_day: float = 0.5
    earn_daily_mission: float = 1.0
    earn_weekly_mission: float = 3.0
    earn_level_evaluation: float = 5.0
    earn_streak_7: float = 2.0
    earn_streak_30: float = 10.0
    limit_reactions_per_day: int = 10
```

### Si NO existe configuración editable
Crear tabla simple:

```python
class EconomyConfig(Base):
    __tablename__ = 'economy_config'
    
    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[float]
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    updated_at: Mapped[datetime]
```

Con seed data inicial basado en `FAVOR_REWARDS` de formatters.py.

---

## F2.3: VERIFICAR SISTEMA DE RACHAS

### Contexto
El usuario indica que StreakService ya existe.

### Tarea
1. Localizar StreakService en el proyecto
2. Verificar que tenga estos métodos (o equivalentes):

```python
# Métodos esperados:
record_activity(user_id) -> StreakUpdate
check_streak_status(user_id) -> StreakStatus  
break_streak(user_id) -> None
get_streak_leaderboard(limit) -> List
```

3. Verificar que otorgue bonus de Favores al alcanzar hitos (7, 30 días)

### Si falta conexión con Favores
Asegurar que al alcanzar hito de racha se llame:

```python
# Al alcanzar 7 días:
await besito_service.grant_besitos(
    user_id=user_id,
    amount=FAVOR_REWARDS["streak_7_days"],  # 2.0
    transaction_type=TransactionType.STREAK_BONUS,
    description="Racha de 7 días consecutivos"
)

# Al alcanzar 30 días:
await besito_service.grant_besitos(
    user_id=user_id,
    amount=FAVOR_REWARDS["streak_30_days"],  # 10.0
    transaction_type=TransactionType.STREAK_BONUS,
    description="Racha de 30 días consecutivos"
)
```

---

## F2.4: VERIFICAR LEVEL-UP AUTOMÁTICO

### Contexto
Cuando un usuario gana Favores, debería verificarse si sube de nivel.

### Tarea
1. Verificar si `grant_besitos()` llama a `check_and_apply_level_up()`
2. Si no lo hace, agregar la llamada

### Ubicación
En `bot/gamification/services/besito.py`, método `grant_besitos()`:

```python
async def grant_besitos(self, user_id, amount, ...):
    # ... código existente de otorgar besitos ...
    
    # Agregar al final, antes del return:
    # Verificar level up
    from bot.gamification.services.level import LevelService
    level_service = LevelService(self.session)
    level_changed, old_level, new_level = await level_service.check_and_apply_level_up(user_id)
    
    if level_changed:
        # Opcional: notificar level up
        logger.info(f"User {user_id} leveled up: {old_level} -> {new_level}")
    
    return amount, level_changed, new_level  # Ajustar return si es necesario
```

### Alternativa
Si no se quiere modificar grant_besitos, crear un método wrapper:

```python
async def grant_besitos_with_level_check(self, user_id, amount, ...):
    result = await self.grant_besitos(user_id, amount, ...)
    level_result = await self.level_service.check_and_apply_level_up(user_id)
    return result, level_result
```

---

## F2.5: VERIFICAR LÍMITES DIARIOS

### Contexto
Debe haber límite de cuántas reacciones dan Favores por día (anti-spam).

### Tarea
1. Verificar si ReactionService ya implementa límite diario
2. Si no, agregar validación

### Verificar en ReactionService
Buscar en `record_reaction()` o equivalente:

```python
# Debería existir algo como:
daily_count = await self._count_reactions_today(user_id)
if daily_count >= MAX_REACTIONS_PER_DAY:
    return False, "Límite diario alcanzado", 0
```

### Si no existe, agregar
```python
async def _count_reactions_today(self, user_id: int) -> int:
    """Cuenta reacciones del usuario hoy."""
    today_start = datetime.now(UTC).replace(hour=0, minute=0, second=0)
    
    result = await self.session.execute(
        select(func.count(UserReaction.id))
        .where(UserReaction.user_id == user_id)
        .where(UserReaction.reacted_at >= today_start)
    )
    return result.scalar() or 0

async def can_earn_from_reaction(self, user_id: int) -> bool:
    """Verifica si usuario puede ganar Favores por reacción."""
    count = await self._count_reactions_today(user_id)
    limit = FAVOR_REWARDS.get("reaction_daily_limit", 10)
    return count < limit
```

---

## F2.6: VERIFICAR BONUS PRIMERA REACCIÓN DEL DÍA

### Contexto
La primera reacción del día debe dar bonus extra (0.5 Favores).

### Tarea
Verificar si ReactionService otorga bonus por primera reacción diaria.

### Lógica esperada
```python
async def record_reaction(self, user_id, emoji, ...):
    # Verificar si es primera reacción del día
    is_first_today = await self._is_first_reaction_today(user_id)
    
    # Calcular Favores
    base_amount = FAVOR_REWARDS["reaction_base"]  # 0.1
    
    if is_first_today:
        bonus = FAVOR_REWARDS["reaction_first_daily"]  # 0.5
        total_amount = base_amount + bonus
        description = "Reacción + Bonus primera del día"
    else:
        total_amount = base_amount
        description = "Reacción a publicación"
    
    # Otorgar
    await besito_service.grant_besitos(
        user_id=user_id,
        amount=total_amount,
        transaction_type=TransactionType.REACTION,
        description=description
    )
```

---

## F2.7: COMANDOS DE ADMIN PARA ECONOMÍA

### Contexto
Admins necesitan poder gestionar la economía manualmente.

### Verificar si existen
Buscar handlers para:
- `/admin_grant` o similar - otorgar Favores
- `/admin_deduct` o similar - quitar Favores
- `/admin_balance` o similar - ver balance de usuario

### Si no existen, crear
Ubicación sugerida: `bot/gamification/handlers/admin/economy_admin.py`

```python
# Comandos a implementar:

@router.message(Command("admin_grant"))
async def admin_grant_besitos(message: Message, session: AsyncSession):
    """
    Uso: /admin_grant <user_id> <amount> <reason>
    Ejemplo: /admin_grant 123456 10 Compensación por bug
    """
    # Parsear argumentos
    # Validar que quien llama es admin
    # Llamar a besito_service.grant_besitos con TransactionType.ADMIN_GRANT
    # Confirmar acción

@router.message(Command("admin_deduct"))
async def admin_deduct_besitos(message: Message, session: AsyncSession):
    """
    Uso: /admin_deduct <user_id> <amount> <reason>
    """
    # Similar a grant pero con deduct

@router.message(Command("admin_balance"))
async def admin_check_balance(message: Message, session: AsyncSession):
    """
    Uso: /admin_balance <user_id>
    Muestra: balance, nivel, racha, últimas transacciones
    """
    # Obtener info completa del usuario
    # Formatear y mostrar

@router.message(Command("admin_economy_stats"))
async def admin_economy_stats(message: Message, session: AsyncSession):
    """
    Muestra estadísticas globales de la economía.
    """
    # Total Favores en circulación
    # Promedio por usuario
    # Favores otorgados/gastados hoy/semana/mes
```

---

## F2.8: MENSAJES DE LUCIEN PARA ECONOMÍA

### Contexto
Las notificaciones de Favores deben usar la voz de Lucien.

### Verificar
¿Existe archivo de mensajes centralizados? Buscar:
- `bot/utils/lucien_messages.py`
- `bot/gamification/messages.py`
- Constantes de mensajes en algún lugar

### Si no existe, crear sección en mensajes
Agregar a archivo de mensajes (crear si no existe):

```python
# Mensajes relacionados con Favores

FAVOR_EARNED_SMALL = "+{amount} Favor. Diana lo nota."

FAVOR_EARNED_MEDIUM = """
+{amount} Favores. Su cuenta crece.

Total: {new_total}
"""

FAVOR_EARNED_LARGE = """
+{amount} Favores.

Eso fue significativo. Diana ha sido informada.

Total: {new_total}
"""

FAVOR_MILESTONE = """
Ha alcanzado {total} Favores.

Eso lo coloca entre quienes Diana considera... relevantes.
"""

FAVOR_INSUFFICIENT = """
Sus Favores son insuficientes.

Necesita: {required}
Tiene: {current}

Diana no otorga crédito. Acumule más Favores y regrese.
"""

FAVOR_BALANCE = """
Su cuenta de Favores con Diana:

━━━━━━━━━━━━━━━━━━━━━━━━
💫 BALANCE ACTUAL
━━━━━━━━━━━━━━━━━━━━━━━━

Favores acumulados: {total}

{comment}
"""

# Comentarios según cantidad
FAVOR_COMMENTS = {
    (0, 5): "Apenas comenzando. La constancia construye Favores.",
    (6, 15): "Un inicio modesto. Hay potencial, si persiste.",
    (16, 35): "Progreso visible. Diana empieza a notar patrones.",
    (36, 70): "Acumulación respetable. El Gabinete tiene opciones para usted.",
    (71, 120): "Una cuenta considerable. Pocos llegan a estos números.",
    (121, 200): "Impresionante moderación. ¿O indecisión? Solo usted lo sabe.",
    (201, float('inf')): "Acumula sin gastar. Prudente. O quizás espera algo específico."
}
```

---

## F2.9: INTEGRACIÓN CON FORMATTERS EXISTENTES

### Contexto
Ya existe `format_currency()` en formatters.py. Asegurar que se use consistentemente.

### Tarea
Verificar que todos los lugares donde se muestran Favores usen el helper:

```python
from bot.gamification.utils.formatters import format_currency, format_currency_change

# En lugar de:
f"Tienes {besitos} besitos"

# Usar:
f"Tienes {format_currency(besitos)}"  # "Tienes 10 Favores"

# Para cambios:
f"{format_currency_change(amount, is_gain=True)}"  # "+5 Favores"
```

### Lugares a verificar
1. Handler de perfil (`/profile`, `/perfil`)
2. Handler de compras (Gabinete)
3. Notificaciones de recompensas
4. Mensajes de misiones completadas
5. Cualquier lugar que muestre cantidad de moneda

---

## F2.10: PREVENCIÓN DE EXPLOITS

### Verificar que existan estas protecciones

1. **Límite de reacciones por día**
   - ¿Implementado en ReactionService?

2. **No permitir balance negativo**
   - Verificar en `deduct_besitos()` que valide `balance >= amount`

3. **Rate limiting en endpoints**
   - ¿Existe middleware de rate limit?

4. **Validación de source_id único**
   - ¿Se previene otorgar múltiples veces por la misma fuente?

### Si falta rate limiting
```python
# Middleware simple de rate limit
from aiogram import BaseMiddleware
from collections import defaultdict
import time

class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: int = 60):  # 60 acciones por minuto
        self.rate_limit = rate_limit
        self.user_actions = defaultdict(list)
    
    async def __call__(self, handler, event, data):
        user_id = event.from_user.id
        now = time.time()
        
        # Limpiar acciones antiguas (más de 1 minuto)
        self.user_actions[user_id] = [
            t for t in self.user_actions[user_id] 
            if now - t < 60
        ]
        
        if len(self.user_actions[user_id]) >= self.rate_limit:
            # Rate limited
            return
        
        self.user_actions[user_id].append(now)
        return await handler(event, data)
```

---

# CRITERIOS DE ACEPTACIÓN

## Verificaciones (no implementar si ya existe)
- [ ] Campo total_besitos soporta decimales (Float/Decimal)
- [ ] Configuración de economía es editable (tabla o config)
- [ ] StreakService existe y otorga bonus en hitos
- [ ] Level-up se verifica al ganar Favores
- [ ] Límite diario de reacciones implementado
- [ ] Bonus primera reacción del día funciona

## Implementaciones (solo si no existe)
- [ ] Migración a decimales si campo es Integer
- [ ] Comandos admin para gestionar economía
- [ ] Mensajes de Lucien para Favores
- [ ] Rate limiting si no existe

## Integraciones
- [ ] format_currency() usado en toda la UI
- [ ] TransactionType tiene todos los tipos necesarios
- [ ] Todas las ganancias de Favores crean BesitoTransaction

---

# ORDEN DE EJECUCIÓN SUGERIDO

1. **Primero:** Verificar tipo de dato de total_besitos (F2.1)
2. **Segundo:** Verificar y completar sistema de rachas (F2.3)
3. **Tercero:** Verificar level-up automático (F2.4)
4. **Cuarto:** Verificar límites y bonus de reacciones (F2.5, F2.6)
5. **Quinto:** Crear comandos admin si no existen (F2.7)
6. **Sexto:** Asegurar uso consistente de formatters (F2.9)
7. **Último:** Verificar protecciones anti-exploit (F2.10)

---

# ARCHIVOS CLAVE A REVISAR

```
bot/gamification/
├── services/
│   ├── besito.py          # BesitoService - YA EXISTE
│   ├── level.py           # LevelService - YA EXISTE
│   ├── reaction.py        # ReactionService - YA EXISTE
│   ├── streak.py          # StreakService - VERIFICAR
│   └── container.py       # Container - YA EXISTE
├── database/
│   ├── models.py          # UserGamification - VERIFICAR campos
│   └── enums.py           # TransactionType - YA EXISTE
├── utils/
│   └── formatters.py      # format_currency - YA EXISTE
└── handlers/
    └── admin/
        └── economy_admin.py  # CREAR SI NO EXISTE
```

---

# NOTAS FINALES

1. **No duplicar código:** Si algo ya existe, usarlo
2. **Mantener compatibilidad:** El backend sigue usando "besitos"
3. **UI muestra "Favores":** Siempre usar format_currency() para mostrar
4. **Transacciones:** Toda operación debe crear BesitoTransaction
5. **Testing:** Verificar que tests existentes sigan pasando

---

*Documento actualizado para reflejar estado actual del proyecto*
*Proyecto: El Mayordomo del Diván*
*Fase: 2 - Economía de Favores (REVISADA)*
