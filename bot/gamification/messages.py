"""
Messages for the gamification module, especially for conversion flows.
"""

# === CONVERSIÓN FREE → VIP ===

CONVERSION_VIP_INTRO = """
Ha llegado al final del camino gratuito.

Todo lo que ha experimentado hasta ahora ha sido apenas el umbral.
Lo que viene después... requiere compromiso.
"""

CONVERSION_VIP_THE_DIVAN = """
El Diván es el espacio donde Diana se permite ser... más.

Más cercana. Más reveladora. Más vulnerable.
Más ella.

No es un lugar para todos. Pero usted ha demostrado algo.
Ha completado el Perfil de Deseo. Diana lo revisó personalmente.

Eso significa que tiene... potencial.
"""

# Archetype-based messages
ARCHETYPE_MESSAGES = {
    "EXPLORER": "Su curiosidad insaciable lo trajo hasta aquí. En el Diván hay territorios que sus ojos de explorador aún no han visto.",
    "DIRECT": "No pierde tiempo. Respeto eso. El Diván es acceso directo a lo que realmente busca. Sin filtros innecesarios.",
    "ROMANTIC": "Busca conexión genuina. El Diván es donde Diana permite que esa conexión florezca. Donde deja de ser solo Kinky.",
    "ANALYTICAL": "Ha analizado cada paso. El Diván contiene las piezas que completan el rompecabezas de Diana.",
    "PERSISTENT": "Su persistencia lo trajo aquí. El Diván es la recompensa para quienes no se rinden ante el primer obstáculo.",
    "PATIENT": "Ha esperado. Ha observado. Ha demostrado que entiende que lo valioso toma tiempo. El Diván está listo para usted.",
    "DEFAULT": "Ha demostrado mérito. Eso es suficiente para que Diana considere abrirle las puertas del Diván."
}

CONVERSION_VIP_OFFER = """
La Llave del Diván está disponible.

No es solo un pago. Es una declaración:
'Estoy listo para ver más. Para conocer más. Para ser parte de esto.'

¿Desea conocer las condiciones de acceso?
"""

CONVERSION_VIP_BENEFITS = """
La Llave del Diván otorga:

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

{price} {currency}
{discount_text}

━━━━━━━━━━━━━━━━━━━━━━━━

Diana no ofrece pruebas gratuitas.
Esto es confianza. O no lo es.
"""

CONVERSION_VIP_MANUAL_PAYMENT_INFO = """
━━━━━━━━━━━━━━━━━━━━━━━━
💳 INFORMACIÓN DE PAGO
━━━━━━━━━━━━━━━━━━━━━━━━

Banco: {bank_name}
Cuenta: {account_number}
Titular: {account_holder}
Tipo: {account_type}
{additional_info}
━━━━━━━━━━━━━━━━━━━━━━━━
💰 MONTO A TRANSFERIR
━━━━━━━━━━━━━━━━━━━━━━━━

{price} {currency}

━━━━━━━━━━━━━━━━━━━━━━━━

Por favor realice la transferencia y luego
confirme su pago enviando la captura de pantalla.

Diana verificará su pago manualmente.
El proceso usualmente toma menos de 24 horas.
"""

CONVERSION_VIP_REQUEST_SCREENSHOT = "Por favor envíe la captura de pantalla de su transferencia."

CONVERSION_VIP_SCREENSHOT_RECEIVED = """
✅ Confirmación recibida

Su solicitud de pago ha sido enviada a Diana para verificación.

Producto: La Llave del Diván
Monto: {price} {currency}

Será notificado en cuanto Diana apruebe su pago
(usualmente dentro de 24 horas).

Puede verificar el estado en el menú principal.
"""

CONVERSION_VIP_DECLINED = """
Comprensible. La decisión debe ser suya.

La invitación permanece abierta.
Cuando esté listo, puede encontrarla en el menú principal.

Mientras tanto, el contenido de Los Kinkys sigue disponible.
Aunque... después de lo que ha visto, quizás le sepa diferente.
"""

