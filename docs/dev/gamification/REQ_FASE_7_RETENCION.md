# REQUERIMIENTO: FASE 7 - RETENCIÓN Y ANTI-CHURN
## Proyecto: El Mayordomo del Diván
## Bot de Telegram para Señorita Kinky

---

# CONTEXTO

La retención no es perseguir a quien se va. Es crear razones constantes para quedarse. Lucien no ruega - observa patrones, anticipa abandonos y actúa con dignidad.

**Principio fundamental:** Un usuario que se va por falta de valor no regresará con descuentos. Un usuario que se va por olvido puede regresar con el mensaje correcto en el momento correcto.

**Tipos de churn a prevenir:**
1. **Abandono pasivo** - Usuario simplemente deja de interactuar
2. **Abandono activo** - Usuario decide conscientemente irse
3. **Churn por olvido** - Usuario se distrae, no por desinterés
4. **Churn por frustración** - Algo no funcionó como esperaba

**Dependencias:**
- Todas las fases anteriores completadas
- Sistema de notificaciones funcional
- Tracking de actividad implementado

---

# ARQUITECTURA DE RETENCIÓN

## Ciclo de vida del usuario

```
┌─────────────────────────────────────────────────────────────────────┐
│                     CICLO DE VIDA DEL USUARIO                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  [NUEVO] ──► [ACTIVO] ──► [EN RIESGO] ──► [DORMIDO] ──► [PERDIDO]  │
│     │           │              │              │              │      │
│     │           │              │              │              │      │
│     ▼           ▼              ▼              ▼              ▼      │
│  Onboarding  Engagement    Reactivación   Win-back      Archivo    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

Estados:
- NUEVO: 0-7 días desde registro
- ACTIVO: Interacción en últimos 3 días
- EN RIESGO: 4-7 días sin interacción
- DORMIDO: 8-30 días sin interacción
- PERDIDO: 30+ días sin interacción
```

## Señales de riesgo

| Señal | Peso | Descripción |
|-------|------|-------------|
| Días sin actividad | Alto | Principal indicador |
| Racha rota | Medio | Perdió racha que mantenía |
| Misión abandonada | Medio | Empezó misión y no completó |
| Narrativa pausada | Medio | Dejó historia a medias |
| Descenso de actividad | Alto | Pasó de muy activo a poco activo |
| VIP por vencer | Alto | Suscripción termina pronto |
| Nunca completó onboarding | Alto | Se registró pero no avanzó |

---

# F7.1: SISTEMA DE DETECCIÓN DE RIESGO

## Modelo de datos

```python
class UserEngagementStatus(Base):
    __tablename__ = 'user_engagement_status'
    
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'), primary_key=True)
    
    # Estado actual
    status: Mapped[str]  # NEW, ACTIVE, AT_RISK, DORMANT, LOST
    status_changed_at: Mapped[datetime]
    
    # Métricas de actividad
    last_interaction_at: Mapped[datetime]
    interactions_last_7_days: Mapped[int]
    interactions_last_30_days: Mapped[int]
    avg_daily_interactions: Mapped[float]
    
    # Señales de riesgo
    risk_score: Mapped[float]  # 0-100, mayor = más riesgo
    risk_factors: Mapped[str]  # JSON con factores activos
    
    # Historial de intervenciones
    last_reengagement_sent_at: Mapped[datetime] = mapped_column(nullable=True)
    reengagement_count: Mapped[int] = mapped_column(default=0)
    
    # Tracking
    updated_at: Mapped[datetime]
```

## Cálculo de risk score

