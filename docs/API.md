# Integración con la API de Telegram

Documentación técnica sobre cómo el bot interactúa con la API de Telegram, incluyendo los handlers VIP y Free.

## API de Telegram

### Configuración Básica

El bot se comunica con la API de Telegram a través del framework Aiogram 3, usando el siguiente esquema:

```python
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

bot = Bot(
    token=Config.BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)
```

## Handlers VIP y Free

### Handler de Menú VIP (`/admin` → `admin:vip`)

#### Callback Query: `admin:vip`

**Descripción:** Muestra el submenú de gestión VIP.

**Flujo de ejecución:**
1. Usuario admin selecciona "Gestión Canal VIP" en el menú principal
2. Bot recibe callback `admin:vip`
3. Bot verifica configuración del canal VIP
4. Bot envía mensaje con información del canal y opciones disponibles
5. Bot actualiza el mensaje existente con teclado VIP

**Implementación:**
```python
@admin_router.callback_query(F.data == "admin:vip")
async def callback_vip_menu(callback: CallbackQuery, session: AsyncSession):
    # Verificar si canal VIP está configurado
    is_configured = await container.channel.is_vip_channel_configured()
    
    # Construir mensaje según estado
    if is_configured:
        text = f"📺 <b>Gestión Canal VIP</b>\n\n✅ Canal configurado: <b>{channel_name}</b>..."
    else:
        text = "📺 <b>Gestión Canal VIP</b>\n\n⚠️ Canal VIP no configurado..."
    
    # Enviar mensaje con teclado VIP
    await callback.message.edit_text(
        text=text,
        reply_markup=vip_menu_keyboard(is_configured),
        parse_mode="HTML"
    )
```

**API Calls:**
- `callback.message.edit_text()` - Edita el mensaje existente con nuevo contenido
- `container.channel.is_vip_channel_configured()` - Consulta BD para verificar configuración
- `container.channel.get_vip_channel_id()` - Obtiene ID del canal VIP de la BD
- `container.channel.get_channel_info()` - Obtiene información del canal de la API de Telegram

### Configuración de Canal VIP

#### Callback Query: `vip:setup`

**Descripción:** Inicia el proceso de configuración del canal VIP.

**Flujo de ejecución:**
1. Usuario admin selecciona "⚙️ Configurar Canal VIP"
2. Bot recibe callback `vip:setup`
3. Bot entra en estado FSM `waiting_for_vip_channel`
4. Bot envía instrucciones para reenviar mensaje del canal
5. Bot espera mensaje reenviado

**Implementación:**
```python
@admin_router.callback_query(F.data == "vip:setup")
async def callback_vip_setup(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext
):
    # Entrar en estado FSM
    await state.set_state(ChannelSetupStates.waiting_for_vip_channel)
    
    text = (
        "⚙️ <b>Configurar Canal VIP</b>\n\n"
        "Para configurar el canal VIP, necesito que:\n\n"
        "1️⃣ Vayas al canal VIP\n"
        "2️⃣ Reenvíes cualquier mensaje del canal a este chat\n"
        "3️⃣ Yo extraeré el ID automáticamente\n\n"
        "⚠️ <b>Importante:</b>\n"
        "- El bot debe ser administrador del canal\n"
        "- El bot debe tener permiso para invitar usuarios\n\n"
        "👉 Reenvía un mensaje del canal ahora..."
    )
    
    await callback.message.edit_text(
        text=text,
        reply_markup=create_inline_keyboard([
            [{"text": "❌ Cancelar", "callback_data": "admin:vip"}]
        ]),
        parse_mode="HTML"
    )
```

**API Calls:**
- `state.set_state()` - Establece el estado FSM para esperar mensaje reenviado
- `callback.message.edit_text()` - Edita mensaje con instrucciones

#### Message Handler: `ChannelSetupStates.waiting_for_vip_channel`

**Descripción:** Procesa el mensaje reenviado para configurar el canal VIP.