# Admin notifications
ADMIN_NEW_PENDING_PAYMENT = """
🔔 NUEVO PAGO PENDIENTE

━━━━━━━━━━━━━━━━━━━━━━━━
👤 USUARIO
━━━━━━━━━━━━━━━━━━━━━━━━

Nombre: {full_name}
Username: @{username}
ID: {user_id}

━━━━━━━━━━━━━━━━━━━━━━━━
🛍️ PRODUCTO
━━━━━━━━━━━━━━━━━━━━━━━━

La Llave del Diván
Monto: {amount} {currency}

━━━━━━━━━━━━━━━━━━━━━━━━
📸 COMPROBANTE
━━━━━━━━━━━━━━━━━━━━━━━━
"""

ADMIN_PAYMENT_APPROVED = """
✅ Pago aprobado

El usuario ha sido notificado y su acceso activado.

Acciones realizadas:
• Usuario agregado al canal VIP
• Suscripción activada hasta {expiry_date}
• 15 Favores de bienvenida otorgados
• Narrativa Nivel 4 desbloqueada
"""

USER_PAYMENT_APPROVED = """
🎉 ¡SU PAGO HA SIDO APROBADO!

Bienvenido al Diván.

La Llave es suya. El acceso ha sido activado.
Diana ha sido notificada de su llegada.

Su viaje continúa. Pero ahora, en territorio diferente.

+15 Favores de bienvenida añadidos.
"""

ADMIN_PAYMENT_REJECTED = "El usuario será notificado del rechazo."

USER_PAYMENT_REJECTED = """
❌ Pago no verificado

Diana revisó su comprobante pero no pudo verificar el pago.

Por favor contacte directamente a Diana para aclarar
la situación: @{admin_username}

Su solicitud ha sido archivada.
"""

# === MENSAJES DE LUCIEN (F6.9) ===

LUCIEN_VIP_OFFER_MESSAGES = {
    "EXPLORER": [
        "Lucien observa: Tu curiosidad te ha traído hasta el umbral del Diván. ¿Te atreves a cruzarlo?",
        "Lucien susurra: El conocimiento verdadero no se comparte con cualquiera, pero tú... has demostrado ser digno de consideración."
    ],
    "DIRECT": [
        "Lucien reconoce: No has venido a perder el tiempo. El Diván requiere compromiso real. ¿Estás dispuesto a dárselo?",
        "Lucien advierte: Una vez que cruces, no hay vuelta atrás. ¿Tu decisión está tomada?"
    ],
    "ROMANTIC": [
        "Lucien siente: Buscas conexión auténtica. El Diván es donde Diana revela su esencia más profunda. ¿Estás listo para recibirlo?",
        "Lucien percibe: Tu corazón anhela más que superficie. En el Diván, encontrarás lo que realmente buscas."
    ],
    "ANALYTICAL": [
        "Lucien analiza: Cada paso tuyo ha sido medido y evaluado. El Diván es la culminación de tu proceso. ¿Es este tu veredicto final?",
        "Lucien concluye: Has comprendido el juego hasta ahora. El siguiente nivel requiere inversión. ¿Aceptas el desafío?"
    ],
    "PERSISTENT": [
        "Lucien afirma: Tu tenacidad te ha traído hasta aquí. El Diván es la recompensa para quienes no se rinden. ¿Serás uno de ellos?",
        "Lucien reconoce: Has demostrado resistencia. Ahora debes demostrar compromiso. ¿Vas a cruzar el umbral?"
    ],
    "PATIENT": [
        "Lucien observa: Tu paciencia ha sido notable. El Diván se abre solo para quienes entienden que lo valioso toma tiempo. ¿Has comprendido el mensaje?",
        "Lucien siente: Esperar es una forma de sabiduría. ¿Estás preparado para lo que mereces?"
    ],
    "DEFAULT": [
        "Lucien te observa: Has recorrido un camino largo. El Diván es el siguiente paso para almas como la tuya.",
        "Lucien te pregunta: ¿Estás listo para trascender lo ordinario?"
    ]
}
