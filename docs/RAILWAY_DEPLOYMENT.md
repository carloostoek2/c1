# 🚀 DEPLOYMENT EN RAILWAY - GUÍA RÁPIDA

## Resumen de Cambios para Producción

### ✅ Archivos Creados/Actualizados

1. **`runtime.txt`** - Especifica Python 3.12.8 (compatible con pydantic)
2. **`requirements.txt`** - Actualizado con versiones compatibles:
   - `aiogram==3.15.0`
   - `pydantic==2.10.6`
   - `sqlalchemy==2.0.36`
   - Todas las dependencias actualizadas

3. **`Procfile`** - Configuración para Railway: `web: python main.py`

### 📋 Checklist Pre-Deploy

- [ ] **Variables de Entorno en Railway:**
  ```
  BOT_TOKEN=tu_token_del_botfather
  ADMIN_IDS=123456789,987654321
  ```

- [ ] **Python Runtime:**
  - Railway usará Python 3.12 (especificado en `runtime.txt`)
  - Compatible con todas las dependencias

- [ ] **Volumen Persistente (Recomendado):**
  - Crear volumen para `/app/data`
  - Previene pérdida de base de datos en redeploys

---

## 🔧 PASOS DE DEPLOYMENT

### 1. Preparar Repositorio

```bash
# Verificar que todos los cambios estén commiteados
git status

# Si hay cambios pendientes
git add .
git commit -m "chore: Preparar deployment para Railway"
git push
```

### 2. Crear Proyecto en Railway

1. Ir a [railway.app](https://railway.app)
2. **New Project** → **Deploy from GitHub repo**
3. Seleccionar este repositorio
4. Railway detectará automáticamente Python y usará `runtime.txt`

### 3. Configurar Variables de Entorno

En Railway dashboard → **Variables**:

```bash
BOT_TOKEN=<tu_token_aquí>
ADMIN_IDS=<tu_user_id_aquí>
```

**Importante:** Obtén tu User ID enviando `/start` a [@userinfobot](https://t.me/userinfobot)

### 4. Configurar Volumen Persistente (Opcional pero Recomendado)

1. En Railway → **Data** → **New Volume**
2. Mount path: `/app`
3. Esto previene pérdida de base de datos en redeploys

### 5. Verificar Deploy

Railway deployará automáticamente. Ver logs en tiempo real:

```bash
# Si tienes Railway CLI instalado
railway logs

# O ver en dashboard web
https://railway.app/project/<tu-proyecto>/deployments
```

**Logs esperados:**
```
🔧 Inicializando base de datos...
✅ SQLite configurado (WAL mode, cache 64MB)
✅ Tablas creadas/verificadas
✅ BotConfig inicial creado
✅ Background tasks iniciados
🤖 Bot iniciado correctamente
```

---

## ✅ VALIDACIÓN POST-DEPLOYMENT

### 1. Verificar que el Bot Responde

- Abre Telegram y busca tu bot
- Envía `/start`
- Debe responder con el menú principal

### 2. Configurar Canales

#### Canal VIP

1. Agrega el bot a tu canal VIP como **administrador**
2. Asegúrate que tenga permisos:
   - ✅ Publicar mensajes
   - ✅ Invitar usuarios
   - ✅ Restringir miembros

3. En el bot, ejecuta:
   ```
   /admin → Gestión Canal VIP → Configurar Canal VIP
   ```

4. Reenvía un mensaje del canal VIP al bot

5. Deberías ver: **"✅ Canal VIP configurado: [Nombre del Canal]"**

#### Canal Free

1. Repite los mismos pasos para el canal Free
2. `/admin → Gestión Canal Free → Configurar Canal Free`
3. Reenvía un mensaje del canal Free

#### Configurar Tiempo de Espera

```
/admin → Gestión Canal Free → Configurar Tiempo de Espera
Envía: 5   (5 minutos de espera)
```

### 3. Verificar Dashboard

```
/admin → Ver Estado del Bot
```

Debe mostrar:
- ✅ **Canal VIP:** Configurado
- ✅ **Canal Free:** Configurado
- ✅ **Tiempo de espera:** 5 minutos
- ✅ **Background tasks:** Running

### 4. Probar Flujo VIP

#### Como Admin:

```
/admin → Gestión Canal VIP → Generar Token
```

Copia el link generado: `https://t.me/BOTUSERNAME?start=TOKEN`

#### Como Usuario:

1. Haz click en el link (o envíaselo a alguien)
2. Debe mostrar: **"¡Suscripción VIP Activada!"**
3. Click en **"Unirse al Canal VIP"**
4. Acceso inmediato al canal VIP

### 5. Probar Flujo Free

Como usuario:

```
/start → Solicitar Acceso Free
```

- Debe mostrar: **"Solicitud registrada. Espera 5 minutos..."**
- Después de 5 minutos, el background task enviará el invite link automáticamente

---

## 🐛 TROUBLESHOOTING

### Error: "pydantic-core build failed"

**Solución:** Verificar que `runtime.txt` esté en el repo y especifique Python 3.12

```bash
# Verificar archivo
cat runtime.txt
# Debe mostrar: python-3.12.8

# Redeploy
git push
```

### Error: "Chat not found" al configurar canal

**Causa:** El bot no está en el canal o no es administrador

**Solución:**
1. Agrega el bot al canal
2. Hazlo **administrador** (no solo miembro)
3. Verifica permisos (Invitar usuarios, Publicar mensajes)
4. Intenta configurar nuevamente

### Bot no responde a comandos

**Solución:**

1. Ver logs de Railway:
   ```bash
   railway logs | grep ERROR
   ```

2. Verificar que `BOT_TOKEN` esté configurado correctamente

3. Verificar que el bot esté corriendo:
   ```bash
   railway ps
   ```

### Base de datos se borra en cada deploy

**Solución:** Configurar volumen persistente (ver Paso 4 arriba)

### Background tasks no ejecutan

**Verificar logs:**
```bash
railway logs | grep "Background"
```

Debe mostrar:
```
Background tasks iniciados
Job: expire_and_kick_vip_subscribers | Intervalo: 60 minutos
Job: process_free_queue | Intervalo: 5 minutos
```

---

## 📊 MONITOREO

### Ver Logs en Tiempo Real

```bash
# Con Railway CLI
railway logs --tail 100

# Ver solo errores
railway logs | grep ERROR

# Ver background tasks
railway logs | grep "Background\|Job"
```

### Métricas en el Bot

```
/admin → Ver Estado del Bot
```

Muestra:
- Suscriptores VIP activos
- Solicitudes Free pendientes
- Tokens generados/usados
- Estado de background tasks

---

## 🔒 SEGURIDAD

### ✅ Checklist

- [ ] `BOT_TOKEN` NO está en el código fuente
- [ ] `BOT_TOKEN` está en variables de entorno de Railway
- [ ] `.env` está en `.gitignore`
- [ ] Solo administradores pueden ejecutar `/admin`
- [ ] Tokens expiran después de 24 horas
- [ ] Invite links de un solo uso

---

## 📞 SOPORTE

**Railway Issues:** [railway.app/help](https://railway.app/help)
**Telegram Bot API:** [core.telegram.org/bots](https://core.telegram.org/bots)

**Logs Completos:**
```bash
railway logs
```

---

**✅ Deployment Completo**

Una vez completados todos los pasos, tu bot estará:
- ✅ Corriendo 24/7 en Railway
- ✅ Con base de datos persistente
- ✅ Background tasks automáticos
- ✅ Canales VIP y Free configurados
- ✅ Listo para usuarios