**Flujo de ejecución:**
1. Usuario reenvía mensaje del canal VIP al bot
2. Bot recibe mensaje mientras está en estado `waiting_for_vip_channel`
3. Bot verifica que sea un reenvío de canal
4. Bot extrae ID del canal del mensaje reenviado
5. Bot configura el canal VIP
6. Bot sale del estado FSM

**Implementación:**
```python
@admin_router.message(ChannelSetupStates.waiting_for_vip_channel)
async def process_vip_channel_forward(
    message: Message,
    session: AsyncSession,
    state: FSMContext
):
    # Verificar que es un forward de un canal
    if not message.forward_from_chat:
        await message.answer(
            "❌ Debes <b>reenviar</b> un mensaje del canal VIP...",
            parse_mode="HTML"
        )
        return
    
    forward_chat = message.forward_from_chat
    
    # Verificar que es un canal
    if forward_chat.type not in ["channel", "supergroup"]:
        await message.answer(
            "❌ El mensaje debe ser de un <b>canal</b>...",
            parse_mode="HTML"
        )
        return
    
    channel_id = str(forward_chat.id)
    
    # Configurar canal VIP
    container = ServiceContainer(session, message.bot)
    success, msg = await container.channel.setup_vip_channel(channel_id)
    
    if success:
        await message.answer(
            f"✅ <b>Canal VIP Configurado</b>...",
            parse_mode="HTML",
            reply_markup=vip_menu_keyboard(True)
        )
        await state.clear()
    else:
        await message.answer(f"{msg}...", parse_mode="HTML")
```

**API Calls:**
- `message.forward_from_chat` - Accede a la información del canal reenviado
- `message.answer()` - Envía mensaje de respuesta al usuario
- `state.clear()` - Limpia el estado FSM
- `container.channel.setup_vip_channel()` - Configura el canal en la BD y verifica permisos

### Generación de Tokens VIP

#### Callback Query: `vip:generate_token`

**Descripción:** Genera un token de invitación VIP.

**Flujo de ejecución:**
1. Usuario admin selecciona "🎟️ Generar Token de Invitación"
2. Bot recibe callback `vip:generate_token`
3. Bot verifica que canal VIP esté configurado
4. Bot genera token único con duración configurable
5. Bot envía token al administrador

**Implementación:**
```python
@admin_router.callback_query(F.data == "vip:generate_token")
async def callback_generate_vip_token(
    callback: CallbackQuery,
    session: AsyncSession
):
    container = ServiceContainer(session, callback.bot)
    
    # Verificar que canal VIP está configurado
    if not await container.channel.is_vip_channel_configured():
        await callback.answer(
            "❌ Debes configurar el canal VIP primero",
            show_alert=True
        )
        return
    
    # Generar token
    token = await container.subscription.generate_vip_token(
        generated_by=callback.from_user.id,
        duration_hours=Config.DEFAULT_TOKEN_DURATION_HOURS
    )
    
    # Enviar token al admin
    token_message = (
        f"🎟️ <b>Token VIP Generado</b>\n\n"
        f"Token: <code>{token.token}</code>\n\n"
        f"⏱️ Válido por: {token.duration_hours} horas\n"
        f"📅 Expira: {token.created_at.strftime('%Y-%m-%d %H:%M')} UTC\n\n"
        f"👉 Comparte este token con el usuario."
    )
    
    await callback.message.answer(
        text=token_message,
        parse_mode="HTML"
    )
```

**API Calls:**
- `callback.answer()` - Responde al callback (con alerta si error)
- `callback.message.answer()` - Envía mensaje con token generado
- `container.subscription.generate_vip_token()` - Genera token en la BD

## Handlers Free

### Handler de Menú Free (`/admin` → `admin:free`)

#### Callback Query: `admin:free`

**Descripción:** Muestra el submenú de gestión Free.

**Flujo de ejecución:**
1. Usuario admin selecciona "Gestión Canal Free" en el menú principal
2. Bot recibe callback `admin:free`
3. Bot verifica configuración del canal Free y tiempo de espera
4. Bot envía mensaje con información del canal y tiempo de espera
5. Bot actualiza el mensaje existente con teclado Free