```python
async def calculate_risk_score(user_id: int) -> tuple[float, list[str]]:
    """
    Calcula score de riesgo de churn (0-100).
    
    Returns:
        (risk_score, risk_factors)
    """
    factors = []
    score = 0
    
    user = await get_user_engagement(user_id)
    
    # Factor: Días sin actividad (máx 40 puntos)
    days_inactive = (now() - user.last_interaction_at).days
    if days_inactive >= 7:
        score += min(days_inactive * 4, 40)
        factors.append(f"inactive_{days_inactive}_days")
    
    # Factor: Racha rota (20 puntos)
    streak = await get_user_streak(user_id)
    if streak.was_broken_recently:  # Últimos 7 días
        score += 20
        factors.append("streak_broken")
    
    # Factor: Misión abandonada (15 puntos)
    if await has_abandoned_mission(user_id):
        score += 15
        factors.append("mission_abandoned")
    
    # Factor: Narrativa pausada (10 puntos)
    if await has_paused_narrative(user_id):
        score += 10
        factors.append("narrative_paused")
    
    # Factor: Descenso de actividad (15 puntos)
    if user.interactions_last_7_days < user.avg_daily_interactions * 3:
        score += 15
        factors.append("activity_declining")
    
    # Factor: VIP por vencer sin renovación (20 puntos)
    if await vip_expiring_soon(user_id) and not await has_auto_renew(user_id):
        score += 20
        factors.append("vip_expiring")
    
    # Factor: Onboarding incompleto (25 puntos)
    if not await completed_onboarding(user_id):
        score += 25
        factors.append("onboarding_incomplete")
    
    return min(score, 100), factors
```

## Job de actualización de estados

```python
async def update_engagement_statuses():
    """
    Job que corre cada hora para actualizar estados.
    """
    users = await get_all_users_with_activity()
    
    for user in users:
        days_inactive = (now() - user.last_interaction_at).days
        
        # Determinar nuevo estado
        if days_inactive <= 3:
            new_status = 'ACTIVE'
        elif days_inactive <= 7:
            new_status = 'AT_RISK'
        elif days_inactive <= 30:
            new_status = 'DORMANT'
        else:
            new_status = 'LOST'
        
        # Si estado cambió, actualizar
        if user.status != new_status:
            await update_user_status(user.user_id, new_status)
            
            # Trigger acciones según transición
            if new_status == 'AT_RISK':
                await schedule_reengagement(user.user_id, 'at_risk')
            elif new_status == 'DORMANT':
                await schedule_reengagement(user.user_id, 'dormant')
```

---

# F7.2: MENSAJES DE RE-ENGAGEMENT

## Estrategia por estado

| Estado | Timing | Tono | Frecuencia máx |
|--------|--------|------|----------------|
| AT_RISK | Día 4-5 | Sutil, curioso | 1 mensaje |
| DORMANT | Día 8-10 | Más directo | 2 mensajes (espaciados 7 días) |
| LOST | Día 30+ | Último intento | 1 mensaje final |

## Mensajes para AT_RISK (4-7 días inactivo)

### Variante 1: Observación de Lucien
```
Speaker: LUCIEN

"Una observación.

Han pasado {days} días desde su última visita.

No es una queja. Solo... registro.
Diana publicó {new_posts} cosas nuevas desde entonces.
{Si tenía racha: 'Y su racha de {streak} días... bueno, ya sabe.'}

El Diván sigue aquí. Cuando quiera regresar."

[NO incluir botones agresivos - solo texto]
```

### Variante 2: Contenido que se perdió
```
Speaker: LUCIEN

"Mientras no estaba...

Diana compartió algo que creo le habría interesado.
{descripción_breve_de_contenido_reciente}

No es urgente. Pero pensé que debía saber."

[BOTÓN opcional]
[Ver qué me perdí]
```

### Variante 3: Progreso pendiente
```
Speaker: LUCIEN

"Un recordatorio sobre su progreso.

{Si tenía misión}: Su misión '{mission_name}' quedó en {progress}%.
{Si tenía narrativa}: El capítulo {chapter} quedó a medias.
{Si tenía Favores}: Sus {favors} Favores siguen esperando.

Nada de esto caduca. Pero quizás quería saberlo."
```

## Mensajes para DORMANT (8-30 días inactivo)

