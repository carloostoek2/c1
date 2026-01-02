# CHECKLIST DE VALIDACIÓN PRE-PRODUCCIÓN
## Bot de Telegram VIP/Free - Módulo de Canales

**Versión:** 1.0
**Fecha:** 2026-01-02
**Plataforma:** Railway

---

## ═══════════════════════════════════════════════════════════════
## 📋 1. DEPENDENCIAS Y COMPATIBILIDAD
## ═══════════════════════════════════════════════════════════════

### ✅ Python Runtime
- [ ] **Python 3.12.8** especificado en `runtime.txt`
- [ ] Verificar que Railway use Python 3.12 (NO 3.13)
- [ ] Comando: `python --version` debe mostrar 3.12.x

### ✅ Dependencias Actualizadas
- [ ] `aiogram==3.15.0` (compatible con Python 3.12)
- [ ] `pydantic==2.10.6` (compatible con Python 3.12)
- [ ] `sqlalchemy==2.0.36`
- [ ] `aiosqlite==0.20.0`
- [ ] `alembic==1.14.0`
- [ ] `APScheduler==3.10.4`
- [ ] Todas las dependencias instaladas sin errores

### ✅ Instalación
```bash
# Verificar instalación completa
pip install -r requirements.txt

# Debe completar sin errores de compilación
```

---

## ═══════════════════════════════════════════════════════════════
## 🔧 2. CONFIGURACIÓN DE VARIABLES DE ENTORNO
## ═══════════════════════════════════════════════════════════════

### ✅ Variables Requeridas (Railway)
- [ ] `BOT_TOKEN` - Token del bot de Telegram
- [ ] `ADMIN_IDS` - IDs de administradores (comma-separated)
- [ ] `DATABASE_URL` - Ruta a base de datos SQLite (default: `sqlite+aiosqlite:///./bot_database.db`)

### ✅ Variables Opcionales
- [ ] `LOG_LEVEL` - Nivel de logging (default: INFO)
- [ ] `ENVIRONMENT` - Entorno (production/development)

### ✅ Validación de Variables
```bash
# Verificar que todas las variables estén definidas
python -c "import os; print('BOT_TOKEN:', 'OK' if os.getenv('BOT_TOKEN') else 'MISSING')"
python -c "import os; print('ADMIN_IDS:', 'OK' if os.getenv('ADMIN_IDS') else 'MISSING')"
```

---

## ═══════════════════════════════════════════════════════════════
## 🗄️ 3. BASE DE DATOS
## ═══════════════════════════════════════════════════════════════

### ✅ Inicialización
- [ ] Base de datos SQLite creada automáticamente
- [ ] Tablas inicializadas correctamente
- [ ] `BotConfig` con registro por defecto (id=1)

### ✅ Migraciones (si aplica)
- [ ] Ejecutar migraciones de Alembic si es necesario
```bash
alembic current  # Ver migración actual
alembic upgrade head  # Aplicar migraciones pendientes
```

### ✅ Verificación de Modelos
- [ ] `BotConfig` - Configuración global
- [ ] `VIPSubscriber` - Suscriptores VIP
- [ ] `InvitationToken` - Tokens de invitación
- [ ] `FreeChannelRequest` - Solicitudes Free

### ✅ Persistencia
- [ ] Verificar que Railway tenga volumen persistente configurado
- [ ] Base de datos NO debe reiniciarse en cada deploy

---

## ═══════════════════════════════════════════════════════════════
## 🤖 4. CONFIGURACIÓN DEL BOT
## ═══════════════════════════════════════════════════════════════

