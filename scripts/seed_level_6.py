"""
Script de seed para Nivel 6 - Culminación (VIP)

Carga el contenido narrativo completo del sexto nivel según
especificación de Fase 5.

Fragmentos: 10 (L6_01 a L6_10)
Decisiones: ~8
Flags: completed_all_levels, witnessed_authenticity
Rewards: +25 favores, acceso a Círculo Íntimo, introducción al Mapa del Deseo
"""
import asyncio
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.database.engine import get_session, init_db
from bot.narrative.services.container import NarrativeContainer


async def seed_level_6():
    """Carga contenido del Nivel 6 - Culminación (VIP)."""

    print("🌱 Iniciando seed del Nivel 6 - Culminación (VIP)...")

    # Inicializar BD
    await init_db()

    async with get_session() as session:
        container = NarrativeContainer(session)

        # ===== CAPÍTULO L6_CULMINATION =====
        print("\n📖 Creando capítulo L6_CULMINATION...")

        from bot.narrative.database.enums import ChapterType

        chapter = await container.chapter.create_chapter(
            name="Nivel 6: Culminación",
            slug="l6-culminacion",
            chapter_type=ChapterType.VIP,
            order=6,
            description="El secreto final de Diana. El viaje llega a su culminación."
        )

        # Fase 5: Configurar campos de nivel
        chapter.level = 6
        chapter.requires_level = 5
        chapter.estimated_duration_minutes = 15
        chapter.favor_reward = 25.0
        chapter.badge_reward = "inner_circle"
        chapter.item_reward = "desire_map_access"

        await session.flush()

        print(f"  ✓ Capítulo creado: {chapter.slug} (ID: {chapter.id})")

        # ===== FRAGMENTO L6_01: Lucien abre el capítulo final =====
        print("\n📝 Creando fragmento L6_01...")

        l6_01 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l6_01_lucien_opening",
            title="El último nivel",
            speaker="lucien",
            content=(
                "Nivel 6. El final del viaje.\n\n"
                "Ha recorrido un largo camino. Desde Los Kinkys hasta aquí. "
                "Actuó cuando otros solo observaban. "
                "Observó cuando otros se distraían. "
                "Comprendió cuando otros juzgaban.\n\n"
                "Diana tiene algo que decirle. Algo que cambiará "
                "su perspectiva de todo esto."
            ),
            order=1,
            is_entry_point=True,
            is_ending=False,
        )

        l6_01.delay_seconds = 0
        l6_01.is_decision_point = False
        l6_01.next_fragment_key = "l6_02_diana_revelation"

        await session.flush()
        print(f"  ✓ L6_01 creado (ID: {l6_01.id})")

        await container.decision.create_decision(
            fragment_id=l6_01.id,
            button_text="Continuar",
            target_fragment_key="l6_02_diana_revelation",
            order=0,
            button_emoji="▶️"
        )

        # ===== FRAGMENTO L6_02: Diana revela que también evaluaba =====
        print("\n📝 Creando fragmento L6_02...")

        l6_02 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l6_02_diana_revelation",
            title="La revelación de Diana",
            speaker="diana",
            content=(
                "Hay algo que necesitas saber.\n\n"
                "Todo este tiempo, mientras tú me conocías... "
                "yo también te estaba conociendo a ti.\n\n"
                "Cada decisión que tomaste. Cada respuesta que diste. "
                "Cada momento en que elegiste actuar o esperar.\n\n"
                "No fue un juego. Fue una evaluación mutua.\n\n"
                "Porque yo también necesito saber con quién comparto "
                "las partes de mí que no muestro a nadie."
            ),
            order=2,
            is_entry_point=False,
            is_ending=False,
        )

        l6_02.delay_seconds = 2
        l6_02.is_decision_point = True

        await session.flush()
        print(f"  ✓ L6_02 creado (ID: {l6_02.id})")

        await container.decision.create_decision(
            fragment_id=l6_02.id,
            button_text="Eso tiene sentido",
            target_fragment_key="l6_03_understanding",
            order=0,
            button_emoji="💡"
        )

        await container.decision.create_decision(
            fragment_id=l6_02.id,
            button_text="Me siento... evaluado",
            target_fragment_key="l6_03_honest_reaction",
            order=1,
            button_emoji="🤔"
        )

        # ===== Variantes de respuesta =====

        # Respuesta: Comprensión
        print("\n📝 Creando fragmento L6_03_UNDERSTANDING...")

        l6_03_und = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l6_03_understanding",
            title="Comprensión mutua",
            speaker="diana",
            content=(
                "Sí. Lo entiendes.\n\n"
                "No puedo simplemente... abrirme a cualquiera. "
                "Necesito saber que quien está del otro lado "
                "puede manejar lo que comparto.\n\n"
                "Y tú... lo manejaste."
            ),
            order=3,
            is_entry_point=False,
            is_ending=False,
        )

        l6_03_und.delay_seconds = 2
        l6_03_und.next_fragment_key = "l6_04_the_journey"

        await session.flush()
        print(f"  ✓ L6_03_UNDERSTANDING creado (ID: {l6_03_und.id})")

        await container.decision.create_decision(
            fragment_id=l6_03_und.id,
            button_text="Continuar",
            target_fragment_key="l6_04_the_journey",
            order=0,
            button_emoji="▶️"
        )

        # Respuesta: Honestidad sobre sentirse evaluado
        print("\n📝 Creando fragmento L6_03_HONEST...")

        l6_03_hon = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l6_03_honest_reaction",
            title="Reacción honesta",
            speaker="diana",
            content=(
                "Lo sé. Y está bien sentirse así.\n\n"
                "La vulnerabilidad nunca es unidireccional. "
                "Si yo me abro, necesito saber que el otro lado es seguro.\n\n"
                "Por eso evaluaba. No para juzgarte. "
                "Sino para protegerme."
            ),
            order=4,
            is_entry_point=False,
            is_ending=False,
        )

        l6_03_hon.delay_seconds = 2
        l6_03_hon.next_fragment_key = "l6_04_the_journey"

        await session.flush()
        print(f"  ✓ L6_03_HONEST creado (ID: {l6_03_hon.id})")

        await container.decision.create_decision(
            fragment_id=l6_03_hon.id,
            button_text="Continuar",
            target_fragment_key="l6_04_the_journey",
            order=0,
            button_emoji="▶️"
        )

        # ===== FRAGMENTO L6_04: Reflexión sobre el viaje =====
        print("\n📝 Creando fragmento L6_04...")

        l6_04 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l6_04_the_journey",
            title="Síntesis del viaje",
            speaker="diana",
            content=(
                "Piensa en todo lo que pasó.\n\n"
                "Nivel 1: Probaste que podías actuar.\n"
                "Nivel 2: Probaste que podías observar.\n"
                "Nivel 3: Te conocí a través de tus deseos.\n"
                "Nivel 4: Comprendiste mis contradicciones.\n"
                "Nivel 5: Mostraste empatía ante mi vulnerabilidad.\n\n"
                "Y ahora estás aquí. En el nivel 6.\n"
                "Habiendo visto más de mí que la mayoría verá jamás."
            ),
            order=5,
            is_entry_point=False,
            is_ending=False,
        )

        l6_04.delay_seconds = 3
        l6_04.next_fragment_key = "l6_05_the_paradox"

        await session.flush()
        print(f"  ✓ L6_04 creado (ID: {l6_04.id})")

        await container.decision.create_decision(
            fragment_id=l6_04.id,
            button_text="Continuar",
            target_fragment_key="l6_05_the_paradox",
            order=0,
            button_emoji="▶️"
        )

        # ===== FRAGMENTO L6_05: La paradoja final =====
        print("\n📝 Creando fragmento L6_05...")

        l6_05 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l6_05_the_paradox",
            title="La paradoja del misterio",
            speaker="diana",
            content=(
                "Pero aquí está la paradoja.\n\n"
                "Después de mostrarte todo esto... "
                "después de compartir mis vulnerabilidades, "
                "mis contradicciones, mis miedos...\n\n"
                "¿Me conoces realmente?\n\n"
                "O solo conoces la versión de mí que elegí mostrarte, "
                "estructurada cuidadosamente a través de estos seis niveles?\n\n"
                "Quizás nunca lo sepas.\n"
                "Quizás ese es el punto."
            ),
            order=6,
            is_entry_point=False,
            is_ending=False,
        )

        l6_05.delay_seconds = 3
        l6_05.next_fragment_key = "l6_06_lucien_synthesis"

        await session.flush()
        print(f"  ✓ L6_05 creado (ID: {l6_05.id})")

        await container.decision.create_decision(
            fragment_id=l6_05.id,
            button_text="Continuar",
            target_fragment_key="l6_06_lucien_synthesis",
            order=0,
            button_emoji="▶️"
        )

        # ===== FRAGMENTO L6_06: Lucien - Humanidad auténtica =====
        print("\n📝 Creando fragmento L6_06...")

        l6_06 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l6_06_lucien_synthesis",
            title="Humanidad auténtica",
            speaker="lucien",
            content=(
                "Ha presenciado humanidad auténtica.\n\n"
                "No la perfección de Kinky. No la construcción.\n"
                "Sino a Diana, con sus grietas y contradicciones.\n\n"
                "Eso es raro. La mayoría prefiere la fantasía.\n"
                "Usted eligió la complejidad.\n\n"
                "Por eso está aquí. En el Círculo Íntimo."
            ),
            order=7,
            is_entry_point=False,
            is_ending=False,
        )

        l6_06.delay_seconds = 2
        l6_06.next_fragment_key = "l6_07_circle_access"

        await session.flush()
        print(f"  ✓ L6_06 creado (ID: {l6_06.id})")

        await container.decision.create_decision(
            fragment_id=l6_06.id,
            button_text="Continuar",
            target_fragment_key="l6_07_circle_access",
            order=0,
            sets_flag="witnessed_authenticity",
            button_emoji="▶️"
        )

        # ===== FRAGMENTO L6_07: Acceso al Círculo Íntimo =====
        print("\n📝 Creando fragmento L6_07...")

        l6_07 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l6_07_circle_access",
            title="Acceso al Círculo Íntimo",
            speaker="diana",
            content=(
                "El Círculo Íntimo no es solo otro nivel de contenido.\n\n"
                "Es donde converso directamente con quienes me conocen. "
                "Donde comparto cosas que no estructuro narrativamente. "
                "Momentos reales, sin editar.\n\n"
                "Tienes acceso ahora. Úsalo sabiamente."
            ),
            order=8,
            is_entry_point=False,
            is_ending=False,
        )

        l6_07.delay_seconds = 2
        l6_07.next_fragment_key = "l6_08_desire_map_intro"

        await session.flush()
        print(f"  ✓ L6_07 creado (ID: {l6_07.id})")

        await container.decision.create_decision(
            fragment_id=l6_07.id,
            button_text="Continuar",
            target_fragment_key="l6_08_desire_map_intro",
            order=0,
            button_emoji="▶️"
        )

        # ===== FRAGMENTO L6_08: Introducción al Mapa del Deseo (upsell) =====
        print("\n📝 Creando fragmento L6_08...")

        l6_08 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l6_08_desire_map_intro",
            title="El Mapa del Deseo",
            speaker="lucien",
            content=(
                "Un último detalle.\n\n"
                "Diana ha creado algo llamado el <b>Mapa del Deseo</b>.\n\n"
                "Es un sistema más profundo. Personalizado. "
                "Donde ella y usted exploran juntos territorios específicos "
                "basados en su arquetipo, sus respuestas, su viaje.\n\n"
                "No es para todos. Requiere compromiso adicional.\n"
                "Pero si llegó hasta aquí... quizás le interese.\n\n"
                "<i>Información disponible en el menú principal.</i>"
            ),
            order=9,
            is_entry_point=False,
            is_ending=False,
        )

        l6_08.delay_seconds = 2
        l6_08.next_fragment_key = "l6_09_final_words"

        await session.flush()
        print(f"  ✓ L6_08 creado (ID: {l6_08.id})")

        await container.decision.create_decision(
            fragment_id=l6_08.id,
            button_text="Continuar",
            target_fragment_key="l6_09_final_words",
            order=0,
            button_emoji="▶️"
        )

        # ===== FRAGMENTO L6_09: Palabras finales de Diana =====
        print("\n📝 Creando fragmento L6_09...")

        l6_09 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l6_09_final_words",
            title="Palabras finales",
            speaker="diana",
            content=(
                "Gracias por llegar hasta aquí.\n\n"
                "Por escuchar. Por comprender. Por no intentar arreglarme.\n"
                "Por aceptar que puedo ser Kinky y Diana al mismo tiempo.\n\n"
                "Este es el final del viaje estructurado.\n"
                "Pero no es el final de nuestra historia.\n\n"
                "Nos vemos en el Círculo Íntimo. 💋"
            ),
            order=10,
            is_entry_point=False,
            is_ending=False,
        )

        l6_09.delay_seconds = 3
        l6_09.next_fragment_key = "l6_10_rewards"

        await session.flush()
        print(f"  ✓ L6_09 creado (ID: {l6_09.id})")

        await container.decision.create_decision(
            fragment_id=l6_09.id,
            button_text="Continuar",
            target_fragment_key="l6_10_rewards",
            order=0,
            button_emoji="▶️"
        )

        # ===== FRAGMENTO L6_10: Recompensas finales =====
        print("\n📝 Creando fragmento L6_10...")

        l6_10 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l6_10_rewards",
            title="Recompensas finales",
            speaker="lucien",
            content=(
                "🎉 <b>NIVEL 6 COMPLETADO</b> 🎉\n\n"
                "Ha culminado el viaje de los seis niveles.\n\n"
                "<b>Recompensas finales:</b>\n"
                "• +25 Favores de Diana\n"
                "• Badge: <i>Inner Circle</i>\n"
                "• Acceso permanente al <b>Círculo Íntimo</b>\n"
                "• Información sobre el <i>Mapa del Deseo</i>\n\n"
                "<b>Estadísticas del viaje:</b>\n"
                "• 6 niveles completados\n"
                "• ~60 fragmentos narrativos experimentados\n"
                "• Arquetipo detectado y personalizado\n"
                "• Humanidad auténtica presenciada\n\n"
                "Felicitaciones. Muy pocos llegan hasta aquí."
            ),
            order=11,
            is_entry_point=False,
            is_ending=True,
        )

        l6_10.delay_seconds = 2

        l6_10.extra_metadata = {
            "sets_flag": "completed_all_levels",  # Flag se setea al completar el fragmento
            "completion_milestone": True
        }

        await session.flush()
        print(f"  ✓ L6_10 creado (ID: {l6_10.id})")

        # Fragmento final no necesita decisión (is_ending=True lo cierra automáticamente)
        # El flag "completed_all_levels" se setea via metadata

        # ===== COMMIT FINAL =====
        await session.commit()

        print("\n" + "="*60)
        print("✅ Nivel 6 - Culminación cargado exitosamente!")
        print("="*60)
        print(f"   Capítulo: {chapter.slug}")
        print(f"   Fragmentos creados: 10")
        print(f"   Decisiones creadas: ~8")
        print(f"   Flags: witnessed_authenticity, completed_all_levels")
        print(f"   Rewards: +25 favores, inner_circle, desire_map_access")
        print("="*60)


if __name__ == "__main__":
    asyncio.run(seed_level_6())
