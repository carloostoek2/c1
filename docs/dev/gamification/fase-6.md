# REQUERIMIENTO: FASE 6 - CONVERSIÓN Y UPSELL
## Proyecto: El Mayordomo del Diván
## Bot de Telegram para Señorita Kinky

---

# CONTEXTO

La conversión no es una venta. Es el momento donde Lucien presenta una puerta y el usuario decide si la cruza. Cada oferta debe sentirse como una revelación, no como un pitch comercial.

**Principio fundamental:** El usuario debe desear el siguiente nivel ANTES de que se le ofrezca. La narrativa construye el deseo, la oferta solo lo captura.

**Flujos de conversión:**
1. **Free → VIP** ("La Llave del Diván")
2. **VIP → Premium** (Contenido exclusivo individual)
3. **VIP → Mapa del Deseo** (Paquetes de 3 tiers)

**Dependencias:**
- Fase 5 completada (narrativa crea el contexto)
- Sistema de pagos existente en el bot
- Canales VIP/Free configurados

---

# ARQUITECTURA DE CONVERSIÓN

## Momentos de conversión (triggers)

| Momento | Trigger | Tipo de Oferta |
|---------|---------|----------------|
| Fin de Nivel 3 narrativo | Completar Perfil de Deseo | Llave del Diván (Free→VIP) |
| Usuario Free nivel 4+ con alta actividad | 7+ días activo, 20+ Favores | Recordatorio sutil VIP |
| Easter egg de contenido VIP | Ver preview bloqueado | Oferta contextual VIP |
| Usuario VIP completa Nivel 4 | Evaluación de comprensión | Intro a Premium |
| Usuario VIP nivel 5+ | 30+ días como VIP | Mapa del Deseo |
| Usuario VIP completa Nivel 6 | Culminación narrativa | Círculo Íntimo directo |
| Contenido Premium publicado | Nuevo contenido disponible | Oferta de pieza individual |

## Tipos de oferta

| Tipo | Descripción | Presión |
|------|-------------|---------|
| **Narrativa** | Surge naturalmente de la historia | Ninguna |
| **Contextual** | Aparece cuando usuario muestra interés | Baja |
| **Recordatorio** | Para usuarios que vieron oferta pero no compraron | Media |
| **Urgencia** | Descuento por tiempo limitado | Alta (usar con moderación) |

---

# F6.1: FLUJO FREE → VIP ("LA LLAVE DEL DIVÁN")

## Trigger principal
Usuario completa Nivel 3 de narrativa (Perfil de Deseo)

## Secuencia completa

### Paso 1: Transición desde narrativa
```
[Después de completar L3_10 - La Invitación]

Speaker: LUCIEN
Delay: 3 segundos

"Ha llegado al final del camino gratuito.

Todo lo que ha experimentado hasta ahora - las pruebas, las revelaciones, 
los fragmentos de Diana - ha sido apenas el umbral.

Lo que viene después... requiere compromiso."
```

### Paso 2: Presentación del Diván
```
Speaker: LUCIEN
Delay: 2 segundos

"El Diván es el espacio donde Diana se permite ser... más.

Más cercana. Más reveladora. Más vulnerable.
Más ella.

No es un lugar para todos. Pero usted ha demostrado algo.
Ha completado el Perfil de Deseo. Diana lo revisó personalmente.

Eso significa que tiene... potencial."
```

### Paso 3: Reconocimiento por arquetipo
```
Speaker: LUCIEN
Delay: 2 segundos

[VARIACIÓN POR ARQUETIPO]

EXPLORER:
"Su curiosidad insaciable lo trajo hasta aquí. En el Diván hay 
territorios que sus ojos de explorador aún no han visto."

DIRECT:
"No pierde tiempo. Respeto eso. El Diván es acceso directo 
a lo que realmente busca. Sin filtros innecesarios."

ROMANTIC:
"Busca conexión genuina. El Diván es donde Diana permite 
que esa conexión florezca. Donde deja de ser solo Kinky."

ANALYTICAL:
"Ha analizado cada paso. El Diván contiene las piezas 
que completan el rompecabezas de Diana."

PERSISTENT:
"Su persistencia lo trajo aquí. El Diván es la recompensa 
para quienes no se rinden ante el primer obstáculo."

PATIENT:
"Ha esperado. Ha observado. Ha demostrado que entiende 
que lo valioso toma tiempo. El Diván está listo para usted."

[SIN ARQUETIPO DEFINIDO]:
"Ha demostrado mérito. Eso es suficiente para que Diana 
considere abrirle las puertas del Diván."
```