**Implementación:**
```python
@admin_router.callback_query(F.data == "admin:free")
async def callback_free_menu(callback: CallbackQuery, session: AsyncSession):
    container = ServiceContainer(session, callback.bot)
    
    # Verificar si canal Free está configurado
    is_configured = await container.channel.is_free_channel_configured()
    wait_time = await container.config.get_wait_time()
    
    # Construir mensaje según estado
    if is_configured:
        text = f"📺 <b>Gestión Canal Free</b>\n\n✅ Canal configurado: <b>{channel_name}</b>..."
    else:
        text = "📺 <b>Gestión Canal Free</b>\n\n⚠️ Canal Free no configurado..."
    
    await callback.message.edit_text(
        text=text,
        reply_markup=free_menu_keyboard(is_configured),
        parse_mode="HTML"
    )
```

### Configuración de Canal Free

#### Callback Query: `free:setup`

**Descripción:** Inicia el proceso de configuración del canal Free.

**Flujo de ejecución:**
1. Usuario admin selecciona "⚙️ Configurar Canal Free"
2. Bot recibe callback `free:setup`
3. Bot entra en estado FSM `waiting_for_free_channel`
4. Bot envía instrucciones para reenviar mensaje del canal
5. Bot espera mensaje reenviado

**Implementación similar a VIP setup pero con estado `waiting_for_free_channel`.**

#### Message Handler: `ChannelSetupStates.waiting_for_free_channel`

**Descripción:** Procesa el mensaje reenviado para configurar el canal Free.

**API Calls y flujo similar a la configuración de canal VIP, pero configurando el canal Free.**

### Configuración de Tiempo de Espera

#### Callback Query: `free:set_wait_time`

**Descripción:** Inicia configuración de tiempo de espera para acceso Free.

**Flujo de ejecución:**
1. Usuario admin selecciona "⏱️ Configurar Tiempo de Espera"
2. Bot recibe callback `free:set_wait_time`
3. Bot entra en estado FSM `waiting_for_minutes`
4. Bot solicita ingresar nuevo tiempo en minutos
5. Bot espera mensaje con número de minutos

**Implementación:**
```python
@admin_router.callback_query(F.data == "free:set_wait_time")
async def callback_set_wait_time(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext
):
    container = ServiceContainer(session, callback.bot)
    current_wait_time = await container.config.get_wait_time()
    
    # Entrar en estado FSM
    await state.set_state(WaitTimeSetupStates.waiting_for_minutes)
    
    text = (
        f"⏱️ <b>Configurar Tiempo de Espera</b>\n\n"
        f"Tiempo actual: <b>{current_wait_time} minutos</b>\n\n"
        f"Envía el nuevo tiempo de espera en minutos.\n"
        f"Ejemplo: <code>5</code>\n\n"
        f"El tiempo debe ser mayor o igual a 1 minuto."
    )
    
    await callback.message.edit_text(
        text=text,
        reply_markup=create_inline_keyboard([
            [{"text": "❌ Cancelar", "callback_data": "admin:free"}]
        ]),
        parse_mode="HTML"
    )
```

**API Calls:**
- `state.set_state()` - Establece estado FSM para esperar minutos
- `container.config.get_wait_time()` - Obtiene tiempo actual de la BD
- `callback.message.edit_text()` - Edita mensaje con instrucciones

#### Message Handler: `WaitTimeSetupStates.waiting_for_minutes`

**Descripción:** Procesa el input de tiempo de espera.

**Flujo de ejecución:**
1. Usuario envía número de minutos
2. Bot recibe mensaje mientras está en estado `waiting_for_minutes`
3. Bot convierte texto a número
4. Bot valida rango (mínimo 1 minuto)
5. Bot actualiza configuración de tiempo de espera
6. Bot sale del estado FSM

