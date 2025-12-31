# Contexto del Proyecto: Bot de Administración VIP/Free

## 📁 Estructura General
Este es un bot de Telegram en Python construido con el framework aiogram. La estructura sigue una arquitectura modular con servicios, handlers, middlewares y bases de datos claramente separados. El bot administra canales VIP y Free, con sistemas de gamificación y narrativa interactiva.

## 🏗️ Stack Tecnológico
- Framework: aiogram 3.x (Python)
- Base de datos: SQLAlchemy con SQLite (aiosqlite)
- Patrón: Inyección de dependencias con contenedores de servicios
- Estado: FSM (Finite State Machine) para flujos interactivos
- Otras tecnologías: Aiohttp (sesiones HTTP), Python-dotenv (variables de entorno)

## 📦 Sistemas/Módulos Principales

### Sistema de Administración de Canales
- **Ubicación:** `/bot/handlers/admin/`, `/bot/services/`
- **Propósito:** Gestión de canales VIP y Free, broadcasting, configuración de tiempos de espera, flujos de aprobación automática
- **Archivos clave:** `admin/main.py`, `admin/broadcast.py`, `admin/free.py`, `broadcast.py`, `channel.py`, `subscription.py`

### Sistema de Gamificación
- **Ubicación:** `/bot/gamification/`
- **Propósito:** Sistema de puntos (besitos/favores), reacciones personalizadas (no nativas), misiones, niveles, tablas de clasificación
- **Archivos clave:** `handlers/user/reactions.py`, `services/container.py`, `database/models.py`, `handlers/admin/`

### Sistema de Narrativa
- **Ubicación:** `/bot/narrative/`
- **Propósito:** Historia interactiva con capítulos, fragmentos, decisiones del usuario, coleccionables (clues), progreso narrativo
- **Archivos clave:** `handlers/user/story.py`, `services/container.py`, `database/models.py`, `handlers/admin/`

## 👤 Modelos de Datos Principales
| Modelo | Ubicación | Descripción |
|--------|-----------|-------------|
| User | `/bot/database/models.py` | Usuarios del sistema con información de perfil y estadísticas |
| BroadcastMessage | `/bot/database/models.py` | Mensajes enviados con sistema de gamificación |
| Subscription | `/bot/database/models.py` | Suscripciones VIP y solicitudes de acceso Free |
| CustomReaction | `/bot/gamification/database/models.py` | Reacciones personalizadas de usuarios a mensajes |
| NarrativeProgress | `/bot/narrative/database/models.py` | Progreso narrativo del usuario (capítulos, decisiones, pistas) |

## 🔀 Rutas/Endpoints Principales
- **Comandos Admin:** `/admin` - Menú principal de administración
- **Solicitud Free:** `ChatJoinRequest` - Handler automático para solicitudes de unión al canal Free
- **Reacciones:** `callback_data="react:{id}"` - Sistema de reacciones personalizadas (no nativas) con ganancia de puntos
- **Historia:** `/historia` - Acceso al sistema narrativo interactivo
- **Gamificación:** `/perfil`, `/misiones`, `/recompensas` - Comandos del sistema de gamificación

## 🔧 Configuración y Variables de Entorno
- **Archivo(s) de config:** `config.py`, `.env` (con `.env.example`)
- **Variables críticas:** `BOT_TOKEN`, `ADMIN_USER_IDS`, `DATABASE_URL`, `DEFAULT_WAIT_TIME_MINUTES`, `VIP_CHANNEL_ID`, `FREE_CHANNEL_ID`

## 📝 Convenciones del Proyecto
- Prefijos en callback_data: `admin:`, `broadcast:`, `react:`, `story:`, `gamif:`
- Estados FSM en `/bot/states/` con nombres descriptivos como `BroadcastStates`, `ChannelSetupStates`
- Contenedores de servicios para inyección de dependencias en `/bot/services/container.py`
- Middlewares para inyección automática de sesiones de BD y validación de admin
- Prefijo `besitos` para el sistema de puntos de la gamificación (internamente) y `favores` para el usuario
- El sistema de menús adapta su contenido según el rol/estatus del usuario (gratuito, VIP o administrador)
- Los sistemas de modificación de datos se conectan mediante el wizard de creación en gamificación (creación de misiones, recompensas, niveles)

## ⚠️ Puntos de Entrada
- **Aplicación principal:** `main.py` - Punto de entrada con ciclo de vida completo del bot
- **Scripts importantes:** `run_bot_test.sh` - Script para pruebas del bot

## 🔗 Integraciones Externas
- **Telegram Bot API** - Integración completa para envío de mensajes, reacciones personalizadas (no nativas), manejo de canales
- **Sistema de canales** - Configuración y administración automática de canales VIP/Free
- **Base de datos SQLite** - Almacenamiento persistente de usuarios, mensajes, reacciones y progreso narrativo