### Paso 4: La oferta
```
Speaker: LUCIEN
Delay: 2 segundos

"La Llave del Diván está disponible.

No es solo un pago. Es una declaración:
'Estoy listo para ver más. Para conocer más. Para ser parte de esto.'

¿Desea conocer las condiciones de acceso?"

[BOTONES]
[🔑 Ver la Llave del Diván]    [Necesito pensarlo]
```

### Paso 5A: Si toca "Ver la Llave"
```
Speaker: LUCIEN

"La Llave del Diván otorga:

━━━━━━━━━━━━━━━━━━━━━━━━
🔑 ACCESO PERMANENTE
━━━━━━━━━━━━━━━━━━━━━━━━

• Entrada al canal privado de Diana
• Contenido que jamás aparecerá en Los Kinkys
• Archivo de +2000 publicaciones exclusivas
• Niveles narrativos 4, 5 y 6
• Su nombre en el registro personal de Diana

━━━━━━━━━━━━━━━━━━━━━━━━
💰 INVERSIÓN
━━━━━━━━━━━━━━━━━━━━━━━━

{precio} {moneda}
{Si tiene descuento por nivel/favores: 'Precio especial por su nivel: {precio_descuento}'}

━━━━━━━━━━━━━━━━━━━━━━━━

Diana no ofrece pruebas gratuitas.
Esto es confianza. O no lo es."

[BOTONES]
[🔑 Obtener mi Llave]    [Tengo preguntas]    [Ahora no]
```

### Paso 5B: Si toca "Necesito pensarlo"
```
Speaker: LUCIEN

"Comprensible. La decisión debe ser suya, no mía.

La invitación permanece abierta. Cuando esté listo, 
puede encontrarla en el menú principal.

Mientras tanto, el contenido de Los Kinkys sigue disponible.
Aunque... después de lo que ha visto, quizás le sepa diferente."

[Guardar estado: invitation_pending = true]
[Volver al menú principal]
```

### Paso 6: Proceso de pago
```
[Si toca "Obtener mi Llave"]

Speaker: SYSTEM

"Procesando solicitud de Llave del Diván...

Será redirigido al proceso de pago.
Una vez completado, su acceso se activará automáticamente."

[BOTÓN DE PAGO - Integrar con sistema existente]
```

### Paso 7A: Pago exitoso
```
Speaker: LUCIEN

"Bienvenido al Diván.

La Llave es suya. El acceso ha sido activado.

Diana ha sido notificada de su llegada. No espere una bienvenida 
inmediata - ella aparece cuando lo decide. Pero sabe que está aquí.

Su viaje continúa. Pero ahora, en territorio diferente.

+15 Favores de bienvenida han sido añadidos a su cuenta."

[BOTÓN]
[Entrar al Diván]

[Acciones técnicas:]
- Agregar usuario a canal VIP
- Crear registro de suscripción
- Otorgar 15 Favores de bienvenida
- Activar narrativa Nivel 4
- Enviar notificación de nuevo miembro (si está configurado)
```

### Paso 7B: Pago fallido/cancelado
```
Speaker: LUCIEN

"El proceso no se completó.

No hay problema. La invitación sigue vigente.
Cuando esté listo, la Llave estará esperando.

Puede encontrarla en cualquier momento desde el menú."

[Volver al menú]
```

---

# F6.2: OFERTAS CONTEXTUALES VIP (Para Free que no han comprado)

## Trigger: Usuario Free con alta actividad
Condiciones:
- Nivel 3+ de Favores (15+)
- 7+ días desde registro
- No ha visto oferta en últimos 3 días
- No tiene `invitation_declined_permanent`

## Mensaje contextual sutil
```
Speaker: LUCIEN
[Aparece después de interacción normal]

"Una observación, si me permite.

Su actividad en Los Kinkys ha sido... notable.
{reactions_count} reacciones. {days_active} días de presencia.

Diana nota a quienes realmente prestan atención.

Hay contenido en el Diván que creo apreciaría.
No es una venta. Es una observación."

[BOTONES]
[Cuéntame más]    [Quizás después]

[Si ignora: no volver a mostrar por 7 días]
```

## Trigger: Usuario ve contenido bloqueado
```
[Usuario intenta acceder a contenido marcado como VIP-only]

Speaker: LUCIEN

"Este contenido está reservado para el Diván.

Es uno de los {count} archivos exclusivos que Diana 
guarda para quienes han cruzado el umbral.

Si tiene curiosidad por lo que hay detrás de esta puerta..."

[BOTONES]
[Ver cómo acceder]    [Entendido]
```

---

# F6.3: FLUJO VIP → PREMIUM (Contenido individual)

## Contexto
Premium es contenido extra que se vende por pieza individual:
- Videos de mayor duración
- Contenido más explícito
- Producciones especiales