### Primer mensaje (día 8-10)
```
Speaker: LUCIEN

"Ha pasado tiempo.

{days} días, para ser exactos.

No sé si fue intencional o si simplemente... la vida.
De cualquier forma, quería que supiera:

Su cuenta sigue activa.
Sus {favors} Favores siguen ahí.
{Si es VIP}: Su acceso al Diván sigue vigente.

Diana no olvida a quienes estuvieron.
Aunque sea un momento."

[BOTÓN]
[Volver a ver]
```

### Segundo mensaje (día 15-17, si no respondió al primero)
```
Speaker: LUCIEN

"Último mensaje por un tiempo.

No quiero ser insistente. Eso no es mi estilo.

Pero antes de dejar de escribir, quería dejar esto claro:
Cuando quiera volver, si quiere volver, estará todo como lo dejó.

Sin reproches. Sin explicaciones necesarias.

Cuídese."

[NO más mensajes hasta que regrese o pasen 30 días]
```

## Mensaje para LOST (30+ días inactivo)

### Mensaje único de despedida
```
Speaker: LUCIEN

"Ha pasado un mes.

Este será mi último mensaje, a menos que decida regresar.

Su cuenta permanecerá activa.
{Si es VIP y expiró}: Su acceso VIP ha expirado, pero puede reactivarse.
{Si tiene Favores}: Sus {favors} Favores seguirán esperando.

Diana me pidió que le dijera algo:
'Las puertas no se cierran. Solo se alejan.'

Hasta que nos veamos de nuevo. O no."

[NO más mensajes automáticos - usuario en estado LOST]
```

---

# F7.3: MENSAJES POR EVENTO ESPECÍFICO

## Racha rota
```
[Trigger: Usuario tenía racha de 7+ días y la perdió]

Speaker: LUCIEN

"Su racha de {streak_days} días ha terminado.

No voy a decir que es una tragedia.
Pero sé que había esfuerzo detrás de esos días.

La buena noticia: puede comenzar una nueva racha hoy.
Un día. Luego otro. Ya conoce el proceso."

[BOTÓN]
[Comenzar nueva racha]
```

## Misión expirada
```
[Trigger: Misión activa expiró sin completarse]

Speaker: LUCIEN

"La misión '{mission_name}' ha expirado.

Llegó al {progress}% antes de que el tiempo terminara.

No es el fin del mundo. Habrá otras misiones.
Pero quería que supiera que lo noté."

[BOTÓN]
[Ver misiones disponibles]
```

## VIP por vencer (7 días antes)
```
[Trigger: Suscripción VIP vence en 7 días]

Speaker: LUCIEN

"Una nota sobre su acceso al Diván.

Su suscripción vence en 7 días.

No es una amenaza. Es información.
Puede renovar cuando quiera. O no renovar.

Si no renueva, su acceso se pausará.
Sus Favores, progreso y badges permanecerán.
Podrá reactivar cuando desee."

[BOTONES]
[Renovar ahora]    [Recordarme después]
```

## VIP por vencer (1 día antes)
```
[Trigger: Suscripción VIP vence mañana]

Speaker: LUCIEN

"Último aviso: su acceso al Diván vence mañana.

Después de mañana:
• No podrá ver nuevo contenido del Diván
• Los niveles 4-6 de narrativa se pausarán
• Su progreso se conservará para cuando regrese

{Si tiene descuento disponible}:
Por su nivel, tiene un {discount}% de descuento en renovación."

[BOTONES]
[Renovar con descuento]    [Dejar que expire]
```

## VIP expirado
```
[Trigger: Suscripción VIP acaba de expirar]

Speaker: LUCIEN

"Su acceso al Diván ha expirado.

No es un adiós. Es una pausa.

Todo lo que construyó sigue ahí:
• {favors} Favores
• Nivel {level} alcanzado
• {badges} badges obtenidos
• Progreso narrativo guardado

El Diván estará aquí cuando decida volver.
Diana no olvida a quienes cruzaron el umbral."

[BOTÓN]
[Reactivar acceso]    [Quizás después]
```