### ✅ Token y Permisos
- [ ] Bot creado en [@BotFather](https://t.me/BotFather)
- [ ] Token válido y funcional
- [ ] Bot agregado a canales VIP y Free como **administrador**

### ✅ Permisos del Bot en Canales
- [ ] ✅ **Puede publicar mensajes** (`can_post_messages`)
- [ ] ✅ **Puede invitar usuarios** (`can_invite_users`)
- [ ] ✅ **Puede editar mensajes** (`can_edit_messages`) (opcional)
- [ ] ✅ **Puede eliminar mensajes** (`can_delete_messages`) (opcional)
- [ ] ✅ **Puede restringir miembros** (`can_restrict_members`) (para expulsión VIP)

### ✅ Verificación Manual
```bash
# 1. Agregar bot a canal de prueba
# 2. Darle permisos de administrador
# 3. Ejecutar comando en el bot: /admin → Configurar Canal VIP
# 4. Reenviar mensaje del canal
# 5. Verificar que el bot detecte el canal correctamente
```

---

## ═══════════════════════════════════════════════════════════════
## 🧪 5. TESTS Y VALIDACIÓN
## ═══════════════════════════════════════════════════════════════

### ✅ Tests Unitarios
```bash
# Ejecutar todos los tests
pytest tests/ -v

# Ejecutar solo tests de producción de canales
pytest tests/test_production_channels.py -v

# Ejecutar con coverage
pytest tests/ --cov=bot --cov-report=term-missing
```

### ✅ Tests Esperados
- [ ] **18 tests de canales** - `test_production_channels.py`
  - 3 tests de configuración
  - 3 tests de validación
  - 3 tests de envío
  - 2 tests de invite links
  - 1 test de integración
  - 1 test de manejo de errores
  - 1 test de permisos
  - 4 tests de edge cases

- [ ] **Tests E2E existentes** - Todos pasando
  - 9 tests básicos (`test_e2e.py`)
  - 12 tests ONDA 2 (`test_e2e_onda2.py`)
  - 7 tests A3 deep links (`test_a3_deep_links.py`)

### ✅ Validación Total
```bash
# Ejecutar TODOS los tests (46+ tests)
pytest tests/ -v --tb=short

# Resultado esperado: 100% tests pasando ✅
```

---

## ═══════════════════════════════════════════════════════════════
## 🚀 6. DEPLOYMENT EN RAILWAY
## ═══════════════════════════════════════════════════════════════

### ✅ Configuración de Railway

#### 1. Crear Proyecto en Railway
- [ ] Ir a [railway.app](https://railway.app)
- [ ] Conectar con GitHub
- [ ] Crear nuevo proyecto desde repositorio

#### 2. Configurar Variables de Entorno
- [ ] Agregar `BOT_TOKEN`
- [ ] Agregar `ADMIN_IDS`
- [ ] Verificar `DATABASE_URL` (default OK si no se especifica)

#### 3. Configurar Build Settings
- [ ] **Build Command:** (vacío, usa `requirements.txt` automáticamente)
- [ ] **Start Command:** `python main.py`
- [ ] **Root Directory:** `/` (raíz del proyecto)

#### 4. Configurar Runtime
- [ ] Verificar que use Python 3.12 (archivo `runtime.txt`)
- [ ] Si no detecta `runtime.txt`, especificar manualmente

#### 5. Configurar Volumen Persistente
- [ ] Crear volumen para base de datos
- [ ] Mount path: `/app/data` (o donde esté `bot_database.db`)
- [ ] Esto previene pérdida de datos en redeploys

### ✅ Deploy Inicial
```bash
# Railway deployará automáticamente desde GitHub
# O puedes usar Railway CLI:

railway login
railway link  # Vincular proyecto
railway up    # Deploy manual
```

### ✅ Verificar Logs
```bash
# Ver logs en tiempo real
railway logs

# Buscar errores de inicio
railway logs | grep ERROR
```

---

## ═══════════════════════════════════════════════════════════════
## ✅ 7. VALIDACIÓN POST-DEPLOYMENT
## ═══════════════════════════════════════════════════════════════

### ✅ Healthcheck Básico
- [ ] Bot responde a comandos
- [ ] `/start` funciona correctamente
- [ ] `/admin` muestra menú de administración

### ✅ Configuración de Canales

#### Canal VIP
- [ ] Comando: `/admin` → Gestión Canal VIP → Configurar Canal VIP
- [ ] Reenviar mensaje del canal VIP
- [ ] Verificar confirmación: "Canal VIP configurado exitosamente"

#### Canal Free
- [ ] Comando: `/admin` → Gestión Canal Free → Configurar Canal Free
- [ ] Reenviar mensaje del canal Free
- [ ] Verificar confirmación: "Canal Free configurado exitosamente"

#### Tiempo de Espera
- [ ] Comando: `/admin` → Gestión Canal Free → Configurar Tiempo de Espera
- [ ] Enviar número de minutos (ej: 5)
- [ ] Verificar confirmación

### ✅ Verificar Dashboard
- [ ] Comando: `/admin` → Ver Estado del Bot
- [ ] Debe mostrar:
  - ✅ Canal VIP: Configurado
  - ✅ Canal Free: Configurado
  - ✅ Tiempo de espera: X minutos
  - ✅ Background tasks: Running

### ✅ Flujo VIP Completo

#### 1. Generar Token
- [ ] `/admin` → Gestión Canal VIP → Generar Token
- [ ] Copiar token generado
- [ ] Formato: `https://t.me/BOTUSERNAME?start=TOKEN`

#### 2. Canjear Token (como usuario)
- [ ] Click en link del token
- [ ] Verificar mensaje: "¡Suscripción VIP Activada!"
- [ ] Click en "Unirse al Canal VIP"
- [ ] Verificar acceso al canal VIP

#### 3. Verificar Suscriptor
- [ ] `/admin` → Ver Estado del Bot
- [ ] Debe mostrar: "1 suscriptor VIP activo"

### ✅ Flujo Free Completo

#### 1. Solicitar Acceso Free
- [ ] Como usuario: `/start` → Solicitar Acceso Free
- [ ] Verificar mensaje: "Solicitud registrada, espera X minutos"

#### 2. Verificar Cola
- [ ] `/admin` → Ver Estado del Bot
- [ ] Debe mostrar: "1 solicitud Free pendiente"

#### 3. Procesamiento Automático
- [ ] Esperar tiempo configurado (background task)
- [ ] Usuario recibe link de acceso Free por privado
- [ ] Click en "Unirse al Canal Free"
- [ ] Verificar acceso al canal Free

### ✅ Background Tasks

#### Expulsión VIP Automática
- [ ] Crear suscriptor VIP con expiración próxima
- [ ] Esperar a que expire
- [ ] Verificar que background task lo expulse del canal VIP

#### Procesamiento Cola Free
- [ ] Crear solicitud Free
- [ ] Esperar tiempo configurado (5 min por defecto)
- [ ] Verificar que se procese automáticamente

---

## ═══════════════════════════════════════════════════════════════
## 🛡️ 8. SEGURIDAD Y MEJORES PRÁCTICAS
## ═══════════════════════════════════════════════════════════════

### ✅ Secretos
- [ ] `BOT_TOKEN` NO debe estar en el código fuente
- [ ] `BOT_TOKEN` debe estar en variables de entorno de Railway
- [ ] `.env` en `.gitignore`

### ✅ Validaciones
- [ ] Solo administradores pueden ejecutar `/admin`
- [ ] Tokens expiran correctamente (24 horas)
- [ ] Invite links expiran correctamente (5 horas)
- [ ] Usuarios no pueden duplicar solicitudes Free

### ✅ Logging
- [ ] Logs de nivel INFO en producción
- [ ] Logs de errores capturados correctamente
- [ ] Sin información sensible en logs

### ✅ Rate Limiting
- [ ] Considerar limitar solicitudes Free por usuario
- [ ] Considerar limitar generación de tokens por admin

---

## ═══════════════════════════════════════════════════════════════
## 📊 9. MONITOREO Y MÉTRICAS
## ═══════════════════════════════════════════════════════════════

### ✅ Métricas a Monitorear
- [ ] Número de suscriptores VIP activos
- [ ] Número de solicitudes Free pendientes
- [ ] Tokens generados vs canjeados
- [ ] Tasa de expulsión VIP
- [ ] Errores en background tasks

### ✅ Comandos de Monitoreo
```bash
# Ver logs de Railway
railway logs --tail 100

# Ver estado del sistema
# En el bot: /admin → Ver Estado del Bot

# Ver base de datos (si tienes acceso)
sqlite3 bot_database.db "SELECT COUNT(*) FROM vip_subscribers WHERE status='active';"
```

---

## ═══════════════════════════════════════════════════════════════
## 🔥 10. TROUBLESHOOTING
## ═══════════════════════════════════════════════════════════════

### ❌ Problema: "pydantic-core build failed"
**Solución:**
- Verificar que `runtime.txt` especifica Python 3.12
- Actualizar `pydantic==2.10.6` en `requirements.txt`
- Redeploy

### ❌ Problema: "Chat not found" al configurar canal
**Solución:**
- Verificar que el bot esté agregado al canal
- Verificar que el bot sea **administrador** del canal
- Verificar permisos del bot

### ❌ Problema: Bot no responde a comandos
**Solución:**
- Verificar que `BOT_TOKEN` esté configurado en Railway
- Ver logs: `railway logs | grep ERROR`
- Verificar que el bot esté corriendo: `railway ps`

### ❌ Problema: Base de datos se borra en cada deploy
**Solución:**
- Configurar volumen persistente en Railway
- Mount path debe coincidir con ubicación de `bot_database.db`

### ❌ Problema: Background tasks no ejecutan
**Solución:**
- Verificar logs: `railway logs | grep "Background"`
- Verificar que APScheduler esté instalado
- Verificar que `start_background_tasks()` se ejecute en `main.py`

---

## ═══════════════════════════════════════════════════════════════
## ✅ CHECKLIST RÁPIDO DE PRODUCCIÓN
## ═══════════════════════════════════════════════════════════════

### Antes de Deploy
- [ ] Todos los tests pasando (46+ tests)
- [ ] `runtime.txt` con Python 3.12.8
- [ ] `requirements.txt` actualizado
- [ ] Variables de entorno definidas en Railway
- [ ] Bot creado y token válido

### Deploy
- [ ] Push a GitHub (auto-deploy) o `railway up`
- [ ] Verificar logs sin errores
- [ ] Bot responde a `/start`

### Post-Deploy
- [ ] Configurar canal VIP
- [ ] Configurar canal Free
- [ ] Configurar tiempo de espera
- [ ] Probar flujo VIP completo
- [ ] Probar flujo Free completo
- [ ] Verificar background tasks

---

## 📞 SOPORTE

**Errores de Railway:** [railway.app/help](https://railway.app/help)
**Errores de Telegram Bot:** [core.telegram.org/bots](https://core.telegram.org/bots)
**Logs:** `railway logs`

---

**Status:** ✅ Checklist completo
**Última actualización:** 2026-01-02
