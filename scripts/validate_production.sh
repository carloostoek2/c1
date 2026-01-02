#!/bin/bash

# ═══════════════════════════════════════════════════════════════
# SCRIPT DE VALIDACIÓN PRE-PRODUCCIÓN
# ═══════════════════════════════════════════════════════════════
#
# Valida que el bot esté listo para deployment en Railway
#
# Uso:
#   bash scripts/validate_production.sh
#
# Exit codes:
#   0 - Todo OK, listo para producción
#   1 - Falló alguna validación
#
# ═══════════════════════════════════════════════════════════════

set -e  # Exit on error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Contadores
PASSED=0
FAILED=0
WARNINGS=0

# ═══════════════════════════════════════════════════════════════
# FUNCIONES HELPER
# ═══════════════════════════════════════════════════════════════

print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_check() {
    echo -e "${YELLOW}⏳ Verificando: $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ PASS: $1${NC}"
    ((PASSED++))
}

print_error() {
    echo -e "${RED}❌ FAIL: $1${NC}"
    ((FAILED++))
}

print_warning() {
    echo -e "${YELLOW}⚠️  WARN: $1${NC}"
    ((WARNINGS++))
}

# ═══════════════════════════════════════════════════════════════
# VALIDACIONES
# ═══════════════════════════════════════════════════════════════

print_header "🚀 VALIDACIÓN PRE-PRODUCCIÓN - BOT TELEGRAM VIP/FREE"

# ───────────────────────────────────────────────────────────────
# 1. PYTHON VERSION
# ───────────────────────────────────────────────────────────────
print_check "Python version"

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 11 ]; then
    print_success "Python $PYTHON_VERSION (OK para desarrollo)"

    if [ "$PYTHON_MINOR" -eq 13 ]; then
        print_warning "Python 3.13 detectado - Railway usará Python 3.12 (especificado en runtime.txt)"
    fi
else
    print_error "Python $PYTHON_VERSION no soportado. Requiere Python 3.11+"
fi

# ───────────────────────────────────────────────────────────────
# 2. RUNTIME.TXT
# ───────────────────────────────────────────────────────────────
print_check "runtime.txt para Railway"

if [ -f "runtime.txt" ]; then
    RUNTIME_VERSION=$(cat runtime.txt)
    if [[ "$RUNTIME_VERSION" == "python-3.12"* ]]; then
        print_success "runtime.txt especifica Python 3.12 (correcto)"
    else
        print_warning "runtime.txt especifica $RUNTIME_VERSION (recomendado: python-3.12.8)"
    fi
else
    print_error "runtime.txt NO existe - Railway usará versión por defecto"
fi

# ───────────────────────────────────────────────────────────────
# 3. REQUIREMENTS.TXT
# ───────────────────────────────────────────────────────────────
print_check "requirements.txt"

if [ -f "requirements.txt" ]; then
    print_success "requirements.txt existe"

    # Verificar dependencias clave
    if grep -q "aiogram" requirements.txt; then
        print_success "aiogram especificado"
    else
        print_error "aiogram NO encontrado en requirements.txt"
    fi

    if grep -q "pydantic" requirements.txt; then
        PYDANTIC_VERSION=$(grep "pydantic" requirements.txt | cut -d'=' -f3)
        print_success "pydantic especificado (v$PYDANTIC_VERSION)"
    else
        print_warning "pydantic NO especificado explícitamente"
    fi

    if grep -q "sqlalchemy" requirements.txt; then
        print_success "sqlalchemy especificado"
    else
        print_error "sqlalchemy NO encontrado en requirements.txt"
    fi
else
    print_error "requirements.txt NO existe"
fi

# ───────────────────────────────────────────────────────────────
# 4. PROCFILE
# ───────────────────────────────────────────────────────────────
print_check "Procfile para Railway"

if [ -f "Procfile" ]; then
    if grep -q "python main.py" Procfile; then
        print_success "Procfile configurado correctamente"
    else
        print_warning "Procfile existe pero no ejecuta main.py"
    fi
else
    print_warning "Procfile NO existe (Railway puede autodetectar)"
fi

# ───────────────────────────────────────────────────────────────
# 5. ARCHIVOS CORE
# ───────────────────────────────────────────────────────────────
print_check "Archivos core del proyecto"

CORE_FILES=(
    "main.py"
    "config.py"
    "bot/database/models.py"
    "bot/services/container.py"
    "bot/services/channel.py"
    "bot/services/config.py"
    "bot/services/subscription.py"
)

for file in "${CORE_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "Archivo existe: $file"
    else
        print_error "Archivo FALTANTE: $file"
    fi
done

# ───────────────────────────────────────────────────────────────
# 6. VARIABLES DE ENTORNO
# ───────────────────────────────────────────────────────────────
print_check "Variables de entorno"

if [ -f ".env" ]; then
    print_warning ".env existe (OK para dev, NO commitear a git)"

    # Verificar .gitignore
    if [ -f ".gitignore" ]; then
        if grep -q ".env" .gitignore; then
            print_success ".env en .gitignore (correcto)"
        else
            print_error ".env NO está en .gitignore - RIESGO DE SEGURIDAD"
        fi
    fi