---

# F7.4: INCENTIVOS DE RETENCIÓN

## Bonus por regreso

| Días ausente | Bonus al volver | Condición |
|--------------|-----------------|-----------|
| 7-14 días | +2 Favores | Primera interacción |
| 15-30 días | +5 Favores | Primera interacción |
| 30+ días | +10 Favores | Completar una acción |

### Mensaje de bonus por regreso
```
Speaker: LUCIEN

"Ha vuelto.

{days} días sin vernos. Pero aquí está de nuevo.

Diana autorizó un pequeño reconocimiento por su regreso:
+{bonus} Favores han sido añadidos a su cuenta.

{Si tenía racha rota}: Su racha anterior se perdió, pero hoy es día 1 de una nueva.
{Si tenía misión pendiente}: Hay una nueva misión esperándolo.

Bienvenido de vuelta."
```

## Descuento por renovación temprana

| Días antes de vencimiento | Descuento |
|---------------------------|-----------|
| 14+ días | 15% |
| 7-13 días | 10% |
| 1-6 días | 5% |
| Después de vencimiento | 0% |

### Mensaje de descuento por renovación temprana
```
[Trigger: VIP vence en 14+ días y usuario es muy activo]

Speaker: LUCIEN

"Una oportunidad anticipada.

Su suscripción al Diván vence en {days} días.
Pero por su actividad reciente, Diana autorizó algo especial:

Si renueva ahora, obtiene {discount}% de descuento.
Precio regular: {precio}
Su precio: {precio_descuento}

La oferta es válida hasta que su suscripción actual expire.
Después, el precio vuelve a la normalidad."

[BOTONES]
[Renovar con {discount}%]    [Esperar]
```

## Contenido exclusivo para retención

### "Fragmento del Ausente"
```
[Item especial que solo se desbloquea al volver después de 14+ días]

Speaker: LUCIEN

"Hay algo que Diana preparó para quienes regresan.

Lo llama 'El Fragmento del Ausente'.
Un contenido que solo pueden ver quienes se fueron... y volvieron.

No es castigo. Es reconocimiento.
De que el regreso tiene su propio valor."

[BOTÓN]
[Ver el Fragmento]

[Contenido: Mensaje especial de Diana sobre ausencia y regreso]
```

---

# F7.5: PREVENCIÓN PROACTIVA

## Felicitaciones por hitos (engagement positivo)

### Racha de 7 días
```
Speaker: LUCIEN

"7 días consecutivos.

No es casualidad. Es decisión.
Cada día eligió volver. Eso dice algo.

+{bonus} Favores por su constancia.
Diana ha sido notificada de su racha."
```

### Racha de 30 días
```
Speaker: LUCIEN

"Un mes.

30 días consecutivos de presencia.
Eso lo coloca en el {percentile}% superior de todos los usuarios.

Diana quiso que recibiera algo especial por esto.
+{bonus} Favores. Y un badge que pocos tienen."

[Badge: "El Constante" 📅]
```

### Racha de 100 días
```
Speaker: DIANA
[Sí, Diana habla directamente]

"100 días.

No sé qué decir que no suene insuficiente.
Has estado aquí, cada día, por más de tres meses.

Eso no es casualidad. No es costumbre.
Es algo más.

Gracias. De verdad."

Speaker: LUCIEN

"+{bonus} Favores otorgados.
Badge legendario: 'Guardián del Tiempo' desbloqueado.
Su nombre ha sido añadido al registro permanente de Diana."

[Badge: "Guardián del Tiempo" ⏰ - Rarity: LEGENDARY]
```

### Completar toda la narrativa
```
Speaker: LUCIEN

"Ha llegado al final.

Todos los capítulos. Todas las decisiones. Todos los secretos.
Ha visto más de Diana que el 99% de quienes entran aquí.

Esto no es un final. Es un cambio.
A partir de ahora, la relación es diferente.
Ya no es descubrimiento. Es... presencia.

Badge 'El Que Llegó al Final' desbloqueado."

[Badge: "El Que Llegó al Final" 🏁 - Rarity: LEGENDARY]
```

