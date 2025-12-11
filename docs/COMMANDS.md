# Comandos del Bot VIP/Free

Documentación completa de los comandos disponibles en el bot de administración de canales VIP y Free.

## Comandos de Administración

### `/admin` - Panel de Administración Principal

**Descripción:** Abre el panel de administración principal con acceso a todas las funciones de gestión.

**Permisos:** Solo administradores (definidos en `ADMIN_USER_IDS`)

**Flujo de uso:**
1. El administrador envía `/admin`
2. El bot verifica permisos y muestra el menú principal
3. Opciones disponibles:
   - Gestión Canal VIP
   - Gestión Canal Free
   - Configuración

**Ejemplo:**
```
/admin
🤖 Panel de Administración
✅ Bot configurado correctamente

Selecciona una opción:
- 📺 Gestión Canal VIP
- 📺 Gestión Canal Free
- ⚙️ Configuración
```

## Submenú VIP

### `Gestión Canal VIP` - Opción del menú admin

**Descripción:** Accede al submenú de gestión del canal VIP.

**Permisos:** Solo administradores

**Funcionalidades:**
- Verificar estado de configuración del canal VIP
- Generar tokens de invitación VIP
- Configurar o reconfigurar el canal VIP

**Flujo de uso:**
1. Seleccionar "Gestión Canal VIP" en el menú principal
2. El bot muestra estado actual del canal VIP
3. Opciones disponibles dependiendo del estado:
   - Si está configurado: "🎟️ Generar Token de Invitación", "🔧 Reconfigurar Canal"
   - Si no está configurado: "⚙️ Configurar Canal VIP"

### `Configurar Canal VIP` - Configuración del canal VIP

**Descripción:** Configura el canal VIP por reenvío de mensajes.

**Permisos:** Solo administradores

**Flujo de uso:**
1. Seleccionar "⚙️ Configurar Canal VIP"
2. El bot solicita reenviar un mensaje del canal VIP
3. El administrador va al canal VIP y reenvía cualquier mensaje al bot
4. El bot extrae automáticamente el ID del canal
5. El bot verifica permisos y configura el canal
6. El bot actualiza el menú con el canal configurado

**Requisitos:**
- El bot debe ser administrador del canal VIP
- El bot debe tener permiso para invitar usuarios

**Ejemplo de interacción:**
```
👉 Reenvía un mensaje del canal ahora...

(Administrador reenvía un mensaje del canal VIP)
✅ Canal VIP Configurado
Canal: Mi Canal VIP
ID: -1001234567890
Ya puedes generar tokens de invitación.
```

### `Generar Token de Invitación` - Creación de tokens VIP

**Descripción:** Genera un token de invitación para acceso VIP.

**Permisos:** Solo administradores

**Flujo de uso:**
1. Asegurarse de que el canal VIP esté configurado
2. Seleccionar "🎟️ Generar Token de Invitación"
3. El bot genera un token único con duración configurable
4. El bot envía el token al administrador
5. El administrador comparte el token con el usuario

**Características del token:**
- 16 caracteres alfanuméricos
- Válido por 24 horas (por defecto)
- Un solo uso
- Se marca como usado después del primer canje

**Ejemplo de token generado:**
```
🎟️ Token VIP Generado

Token: ABCD1234EFGH5678
⏱️ Válido por: 24 horas
📅 Expira: 2025-12-12 10:30 UTC

👉 Comparte este token con el usuario.
El usuario debe enviarlo al bot para canjear acceso VIP.
```

## Submenú Free

### `Gestión Canal Free` - Opción del menú admin

**Descripción:** Accede al submenú de gestión del canal Free.

**Permisos:** Solo administradores

**Funcionalidades:**
- Verificar estado de configuración del canal Free
- Configurar o reconfigurar el canal Free
- Configurar tiempo de espera para acceso Free

**Flujo de uso:**
1. Seleccionar "Gestión Canal Free" en el menú principal
2. El bot muestra estado actual del canal Free y tiempo de espera
3. Opciones disponibles dependiendo del estado:
   - Si está configurado: "⏱️ Configurar Tiempo de Espera", "🔧 Reconfigurar Canal"
   - Si no está configurado: "⚙️ Configurar Canal Free"