## Trigger: Nuevo contenido Premium disponible
```
[Broadcast a usuarios VIP cuando hay nuevo Premium]

Speaker: LUCIEN

"Hay algo nuevo en la colección de Diana.

'{nombre_contenido}'
{descripción_breve}

Duración: {duración}
Categoría: {categoría}

Este contenido no está incluido en el Diván estándar.
Es una producción especial que Diana preparó aparte.

Precio: {precio}"

[BOTONES]
[Ver preview]    [Adquirir ahora]    [No me interesa]
```

## Trigger: Usuario completa Nivel 4 narrativo
```
Speaker: LUCIEN

"Ha demostrado comprensión del Diván.

Hay contenido que Diana reserva para quienes llegan a este punto.
No es parte del archivo regular. Es... Premium.

Producciones especiales. Mayor duración. Mayor intensidad.

Si desea explorar esta categoría, el catálogo está disponible."

[BOTONES]
[Ver catálogo Premium]    [Continuar con la historia]
```

## Vista de catálogo Premium
```
Speaker: LUCIEN

"El Catálogo Premium de Diana:

━━━━━━━━━━━━━━━━━━━━━━━━

{Para cada item Premium disponible:}

📹 {nombre}
{descripción_corta}
Duración: {duración} | Precio: {precio}
[Ver detalles]

━━━━━━━━━━━━━━━━━━━━━━━━

Estos contenidos son independientes de su suscripción.
Una vez adquiridos, son suyos permanentemente."

[BOTONES por cada item]
[🔙 Volver]
```

---

# F6.4: FLUJO VIP → MAPA DEL DESEO (Paquetes)

## Contexto
El Mapa del Deseo son 3 tiers de compromiso creciente:
1. **La Llave Premium** - VIP + 2 videos Premium (bundle)
2. **Círculo Íntimo** - Todo lo anterior + sesión personalizada
3. **El Secreto** - Acceso total + comunicación libre con Diana

## Trigger: Usuario VIP nivel 5+ o completa Nivel 5 narrativo
```
Speaker: DIANA
[Sí, Diana habla directamente aquí - momento especial]

"Has llegado lejos.

Más lejos que la mayoría. Has visto cosas que otros no verán nunca.
Pero aún hay territorios que no has explorado.

Hay un mapa. Mi mapa. El Mapa del Deseo.

Tres niveles de acceso a... mí.

Lucien te explicará los detalles. 
Pero quería que supieras: esto es personal."
```

```
Speaker: LUCIEN
Delay: 3 segundos

"Lo que Diana acaba de ofrecerle es significativo.

El Mapa del Deseo no es un producto. Es un camino.
Tres niveles de proximidad. Tres niveles de compromiso.

Permítame explicar cada uno."
```

## Presentación de Tiers

### Tier 1: La Llave Premium
```
Speaker: LUCIEN

"━━━━━━━━━━━━━━━━━━━━━━━━
🗝️ NIVEL 1: LA LLAVE PREMIUM
━━━━━━━━━━━━━━━━━━━━━━━━

Incluye:
• Suscripción completa al Diván (1 mes)
• 2 videos Premium seleccionados por Diana
• Acceso a la narrativa completa
• Badge 'Portador de la Llave Premium'

Valor por separado: {valor_separado}
Precio del Mapa: {precio_tier1}
Ahorro: {ahorro}

Este es el primer paso. La entrada formal al camino."

[BOTONES]
[Ver siguiente nivel]    [Elegir este nivel]
```

### Tier 2: Círculo Íntimo
```
Speaker: LUCIEN

"━━━━━━━━━━━━━━━━━━━━━━━━
💫 NIVEL 2: CÍRCULO ÍNTIMO
━━━━━━━━━━━━━━━━━━━━━━━━

Todo lo del Nivel 1, más:
• Sesión personalizada con Diana
• Trato directo para esa sesión
• Contenido creado según sus preferencias
• Badge 'Miembro del Círculo'
• Acceso prioritario a contenido nuevo

Precio: {precio_tier2}

Aquí Diana deja de ser una figura distante.
Se dirige a usted. Personalmente."

[BOTONES]
[Ver siguiente nivel]    [Elegir este nivel]    [Volver al anterior]
```

