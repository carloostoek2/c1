#!/usr/bin/env python3
"""
Migration script to add the database tables for CMS Journey (Content Sets).

This script ensures the following tables and columns are created:
- content_sets (table)
- user_content_access (table)
- shop_items.content_set_id (column)
- narrative_fragments.content_set_id (column)
- rewards.content_set_id (column)
"""
import asyncio
import logging
import sys
import os
from sqlalchemy import text

# Add project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def migrate_content_sets():
    """Executes the migration to add Content Set tables."""
    logger.info("🚀 Starting migration: Add Content Set Tables")
    
    try:
        from bot.database.engine import init_db, get_engine, close_db

        # This will create all tables defined in the models, including the new ones.
        await init_db()

        engine = get_engine()
        
        tables_to_check = [
            "content_sets",
            "user_content_access",
        ]
        
        columns_to_check = {
            "shop_items": "content_set_id",
            "narrative_fragments": "content_set_id",
            "rewards": "content_set_id",
        }

        async with engine.begin() as conn:
            for table_name in tables_to_check:
                result = await conn.execute(
                    text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                )
                if result.scalar() is not None:
                    logger.info(f"✅ Table '{table_name}' found.")
                else:
                    logger.error(f"❌ Migration failed: Table '{table_name}' was not created.")
                    return False
            
            for table_name, column_name in columns_to_check.items():
                result = await conn.execute(
                    text(f"PRAGMA table_info({table_name})")
                )
                columns = [row[1] for row in result.fetchall()]
                if column_name in columns:
                    logger.info(f"✅ Column '{column_name}' found in table '{table_name}'.")
                else:
                    logger.error(f"❌ Migration failed: Column '{column_name}' not found in table '{table_name}'.")
                    return False

        await close_db()
        logger.info("✅ Content Sets migration completed successfully.")
        return True

    except Exception as e:
        logger.error(f"❌ An error occurred during migration: {e}", exc_info=True)
        return False

async def main():
    """Script entry point."""
    success = await migrate_content_sets()
    if not success:
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())