### Primera compra
```
Speaker: LUCIEN

"Su primera adquisición en el Gabinete.

'{item_name}' es suyo.

Esto marca un antes y un después.
Ya no es solo un observador. Es un participante.

Diana nota la diferencia."
```

---

# F7.6: SISTEMA DE NOTIFICACIONES

## Configuración de usuario

```python
class UserNotificationPreferences(Base):
    __tablename__ = 'user_notification_preferences'
    
    user_id: Mapped[int] = mapped_column(primary_key=True)
    
    # Tipos de notificación
    new_content: Mapped[bool] = mapped_column(default=True)
    mission_reminders: Mapped[bool] = mapped_column(default=True)
    streak_warnings: Mapped[bool] = mapped_column(default=True)
    reengagement: Mapped[bool] = mapped_column(default=True)
    promotional: Mapped[bool] = mapped_column(default=False)
    
    # Horarios preferidos
    quiet_hours_start: Mapped[int] = mapped_column(default=22)  # 10 PM
    quiet_hours_end: Mapped[int] = mapped_column(default=9)     # 9 AM
    timezone: Mapped[str] = mapped_column(default='America/Mexico_City')
    
    # Límites
    max_notifications_per_day: Mapped[int] = mapped_column(default=3)
    
    updated_at: Mapped[datetime]
```

## Comando de preferencias
```
/notificaciones

Speaker: LUCIEN

"Sus preferencias de comunicación:

━━━━━━━━━━━━━━━━━━━━━━━━
📬 NOTIFICACIONES
━━━━━━━━━━━━━━━━━━━━━━━━

{✓/✗} Contenido nuevo
{✓/✗} Recordatorios de misiones
{✓/✗} Alertas de racha
{✓/✗} Mensajes de re-engagement
{✓/✗} Ofertas especiales

━━━━━━━━━━━━━━━━━━━━━━━━
🕐 HORARIO SILENCIOSO
━━━━━━━━━━━━━━━━━━━━━━━━

No molestar de {start} a {end}

━━━━━━━━━━━━━━━━━━━━━━━━

¿Desea modificar algo?"

[BOTONES]
[Modificar preferencias]    [Está bien así]
```

## Respeto de preferencias
```python
async def can_send_notification(user_id: int, notification_type: str) -> bool:
    """
    Verifica si se puede enviar notificación a usuario.
    """
    prefs = await get_notification_preferences(user_id)
    
    # Verificar tipo habilitado
    if notification_type == 'new_content' and not prefs.new_content:
        return False
    if notification_type == 'reengagement' and not prefs.reengagement:
        return False
    # ... etc
    
    # Verificar horario silencioso
    user_hour = get_user_local_hour(user_id, prefs.timezone)
    if prefs.quiet_hours_start <= user_hour or user_hour < prefs.quiet_hours_end:
        return False
    
    # Verificar límite diario
    sent_today = await count_notifications_today(user_id)
    if sent_today >= prefs.max_notifications_per_day:
        return False
    
    return True
```

---

# F7.7: ANÁLISIS Y REPORTES

## Dashboard de retención (para admin)

```
/admin_retention

Muestra:

━━━━━━━━━━━━━━━━━━━━━━━━
📊 ESTADO DE USUARIOS
━━━━━━━━━━━━━━━━━━━━━━━━

Activos (últimos 3 días): {count} ({percent}%)
En riesgo (4-7 días): {count} ({percent}%)
Dormidos (8-30 días): {count} ({percent}%)
Perdidos (30+ días): {count} ({percent}%)

━━━━━━━━━━━━━━━━━━━━━━━━
📈 MÉTRICAS CLAVE
━━━━━━━━━━━━━━━━━━━━━━━━

Tasa de retención 7 días: {rate}%
Tasa de retención 30 días: {rate}%
Churn mensual: {rate}%
Promedio días activos: {days}

━━━━━━━━━━━━━━━━━━━━━━━━
🔄 RE-ENGAGEMENT
━━━━━━━━━━━━━━━━━━━━━━━━

Mensajes enviados (7 días): {count}
Tasa de respuesta: {rate}%
Reactivaciones exitosas: {count}

━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ ALERTAS
━━━━━━━━━━━━━━━━━━━━━━━━

{count} VIPs expiran esta semana
{count} usuarios con risk score > 80
{count} rachas largas en peligro
```