### Tier 3: El Secreto
```
Speaker: LUCIEN

"━━━━━━━━━━━━━━━━━━━━━━━━
👑 NIVEL 3: EL SECRETO
━━━━━━━━━━━━━━━━━━━━━━━━

El nivel máximo del Mapa.

Todo lo anterior, más:
• Acceso total a todo el contenido Premium
• Comunicación libre con Diana (sin límites de tema)
• Participación en decisiones de contenido
• Reconocimiento como 'Guardián del Secreto'
• Acceso de por vida a contenido futuro de esta categoría

Precio: {precio_tier3}

Este nivel es para quienes no quieren límites.
Para quienes buscan la conexión completa.

No es para todos. Es para los guardianes de sus secretos más profundos."

[BOTONES]
[Elegir este nivel]    [Volver a ver opciones]    [Necesito pensarlo]
```

## Comparativa de Tiers
```
Speaker: LUCIEN
[Si usuario pide comparar]

"Los tres niveles, lado a lado:

┌─────────────────────────────────────────────────────────┐
│                    MAPA DEL DESEO                       │
├─────────────────────────────────────────────────────────┤
│ Beneficio          │ Llave  │ Círculo │ Secreto        │
├─────────────────────────────────────────────────────────┤
│ Suscripción VIP    │   ✓    │    ✓    │    ✓           │
│ 2 Videos Premium   │   ✓    │    ✓    │    ✓           │
│ Sesión personal    │   ✗    │    ✓    │    ✓           │
│ Todo Premium       │   ✗    │    ✗    │    ✓           │
│ Comunicación libre │   ✗    │    ✗    │    ✓           │
│ Contenido futuro   │   ✗    │    ✗    │    ✓           │
├─────────────────────────────────────────────────────────┤
│ Precio             │ {t1}   │  {t2}   │   {t3}         │
└─────────────────────────────────────────────────────────┘

La decisión depende de qué tan profundo desea llegar."

[BOTONES]
[Elegir Llave Premium]    [Elegir Círculo]    [Elegir Secreto]
```

---

# F6.5: SISTEMA DE DESCUENTOS Y URGENCIA

## Descuentos por mérito

| Condición | Descuento | Aplicable a |
|-----------|-----------|-------------|
| Nivel 5+ de Favores | 5% | VIP, Premium |
| Nivel 6+ de Favores | 10% | VIP, Premium, Mapa |
| Racha 30+ días | 5% adicional | Todo |
| Primera compra | 10% | Solo VIP |
| Referido activo | 15% | VIP |
| Badge "Guardián de Secretos" | 15% | Todo |

## Descuentos por tiempo limitado
```
[Usar con moderación - máximo 1 vez al mes]

Speaker: LUCIEN

"Una oportunidad limitada.

Por las próximas {horas} horas, Diana ha autorizado 
un descuento especial en {producto}.

Precio regular: {precio_regular}
Precio especial: {precio_descuento}
Ahorro: {ahorro}

⏰ Expira en: {countdown}

Esta oferta no se repetirá pronto."

[BOTONES]
[Aprovechar oferta]    [Dejar pasar]
```

## Recordatorio de carrito abandonado
```
[Si usuario vio oferta pero no completó - después de 24-48 horas]

Speaker: LUCIEN

"Una nota sobre su visita anterior.

Revisó la información sobre {producto} pero no completó el proceso.

No es presión. Solo... seguimiento.

La oferta sigue disponible. Las condiciones no han cambiado.
{Si había descuento que expiró: 'Aunque el descuento especial ya no está vigente.'}

Si tiene dudas que pueda resolver, estoy aquí."

[BOTONES]
[Retomar donde dejé]    [Tengo preguntas]    [No me interesa]
```

---

# F6.6: MANEJO DE OBJECIONES

## Objeciones comunes y respuestas de Lucien

### "Es muy caro"
```
Speaker: LUCIEN

"Entiendo la consideración.

El precio refleja lo que Diana invierte en crear este contenido.
No es producción masiva. Es trabajo personal, íntimo.

Dicho esto, hay opciones:
• Puede empezar con contenido Premium individual
• Puede acumular Favores para descuentos
• Puede esperar ofertas especiales (aparecen ocasionalmente)

La puerta no se cierra. Solo usted decide cuándo cruzarla."
```

### "No estoy seguro de que valga la pena"
```
Speaker: LUCIEN

"Una duda razonable.

No puedo garantizarle que valdrá la pena para usted.
Lo que puedo decirle es esto:

• {count_vip} personas están actualmente en el Diván
• El contenido se actualiza {frecuencia}
• La narrativa tiene {chapters} capítulos exclusivos
• Diana interactúa directamente con miembros

Pero el valor es subjetivo. Solo usted sabe lo que busca.
Si no está seguro, quizás no es el momento."
```

### "¿Hay prueba gratuita?"
```
Speaker: LUCIEN

"No.

Diana no ofrece pruebas. Nunca lo ha hecho.

Lo que ofrece es el contenido gratuito en Los Kinkys.
Si eso le ha interesado, el Diván es la continuación natural.
Si no... quizás este no es el lugar para usted.

No lo digo con desprecio. Lo digo con honestidad."
```

