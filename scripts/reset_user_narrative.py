#!/usr/bin/env python3
"""
Script para reiniciar el progreso narrativo de un usuario.

Elimina todo el progreso narrativo de un usuario específico,
permitiéndole empezar la historia desde cero.

Uso:
    python scripts/reset_user_narrative.py <user_id>
"""
import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from bot.database import get_session, init_db, close_db


async def reset_user_narrative(user_id: int):
    """Reinicia el progreso narrativo del usuario."""
    print(f"🔄 Reiniciando progreso narrativo del usuario {user_id}...")

    # Inicializar BD
    await init_db()

    async with get_session() as session:
        # 1. Eliminar progreso narrativo general
        print("\n📝 Eliminando progreso narrativo general...")
        result = await session.execute(
            text("""
                DELETE FROM user_narrative_progress
                WHERE user_id = :user_id
            """),
            {"user_id": user_id}
        )
        progress_deleted = result.rowcount
        print(f"  ✅ {progress_deleted} registros de progreso eliminados")

        # 2. Eliminar completions de capítulos
        print("\n📝 Eliminando capítulos completados...")
        result = await session.execute(
            text("""
                DELETE FROM chapter_completions
                WHERE user_id = :user_id
            """),
            {"user_id": user_id}
        )
        chapters_deleted = result.rowcount
        print(f"  ✅ {chapters_deleted} capítulos completados eliminados")

        # 3. Eliminar visitas a fragmentos
        print("\n📝 Eliminando visitas a fragmentos...")
        result = await session.execute(
            text("""
                DELETE FROM user_fragment_visits
                WHERE user_id = :user_id
            """),
            {"user_id": user_id}
        )
        fragments_deleted = result.rowcount
        print(f"  ✅ {fragments_deleted} visitas a fragmentos eliminadas")

        # 4. Eliminar historial de decisiones
        print("\n📝 Eliminando historial de decisiones...")
        result = await session.execute(
            text("""
                DELETE FROM user_decision_history
                WHERE user_id = :user_id
            """),
            {"user_id": user_id}
        )
        decisions_deleted = result.rowcount
        print(f"  ✅ {decisions_deleted} decisiones eliminadas")

        # 5. Eliminar cooldowns narrativos
        print("\n📝 Eliminando cooldowns narrativos...")
        result = await session.execute(
            text("""
                DELETE FROM narrative_cooldowns
                WHERE user_id = :user_id
            """),
            {"user_id": user_id}
        )
        cooldowns_deleted = result.rowcount
        print(f"  ✅ {cooldowns_deleted} cooldowns eliminados")

        # 6. Verificar user_inventory_items para pistas (si existe la tabla)
        print("\n📝 Buscando pistas en inventario...")
        result = await session.execute(
            text("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='user_inventory_items'
            """)
        )
        if result.scalar():
            # Verificar schema primero
            schema_result = await session.execute(
                text("PRAGMA table_info(user_inventory_items)")
            )
            columns = [row[1] for row in schema_result.fetchall()]

            if 'item_type' in columns:
                result = await session.execute(
                    text("""
                        DELETE FROM user_inventory_items
                        WHERE user_id = :user_id AND item_type = 'clue'
                    """),
                    {"user_id": user_id}
                )
                clues_deleted = result.rowcount
                print(f"  ✅ {clues_deleted} pistas eliminadas")
            else:
                print(f"  ⚠️ Tabla user_inventory_items existe pero no tiene item_type")
        else:
            print(f"  ℹ️ Tabla user_inventory_items no existe, omitiendo")

        await session.commit()

    await close_db()

    print("\n" + "=" * 60)
    print("✅ Reinicio completado!")
    print("=" * 60)
    print(f"\nResumen para usuario {user_id}:")
    print(f"  - Progreso general eliminado: {progress_deleted}")
    print(f"  - Capítulos completados reiniciados: {chapters_deleted}")
    print(f"  - Visitas a fragmentos eliminadas: {fragments_deleted}")
    print(f"  - Decisiones eliminadas: {decisions_deleted}")
    print(f"  - Cooldowns eliminados: {cooldowns_deleted}")
    print(f"\n🎮 El usuario puede empezar la historia desde cero.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python scripts/reset_user_narrative.py <user_id>")
        sys.exit(1)

    try:
        user_id = int(sys.argv[1])
    except ValueError:
        print("Error: user_id debe ser un número entero")
        sys.exit(1)

    asyncio.run(reset_user_narrative(user_id))