## Métricas a calcular

```python
async def calculate_retention_metrics() -> RetentionMetrics:
    """
    Calcula métricas de retención.
    """
    return RetentionMetrics(
        # Retención
        day_1_retention=await calc_retention(1),
        day_7_retention=await calc_retention(7),
        day_30_retention=await calc_retention(30),
        
        # Churn
        monthly_churn_rate=await calc_monthly_churn(),
        churn_by_reason=await calc_churn_reasons(),
        
        # Engagement
        avg_session_length=await calc_avg_session(),
        avg_sessions_per_week=await calc_sessions_per_week(),
        avg_actions_per_session=await calc_actions_per_session(),
        
        # Re-engagement
        reengagement_success_rate=await calc_reengagement_success(),
        avg_days_to_reactivate=await calc_days_to_reactivate(),
        
        # Cohortes
        cohort_retention=await calc_cohort_retention()
    )
```

## Alertas automáticas

```python
async def check_retention_alerts():
    """
    Job que verifica alertas de retención.
    """
    alerts = []
    
    # Alerta: Muchos usuarios en riesgo
    at_risk_count = await count_users_by_status('AT_RISK')
    at_risk_percent = at_risk_count / total_users * 100
    if at_risk_percent > 20:
        alerts.append(f"⚠️ {at_risk_percent}% de usuarios en riesgo")
    
    # Alerta: Churn alto
    weekly_churn = await calc_weekly_churn()
    if weekly_churn > 10:
        alerts.append(f"⚠️ Churn semanal alto: {weekly_churn}%")
    
    # Alerta: VIPs por vencer
    expiring_vips = await count_vips_expiring_this_week()
    if expiring_vips > 10:
        alerts.append(f"⚠️ {expiring_vips} VIPs expiran esta semana")
    
    # Alerta: Rachas largas en peligro
    long_streaks_at_risk = await count_long_streaks_at_risk()
    if long_streaks_at_risk > 5:
        alerts.append(f"⚠️ {long_streaks_at_risk} rachas de 30+ días en peligro")
    
    if alerts:
        await send_admin_alert("\n".join(alerts))
```

---

# F7.8: JOBS PROGRAMADOS

## Lista de jobs de retención

| Job | Frecuencia | Función |
|-----|------------|---------|
| update_engagement_statuses | Cada hora | Actualizar estados de usuarios |
| send_at_risk_messages | Diario 10 AM | Enviar mensajes a usuarios AT_RISK |
| send_dormant_messages | Diario 2 PM | Enviar mensajes a usuarios DORMANT |
| check_expiring_vips | Diario 9 AM | Alertar VIPs por vencer |
| check_broken_streaks | Cada 6 horas | Detectar rachas rotas |
| calculate_retention_metrics | Diario medianoche | Calcular métricas |
| send_admin_alerts | Cada hora | Verificar y enviar alertas |

## Implementación de jobs

