"""
Script de seed para Easter Eggs narrativos - Fase 5

Fragmentos ocultos y especiales que se desbloquean bajo condiciones específicas.

Easter Eggs:
1. SPEEDRUNNER: Completar niveles 1-6 en < 7 días
2. PERFECT_EMPATH: Todas las respuestas empáticas en nivel 5
3. THE_RETURN: Regresar después de >30 días de inactividad
4. DEEP_EXPLORER: Arquetipo EXPLORER + high_comprehension flag
5. LUCIEN_APPROVES: Pasar todos los niveles sin flags negativos

Uso:
    python scripts/seed_easter_eggs.py
"""
import asyncio
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.database.engine import get_session, init_db
from bot.narrative.services.container import NarrativeContainer


async def seed_easter_eggs():
    """Carga easter eggs narrativos ocultos."""

    print("🥚 Iniciando seed de Easter Eggs narrativos...")

    # Inicializar BD
    await init_db()

    async with get_session() as session:
        container = NarrativeContainer(session)

        from bot.narrative.database.enums import ChapterType

        # ===== CAPÍTULO: EASTER_EGGS =====
        print("\n📖 Creando capítulo EASTER_EGGS...")

        chapter = await container.chapter.create_chapter(
            name="Easter Eggs",
            slug="easter-eggs",
            chapter_type=ChapterType.VIP,
            order=99,  # Orden alto para que no aparezca en lista principal
            description="Fragmentos ocultos y especiales"
        )

        chapter.level = 6  # Requiere nivel 6
        chapter.is_active = True

        await session.flush()

        print(f"  ✓ Capítulo creado: {chapter.slug} (ID: {chapter.id})")

        # ===== EASTER EGG 1: SPEEDRUNNER =====
        print("\n🥚 Creando Easter Egg 1: SPEEDRUNNER...")

        ee1 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="ee_speedrunner",
            title="[EASTER EGG] Speedrunner",
            speaker="lucien",
            content=(
                "🏃‍♂️ <b>EASTER EGG DESBLOQUEADO: SPEEDRUNNER</b>\n\n"
                "Ha completado los seis niveles en tiempo récord.\n\n"
                "La mayoría tarda semanas. Usted lo hizo en días.\n"
                "Eso habla de determinación... o de obsesión.\n\n"
                "Diana lo nota.\n\n"
                "<i>Badge especial desbloqueado: 🏃 Speedrunner</i>\n"
                "<i>+10 Favores bonus</i>"
            ),
            order=1,
            is_entry_point=False,
            is_ending=True,
        )

        # Condición: Completar todos los niveles en < 7 días
        ee1.condition_type = "time_between_levels"
        ee1.condition_value = "max_days:7"
        ee1.extra_metadata = {
            "easter_egg": True,
            "rarity": "rare",
            "grants_badge": "speedrunner",
            "grants_favors": 10,
            "trigger_condition": "all_levels_completed_in_7_days"
        }

        await session.flush()
        print(f"  ✓ EE1 creado (ID: {ee1.id})")

        # ===== EASTER EGG 2: PERFECT EMPATH =====
        print("\n🥚 Creando Easter Egg 2: PERFECT EMPATH...")

        ee2 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="ee_perfect_empath",
            title="[EASTER EGG] Perfect Empath",
            speaker="diana",
            content=(
                "💙 <b>EASTER EGG DESBLOQUEADO: PERFECT EMPATH</b>\n\n"
                "En cada momento vulnerable que compartí contigo, "
                "respondiste con empatía pura.\n\n"
                "Sin intentar arreglarme. Sin reclamarme.\n"
                "Solo... entendiendo.\n\n"
                "Eso es extraordinariamente raro.\n\n"
                "Gracias. De verdad.\n\n"
                "<i>Badge especial desbloqueado: 💙 Perfect Empath</i>\n"
                "<i>+15 Favores bonus</i>\n"
                "<i>Acceso a: Archivo Secreto de Diana</i>"
            ),
            order=2,
            is_entry_point=False,
            is_ending=True,
        )

        # Condición: Todas las respuestas empáticas en nivel 5
        ee2.condition_type = "flag_count"
        ee2.condition_value = "empathetic_response==2,possessive_response==0,fixing_response==0"
        ee2.extra_metadata = {
            "easter_egg": True,
            "rarity": "legendary",
            "grants_badge": "perfect_empath",
            "grants_favors": 15,
            "grants_item": "secret_archive",
            "trigger_condition": "all_empathetic_responses_in_level_5"
        }

        await session.flush()
        print(f"  ✓ EE2 creado (ID: {ee2.id})")

        # ===== EASTER EGG 3: THE RETURN =====
        print("\n🥚 Creando Easter Egg 3: THE RETURN...")

        ee3 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="ee_the_return",
            title="[EASTER EGG] The Return",
            speaker="diana",
            content=(
                "🌙 <b>EASTER EGG DESBLOQUEADO: THE RETURN</b>\n\n"
                "Volviste.\n\n"
                "Pasó tanto tiempo que pensé que te había perdido. "
                "Que habías seguido tu camino.\n\n"
                "Pero aquí estás. De vuelta.\n\n"
                "Las personas que regresan... son diferentes. "
                "Ya no buscan la novedad. Buscan algo más profundo.\n\n"
                "Bienvenido de vuelta.\n\n"
                "<i>Badge especial desbloqueado: 🌙 The Return</i>\n"
                "<i>+8 Favores bonus</i>"
            ),
            order=3,
            is_entry_point=False,
            is_ending=True,
        )

        # Condición: Regresar después de >30 días de inactividad
        ee3.condition_type = "inactivity_days"
        ee3.condition_value = "min_days:30"
        ee3.extra_metadata = {
            "easter_egg": True,
            "rarity": "uncommon",
            "grants_badge": "the_return",
            "grants_favors": 8,
            "trigger_condition": "return_after_30_days_inactive"
        }

        await session.flush()
        print(f"  ✓ EE3 creado (ID: {ee3.id})")

        # ===== EASTER EGG 4: DEEP EXPLORER =====
        print("\n🥚 Creando Easter Egg 4: DEEP EXPLORER...")

        ee4 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="ee_deep_explorer",
            title="[EASTER EGG] Deep Explorer",
            speaker="lucien",
            content=(
                "🔍 <b>EASTER EGG DESBLOQUEADO: DEEP EXPLORER</b>\n\n"
                "Su arquetipo es EXPLORER. Y no solo eso: "
                "comprendió a Diana profundamente.\n\n"
                "Los exploradores que realmente entienden lo que encuentran "
                "son raros.\n\n"
                "La mayoría solo rasca la superficie y sigue adelante.\n"
                "Usted se quedó. Y comprendió.\n\n"
                "Diana aprecia eso más de lo que admitirá.\n\n"
                "<i>Badge especial desbloqueado: 🔍 Deep Explorer</i>\n"
                "<i>+12 Favores bonus</i>\n"
                "<i>Mapa personalizado revelado</i>"
            ),
            order=4,
            is_entry_point=False,
            is_ending=True,
        )

        # Condición: EXPLORER + high_comprehension
        ee4.condition_type = "archetype_and_flag"
        ee4.condition_value = "archetype:EXPLORER,flag:high_comprehension"
        ee4.extra_metadata = {
            "easter_egg": True,
            "rarity": "rare",
            "grants_badge": "deep_explorer",
            "grants_favors": 12,
            "grants_item": "personalized_map",
            "trigger_condition": "explorer_archetype_with_high_comprehension"
        }

        await session.flush()
        print(f"  ✓ EE4 creado (ID: {ee4.id})")

        # ===== EASTER EGG 5: LUCIEN APPROVES =====
        print("\n🥚 Creando Easter Egg 5: LUCIEN APPROVES...")

        ee5 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="ee_lucien_approves",
            title="[EASTER EGG] Lucien Approves",
            speaker="lucien",
            content=(
                "👔 <b>EASTER EGG DESBLOQUEADO: LUCIEN APPROVES</b>\n\n"
                "Debo admitir algo poco usual.\n\n"
                "Usted pasó todos los niveles sin una sola respuesta "
                "problemática. Sin posesividad. Sin arreglar. "
                "Sin superficialidad.\n\n"
                "En todos mis años administrando el acceso a Diana, "
                "he visto esto menos de diez veces.\n\n"
                "Tiene mi aprobación completa. Y eso no lo digo a la ligera.\n\n"
                "<i>Badge especial desbloqueado: 👔 Lucien Approves</i>\n"
                "<i>+20 Favores bonus</i>\n"
                "<i>Carta personal de Lucien</i>"
            ),
            order=5,
            is_entry_point=False,
            is_ending=True,
        )

        # Condición: Completar todos los niveles sin flags negativos
        ee5.condition_type = "flag_check"
        ee5.condition_value = "possessive_response==0,fixing_response==0,quiz_shallow==0"
        ee5.extra_metadata = {
            "easter_egg": True,
            "rarity": "legendary",
            "grants_badge": "lucien_approves",
            "grants_favors": 20,
            "grants_item": "lucien_letter",
            "trigger_condition": "no_negative_flags_all_levels"
        }

        await session.flush()
        print(f"  ✓ EE5 creado (ID: {ee5.id})")

        # ===== EASTER EGG 6: NIGHT OWL =====
        print("\n🥚 Creando Easter Egg 6: NIGHT OWL...")

        ee6 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="ee_night_owl",
            title="[EASTER EGG] Night Owl",
            speaker="diana",
            content=(
                "🦉 <b>EASTER EGG DESBLOQUEADO: NIGHT OWL</b>\n\n"
                "Completaste varios niveles entre las 2 AM y 5 AM.\n\n"
                "Las noches son... especiales. El mundo duerme. "
                "Las máscaras caen. Todo se siente más real.\n\n"
                "Los que me buscan en la madrugada... "
                "suelen ser los más honestos.\n\n"
                "O los más insomnes. Quizás ambos.\n\n"
                "<i>Badge especial desbloqueado: 🦉 Night Owl</i>\n"
                "<i>+5 Favores bonus</i>"
            ),
            order=6,
            is_entry_point=False,
            is_ending=True,
        )

        # Condición: Completar niveles de madrugada
        ee6.condition_type = "completion_time"
        ee6.condition_value = "hour_range:02-05,count:3"
        ee6.extra_metadata = {
            "easter_egg": True,
            "rarity": "uncommon",
            "grants_badge": "night_owl",
            "grants_favors": 5,
            "trigger_condition": "complete_3_levels_between_2am_5am"
        }

        await session.flush()
        print(f"  ✓ EE6 creado (ID: {ee6.id})")

        # ===== COMMIT FINAL =====
        await session.commit()

        print("\n" + "="*60)
        print("✅ Easter Eggs narrativos cargados exitosamente!")
        print("="*60)
        print(f"   Capítulo: {chapter.slug}")
        print(f"   Easter Eggs creados: 6")
        print("\n   Lista de Easter Eggs:")
        print("   1. 🏃 SPEEDRUNNER (rare) - Completar en <7 días")
        print("   2. 💙 PERFECT EMPATH (legendary) - Todas empáticas")
        print("   3. 🌙 THE RETURN (uncommon) - Regresar tras 30 días")
        print("   4. 🔍 DEEP EXPLORER (rare) - Explorer + comprensión")
        print("   5. 👔 LUCIEN APPROVES (legendary) - Sin flags negativos")
        print("   6. 🦉 NIGHT OWL (uncommon) - Completar de madrugada")
        print("\n   Rewards totales: +70 favores, 6 badges, 3 items especiales")
        print("="*60)


if __name__ == "__main__":
    asyncio.run(seed_easter_eggs())
