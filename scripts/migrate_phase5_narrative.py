"""
Script de migración manual para Fase 5 - Narrativa.

Aplica todos los cambios de esquema necesarios para los campos de Fase 5
en los modelos narrativos.
"""
import sqlite3
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

DB_PATH = "bot.db"


def migrate_phase5_fields():
    """Aplicar migración de Fase 5 a la base de datos."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("🔄 Iniciando migración Fase 5 - Narrativa...")

    try:
        # NarrativeChapter: Sistema de niveles y requisitos
        print("  → Extendiendo narrative_chapters...")

        # Verificar si columnas ya existen
        cursor.execute("PRAGMA table_info(narrative_chapters)")
        existing_columns = {col[1] for col in cursor.fetchall()}

        narrative_chapter_columns = [
            ("level", "INTEGER"),
            ("requires_level", "INTEGER"),
            ("requires_chapter_completed", "INTEGER"),
            ("requires_archetype", "VARCHAR(50)"),
            ("estimated_duration_minutes", "INTEGER"),
            ("favor_reward", "REAL"),
            ("badge_reward", "VARCHAR(50)"),
            ("item_reward", "VARCHAR(50)"),
        ]

        for col_name, col_type in narrative_chapter_columns:
            if col_name not in existing_columns:
                cursor.execute(f"ALTER TABLE narrative_chapters ADD COLUMN {col_name} {col_type}")
                print(f"    ✓ Agregado: {col_name}")

        # NarrativeFragment: Navegación y condiciones
        print("  → Extendiendo narrative_fragments...")
        cursor.execute("PRAGMA table_info(narrative_fragments)")
        existing_columns = {col[1] for col in cursor.fetchall()}

        narrative_fragment_columns = [
            ("delay_seconds", "INTEGER DEFAULT 0"),
            ("is_decision_point", "BOOLEAN DEFAULT 0"),
            ("next_fragment_key", "VARCHAR(50)"),
            ("condition_type", "VARCHAR(50)"),
            ("condition_value", "VARCHAR(100)"),
        ]

        for col_name, col_type in narrative_fragment_columns:
            if col_name not in existing_columns:
                cursor.execute(f"ALTER TABLE narrative_fragments ADD COLUMN {col_name} {col_type}")
                print(f"    ✓ Agregado: {col_name}")

        # FragmentDecision: Sistema de flags y favores
        print("  → Extendiendo fragment_decisions...")
        cursor.execute("PRAGMA table_info(fragment_decisions)")
        existing_columns = {col[1] for col in cursor.fetchall()}

        fragment_decision_columns = [
            ("subtext", "VARCHAR(200)"),
            ("favor_change", "REAL"),
            ("sets_flag", "VARCHAR(50)"),
            ("requires_flag", "VARCHAR(50)"),
        ]

        for col_name, col_type in fragment_decision_columns:
            if col_name not in existing_columns:
                cursor.execute(f"ALTER TABLE fragment_decisions ADD COLUMN {col_name} {col_type}")
                print(f"    ✓ Agregado: {col_name}")

        # UserNarrativeProgress: Niveles, flags, misiones
        print("  → Extendiendo user_narrative_progress...")
        cursor.execute("PRAGMA table_info(user_narrative_progress)")
        existing_columns = {col[1] for col in cursor.fetchall()}

        user_progress_columns = [
            ("current_level", "INTEGER DEFAULT 1"),
            ("chapters_completed_list", "TEXT"),  # JSON
            ("fragments_seen", "TEXT"),  # JSON
            ("decisions_made", "TEXT"),  # JSON
            ("narrative_flags", "TEXT"),  # JSON
            ("active_mission_id", "VARCHAR(50)"),
            ("mission_started_at", "TIMESTAMP"),
            ("mission_data", "TEXT"),  # JSON
            ("level_1_completed_at", "TIMESTAMP"),
            ("level_2_completed_at", "TIMESTAMP"),
            ("level_3_completed_at", "TIMESTAMP"),
            ("level_4_completed_at", "TIMESTAMP"),
            ("level_5_completed_at", "TIMESTAMP"),
            ("level_6_completed_at", "TIMESTAMP"),
        ]

        for col_name, col_type in user_progress_columns:
            if col_name not in existing_columns:
                cursor.execute(f"ALTER TABLE user_narrative_progress ADD COLUMN {col_name} {col_type}")
                print(f"    ✓ Agregado: {col_name}")

        # Commit cambios
        conn.commit()
        print("\n✅ Migración completada exitosamente!")

        # Mostrar resumen
        print("\n📊 Resumen de cambios:")
        print(f"  • narrative_chapters: +{len(narrative_chapter_columns)} campos")
        print(f"  • narrative_fragments: +{len(narrative_fragment_columns)} campos")
        print(f"  • fragment_decisions: +{len(fragment_decision_columns)} campos")
        print(f"  • user_narrative_progress: +{len(user_progress_columns)} campos")
        print(f"\n  Total: +{len(narrative_chapter_columns) + len(narrative_fragment_columns) + len(fragment_decision_columns) + len(user_progress_columns)} campos")

    except sqlite3.Error as e:
        print(f"\n❌ Error durante migración: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

    return True


if __name__ == "__main__":
    success = migrate_phase5_fields()
    sys.exit(0 if success else 1)