```python
# Usando APScheduler o similar

from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', hour='*')  # Cada hora
async def job_update_statuses():
    await update_engagement_statuses()

@scheduler.scheduled_job('cron', hour=10, minute=0)  # 10 AM
async def job_at_risk_messages():
    users = await get_users_by_status('AT_RISK')
    for user in users:
        if await can_send_notification(user.id, 'reengagement'):
            if await should_send_reengagement(user.id):
                await send_at_risk_message(user.id)

@scheduler.scheduled_job('cron', hour=14, minute=0)  # 2 PM
async def job_dormant_messages():
    users = await get_users_by_status('DORMANT')
    for user in users:
        if await can_send_notification(user.id, 'reengagement'):
            if await should_send_reengagement(user.id):
                await send_dormant_message(user.id)

@scheduler.scheduled_job('cron', hour=9, minute=0)  # 9 AM
async def job_vip_reminders():
    expiring = await get_vips_expiring_soon()
    for user in expiring:
        days_left = (user.vip_expires_at - now()).days
        if days_left == 7:
            await send_vip_expiring_message(user.id, days=7)
        elif days_left == 1:
            await send_vip_expiring_message(user.id, days=1)

scheduler.start()
```

---

# F7.9: MENSAJES DE LUCIEN PARA RETENCIÓN

## Agregar a biblioteca de mensajes

```python
# === RE-ENGAGEMENT ===

REENGAGEMENT_AT_RISK = """
Una observación.

Han pasado {days} días desde su última visita.
Diana publicó {new_posts} cosas nuevas desde entonces.

El Diván sigue aquí. Cuando quiera regresar.
"""

REENGAGEMENT_DORMANT_1 = """
Ha pasado tiempo.

{days} días, para ser exactos.

Su cuenta sigue activa.
Sus {favors} Favores siguen ahí.

Diana no olvida a quienes estuvieron.
"""

REENGAGEMENT_DORMANT_2 = """
Último mensaje por un tiempo.

Cuando quiera volver, estará todo como lo dejó.
Sin reproches. Sin explicaciones.

Cuídese.
"""

REENGAGEMENT_LOST = """
Ha pasado un mes.

Este será mi último mensaje.
Su cuenta permanecerá activa.

Las puertas no se cierran. Solo se alejan.
"""

# === RACHAS ===

STREAK_BROKEN = """
Su racha de {streak_days} días ha terminado.

Puede comenzar una nueva racha hoy.
Un día. Luego otro. Ya conoce el proceso.
"""

STREAK_7_DAYS = """
7 días consecutivos.

No es casualidad. Es decisión.
+{bonus} Favores por su constancia.
"""

STREAK_30_DAYS = """
Un mes. 30 días consecutivos.

Eso lo coloca en el {percentile}% superior.
+{bonus} Favores. Y un badge que pocos tienen.
"""

STREAK_100_DAYS = """
100 días.

Gracias. De verdad.
"""

# === VIP ===

VIP_EXPIRING_7_DAYS = """
Su suscripción al Diván vence en 7 días.

Puede renovar cuando quiera. O no renovar.
Si no renueva, su acceso se pausará.
"""

VIP_EXPIRING_1_DAY = """
Último aviso: su acceso al Diván vence mañana.

Después de mañana no podrá ver nuevo contenido.
Su progreso se conservará para cuando regrese.
"""

VIP_EXPIRED = """
Su acceso al Diván ha expirado.

No es un adiós. Es una pausa.
Todo lo que construyó sigue ahí.

El Diván estará aquí cuando decida volver.
"""

# === REGRESO ===

WELCOME_BACK = """
Ha vuelto.

{days} días sin vernos. Pero aquí está de nuevo.
+{bonus} Favores por su regreso.

Bienvenido de vuelta.
"""

# === HITOS ===

MILESTONE_NARRATIVE_COMPLETE = """
Ha llegado al final.

Todos los capítulos. Todas las decisiones.
Ha visto más de Diana que el 99% de quienes entran.

Badge 'El Que Llegó al Final' desbloqueado.
"""

MILESTONE_FIRST_PURCHASE = """
Su primera adquisición en el Gabinete.

Ya no es solo observador. Es participante.
Diana nota la diferencia.
"""
```

---

# F7.10: INTEGRACIÓN CON OTROS SISTEMAS

