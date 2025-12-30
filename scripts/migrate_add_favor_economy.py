#!/usr/bin/env python3
"""
Script de migración para agregar soporte de economía de Favores.

Este script:
1. Convierte campos de besitos de Integer a Float en user_gamification y besito_transactions
2. Agrega campos de configuración de economía a gamification_config

Uso:
    python scripts/migrate_add_favor_economy.py
"""
import asyncio
import logging
import sys
from sqlalchemy import text

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def migrate_add_favor_economy():
    """Ejecuta la migración para agregar economía de Favores."""

    try:
        # Importar después de logging configurado
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy.pool import NullPool
        from config import Config

        logger.info("🚀 Iniciando migración: soporte de economía de Favores")
        logger.info("")

        # Crear engine directamente
        engine = create_async_engine(
            Config.DATABASE_URL,
            echo=False,
            poolclass=NullPool,
            connect_args={"check_same_thread": False, "timeout": 30}
        )
        logger.info("✅ Engine creado")

        async with engine.begin() as conn:
            # ============================================================
            # PASO 1: Convertir user_gamification a Float
            # ============================================================
            logger.info("📊 Paso 1: Convirtiendo user_gamification.besitos a Float...")

            # Verificar si la tabla existe
            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name='user_gamification'")
            )
            table_exists = result.scalar() is not None

            if not table_exists:
                logger.info("  ⚠️ Tabla 'user_gamification' no existe, se creará con los modelos nuevos")
            else:
                # Verificar si ya tiene los campos Float
                result = await conn.execute(
                    text("PRAGMA table_info(user_gamification)")
                )
                columns = {row[1]: row[2] for row in result.fetchall()}

                if 'total_besitos' in columns:
                    current_type = columns['total_besitos']
                    if current_type.upper() in ['INTEGER', 'INT']:
                        logger.info("  🔄 Convirtiendo de INTEGER a REAL (Float)...")

                        # Crear tabla nueva con Float
                        await conn.execute(text("""
                            CREATE TABLE user_gamification_new (
                                user_id INTEGER NOT NULL PRIMARY KEY,
                                total_besitos REAL NOT NULL DEFAULT 0.0,
                                besitos_earned REAL NOT NULL DEFAULT 0.0,
                                besitos_spent REAL NOT NULL DEFAULT 0.0,
                                current_level_id INTEGER,
                                created_at DATETIME NOT NULL,
                                updated_at DATETIME NOT NULL,
                                FOREIGN KEY(user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                                FOREIGN KEY(current_level_id) REFERENCES levels (id)
                            )
                        """))

                        # Copiar datos
                        await conn.execute(text("""
                            INSERT INTO user_gamification_new (
                                user_id, total_besitos, besitos_earned, besitos_spent,
                                current_level_id, created_at, updated_at
                            )
                            SELECT
                                user_id,
                                CAST(total_besitos AS REAL),
                                CAST(besitos_earned AS REAL),
                                CAST(besitos_spent AS REAL),
                                current_level_id,
                                created_at,
                                updated_at
                            FROM user_gamification
                        """))

                        # Drop old table
                        await conn.execute(text("DROP TABLE user_gamification"))

                        # Rename new table
                        await conn.execute(text("ALTER TABLE user_gamification_new RENAME TO user_gamification"))

                        # Recreate index
                        await conn.execute(text("""
                            CREATE INDEX ix_user_gamification_total_besitos ON user_gamification (total_besitos)
                        """))

                        logger.info("  ✅ user_gamification convertido a Float")
                    else:
                        logger.info(f"  ✓ user_gamification.total_besitos ya es {current_type}")

            # ============================================================
            # PASO 2: Convertir besito_transactions a Float
            # ============================================================
            logger.info("📊 Paso 2: Convirtiendo besito_transactions a Float...")

            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name='besito_transactions'")
            )
            table_exists = result.scalar() is not None

            if not table_exists:
                logger.info("  ⚠️ Tabla 'besito_transactions' no existe, se creará con los modelos nuevos")
            else:
                # Verificar tipo actual
                result = await conn.execute(
                    text("PRAGMA table_info(besito_transactions)")
                )
                columns = {row[1]: row[2] for row in result.fetchall()}

                if 'amount' in columns and columns['amount'].upper() in ['INTEGER', 'INT']:
                    logger.info("  🔄 Convirtiendo de INTEGER a REAL (Float)...")

                    # Crear tabla nueva
                    await conn.execute(text("""
                        CREATE TABLE besito_transactions_new (
                            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            amount REAL NOT NULL,
                            transaction_type VARCHAR(50) NOT NULL,
                            description VARCHAR(500) NOT NULL,
                            reference_id INTEGER,
                            balance_after REAL NOT NULL,
                            created_at DATETIME NOT NULL,
                            FOREIGN KEY(user_id) REFERENCES users (user_id) ON DELETE CASCADE
                        )
                    """))

                    # Copiar datos
                    await conn.execute(text("""
                        INSERT INTO besito_transactions_new (
                            id, user_id, amount, transaction_type, description,
                            reference_id, balance_after, created_at
                        )
                        SELECT
                            id, user_id,
                            CAST(amount AS REAL),
                            transaction_type, description,
                            reference_id,
                            CAST(balance_after AS REAL),
                            created_at
                        FROM besito_transactions
                    """))

                    # Drop old
                    await conn.execute(text("DROP TABLE besito_transactions"))

                    # Rename
                    await conn.execute(text("ALTER TABLE besito_transactions_new RENAME TO besito_transactions"))

                    # Recreate indexes
                    await conn.execute(text("""
                        CREATE INDEX idx_user_transactions_history ON besito_transactions (user_id, created_at)
                    """))
                    await conn.execute(text("""
                        CREATE INDEX idx_user_transaction_type ON besito_transactions (user_id, transaction_type)
                    """))
                    await conn.execute(text("""
                        CREATE INDEX idx_reference_transaction ON besito_transactions (reference_id, transaction_type)
                    """))

                    logger.info("  ✅ besito_transactions convertido a Float")
                else:
                    logger.info("  ✓ besito_transactions.amount ya es Float/REAL")

            # ============================================================
            # PASO 3: Agregar campos de economía a gamification_config
            # ============================================================
            logger.info("⚙️ Paso 3: Agregando campos de economía a gamification_config...")

            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name='gamification_config'")
            )
            table_exists = result.scalar() is not None

            if not table_exists:
                logger.info("  ⚠️ Tabla 'gamification_config' no existe, se creará con los modelos nuevos")
            else:
                # Verificar si los campos ya existen
                result = await conn.execute(
                    text("PRAGMA table_info(gamification_config)")
                )
                columns = {row[1] for row in result.fetchall()}

                economy_fields = [
                    ('earn_reaction_base', 'REAL NOT NULL DEFAULT 0.1'),
                    ('earn_first_reaction_day', 'REAL NOT NULL DEFAULT 0.5'),
                    ('limit_reactions_per_day', 'INTEGER NOT NULL DEFAULT 10'),
                    ('earn_mission_daily', 'REAL NOT NULL DEFAULT 1.0'),
                    ('earn_mission_weekly', 'REAL NOT NULL DEFAULT 3.0'),
                    ('earn_level_evaluation', 'REAL NOT NULL DEFAULT 5.0'),
                    ('earn_streak_7_days', 'REAL NOT NULL DEFAULT 2.0'),
                    ('earn_streak_30_days', 'REAL NOT NULL DEFAULT 10.0'),
                    ('earn_easter_egg_min', 'REAL NOT NULL DEFAULT 2.0'),
                    ('earn_easter_egg_max', 'REAL NOT NULL DEFAULT 5.0'),
                    ('earn_referral_active', 'REAL NOT NULL DEFAULT 5.0'),
                ]

                added_count = 0
                for field_name, field_def in economy_fields:
                    if field_name not in columns:
                        await conn.execute(text(f"""
                            ALTER TABLE gamification_config
                            ADD COLUMN {field_name} {field_def}
                        """))
                        logger.info(f"  ✅ Agregado campo: {field_name}")
                        added_count += 1
                    else:
                        logger.debug(f"  ✓ Campo {field_name} ya existe")

                if added_count > 0:
                    logger.info(f"  ✅ {added_count} campos de economía agregados")
                else:
                    logger.info("  ✓ Todos los campos de economía ya existen")

        # Cerrar engine
        await engine.dispose()
        logger.info("✅ Engine cerrado")

        logger.info("")
        logger.info("="*60)
        logger.info("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        logger.info("="*60)
        logger.info("")
        logger.info("Cambios aplicados:")
        logger.info("1. ✅ user_gamification.besitos → Float (soporte decimales)")
        logger.info("2. ✅ besito_transactions.amount/balance_after → Float")
        logger.info("3. ✅ 11 campos de configuración de economía agregados")
        logger.info("")
        logger.info("Configuración de economía:")
        logger.info("  - earn_reaction_base: 0.1 Favores")
        logger.info("  - earn_first_reaction_day: 0.5 Favores")
        logger.info("  - limit_reactions_per_day: 10")
        logger.info("  - earn_mission_daily: 1.0 Favores")
        logger.info("  - earn_mission_weekly: 3.0 Favores")
        logger.info("  - earn_level_evaluation: 5.0 Favores")
        logger.info("  - earn_streak_7/30_days: 2.0/10.0 Favores")
        logger.info("  - earn_easter_egg: 2.0-5.0 Favores")
        logger.info("  - earn_referral_active: 5.0 Favores")
        logger.info("")
        logger.info("Próximos pasos:")
        logger.info("1. Reiniciar el bot")
        logger.info("2. Los Favores ahora soportan decimales (0.1, 0.5, etc.)")
        logger.info("3. Configuración de economía disponible en BD")

        return True

    except Exception as e:
        logger.error(f"❌ Error en migración: {e}", exc_info=True)
        return False


async def main():
    """Punto de entrada."""
    try:
        success = await migrate_add_favor_economy()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
