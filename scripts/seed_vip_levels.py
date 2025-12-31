"""
Script maestro para cargar todos los niveles VIP (4-6) en orden.

Ejecuta los seeds de:
- Nivel 4: Entrada al Diván
- Nivel 5: Profundización
- Nivel 6: Culminación

Uso:
    python scripts/seed_vip_levels.py
"""
import asyncio
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.seed_level_4 import seed_level_4
from scripts.seed_level_5 import seed_level_5
from scripts.seed_level_6 import seed_level_6


async def seed_all_vip_levels():
    """Carga todos los niveles VIP en secuencia."""

    print("="*70)
    print("🎯 SEED DE NIVELES VIP (4-6) - FASE 5 SPRINT 3")
    print("="*70)
    print("\nEste script cargará los niveles VIP completos:")
    print("  • Nivel 4: Entrada al Diván (12 fragmentos)")
    print("  • Nivel 5: Profundización (15 fragmentos)")
    print("  • Nivel 6: Culminación (10 fragmentos)")
    print("\nTotal: 37 fragmentos VIP\n")
    print("="*70)

    try:
        # Nivel 4
        print("\n\n🔹 NIVEL 4: ENTRADA AL DIVÁN")
        print("-" * 70)
        await seed_level_4()

        # Nivel 5
        print("\n\n🔹 NIVEL 5: PROFUNDIZACIÓN")
        print("-" * 70)
        await seed_level_5()

        # Nivel 6
        print("\n\n🔹 NIVEL 6: CULMINACIÓN")
        print("-" * 70)
        await seed_level_6()

        # Resumen final
        print("\n\n" + "="*70)
        print("✅ ✅ ✅  TODOS LOS NIVELES VIP CARGADOS EXITOSAMENTE  ✅ ✅ ✅")
        print("="*70)
        print("\n📊 RESUMEN COMPLETO:")
        print(f"   • Nivel 4: 12 fragmentos, ~15 decisiones")
        print(f"   • Nivel 5: 15 fragmentos, ~18 decisiones")
        print(f"   • Nivel 6: 10 fragmentos, ~8 decisiones")
        print(f"\n   TOTAL: 37 fragmentos, ~41 decisiones")
        print(f"\n   Flags narrativos: ~12 (high_comprehension, empathetic_response, etc.)")
        print(f"   Rewards totales: +60 favores, 3 badges, acceso Círculo Íntimo")
        print("\n" + "="*70)
        print("\n🎮 Los usuarios VIP pueden ahora acceder a los niveles 4-6 desde /historia")
        print("="*70)

    except Exception as e:
        print(f"\n❌ Error durante el seed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(seed_all_vip_levels())