## Con sistema de notificaciones
```python
async def send_retention_message(user_id: int, message_type: str, **kwargs):
    """
    Envía mensaje de retención respetando preferencias.
    """
    # Verificar si puede recibir
    if not await can_send_notification(user_id, 'reengagement'):
        return False
    
    # Obtener mensaje
    message = get_retention_message(message_type, **kwargs)
    
    # Enviar
    await bot.send_message(user_id, message)
    
    # Registrar
    await log_notification_sent(user_id, message_type)
    
    return True
```

## Con sistema de Favores
```python
async def grant_return_bonus(user_id: int, days_absent: int):
    """
    Otorga bonus por regresar después de ausencia.
    """
    if days_absent >= 30:
        bonus = 10
    elif days_absent >= 15:
        bonus = 5
    elif days_absent >= 7:
        bonus = 2
    else:
        return 0
    
    await besito_service.grant_besitos(
        user_id=user_id,
        amount=bonus,
        transaction_type=TransactionType.RETURN_BONUS,
        description=f"Bonus por regresar después de {days_absent} días"
    )
    
    return bonus
```

## Con sistema de VIP
```python
async def check_and_handle_vip_expiration():
    """
    Verifica y maneja expiración de VIPs.
    """
    expiring_soon = await get_vips_expiring_in_days(7)
    for vip in expiring_soon:
        if not await has_received_expiry_warning(vip.user_id, days=7):
            await send_vip_expiring_message(vip.user_id, days=7)
            await mark_expiry_warning_sent(vip.user_id, days=7)
    
    expiring_tomorrow = await get_vips_expiring_in_days(1)
    for vip in expiring_tomorrow:
        if not await has_received_expiry_warning(vip.user_id, days=1):
            await send_vip_expiring_message(vip.user_id, days=1)
            await mark_expiry_warning_sent(vip.user_id, days=1)
    
    just_expired = await get_vips_just_expired()
    for vip in just_expired:
        await send_vip_expired_message(vip.user_id)
        await remove_from_vip_channel(vip.user_id)
```

---

# CRITERIOS DE ACEPTACIÓN

## Detección de riesgo
- [ ] Estados de usuario se actualizan automáticamente
- [ ] Risk score se calcula correctamente
- [ ] Factores de riesgo se identifican

## Mensajes de re-engagement
- [ ] Mensajes AT_RISK se envían en día 4-5
- [ ] Mensajes DORMANT se envían correctamente espaciados
- [ ] Mensaje LOST es único y final
- [ ] Variantes de mensajes funcionan

## Eventos específicos
- [ ] Mensaje de racha rota se envía
- [ ] Alertas de VIP por vencer funcionan
- [ ] Mensaje post-expiración se envía

## Incentivos
- [ ] Bonus por regreso se otorga correctamente
- [ ] Descuentos por renovación temprana funcionan
- [ ] Badges de hitos se otorgan

## Sistema de notificaciones
- [ ] Preferencias de usuario se respetan
- [ ] Horario silencioso funciona
- [ ] Límite diario se aplica

## Jobs
- [ ] Jobs se ejecutan según programación
- [ ] No hay duplicación de mensajes
- [ ] Errores se manejan sin crashear

## Analytics
- [ ] Dashboard de retención muestra datos
- [ ] Métricas se calculan correctamente
- [ ] Alertas se envían a admins

---

# NOTAS DE IMPLEMENTACIÓN

1. **No ser molesto:** Máximo 2-3 mensajes de re-engagement por usuario
2. **Respetar silencio:** Si usuario no responde a 2 mensajes, parar
3. **Horarios locales:** Considerar timezone del usuario
4. **Dignidad:** Lucien no ruega, observa y comunica
5. **Valor real:** Los incentivos deben sentirse ganados, no regalados

---

# ARCHIVOS DE REFERENCIA

- Fase 2: Sistema de Favores para bonuses
- Fase 3: Arquetipos para personalizar mensajes
- Sistema de VIP existente
- Sistema de notificaciones existente

---

*Documento generado para implementación por Claude Code*
*Proyecto: El Mayordomo del Diván*
*Fase: 7 - Retención y Anti-churn*