### `Configurar Canal Free` - Configuración del canal Free

**Descripción:** Configura el canal Free por reenvío de mensajes.

**Permisos:** Solo administradores

**Flujo de uso:**
1. Seleccionar "⚙️ Configurar Canal Free"
2. El bot solicita reenviar un mensaje del canal Free
3. El administrador va al canal Free y reenvía cualquier mensaje al bot
4. El bot extrae automáticamente el ID del canal
5. El bot verifica permisos y configura el canal
6. El bot actualiza el menú con el canal configurado

**Requisitos:**
- El bot debe ser administrador del canal Free
- El bot debe tener permiso para invitar usuarios

**Ejemplo de interacción:**
```
👉 Reenvía un mensaje del canal ahora...

(Administrador reenvía un mensaje del canal Free)
✅ Canal Free Configurado
Canal: Mi Canal Free
ID: -1000987654321
Los usuarios ya pueden solicitar acceso.
```

### `Configurar Tiempo de Espera` - Configuración del tiempo de espera

**Descripción:** Configura el tiempo de espera para acceso al canal Free.

**Permisos:** Solo administradores

**Flujo de uso:**
1. Asegurarse de que el canal Free esté configurado
2. Seleccionar "⏱️ Configurar Tiempo de Espera"
3. El bot solicita ingresar el nuevo tiempo en minutos
4. El administrador envía el número de minutos
5. El bot valida y actualiza la configuración
6. El bot actualiza el menú con el nuevo tiempo

**Requisitos:**
- El tiempo debe ser al menos 1 minuto
- Solo se aceptan valores numéricos

**Ejemplo de interacción:**
```
⏱️ Configurar Tiempo de Espera

Tiempo actual: 10 minutos

Envía el nuevo tiempo de espera en minutos.
Ejemplo: 5

El tiempo debe ser mayor o igual a 1 minuto.

(Administrador envía: 15)
✅ Tiempo de Espera Actualizado
Nuevo tiempo: 15 minutos
Las nuevas solicitudes esperarán 15 minutos antes de procesarse.
```

## Comandos de Usuario (Futuros)

Los siguientes comandos están planeados para implementación futura:

### `/start` - Bienvenida y menú principal de usuario
- Bienvenida al bot
- Opciones para acceso VIP o Free

### `/vip` - Canje de token VIP
- Solicitar acceso VIP ingresando un token
- Validación y procesamiento del token

### `/free` - Solicitud de acceso Free
- Solicitar acceso al canal Free
- Ingreso a cola con tiempo de espera

## Ejemplos de Flujos Completos

### Flujo de Configuración VIP Completo

1. Administrador envía `/admin`
2. Selecciona "Gestión Canal VIP"
3. Selecciona "⚙️ Configurar Canal VIP"
4. Reenvía mensaje del canal VIP
5. Bot configura el canal
6. Selecciona "🎟️ Generar Token de Invitación"
7. Bot genera y envía token VIP

### Flujo de Configuración Free Completo

1. Administrador envía `/admin`
2. Selecciona "Gestión Canal Free"
3. Selecciona "⚙️ Configurar Canal Free"
4. Reenvía mensaje del canal Free
5. Bot configura el canal
6. Selecciona "⏱️ Configurar Tiempo de Espera"
7. Ingresa nuevo tiempo (por ejemplo: 20)
8. Bot actualiza tiempo de espera

## Errores Comunes y Soluciones

### Error de permisos en configuración de canal
- **Problema:** El bot no puede configurar un canal
- **Causa:** El bot no es administrador o no tiene permisos suficientes
- **Solución:** Asegurarse de que el bot sea administrador con permiso para invitar usuarios

### Error de formato en tiempo de espera
- **Problema:** El bot no acepta el tiempo de espera ingresado
- **Causa:** No es un número o es menor a 1
- **Solución:** Ingresar un número entero mayor o igual a 1

### Error de token inválido
- **Problema:** El token no se puede canjear
- **Causas posibles:** 
  - El token ya fue usado
  - El token ha expirado
  - El token no existe
  - El canal VIP no está configurado