**Implementación:**
```python
@admin_router.message(WaitTimeSetupStates.waiting_for_minutes)
async def process_wait_time_input(
    message: Message,
    session: AsyncSession,
    state: FSMContext
):
    # Intentar convertir a número
    try:
        minutes = int(message.text)
    except ValueError:
        await message.answer(
            "❌ Debes enviar un número válido...",
            parse_mode="HTML"
        )
        return
    
    # Validar rango
    if minutes < 1:
        await message.answer(
            "❌ El tiempo debe ser al menos 1 minuto...",
            parse_mode="HTML"
        )
        return
    
    container = ServiceContainer(session, message.bot)
    
    # Actualizar configuración
    await container.config.set_wait_time(minutes)
    
    await message.answer(
        f"✅ <b>Tiempo de Espera Actualizado</b>...",
        parse_mode="HTML",
        reply_markup=free_menu_keyboard(True)
    )
    
    # Limpiar estado
    await state.clear()
```

**API Calls:**
- `message.text` - Accede al texto del mensaje
- `message.answer()` - Envía confirmación de actualización
- `container.config.set_wait_time()` - Actualiza tiempo en la BD
- `state.clear()` - Limpia el estado FSM

## Manejo de Errores y Excepciones

### Manejo de Edición de Mensajes

Para evitar errores de "message is not modified" al editar mensajes:

```python
try:
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
except Exception as e:
    if "message is not modified" not in str(e):
        logger.error(f"Error editando mensaje: {e}")
    else:
        logger.debug("ℹ️ Mensaje sin cambios, ignorando")
```

### Manejo de Permisos

Los middlewares verifican permisos antes de ejecutar handlers:

```python
# AdminAuthMiddleware verifica si el usuario es admin
# DatabaseMiddleware inyecta la sesión de base de datos
```

## Interacción con Teclados Inline

### Creación de Teclados

Los teclados se crean usando el factory `create_inline_keyboard()`:

```python
def vip_menu_keyboard(is_configured: bool) -> "InlineKeyboardMarkup":
    buttons = []
    
    if is_configured:
        buttons.extend([
            [{"text": "🎟️ Generar Token de Invitación", "callback_data": "vip:generate_token"}],
            [{"text": "🔧 Reconfigurar Canal", "callback_data": "vip:setup"}],
        ])
    else:
        buttons.append([{"text": "⚙️ Configurar Canal VIP", "callback_data": "vip:setup"}])
    
    buttons.append([{"text": "🔙 Volver", "callback_data": "admin:main"}])
    
    return create_inline_keyboard(buttons)
```

### Callback Data Format

Los callbacks siguen el formato `modulo:accion`:
- `admin:vip` - Ir al menú VIP
- `admin:free` - Ir al menú Free
- `vip:setup` - Configurar canal VIP
- `vip:generate_token` - Generar token VIP
- `free:setup` - Configurar canal Free
- `free:set_wait_time` - Configurar tiempo de espera
- `admin:main` - Volver al menú principal

## Validaciones y Seguridad

### Validación de Reenvíos

Para asegurar que los mensajes son reenvíos de canales válidos:

```python
if not message.forward_from_chat:
    # No es un reenvío, solicitar reenvío
    return

if forward_chat.type not in ["channel", "supergroup"]:
    # No es un canal válido, solicitar canal
    return
```

### Validación de Números

Para asegurar que los tiempos de espera son válidos:

```python
try:
    minutes = int(message.text)
except ValueError:
    # No es un número, solicitar número válido
    return

if minutes < 1:
    # Valor no válido, solicitar valor >= 1
    return
```

## Flujo Completo de Configuración

### Configuración de Canal por Reenvío

1. Admin selecciona opción de configuración
2. Bot entra en estado FSM correspondiente
3. Bot solicita reenvío de mensaje del canal
4. Admin reenvía mensaje del canal objetivo
5. Bot extrae ID del canal del mensaje reenviado
6. Bot verifica permisos del bot en el canal
7. Bot guarda configuración si todo es válido
8. Bot limpia estado FSM y actualiza menú

### Generación de Tokens

1. Admin selecciona "Generar Token"
2. Bot verifica que canal VIP esté configurado
3. Bot genera token único con duración configurable
4. Bot guarda token en BD
5. Bot envía token al admin