else
    print_warning ".env NO existe (OK si usas Railway variables)"
fi

# ───────────────────────────────────────────────────────────────
# 7. TESTS
# ───────────────────────────────────────────────────────────────
print_check "Ejecutando tests"

if command -v pytest &> /dev/null; then
    print_success "pytest instalado"

    echo ""
    echo -e "${YELLOW}🧪 Ejecutando suite de tests...${NC}"
    echo ""

    # Ejecutar tests con output mínimo
    if pytest tests/ -v --tb=short -q 2>&1 | tee /tmp/pytest_output.txt; then
        TEST_COUNT=$(grep -c "PASSED" /tmp/pytest_output.txt || echo "0")
        print_success "Todos los tests pasaron ($TEST_COUNT tests)"
    else
        FAILED_COUNT=$(grep -c "FAILED" /tmp/pytest_output.txt || echo "desconocido")
        print_error "Tests fallaron ($FAILED_COUNT fallos)"
        echo ""
        echo -e "${RED}Ver output de tests arriba para detalles${NC}"
    fi
else
    print_error "pytest NO instalado - no se pueden ejecutar tests"
fi

# ───────────────────────────────────────────────────────────────
# 8. ESTRUCTURA DE DIRECTORIOS
# ───────────────────────────────────────────────────────────────
print_check "Estructura de directorios"

REQUIRED_DIRS=(
    "bot"
    "bot/database"
    "bot/services"
    "bot/handlers"
    "bot/middlewares"
    "bot/states"
    "bot/utils"
    "bot/background"
    "tests"
    "docs"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        print_success "Directorio existe: $dir"
    else
        print_error "Directorio FALTANTE: $dir"
    fi
done

# ───────────────────────────────────────────────────────────────
# 9. VALIDACIÓN DE IMPORTS
# ───────────────────────────────────────────────────────────────
print_check "Validación de imports Python"

echo ""
echo -e "${YELLOW}📦 Verificando imports...${NC}"
echo ""

if python3 -c "
import sys
try:
    from bot.database import init_db, close_db
    from bot.services.container import ServiceContainer
    from bot.services.channel import ChannelService
    from bot.services.config import ConfigService
    from bot.services.subscription import SubscriptionService
    print('✅ Todos los imports OK')
    sys.exit(0)
except ImportError as e:
    print(f'❌ Error de import: {e}')
    sys.exit(1)
" 2>&1; then
    print_success "Todos los módulos importables"
else
    print_error "Error al importar módulos"
fi

# ───────────────────────────────────────────────────────────────
# 10. SEGURIDAD
# ───────────────────────────────────────────────────────────────
print_check "Validaciones de seguridad"

# Verificar que BOT_TOKEN no esté hardcodeado
if grep -r "BOT_TOKEN.*=" --include="*.py" --exclude-dir=".git" --exclude-dir="venv" . 2>/dev/null | grep -v "getenv\|environ"; then
    print_error "BOT_TOKEN puede estar hardcodeado en el código"
else
    print_success "BOT_TOKEN no está hardcodeado (correcto)"
fi

# Verificar que no haya credenciales en el código
if grep -r "password.*=" --include="*.py" --exclude-dir=".git" --exclude-dir="venv" . 2>/dev/null | grep -v "getenv\|environ" | grep -v "can_"; then
    print_warning "Posibles passwords hardcodeados encontrados"
else
    print_success "No se encontraron passwords hardcodeados"
fi

# ═══════════════════════════════════════════════════════════════
# RESUMEN
# ═══════════════════════════════════════════════════════════════

print_header "📊 RESUMEN DE VALIDACIÓN"

echo -e "${GREEN}✅ Checks pasados:   $PASSED${NC}"
echo -e "${YELLOW}⚠️  Warnings:        $WARNINGS${NC}"
echo -e "${RED}❌ Checks fallados:  $FAILED${NC}"

echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                               ║${NC}"
    echo -e "${GREEN}║  ✅ VALIDACIÓN EXITOSA - LISTO PARA PRODUCCIÓN                ║${NC}"
    echo -e "${GREEN}║                                                               ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Hay $WARNINGS warnings - revisar antes de deploy${NC}"
    fi

    echo ""
    echo -e "${BLUE}Próximos pasos:${NC}"
    echo "1. Configurar variables de entorno en Railway:"
    echo "   - BOT_TOKEN"
    echo "   - ADMIN_IDS"
    echo ""
    echo "2. Push a GitHub (auto-deploy) o ejecutar:"
    echo "   railway up"
    echo ""
    echo "3. Verificar logs después de deploy:"
    echo "   railway logs"
    echo ""
    echo "4. Configurar canales VIP y Free usando /admin"
    echo ""

    exit 0
else
    echo -e "${RED}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                                                               ║${NC}"
    echo -e "${RED}║  ❌ VALIDACIÓN FALLIDA - NO LISTO PARA PRODUCCIÓN             ║${NC}"
    echo -e "${RED}║                                                               ║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${RED}Revisar los errores arriba antes de hacer deploy${NC}"
    echo ""

    exit 1
fi