### "Quiero cancelar / ya no me interesa"
```
Speaker: LUCIEN

"Respetado.

Su decisión es suya. No intentaré convencerlo.

Si cambia de opinión en el futuro, la puerta sigue ahí.
Su progreso en la narrativa se conserva.
Sus Favores permanecen.

Diana no persigue a quienes se van. 
Pero tampoco olvida a quienes estuvieron."

[Marcar: user_declined_permanent = true]
[No mostrar ofertas por 30 días]
```

---

# F6.7: TRACKING Y ANALYTICS

## Eventos a registrar

| Evento | Datos | Propósito |
|--------|-------|-----------|
| offer_shown | user_id, offer_type, trigger, timestamp | Medir alcance |
| offer_clicked | user_id, offer_type, button_clicked | Medir interés |
| offer_abandoned | user_id, offer_type, step_abandoned | Identificar fricción |
| purchase_started | user_id, product, price, discounts | Inicio de conversión |
| purchase_completed | user_id, product, price, payment_method | Conversión exitosa |
| purchase_failed | user_id, product, error_type | Problemas técnicos |
| objection_raised | user_id, objection_type | Entender barreras |

## Modelo de datos para tracking

```python
class ConversionEvent(Base):
    __tablename__ = 'conversion_events'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'))
    event_type: Mapped[str]  # offer_shown, offer_clicked, etc.
    offer_type: Mapped[str]  # vip, premium, map_tier1, etc.
    trigger: Mapped[str]     # narrative, contextual, reminder, etc.
    metadata: Mapped[str]    # JSON con datos adicionales
    created_at: Mapped[datetime]
```

## Métricas clave

```
Calcular periódicamente:

1. Conversion Rate por trigger
   = purchases / offers_shown * 100

2. Funnel Drop-off
   = En qué paso abandonan más usuarios

3. Time to Convert
   = Promedio de días desde primera oferta hasta compra

4. Average Order Value
   = Total revenue / Total purchases

5. Offer Fatigue
   = Conversion rate por número de veces que usuario vio oferta
```

---

# F6.8: INTEGRACIÓN CON SISTEMA DE PAGOS

## Verificar sistema existente

### Tarea
1. Identificar cómo se procesan pagos actualmente
2. Localizar handlers de pago existentes
3. Entender flujo de activación de VIP

