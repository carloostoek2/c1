#!/usr/bin/env python3
"""
Script para eliminar el capítulo demo de la narrativa.

Elimina el capítulo "Los Kinkys Demo" y todos sus fragmentos asociados.

Uso:
    python scripts/delete_demo_chapter.py
"""
import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from bot.database import get_session, init_db, close_db


async def delete_demo_chapter():
    """Elimina el capítulo demo y sus fragmentos."""
    print("🗑️  Eliminando capítulo demo...")

    # Inicializar BD
    await init_db()

    async with get_session() as session:
        # Primero eliminar las decisiones de los fragmentos del capítulo demo
        print("\n📝 Eliminando decisiones de fragmentos...")
        result = await session.execute(
            text("""
                DELETE FROM fragment_decisions
                WHERE fragment_id IN (
                    SELECT id FROM narrative_fragments
                    WHERE chapter_id = (
                        SELECT id FROM narrative_chapters
                        WHERE slug = 'los-kinkys-demo'
                    )
                )
            """)
        )
        print(f"  ✅ {result.rowcount} decisiones eliminadas")

        # Eliminar requisitos de fragmentos
        print("\n📝 Eliminando requisitos de fragmentos...")
        result = await session.execute(
            text("""
                DELETE FROM fragment_requirements
                WHERE fragment_id IN (
                    SELECT id FROM narrative_fragments
                    WHERE chapter_id = (
                        SELECT id FROM narrative_chapters
                        WHERE slug = 'los-kinkys-demo'
                    )
                )
            """)
        )
        print(f"  ✅ {result.rowcount} requisitos eliminados")

        # Eliminar los fragmentos del capítulo
        print("\n📝 Eliminando fragmentos del capítulo...")
        result = await session.execute(
            text("""
                DELETE FROM narrative_fragments
                WHERE chapter_id = (
                    SELECT id FROM narrative_chapters
                    WHERE slug = 'los-kinkys-demo'
                )
            """)
        )
        print(f"  ✅ {result.rowcount} fragmentos eliminados")

        # Finalmente eliminar el capítulo
        print("\n📝 Eliminando capítulo demo...")
        result = await session.execute(
            text("""
                DELETE FROM narrative_chapters
                WHERE slug = 'los-kinkys-demo'
            """)
        )
        print(f"  ✅ {result.rowcount} capítulo eliminado")

        await session.commit()

        # Verificar que se eliminó correctamente
        print("\n📋 Verificando eliminación...")
        result = await session.execute(
            text("SELECT COUNT(*) FROM narrative_chapters WHERE slug = 'los-kinkys-demo'")
        )
        count = result.scalar()
        if count == 0:
            print("  ✅ Capítulo demo eliminado correctamente")
        else:
            print("  ❌ Error: El capítulo aún existe")

    await close_db()

    print("\n" + "=" * 60)
    print("✅ Eliminación completada!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(delete_demo_chapter())
