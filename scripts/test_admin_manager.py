#!/usr/bin/env python3
"""
Script de prueba para admin_user_manager.py

Ejecuta una serie de pruebas para verificar que todas las funcionalidades
del admin user manager funcionan correctamente.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from bot.database.engine import get_session, init_db
from bot.database.models import User
from bot.gamification.database.models import UserGamification


async def find_test_user():
    """Encuentra un usuario de prueba en la base de datos."""
    await init_db()  # Inicializar BD
    async with get_session() as session:
        result = await session.execute(
            select(User).limit(1)
        )
        user = result.scalar_one_or_none()
        return user


async def main():
    """Ejecuta las pruebas."""
    print("🔍 Buscando usuario de prueba en la base de datos...")
    user = await find_test_user()

    if not user:
        print("❌ No se encontraron usuarios en la base de datos.")
        print("ℹ️  Interactúa con el bot primero para crear un usuario.")
        return

    user_id = user.user_id
    print(f"✅ Usuario encontrado: {user.full_name} (ID: {user_id})")
    print(f"\n📋 Para probar el script, ejecuta:")
    print(f"\n1. Ver información completa:")
    print(f"   python scripts/admin_user_manager.py info {user_id}")
    print(f"\n2. Ver historial de transacciones:")
    print(f"   python scripts/admin_user_manager.py transactions {user_id}")
    print(f"\n3. Agregar 100 besitos:")
    print(f"   python scripts/admin_user_manager.py add-besitos {user_id} 100")
    print(f"\n4. Establecer besitos a 500:")
    print(f"   python scripts/admin_user_manager.py set-besitos {user_id} 500")
    print(f"\n5. Resetear estado narrativo:")
    print(f"   python scripts/admin_user_manager.py reset-narrative {user_id}")
    print(f"\n6. ⭐ Resetear onboarding completo (RECOMENDADO para usuarios Free):")
    print(f"   python scripts/admin_user_manager.py reset-onboarding {user_id}")
    print(f"\n7. Resetear daily gift:")
    print(f"   python scripts/admin_user_manager.py reset-daily-gift {user_id}")
    print(f"\n8. Resetear streaks:")
    print(f"   python scripts/admin_user_manager.py reset-streaks {user_id}")
    print(f"\n⚠️  PELIGROSO - Reset completo:")
    print(f"   python scripts/admin_user_manager.py reset-all {user_id} --confirm")


if __name__ == "__main__":
    asyncio.run(main())
