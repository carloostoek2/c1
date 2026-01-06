#!/usr/bin/env python3
"""
Script administrativo para gestión directa de usuarios en la base de datos.

Permite realizar operaciones de mantenimiento y debugging sobre usuarios específicos:
- Ver información completa del usuario
- Resetear estado narrativo
- Gestionar besitos (ver, modificar, agregar, restar)
- Resetear daily gift claims
- Resetear streaks de gamificación
- Ver historial de transacciones
- Limpiar progreso completo

Uso:
    python scripts/admin_user_manager.py info <user_id>
    python scripts/admin_user_manager.py reset-narrative <user_id>
    python scripts/admin_user_manager.py reset-onboarding <user_id>
    python scripts/admin_user_manager.py set-besitos <user_id> <amount>
    python scripts/admin_user_manager.py add-besitos <user_id> <amount>
    python scripts/admin_user_manager.py reset-daily-gift <user_id>
    python scripts/admin_user_manager.py reset-streaks <user_id>
    python scripts/admin_user_manager.py transactions <user_id> [--limit 20]
    python scripts/admin_user_manager.py reset-all <user_id>
"""

import argparse
import asyncio
import sys
from datetime import datetime, UTC
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.engine import get_session, init_db
from bot.database.models import User, FreeChannelRequest, UserLifecycle
from bot.gamification.database.models import (
    UserGamification,
    BesitoTransaction,
    DailyGiftClaim,
    UserStreak,
)
from bot.narrative.database.models import (
    UserNarrativeProgress,
    UserDecisionHistory,
)
from bot.narrative.database.enums import ArchetypeType


