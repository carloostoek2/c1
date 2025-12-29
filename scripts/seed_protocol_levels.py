#!/usr/bin/env python3
"""
Script para inicializar los niveles del Protocolo de Acceso.

Crea los 7 niveles del sistema de gamificación "El Mayordomo del Diván":
1. Visitante (0 Favores) - Usuario nuevo
2. Observado (5 Favores) - Lucien ha notado su presencia
3. Evaluado (15 Favores) - Ha pasado primeras pruebas
4. Reconocido (35 Favores) - Diana sabe que existe
5. Admitido (70 Favores) - Tiene derecho a estar
6. Confidente (120 Favores) - Lucien comparte información
7. Guardián de Secretos (200 Favores) - Círculo más íntimo

Uso:
    python scripts/seed_protocol_levels.py
"""

import asyncio
import sys
from pathlib import Path

# Añadir root al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from bot.database.engine import get_session
from bot.gamification.database.models import Level

# Definición de los niveles del Protocolo de Acceso
PROTOCOL_LEVELS = [
    {
        "name": "Visitante",
        "min_besitos": 0,
        "order": 1,
        "benefits": '{"description": "Usuario nuevo. Lucien observa en silencio."}'
    },
    {
        "name": "Observado",
        "min_besitos": 5,
        "order": 2,
        "benefits": '{"description": "Lucien ha notado su presencia. Primeras interacciones."}'
    },
    {
        "name": "Evaluado",
        "min_besitos": 15,
        "order": 3,
        "benefits": '{"description": "Ha pasado las primeras pruebas. Acceso a misiones básicas."}'
    },
    {
        "name": "Reconocido",
        "min_besitos": 35,
        "order": 4,
        "benefits": '{"description": "Diana sabe que existe. Acceso a contenido exclusivo."}'
    },
    {
        "name": "Admitido",
        "min_besitos": 70,
        "order": 5,
        "benefits": '{"description": "Tiene derecho a estar. Misiones especiales desbloqueadas."}'
    },
    {
        "name": "Confidente",
        "min_besitos": 120,
        "order": 6,
        "benefits": '{"description": "Lucien comparte información privilegiada. Recompensas únicas."}'
    },
    {
        "name": "Guardián de Secretos",
        "min_besitos": 200,
        "order": 7,
        "benefits": '{"description": "Círculo más íntimo de Diana. Máximo nivel de confianza."}'
    },
]


async def seed_protocol_levels(force_update: bool = False):
    """
    Crea o actualiza los niveles del Protocolo de Acceso.

    Args:
        force_update: Si True, actualiza niveles existentes con los nuevos valores
    """
    async with get_session() as session:
        print("📊 Verificando niveles del Protocolo de Acceso...")

        created = 0
        updated = 0
        skipped = 0

        for level_data in PROTOCOL_LEVELS:
            # Verificar si el nivel ya existe por nombre
            stmt = select(Level).where(Level.name == level_data["name"])
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                if force_update:
                    # Actualizar nivel existente
                    existing.min_besitos = level_data["min_besitos"]
                    existing.order = level_data["order"]
                    existing.benefits = level_data["benefits"]
                    existing.active = True
                    print(f"  ✏️  Actualizado: {level_data['name']} ({level_data['min_besitos']} Favores)")
                    updated += 1
                else:
                    print(f"  ⏭️  Ya existe: {level_data['name']}")
                    skipped += 1
            else:
                # Verificar si existe nivel con mismo order o min_besitos
                stmt_order = select(Level).where(Level.order == level_data["order"])
                result_order = await session.execute(stmt_order)
                existing_order = result_order.scalar_one_or_none()

                if existing_order and force_update:
                    # Desactivar nivel antiguo con ese order
                    existing_order.active = False
                    print(f"  🗑️  Desactivado nivel antiguo: {existing_order.name}")

                # Crear nuevo nivel
                new_level = Level(
                    name=level_data["name"],
                    min_besitos=level_data["min_besitos"],
                    order=level_data["order"],
                    benefits=level_data["benefits"],
                    active=True
                )
                session.add(new_level)
                print(f"  ✅ Creado: {level_data['name']} ({level_data['min_besitos']} Favores)")
                created += 1

        await session.commit()

        print("\n" + "=" * 50)
        print(f"📈 Resumen:")
        print(f"   • Niveles creados: {created}")
        print(f"   • Niveles actualizados: {updated}")
        print(f"   • Niveles existentes (sin cambios): {skipped}")
        print("=" * 50)

        # Mostrar todos los niveles activos
        print("\n📊 Niveles del Protocolo de Acceso activos:")
        stmt = select(Level).where(Level.active == True).order_by(Level.order.asc())
        result = await session.execute(stmt)
        levels = result.scalars().all()

        for level in levels:
            print(f"   {level.order}. {level.name} - {level.min_besitos} Favores")


async def main():
    """Punto de entrada principal."""
    import argparse

    parser = argparse.ArgumentParser(description="Inicializa niveles del Protocolo de Acceso")
    parser.add_argument(
        "--force-update", "-f",
        action="store_true",
        help="Actualiza niveles existentes con los nuevos valores"
    )
    args = parser.parse_args()

    print("\n🏛️  El Mayordomo del Diván - Protocolo de Acceso")
    print("=" * 50)

    await seed_protocol_levels(force_update=args.force_update)

    print("\n✅ Proceso completado.")


if __name__ == "__main__":
    asyncio.run(main())