PROPUESTA: ADAPTACIÓN A PAGO MANUAL

  🎯 Cambios Principales

  1. Nuevo Modelo de Base de Datos

  # bot/gamification/database/models.py

  class PendingPayment(Base):
      """Pagos pendientes de aprobación por admin."""

      __tablename__ = 'pending_payments'

      id: Mapped[int] = mapped_column(primary_key=True)
      user_id: Mapped[int]
      product_type: Mapped[str]  # 'vip', 'premium', 'map_tier1', etc.
      product_id: Mapped[Optional[int]]  # ID del producto si aplica
      amount: Mapped[float]  # Monto pagado
      currency: Mapped[str] = mapped_column(default='USD')

      screenshot_file_id: Mapped[str]  # ID del archivo en Telegram
      screenshot_message_id: Mapped[int]  # Para reenviar al admin

      status: Mapped[str]  # 'pending', 'approved', 'rejected'
      admin_notes: Mapped[Optional[str]]  # Notas del admin

      created_at: Mapped[datetime]
      processed_at: Mapped[Optional[datetime]]
      processed_by: Mapped[Optional[int]]  # Admin que procesó

  ---
  2. Configuración de Datos Bancarios

  # bot/gamification/config.py

  PAYMENT_INFO = {
      'bank_name': 'Nombre del Banco',
      'account_number': 'XXXX-XXXX-XXXX',
      'account_holder': 'Diana [Apellido]',
      'account_type': 'Ahorros / Corriente',
      'additional_info': 'Información adicional si es necesaria'
  }

  ---
  3. Flujo de Usuario Adaptado

  ANTES (Paso 5A - Original):
  [🔑 Obtener mi Llave] → Sistema de pago automatizado

  DESPUÉS (Paso 5A - Manual):
  Usuario: Click "🔑 Obtener mi Llave"

  Bot (Lucien):
  "
  ━━━━━━━━━━━━━━━━━━━━━━━━
  💳 INFORMACIÓN DE PAGO
  ━━━━━━━━━━━━━━━━━━━━━━━━

  Banco: [nombre]
  Cuenta: [número]
  Titular: [nombre]
  Tipo: [ahorros/corriente]

  ━━━━━━━━━━━━━━━━━━━━━━━━
  💰 MONTO A TRANSFERIR
  ━━━━━━━━━━━━━━━━━━━━━━━━

  ${precio} {moneda}

  ━━━━━━━━━━━━━━━━━━━━━━━━

  Por favor realice la transferencia y luego
  confirme su pago enviando la captura de pantalla.

  Diana verificará su pago manualmente.
  El proceso usualmente toma menos de 24 horas.
  "

  [Botones]
  [✅ Ya realicé el pago]  [❌ Cancelar]

  Paso 5B - Usuario confirma pago:
  Usuario: Click "✅ Ya realicé el pago"

  Bot: Entra en estado FSM "waiting_for_payment_screenshot"

  "Por favor envíe la captura de pantalla de su transferencia."

  [Botón]
  [Cancelar]

  Paso 5C - Usuario envía captura:
  Usuario: Envía foto

  Bot:
  "
  ✅ Confirmación recibida

  Su solicitud de pago ha sido enviada a Diana para verificación.

  Producto: La Llave del Diván
  Monto: ${precio}

  Será notificado en cuanto Diana apruebe su pago
  (usualmente dentro de 24 horas).

  Puede verificar el estado en el menú principal.
  "

  [Botón]
  [Volver al menú]

  [Acciones técnicas:]
  - Crear registro PendingPayment (status=pending)
  - Guardar screenshot_file_id
  - Enviar notificación a admin
  - state.clear()

  ---
  4. Flujo de Admin (Nuevo)

  Notificación recibida por Admin:
  Bot → Admin (Diana):

  "
  🔔 NUEVO PAGO PENDIENTE

  ━━━━━━━━━━━━━━━━━━━━━━━━
  👤 USUARIO
  ━━━━━━━━━━━━━━━━━━━━━━━━

  Nombre: {first_name} {last_name}
  Username: @{username}
  ID: {user_id}

  ━━━━━━━━━━━━━━━━━━━━━━━━
  🛍️ PRODUCTO
  ━━━━━━━━━━━━━━━━━━━━━━━━

  La Llave del Diván
  Monto: ${precio} USD

  ━━━━━━━━━━━━━━━━━━━━━━━━
  📸 COMPROBANTE
  ━━━━━━━━━━━━━━━━━━━━━━━━
  "

  [Reenvía la foto que envió el usuario]

  [Botones]
  [✅ Aprobar Pago]  [❌ Rechazar]  [💬 Solicitar Info]

  Admin aprueba:
  Admin: Click "✅ Aprobar Pago"

  Bot → Admin:
  "
  ✅ Pago aprobado

  El usuario ha sido notificado y su acceso activado.

  Acciones realizadas:
  • Usuario agregado al canal VIP
  • Suscripción activada hasta {expiry_date}
  • 15 Favores de bienvenida otorgados
  • Narrativa Nivel 4 desbloqueada
  "

  Bot → Usuario:
  "
  🎉 ¡SU PAGO HA SIDO APROBADO!

  Bienvenido al Diván.

  La Llave es suya. El acceso ha sido activado.
  Diana ha sido notificada de su llegada.

  Su viaje continúa. Pero ahora, en territorio diferente.

  +15 Favores de bienvenida añadidos.
  "

  [Botón]
  [Entrar al Diván]

  Admin rechaza:
  Admin: Click "❌ Rechazar"

  Bot → Admin:
  "El usuario será notificado del rechazo."

  Bot → Usuario:
  "
  ❌ Pago no verificado

  Diana revisó su comprobante pero no pudo verificar el pago.

  Por favor contacte directamente a Diana para aclarar
  la situación: @diana_username

  Su solicitud ha sido archivada.
  "

  [Botón]
  [Contactar a Diana]  [Volver al menú]

  ---
  📁 Archivos a Crear/Modificar

  bot/gamification/
  ├── database/
  │   └── models.py                    → Agregar PendingPayment
  │
  ├── services/
  │   ├── conversion_service.py        → NUEVO: Lógica de conversión
  │   └── payment_service.py           → NUEVO: Gestión pagos manuales
  │
  ├── handlers/
  │   ├── user_conversion.py           → NUEVO: Handlers usuario
  │   └── admin_payments.py            → NUEVO: Handlers admin aprobación
  │
  ├── states/
  │   └── conversion.py                → NUEVO: FSM waiting_for_payment_screenshot
  │
  └── config.py                        → Agregar PAYMENT_INFO

  ---
  ✅ Ventajas de Este Enfoque

  1. Mantiene narrativa intacta: Lucien sigue siendo el mayordomo
  2. Flexible: Puedes cambiar datos bancarios sin tocar código
  3. Trazabilidad: Todos los pagos quedan registrados en BD
  4. Admin control: Diana aprueba manualmente (seguridad)
  5. Automatización post-aprobación: Una vez aprobado, todo se activa automáticamente
  6. Futuro-proof: Si algún día quieres automatizar pagos, solo cambias el handler

  ---
  🤔 ¿Te parece bien este enfoque?

  Si estás de acuerdo, puedo empezar a implementar:

  SPRINT 1 (Propuesto):
  - F6.1: Flujo FREE → VIP adaptado
  - F6.8: Sistema de pagos manual
  - F6.9: Mensajes de Lucien