class UserManager:
    """Gestor administrativo de usuarios."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user(self, user_id: int) -> User | None:
        """Obtiene un usuario por su ID."""
        result = await self.session.execute(
            select(User).where(User.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_info(self, user_id: int) -> dict:
        """Obtiene información completa del usuario."""
        user = await self.get_user(user_id)
        if not user:
            return None

        # Gamificación
        gamif_result = await self.session.execute(
            select(UserGamification).where(UserGamification.user_id == user_id)
        )
        gamif = gamif_result.scalar_one_or_none()

        # Narrativa
        narrative_result = await self.session.execute(
            select(UserNarrativeProgress).where(
                UserNarrativeProgress.user_id == user_id
            )
        )
        narrative = narrative_result.scalar_one_or_none()

        # Daily gift
        daily_gift_result = await self.session.execute(
            select(DailyGiftClaim).where(DailyGiftClaim.user_id == user_id)
        )
        daily_gift = daily_gift_result.scalar_one_or_none()

        # Streak
        streak_result = await self.session.execute(
            select(UserStreak).where(UserStreak.user_id == user_id)
        )
        streak = streak_result.scalar_one_or_none()

        return {
            "user": user,
            "gamification": gamif,
            "narrative": narrative,
            "daily_gift": daily_gift,
            "streak": streak,
        }

    async def reset_narrative_progress(self, user_id: int) -> bool:
        """Resetea el progreso narrativo del usuario."""
        # Eliminar historial de decisiones
        await self.session.execute(
            delete(UserDecisionHistory).where(
                UserDecisionHistory.user_id == user_id
            )
        )

        # Resetear progreso narrativo
        result = await self.session.execute(
            select(UserNarrativeProgress).where(
                UserNarrativeProgress.user_id == user_id
            )
        )
        progress = result.scalar_one_or_none()

        if progress:
            progress.current_chapter_id = None
            progress.current_fragment_key = None
            progress.detected_archetype = ArchetypeType.UNKNOWN
            progress.archetype_confidence = 0.0
            progress.total_decisions = 0
            progress.chapters_completed = 0
            progress.last_interaction = datetime.now(UTC)

        await self.session.commit()
        return True

    async def reset_onboarding(self, user_id: int) -> bool:
        """
        Resetea el proceso completo de onboarding del usuario.

        Esto prepara al usuario para empezar desde cero cuando sea
        aceptado nuevamente en el canal Free, incluyendo:
        - Progreso narrativo completo
        - Solicitudes Free pendientes
        - Estado del ciclo de vida (reset a 'new')

        Args:
            user_id: ID del usuario

        Returns:
            bool: True si exitoso
        """
        # 1. Resetear progreso narrativo
        await self.reset_narrative_progress(user_id)

        # 2. Limpiar solicitudes Free pendientes
        await self.session.execute(
            delete(FreeChannelRequest).where(
                FreeChannelRequest.user_id == user_id
            )
        )

        # 3. Resetear estado del ciclo de vida a 'new'
        lifecycle_result = await self.session.execute(
            select(UserLifecycle).where(UserLifecycle.user_id == user_id)
        )
        lifecycle = lifecycle_result.scalar_one_or_none()

        if lifecycle:
            lifecycle.current_state = "new"
            lifecycle.last_activity = datetime.now(UTC)
            lifecycle.risk_score = 0
            lifecycle.messages_sent_count = 0
            lifecycle.last_message_sent = None
            lifecycle.do_not_disturb = False
            lifecycle.state_changed_at = datetime.now(UTC)

        await self.session.commit()
        return True

    async def set_besitos(self, user_id: int, amount: int) -> bool:
        """Establece la cantidad exacta de besitos del usuario."""
        result = await self.session.execute(
            select(UserGamification).where(UserGamification.user_id == user_id)
        )
        gamif = result.scalar_one_or_none()

        if not gamif:
            print(f"⚠️  Usuario {user_id} no tiene perfil de gamificación.")
            return False

        old_amount = gamif.total_besitos
        difference = amount - old_amount

        gamif.total_besitos = amount

        if difference > 0:
            gamif.besitos_earned += difference
        else:
            gamif.besitos_spent += abs(difference)

        gamif.updated_at = datetime.now(UTC)

        # Registrar transacción
        transaction = BesitoTransaction(
            user_id=user_id,
            amount=difference,
            transaction_type="admin_adjustment",
            description=f"Ajuste manual de admin: {old_amount} → {amount}",
            reference_id=None,
            balance_after=amount,
        )
        self.session.add(transaction)

        await self.session.commit()
        return True

    async def add_besitos(self, user_id: int, amount: int) -> bool:
        """Agrega besitos al usuario."""
        result = await self.session.execute(
            select(UserGamification).where(UserGamification.user_id == user_id)
        )
        gamif = result.scalar_one_or_none()

        if not gamif:
            print(f"⚠️  Usuario {user_id} no tiene perfil de gamificación.")
            return False

        old_amount = gamif.total_besitos
        new_amount = old_amount + amount

        gamif.total_besitos = new_amount
        gamif.besitos_earned += amount
        gamif.updated_at = datetime.now(UTC)

        # Registrar transacción
        transaction = BesitoTransaction(
            user_id=user_id,
            amount=amount,
            transaction_type="admin_grant",
            description=f"Concesión manual de admin: +{amount} besitos",
            reference_id=None,
            balance_after=new_amount,
        )
        self.session.add(transaction)

        await self.session.commit()
        return True

    async def subtract_besitos(self, user_id: int, amount: int) -> bool:
        """Resta besitos al usuario."""
        result = await self.session.execute(
            select(UserGamification).where(UserGamification.user_id == user_id)
        )
        gamif = result.scalar_one_or_none()

        if not gamif:
            print(f"⚠️  Usuario {user_id} no tiene perfil de gamificación.")
            return False

        old_amount = gamif.total_besitos
        new_amount = max(0, old_amount - amount)  # No permitir negativos
        actual_subtracted = old_amount - new_amount

        gamif.total_besitos = new_amount
        gamif.besitos_spent += actual_subtracted
        gamif.updated_at = datetime.now(UTC)

        # Registrar transacción
        transaction = BesitoTransaction(
            user_id=user_id,
            amount=-actual_subtracted,
            transaction_type="admin_deduction",
            description=f"Deducción manual de admin: -{actual_subtracted} besitos",
            reference_id=None,
            balance_after=new_amount,
        )
        self.session.add(transaction)

        await self.session.commit()
        return True

    async def reset_daily_gift(self, user_id: int) -> bool:
        """Resetea el daily gift claim del usuario."""
        result = await self.session.execute(
            select(DailyGiftClaim).where(DailyGiftClaim.user_id == user_id)
        )
        daily_gift = result.scalar_one_or_none()

        if daily_gift:
            daily_gift.last_claim_date = None
            daily_gift.current_streak = 0
            daily_gift.updated_at = datetime.now(UTC)
            await self.session.commit()

        return True

    async def reset_streaks(self, user_id: int) -> bool:
        """Resetea los streaks de gamificación del usuario."""
        result = await self.session.execute(
            select(UserStreak).where(UserStreak.user_id == user_id)
        )
        streak = result.scalar_one_or_none()

        if streak:
            streak.current_streak = 0
            streak.last_reaction_date = None
            streak.updated_at = datetime.now(UTC)
            await self.session.commit()

        return True

    async def get_transactions(self, user_id: int, limit: int = 20) -> list:
        """Obtiene el historial de transacciones del usuario."""
        result = await self.session.execute(
            select(BesitoTransaction)
            .where(BesitoTransaction.user_id == user_id)
            .order_by(BesitoTransaction.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def reset_all(self, user_id: int) -> bool:
        """Resetea TODO el progreso del usuario (usar con cuidado)."""
        await self.reset_narrative_progress(user_id)
        await self.reset_daily_gift(user_id)
        await self.reset_streaks(user_id)

        # Resetear gamificación (pero mantener historial de transacciones)
        result = await self.session.execute(
            select(UserGamification).where(UserGamification.user_id == user_id)
        )
        gamif = result.scalar_one_or_none()

        if gamif:
            old_besitos = gamif.total_besitos
            gamif.total_besitos = 0
            gamif.besitos_earned = 0
            gamif.besitos_spent = 0
            gamif.current_level_id = None
            gamif.updated_at = datetime.now(UTC)

            # Registrar transacción de reset
            transaction = BesitoTransaction(
                user_id=user_id,
                amount=-old_besitos,
                transaction_type="admin_reset",
                description="Reset completo del perfil por admin",
                reference_id=None,
                balance_after=0,
            )
            self.session.add(transaction)

        await self.session.commit()
        return True


# ============================================================================
# CLI COMMANDS
# ============================================================================


async def cmd_info(args):
    """Muestra información completa del usuario."""
    await init_db()  # Inicializar BD
    async with get_session() as session:
        manager = UserManager(session)
        info = await manager.get_user_info(args.user_id)

        if not info:
            print(f"❌ Usuario {args.user_id} no encontrado.")
            return

        user = info["user"]
        gamif = info["gamification"]
        narrative = info["narrative"]
        daily_gift = info["daily_gift"]
        streak = info["streak"]

        print("\n" + "=" * 70)
        print(f"👤 INFORMACIÓN DEL USUARIO {user.user_id}")
        print("=" * 70)

        # Usuario básico
        print(f"\n📋 Información Básica:")
        print(f"  • Nombre: {user.full_name}")
        print(f"  • Username: @{user.username or 'N/A'}")
        print(f"  • Rol: {user.role.value}")
        print(f"  • Creado: {user.created_at}")

        # Gamificación
        if gamif:
            print(f"\n🎮 Gamificación:")
            print(f"  • Total Besitos: {gamif.total_besitos}")
            print(f"  • Besitos Ganados: {gamif.besitos_earned}")
            print(f"  • Besitos Gastados: {gamif.besitos_spent}")
            print(f"  • Nivel Actual: {gamif.current_level_id or 'N/A'}")
            print(f"  • Última Actualización: {gamif.updated_at}")
        else:
            print(f"\n🎮 Gamificación: No inicializado")

        # Narrativa
        if narrative:
            print(f"\n📖 Progreso Narrativo:")
            print(f"  • Capítulo Actual: {narrative.current_chapter_id or 'N/A'}")
            print(f"  • Fragmento Actual: {narrative.current_fragment_key or 'N/A'}")
            print(
                f"  • Arquetipo: {narrative.detected_archetype.value if narrative.detected_archetype else 'UNKNOWN'} "
                f"(confianza: {narrative.archetype_confidence:.0%})"
            )
            print(f"  • Total Decisiones: {narrative.total_decisions}")
            print(f"  • Capítulos Completados: {narrative.chapters_completed}")
            print(f"  • Última Interacción: {narrative.last_interaction}")
        else:
            print(f"\n📖 Progreso Narrativo: No inicializado")

        # Daily Gift
        if daily_gift:
            print(f"\n🎁 Regalo Diario:")
            print(
                f"  • Última Reclamación: {daily_gift.last_claim_date or 'Nunca'}"
            )
            print(f"  • Racha Actual: {daily_gift.current_streak} días")
            print(f"  • Récord Racha: {daily_gift.longest_streak} días")
            print(f"  • Total Reclamaciones: {daily_gift.total_claims}")
        else:
            print(f"\n🎁 Regalo Diario: No inicializado")

        # Streaks
        if streak:
            print(f"\n🔥 Rachas:")
            print(f"  • Racha Actual: {streak.current_streak}")
            print(f"  • Récord Racha: {streak.longest_streak}")
            print(
                f"  • Última Reacción: {streak.last_reaction_date or 'Nunca'}"
            )
        else:
            print(f"\n🔥 Rachas: No inicializado")

        print("\n" + "=" * 70 + "\n")


async def cmd_reset_narrative(args):
    """Resetea el estado narrativo del usuario."""
    await init_db()  # Inicializar BD
    async with get_session() as session:
        manager = UserManager(session)
        user = await manager.get_user(args.user_id)

        if not user:
            print(f"❌ Usuario {args.user_id} no encontrado.")
            return

        print(f"🔄 Reseteando estado narrativo de {user.full_name}...")
        success = await manager.reset_narrative_progress(args.user_id)

        if success:
            print(f"✅ Estado narrativo reseteado exitosamente.")
        else:
            print(f"❌ Error al resetear estado narrativo.")


async def cmd_reset_onboarding(args):
    """Resetea el onboarding completo del usuario."""
    await init_db()  # Inicializar BD
    async with get_session() as session:
        manager = UserManager(session)
        user = await manager.get_user(args.user_id)

        if not user:
            print(f"❌ Usuario {args.user_id} no encontrado.")
            return

        print(f"🔄 Reseteando onboarding completo de {user.full_name}...")
        print(f"   • Progreso narrativo")
        print(f"   • Solicitudes Free pendientes")
        print(f"   • Estado del ciclo de vida")

        success = await manager.reset_onboarding(args.user_id)

        if success:
            print(f"✅ Onboarding reseteado exitosamente.")
            print(f"ℹ️  El usuario comenzará desde cero al ser aceptado nuevamente.")
        else:
            print(f"❌ Error al resetear onboarding.")


async def cmd_set_besitos(args):
    """Establece la cantidad exacta de besitos."""
    await init_db()  # Inicializar BD
    async with get_session() as session:
        manager = UserManager(session)
        user = await manager.get_user(args.user_id)

        if not user:
            print(f"❌ Usuario {args.user_id} no encontrado.")
            return

        print(
            f"💰 Estableciendo besitos de {user.full_name} a {args.amount}..."
        )
        success = await manager.set_besitos(args.user_id, args.amount)

        if success:
            print(f"✅ Besitos establecidos a {args.amount}.")
        else:
            print(f"❌ Error al establecer besitos.")


async def cmd_add_besitos(args):
    """Agrega besitos al usuario."""
    await init_db()  # Inicializar BD
    async with get_session() as session:
        manager = UserManager(session)
        user = await manager.get_user(args.user_id)

        if not user:
            print(f"❌ Usuario {args.user_id} no encontrado.")
            return

        print(f"💰 Agregando {args.amount} besitos a {user.full_name}...")
        success = await manager.add_besitos(args.user_id, args.amount)

        if success:
            print(f"✅ Se agregaron {args.amount} besitos.")
        else:
            print(f"❌ Error al agregar besitos.")


async def cmd_subtract_besitos(args):
    """Resta besitos al usuario."""
    await init_db()  # Inicializar BD
    async with get_session() as session:
        manager = UserManager(session)
        user = await manager.get_user(args.user_id)

        if not user:
            print(f"❌ Usuario {args.user_id} no encontrado.")
            return

        print(f"💰 Restando {args.amount} besitos a {user.full_name}...")
        success = await manager.subtract_besitos(args.user_id, args.amount)

        if success:
            print(f"✅ Se restaron {args.amount} besitos.")
        else:
            print(f"❌ Error al restar besitos.")


async def cmd_reset_daily_gift(args):
    """Resetea el daily gift del usuario."""
    await init_db()  # Inicializar BD
    async with get_session() as session:
        manager = UserManager(session)
        user = await manager.get_user(args.user_id)

        if not user:
            print(f"❌ Usuario {args.user_id} no encontrado.")
            return

        print(f"🎁 Reseteando daily gift de {user.full_name}...")
        success = await manager.reset_daily_gift(args.user_id)

        if success:
            print(f"✅ Daily gift reseteado exitosamente.")
        else:
            print(f"❌ Error al resetear daily gift.")


async def cmd_reset_streaks(args):
    """Resetea los streaks del usuario."""
    await init_db()  # Inicializar BD
    async with get_session() as session:
        manager = UserManager(session)
        user = await manager.get_user(args.user_id)

        if not user:
            print(f"❌ Usuario {args.user_id} no encontrado.")
            return

        print(f"🔥 Reseteando streaks de {user.full_name}...")
        success = await manager.reset_streaks(args.user_id)

        if success:
            print(f"✅ Streaks reseteados exitosamente.")
        else:
            print(f"❌ Error al resetear streaks.")


async def cmd_transactions(args):
    """Muestra el historial de transacciones."""
    await init_db()  # Inicializar BD
    async with get_session() as session:
        manager = UserManager(session)
        user = await manager.get_user(args.user_id)

        if not user:
            print(f"❌ Usuario {args.user_id} no encontrado.")
            return

        transactions = await manager.get_transactions(
            args.user_id, args.limit
        )

        if not transactions:
            print(f"ℹ️  No hay transacciones para {user.full_name}.")
            return

        print("\n" + "=" * 90)
        print(
            f"💸 HISTORIAL DE TRANSACCIONES - {user.full_name} (últimas {len(transactions)})"
        )
        print("=" * 90)

        for tx in transactions:
            sign = "+" if tx.amount >= 0 else ""
            print(f"\n📝 Transacción #{tx.id}")
            print(f"  • Monto: {sign}{tx.amount} besitos")
            print(f"  • Tipo: {tx.transaction_type}")
            print(f"  • Descripción: {tx.description}")
            print(f"  • Balance después: {tx.balance_after}")
            print(f"  • Fecha: {tx.created_at}")

        print("\n" + "=" * 90 + "\n")


async def cmd_reset_all(args):
    """Resetea TODO el progreso del usuario."""
    await init_db()  # Inicializar BD
    async with get_session() as session:
        manager = UserManager(session)
        user = await manager.get_user(args.user_id)

        if not user:
            print(f"❌ Usuario {args.user_id} no encontrado.")
            return

        # Confirmación
        if not args.confirm:
            print(
                f"⚠️  ¡ADVERTENCIA! Esta acción reseteará TODO el progreso de {user.full_name}:"
            )
            print("  • Estado narrativo completo")
            print("  • Todos los besitos")
            print("  • Daily gift")
            print("  • Streaks")
            print("\nPara confirmar, ejecuta el comando con --confirm")
            return

        print(f"🔄 Reseteando TODO el progreso de {user.full_name}...")
        success = await manager.reset_all(args.user_id)

        if success:
            print(f"✅ Progreso completo reseteado exitosamente.")
        else:
            print(f"❌ Error al resetear progreso.")


# ============================================================================
# MAIN
# ============================================================================


def main():
    """Punto de entrada principal."""
    parser = argparse.ArgumentParser(
        description="Script administrativo para gestión de usuarios en BD"
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # info
    parser_info = subparsers.add_parser(
        "info", help="Muestra información completa del usuario"
    )
    parser_info.add_argument("user_id", type=int, help="ID del usuario")

    # reset-narrative
    parser_reset_narrative = subparsers.add_parser(
        "reset-narrative", help="Resetea el estado narrativo del usuario"
    )
    parser_reset_narrative.add_argument("user_id", type=int, help="ID del usuario")

    # reset-onboarding
    parser_reset_onboarding = subparsers.add_parser(
        "reset-onboarding", help="Resetea el onboarding completo del usuario"
    )
    parser_reset_onboarding.add_argument("user_id", type=int, help="ID del usuario")

    # set-besitos
    parser_set_besitos = subparsers.add_parser(
        "set-besitos", help="Establece la cantidad exacta de besitos"
    )
    parser_set_besitos.add_argument("user_id", type=int, help="ID del usuario")
    parser_set_besitos.add_argument("amount", type=int, help="Cantidad de besitos")

    # add-besitos
    parser_add_besitos = subparsers.add_parser(
        "add-besitos", help="Agrega besitos al usuario"
    )
    parser_add_besitos.add_argument("user_id", type=int, help="ID del usuario")
    parser_add_besitos.add_argument("amount", type=int, help="Cantidad a agregar")

    # subtract-besitos
    parser_subtract_besitos = subparsers.add_parser(
        "subtract-besitos", help="Resta besitos al usuario"
    )
    parser_subtract_besitos.add_argument("user_id", type=int, help="ID del usuario")
    parser_subtract_besitos.add_argument("amount", type=int, help="Cantidad a restar")

    # reset-daily-gift
    parser_reset_daily = subparsers.add_parser(
        "reset-daily-gift", help="Resetea el daily gift del usuario"
    )
    parser_reset_daily.add_argument("user_id", type=int, help="ID del usuario")

    # reset-streaks
    parser_reset_streaks = subparsers.add_parser(
        "reset-streaks", help="Resetea los streaks del usuario"
    )
    parser_reset_streaks.add_argument("user_id", type=int, help="ID del usuario")

    # transactions
    parser_transactions = subparsers.add_parser(
        "transactions", help="Muestra el historial de transacciones"
    )
    parser_transactions.add_argument("user_id", type=int, help="ID del usuario")
    parser_transactions.add_argument(
        "--limit", type=int, default=20, help="Cantidad de transacciones (default: 20)"
    )

    # reset-all
    parser_reset_all = subparsers.add_parser(
        "reset-all", help="Resetea TODO el progreso del usuario (PELIGROSO)"
    )
    parser_reset_all.add_argument("user_id", type=int, help="ID del usuario")
    parser_reset_all.add_argument(
        "--confirm",
        action="store_true",
        help="Confirmar reset completo",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Mapear comandos a funciones
    commands = {
        "info": cmd_info,
        "reset-narrative": cmd_reset_narrative,
        "reset-onboarding": cmd_reset_onboarding,
        "set-besitos": cmd_set_besitos,
        "add-besitos": cmd_add_besitos,
        "subtract-besitos": cmd_subtract_besitos,
        "reset-daily-gift": cmd_reset_daily_gift,
        "reset-streaks": cmd_reset_streaks,
        "transactions": cmd_transactions,
        "reset-all": cmd_reset_all,
    }

    cmd_func = commands.get(args.command)
    if cmd_func:
        asyncio.run(cmd_func(args))
    else:
        print(f"❌ Comando desconocido: {args.command}")
        parser.print_help()


if __name__ == "__main__":
    main()
