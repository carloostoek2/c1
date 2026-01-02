#!/usr/bin/env python3
"""
Script para corregir los fragmentos de onboarding.

Problemas corregidos:
1. Paso 4: Agregar placeholders {archetype} y {archetype_description}
2. Paso 5: Cambiar callbacks para que completen el onboarding primero
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, UTC

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from bot.database import get_session, init_db, close_db


async def fix_onboarding_fragments():
    """Corrige los fragmentos de onboarding."""
    print("🔧 Corrigiendo fragmentos de onboarding...")
    print("=" * 60)

    # Inicializar BD
    await init_db()

    async with get_session() as session:
        # Actualizar paso 4 - Agregar placeholders de arquetipo
        print("\n📝 Actualizando paso 4 (mostrar arquetipo)...")
        step_4_content = """He estado observando tus elecciones...

Tu forma de tomar decisiones me dice mucho sobre ti.

Este conocimiento me ayudará a adaptar la historia a tu estilo.

{archetype_description}

¿Listo para descubrir qué tipo de viajero eres?"""

        await session.execute(
            text("""
                UPDATE onboarding_fragments
                SET content = :content,
                    updated_at = :now
                WHERE step = 4
            """),
            {
                "content": step_4_content,
                "now": datetime.now(UTC)
            }
        )
        print("  ✅ Paso 4 actualizado con placeholders de arquetipo")

        # Actualizar paso 5 - Usar callbacks estándar
        print("\n📝 Actualizando paso 5 (completar onboarding primero)...")
        step_5_content = """¡Listo! Ya conoces los fundamentos.

Basado en tus elecciones, te he identificado como:

<b>{archetype}</b>

Esta forma de interactuar con el mundo tendrá consecuencias en tu viaje.
Algunos caminos se abrirán, otros se cerrarán.

La historia completa te espera. ¿Estás preparado para comenzar?"""

        step_5_decisions = """[
            {"text": "🚀 Ir al Menú Principal", "callback": "onboard:complete"},
            {"text": "📖 Comenzar la Historia", "callback": "onboard:complete"},
            {"text": "📚 Ver mi Diario", "callback": "onboard:complete"}
        ]"""

        await session.execute(
            text("""
                UPDATE onboarding_fragments
                SET content = :content,
                    decisions = :decisions,
                    updated_at = :now
                WHERE step = 5
            """),
            {
                "content": step_5_content,
                "decisions": step_5_decisions,
                "now": datetime.now(UTC)
            }
        )
        print("  ✅ Paso 5 actualizado para completar onboarding")

        await session.commit()

        # Verificar cambios
        print("\n📋 Verificando cambios...")
        result = await session.execute(
            text("SELECT step, title FROM onboarding_fragments ORDER BY step")
        )
        for row in result:
            print(f"  Paso {row[0]}: {row[1]}")

        print("\n" + "=" * 60)
        print("✅ Fragmentos corregidos exitosamente!")
        print("=" * 60)
        print("\nCambios:")
        print("• Paso 4: Ahora muestra {archetype_description} antes de preguntar")
        print("• Paso 5: Muestra arquetipo detectado y todos los botones completan onboarding")

    await close_db()
    print("\n🔌 Conexión a BD cerrada")


if __name__ == "__main__":
    asyncio.run(fix_onboarding_fragments())