### Puntos de integración

```python
# El flujo de conversión debe llamar al sistema existente

async def initiate_vip_purchase(user_id: int, offer_context: dict):
    """
    Inicia proceso de compra VIP.
    
    Args:
        user_id: ID del usuario
        offer_context: {
            'trigger': str,  # 'narrative', 'contextual', etc.
            'discount_applied': float,
            'original_price': float,
            'final_price': float
        }
    
    Returns:
        payment_url o payment_message dependiendo del sistema
    """
    # Registrar evento de inicio
    await track_conversion_event(
        user_id=user_id,
        event_type='purchase_started',
        offer_type='vip',
        metadata=offer_context
    )
    
    # Llamar al sistema de pagos existente
    # ... integrar con lo que ya existe ...
```

### Webhook de pago completado

```python
async def on_payment_completed(user_id: int, product: str, transaction_id: str):
    """
    Callback cuando se completa un pago.
    
    Acciones:
    1. Activar suscripción/producto
    2. Otorgar Favores de bienvenida
    3. Activar narrativa correspondiente
    4. Enviar mensaje de confirmación de Lucien
    5. Registrar evento de conversión
    """
    if product == 'vip':
        await activate_vip_subscription(user_id)
        await grant_welcome_favors(user_id, amount=15)
        await unlock_narrative_level(user_id, level=4)
        await send_vip_welcome_message(user_id)
    
    elif product.startswith('premium_'):
        await grant_premium_content(user_id, product)
        await send_premium_purchase_confirmation(user_id, product)
    
    elif product.startswith('map_tier'):
        tier = int(product[-1])
        await activate_map_tier(user_id, tier)
        await send_map_welcome_message(user_id, tier)
    
    # Registrar conversión
    await track_conversion_event(
        user_id=user_id,
        event_type='purchase_completed',
        offer_type=product,
        metadata={'transaction_id': transaction_id}
    )
```

---

# F6.9: MENSAJES DE LUCIEN PARA CONVERSIÓN

## Agregar a biblioteca de mensajes

```python
# === CONVERSIÓN FREE → VIP ===

CONVERSION_VIP_INTRO = """
Ha llegado al final del camino gratuito.

Todo lo que ha experimentado hasta ahora ha sido apenas el umbral.
Lo que viene después... requiere compromiso.
"""

CONVERSION_VIP_BENEFITS = """
La Llave del Diván otorga:

━━━━━━━━━━━━━━━━━━━━━━━━
🔑 ACCESO PERMANENTE
━━━━━━━━━━━━━━━━━━━━━━━━

• Entrada al canal privado de Diana
• Contenido exclusivo (+2000 archivos)
• Niveles narrativos 4, 5 y 6
• Su nombre en el registro de Diana
"""

CONVERSION_VIP_SUCCESS = """
Bienvenido al Diván.

La Llave es suya. El acceso ha sido activado.

Diana ha sido notificada de su llegada.
Su viaje continúa. Pero ahora, en territorio diferente.

+15 Favores de bienvenida añadidos.
"""

CONVERSION_VIP_DECLINED = """
Comprensible. La decisión debe ser suya.

La invitación permanece abierta.
Cuando esté listo, puede encontrarla en el menú.
"""

# === PREMIUM ===

CONVERSION_PREMIUM_INTRO = """
Hay contenido que Diana reserva aparte.

No es parte del archivo regular. Es... Premium.
Producciones especiales. Mayor intensidad.
"""

CONVERSION_PREMIUM_SUCCESS = """
'{product_name}' es suyo.

El contenido ha sido desbloqueado en su biblioteca.
Diana fue notificada de su adquisición.
"""

# === MAPA DEL DESEO ===

CONVERSION_MAP_INTRO = """
El Mapa del Deseo no es un producto.
Es un camino. Tres niveles de proximidad a Diana.
"""

CONVERSION_MAP_TIER1_SUCCESS = """
La Llave Premium es suya.

Ha dado el primer paso en el Mapa del Deseo.
Su suscripción y contenido Premium están activos.
"""

CONVERSION_MAP_TIER2_SUCCESS = """
Bienvenido al Círculo Íntimo.

Diana preparará su sesión personalizada.
Será contactado para coordinar los detalles.
"""

CONVERSION_MAP_TIER3_SUCCESS = """
Ha alcanzado El Secreto.

El nivel máximo. Sin límites. Sin barreras.
Diana ha sido notificada personalmente.

A partir de ahora, la comunicación es directa.
Úsela con sabiduría.
"""

# === OBJECIONES ===

OBJECTION_PRICE = """
Entiendo la consideración.

El precio refleja trabajo personal, íntimo.
Hay opciones: contenido individual, descuentos por Favores, ofertas especiales.

La puerta no se cierra. Solo usted decide cuándo cruzarla.
"""

OBJECTION_VALUE = """
Una duda razonable.

No puedo garantizar que valdrá la pena para usted.
El valor es subjetivo. Solo usted sabe lo que busca.

Si no está seguro, quizás no es el momento.
"""

OBJECTION_NO_TRIAL = """
Diana no ofrece pruebas. Nunca lo ha hecho.

El contenido gratuito en Los Kinkys es la muestra.
Si eso le interesó, el Diván es la continuación.
Si no... quizás este no es el lugar.
"""
```

---

# F6.10: COMANDOS Y HANDLERS

## Comando /vip (acceso directo a oferta)
```
[Para usuarios Free que quieren ver oferta sin esperar trigger]

/vip o botón "Acceder al Diván" en menú

Si usuario es Free:
    → Mostrar oferta de Llave del Diván

Si usuario es VIP:
    → Mostrar estado de suscripción + días restantes
    → Opción de renovar si está por vencer
```

## Comando /premium (catálogo premium)
```
[Para usuarios VIP]

/premium o botón "Contenido Premium"

Si usuario es Free:
    → "El contenido Premium está disponible para miembros del Diván."

Si usuario es VIP:
    → Mostrar catálogo de contenido Premium disponible
```

## Comando /mapa (Mapa del Deseo)
```
[Para usuarios VIP nivel 5+]

/mapa o botón "Mapa del Deseo"

Si usuario es Free:
    → Redirigir a oferta VIP primero

Si usuario es VIP < nivel 5:
    → "El Mapa del Deseo se revela a quienes alcanzan el nivel 5."

Si usuario es VIP nivel 5+:
    → Mostrar presentación del Mapa del Deseo
```

---

# CRITERIOS DE ACEPTACIÓN

## Flujo Free → VIP
- [ ] Trigger desde narrativa Nivel 3 funciona
- [ ] Secuencia completa de mensajes de Lucien
- [ ] Variación por arquetipo implementada
- [ ] Integración con sistema de pagos
- [ ] Mensaje de bienvenida post-compra
- [ ] Favores de bienvenida otorgados
- [ ] Usuario agregado a canal VIP

## Ofertas contextuales
- [ ] Trigger por alta actividad funciona
- [ ] Trigger por contenido bloqueado funciona
- [ ] Rate limiting de ofertas (no spam)
- [ ] Opción de "no molestar" respetada

## Premium y Mapa del Deseo
- [ ] Catálogo Premium visible para VIP
- [ ] Presentación de 3 tiers del Mapa
- [ ] Comparativa de tiers funciona
- [ ] Proceso de compra para cada tier

## Descuentos
- [ ] Descuentos por nivel aplicados
- [ ] Descuentos por racha aplicados
- [ ] Descuentos combinados correctamente
- [ ] Ofertas temporales funcionan

## Tracking
- [ ] Eventos de conversión se registran
- [ ] Métricas calculables desde datos

## Manejo de objeciones
- [ ] Respuestas predefinidas funcionan
- [ ] Declinación permanente respetada

---

# NOTAS DE IMPLEMENTACIÓN

1. **No ser agresivo:** La conversión debe sentirse natural, no forzada
2. **Respetar "no":** Si usuario declina permanentemente, no insistir
3. **Rate limit ofertas:** Máximo 1 oferta contextual cada 3 días
4. **Tracking completo:** Todo evento de conversión debe registrarse
5. **Integrar con existente:** Usar sistema de pagos que ya existe

---

# ARCHIVOS DE REFERENCIA

- Fase 5: Narrativa que crea contexto para conversión
- Sistema de pagos existente en el bot
- `bot/gamification/utils/formatters.py` - Para mostrar precios
- Configuración de canales VIP/Free

---

*Documento generado para implementación por Claude Code*
*Proyecto: El Mayordomo del Diván*
*Fase: 6 - Conversión y Upsell*
