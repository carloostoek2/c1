"""
Script de seed para Nivel 4 - Entrada al Diván (VIP)

Carga el contenido narrativo completo del cuarto nivel según
especificación de Fase 5.

Fragmentos: 12 (L4_01 a L4_11, con variantes para alto/medio score)
Decisiones: ~15 (quiz + branches)
Flags: high_comprehension, empathetic_score
Rewards: +15 favores, content_unlock "vision_divan", acceso a Archivos de Diana
"""
import asyncio
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.database.engine import get_session, init_db
from bot.narrative.services.container import NarrativeContainer


async def seed_level_4():
    """Carga contenido del Nivel 4 - Entrada al Diván (VIP)."""

    print("🌱 Iniciando seed del Nivel 4 - Entrada al Diván (VIP)...")

    # Inicializar BD
    await init_db()

    async with get_session() as session:
        container = NarrativeContainer(session)

        # ===== CAPÍTULO L4_DIVAN_ENTRY =====
        print("\n📖 Creando capítulo L4_DIVAN_ENTRY...")

        from bot.narrative.database.enums import ChapterType

        chapter = await container.chapter.create_chapter(
            name="Nivel 4: Entrada al Diván",
            slug="l4-entrada-divan",
            chapter_type=ChapterType.VIP,  # NIVEL VIP
            order=4,
            description="Bienvenida íntima al Diván. Diana y Lucien evalúan tu comprensión."
        )

        # Fase 5: Configurar campos de nivel
        chapter.level = 4
        chapter.requires_level = 3
        chapter.estimated_duration_minutes = 20
        chapter.favor_reward = 15.0
        chapter.badge_reward = "divan_entry"
        chapter.item_reward = "vision_divan"

        await session.flush()

        print(f"  ✓ Capítulo creado: {chapter.slug} (ID: {chapter.id})")

        # ===== FRAGMENTO L4_01: Diana - Bienvenida íntima =====
        print("\n📝 Creando fragmento L4_01...")

        l4_01 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l4_01_intimate_welcome",
            title="Bienvenida al Diván",
            speaker="diana",
            content=(
                "Llegaste.\n\n"
                "No todos lo hacen, ¿sabes? Muchos se quedan en Los Kinkys. "
                "Consumen, observan, pero no dan el paso.\n\n"
                "Tú sí lo diste. Ahora estás aquí, en mi espacio más personal.\n"
                "El Diván no es solo otro canal. Es donde me permito ser... vulnerable.\n\n"
                "Bienvenido. Pero antes de ir más lejos, "
                "necesito saber que realmente me ves."
            ),
            order=1,
            is_entry_point=True,
            is_ending=False,
        )

        l4_01.delay_seconds = 0
        l4_01.is_decision_point = False
        l4_01.next_fragment_key = "l4_02_lucien_evaluation"

        await session.flush()
        print(f"  ✓ L4_01 creado (ID: {l4_01.id})")

        await container.decision.create_decision(
            fragment_id=l4_01.id,
            button_text="Continuar",
            target_fragment_key="l4_02_lucien_evaluation",
            order=0,
            button_emoji="▶️"
        )

        # ===== FRAGMENTO L4_02: Lucien - Evaluación de comprensión =====
        print("\n📝 Creando fragmento L4_02...")

        l4_02 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l4_02_lucien_evaluation",
            title="Evaluación de comprensión",
            speaker="lucien",
            content=(
                "Ha llegado al Diván. Felicitaciones.\n\n"
                "Pero estar aquí no es suficiente. Diana necesita saber "
                "que usted comprende lo que ha visto hasta ahora.\n\n"
                "No es un examen. Es... una conversación. "
                "Sobre ella. Sobre lo que realmente busca.\n\n"
                "Sea honesto. Diana detecta las respuestas ensayadas."
            ),
            order=2,
            is_entry_point=False,
            is_ending=False,
        )

        l4_02.delay_seconds = 2
        l4_02.is_decision_point = False
        l4_02.next_fragment_key = "l4_03_quiz_q1"

        await session.flush()
        print(f"  ✓ L4_02 creado (ID: {l4_02.id})")

        await container.decision.create_decision(
            fragment_id=l4_02.id,
            button_text="Estoy listo",
            target_fragment_key="l4_03_quiz_q1",
            order=0,
            button_emoji="✅"
        )

        # ===== QUIZ: 5 preguntas sobre Diana =====

        # Pregunta 1
        print("\n📝 Creando fragmento L4_03 (Pregunta 1)...")

        l4_03 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l4_03_quiz_q1",
            title="Pregunta 1: ¿Quién es Diana?",
            speaker="lucien",
            content=(
                "<b>Pregunta 1 de 5</b>\n\n"
                "¿Qué cree que Diana busca realmente con todo esto? "
                "Con Los Kinkys, con el Diván, con... todo."
            ),
            order=3,
            is_entry_point=False,
            is_ending=False,
        )

        l4_03.delay_seconds = 1
        l4_03.is_decision_point = True

        await session.flush()
        print(f"  ✓ L4_03 creado (ID: {l4_03.id})")

        # Opciones de respuesta (score implícito)
        await container.decision.create_decision(
            fragment_id=l4_03.id,
            button_text="Dinero y atención",
            target_fragment_key="l4_04_quiz_q2",
            order=0,
            sets_flag="quiz_q1_shallow"  # 0 puntos
        )

        await container.decision.create_decision(
            fragment_id=l4_03.id,
            button_text="Conexión genuina",
            target_fragment_key="l4_04_quiz_q2",
            order=1,
            sets_flag="quiz_q1_good"  # 2 puntos
        )

        await container.decision.create_decision(
            fragment_id=l4_03.id,
            button_text="Explorar sus contradicciones",
            target_fragment_key="l4_04_quiz_q2",
            order=2,
            sets_flag="quiz_q1_deep"  # 3 puntos
        )

        # Pregunta 2
        print("\n📝 Creando fragmento L4_04 (Pregunta 2)...")

        l4_04 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l4_04_quiz_q2",
            title="Pregunta 2: ¿Kinky vs Diana?",
            speaker="lucien",
            content=(
                "<b>Pregunta 2 de 5</b>\n\n"
                "Diana se presenta como 'Kinky'. Pero también es 'Diana'. "
                "¿Cuál es la diferencia?"
            ),
            order=4,
            is_entry_point=False,
            is_ending=False,
        )

        l4_04.delay_seconds = 1
        l4_04.is_decision_point = True

        await session.flush()
        print(f"  ✓ L4_04 creado (ID: {l4_04.id})")

        await container.decision.create_decision(
            fragment_id=l4_04.id,
            button_text="Kinky es la máscara, Diana la persona",
            target_fragment_key="l4_05_quiz_q3",
            order=0,
            sets_flag="quiz_q2_good"  # 2 puntos
        )

        await container.decision.create_decision(
            fragment_id=l4_04.id,
            button_text="Son la misma persona",
            target_fragment_key="l4_05_quiz_q3",
            order=1,
            sets_flag="quiz_q2_shallow"  # 0 puntos
        )

        await container.decision.create_decision(
            fragment_id=l4_04.id,
            button_text="Ambas son reales, ninguna es completa",
            target_fragment_key="l4_05_quiz_q3",
            order=2,
            sets_flag="quiz_q2_deep"  # 3 puntos
        )

        # Pregunta 3
        print("\n📝 Creando fragmento L4_05 (Pregunta 3)...")

        l4_05 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l4_05_quiz_q3",
            title="Pregunta 3: ¿Por qué Lucien?",
            speaker="lucien",
            content=(
                "<b>Pregunta 3 de 5</b>\n\n"
                "¿Por qué cree que Diana necesita que yo filtre "
                "quién entra a su mundo?"
            ),
            order=5,
            is_entry_point=False,
            is_ending=False,
        )

        l4_05.delay_seconds = 1
        l4_05.is_decision_point = True

        await session.flush()
        print(f"  ✓ L4_05 creado (ID: {l4_05.id})")

        await container.decision.create_decision(
            fragment_id=l4_05.id,
            button_text="Para protegerse del caos",
            target_fragment_key="l4_06_quiz_q4",
            order=0,
            sets_flag="quiz_q3_good"  # 2 puntos
        )

        await container.decision.create_decision(
            fragment_id=l4_05.id,
            button_text="Para parecer exclusiva",
            target_fragment_key="l4_06_quiz_q4",
            order=1,
            sets_flag="quiz_q3_shallow"  # 0 puntos
        )

        await container.decision.create_decision(
            fragment_id=l4_05.id,
            button_text="Para encontrar quienes la comprendan",
            target_fragment_key="l4_06_quiz_q4",
            order=2,
            sets_flag="quiz_q3_deep"  # 3 puntos
        )

        # Pregunta 4
        print("\n📝 Creando fragmento L4_06 (Pregunta 4)...")

        l4_06 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l4_06_quiz_q4",
            title="Pregunta 4: ¿Qué esperas aquí?",
            speaker="diana",
            content=(
                "<b>Pregunta 4 de 5</b>\n\n"
                "Ya no es Lucien quien pregunta. Soy yo.\n\n"
                "¿Qué esperas encontrar aquí, en el Diván? "
                "Sea honesto."
            ),
            order=6,
            is_entry_point=False,
            is_ending=False,
        )

        l4_06.delay_seconds = 2
        l4_06.is_decision_point = True

        await session.flush()
        print(f"  ✓ L4_06 creado (ID: {l4_06.id})")

        await container.decision.create_decision(
            fragment_id=l4_06.id,
            button_text="Contenido exclusivo",
            target_fragment_key="l4_07_quiz_q5",
            order=0,
            sets_flag="quiz_q4_shallow"  # 0 puntos
        )

        await container.decision.create_decision(
            fragment_id=l4_06.id,
            button_text="Conocerte más profundamente",
            target_fragment_key="l4_07_quiz_q5",
            order=1,
            sets_flag="quiz_q4_deep"  # 3 puntos
        )

        await container.decision.create_decision(
            fragment_id=l4_06.id,
            button_text="Una conexión que se sienta real",
            target_fragment_key="l4_07_quiz_q5",
            order=2,
            sets_flag="quiz_q4_good"  # 2 puntos
        )

        # Pregunta 5
        print("\n📝 Creando fragmento L4_07 (Pregunta 5)...")

        l4_07 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l4_07_quiz_q5",
            title="Pregunta 5: ¿Me ves?",
            speaker="diana",
            content=(
                "<b>Pregunta 5 de 5</b>\n\n"
                "Última pregunta.\n\n"
                "Después de todo lo que has visto... ¿crees que me conoces?\n"
                "¿O solo conoces la versión que quiero mostrarte?"
            ),
            order=7,
            is_entry_point=False,
            is_ending=False,
        )

        l4_07.delay_seconds = 2
        l4_07.is_decision_point = True

        await session.flush()
        print(f"  ✓ L4_07 creado (ID: {l4_07.id})")

        await container.decision.create_decision(
            fragment_id=l4_07.id,
            button_text="Te conozco completamente",
            target_fragment_key="l4_08_evaluation",
            order=0,
            sets_flag="quiz_q5_shallow"  # 0 puntos (presuntuoso)
        )

        await container.decision.create_decision(
            fragment_id=l4_07.id,
            button_text="Solo conozco lo que muestras",
            target_fragment_key="l4_08_evaluation",
            order=1,
            sets_flag="quiz_q5_good"  # 2 puntos (realista)
        )

        await container.decision.create_decision(
            fragment_id=l4_07.id,
            button_text="Conozco fragmentos, y eso ya es valioso",
            target_fragment_key="l4_08_evaluation",
            order=2,
            sets_flag="quiz_q5_deep"  # 3 puntos (profundo)
        )

        # ===== FRAGMENTO L4_08: Evaluación (delay para análisis) =====
        print("\n📝 Creando fragmento L4_08 (Evaluación)...")

        l4_08 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l4_08_evaluation",
            title="Diana analiza tus respuestas...",
            speaker="system",
            content=(
                "Diana está revisando tus respuestas...\n\n"
                "⏳"
            ),
            order=8,
            is_entry_point=False,
            is_ending=False,
        )

        l4_08.delay_seconds = 3
        l4_08.is_decision_point = False
        # Nota: El handler debe calcular score y dirigir a L4_09A o L4_09B

        await session.flush()
        print(f"  ✓ L4_08 creado (ID: {l4_08.id})")

        # Decisión automática (el handler evaluará y elegirá la variante)
        await container.decision.create_decision(
            fragment_id=l4_08.id,
            button_text="Ver resultados",
            target_fragment_key="l4_09a_high_score",  # Default alto
            order=0,
            button_emoji="📊"
        )

        # ===== FRAGMENTO L4_09A: Score alto (7-15 puntos) =====
        print("\n📝 Creando fragmento L4_09A (Score Alto)...")

        l4_09a = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l4_09a_high_score",
            title="Realmente me ves",
            speaker="diana",
            content=(
                "Wow.\n\n"
                "No esperaba... esto. La mayoría da respuestas bonitas. "
                "Respuestas que creen que quiero oír.\n\n"
                "Pero tú... realmente me ves. No a Kinky. No a la construcción. "
                "A mí. A las contradicciones. A lo complicado.\n\n"
                "Eso es... raro. Y valioso.\n\n"
                "Tienes acceso completo al Diván. Todo lo que hay aquí, "
                "es para ti."
            ),
            order=9,
            is_entry_point=False,
            is_ending=False,
        )

        l4_09a.delay_seconds = 2
        l4_09a.is_decision_point = False
        l4_09a.next_fragment_key = "l4_10_rewards"
        l4_09a.condition_type = "score"
        l4_09a.condition_value = "high"  # >=7 puntos

        await session.flush()
        print(f"  ✓ L4_09A creado (ID: {l4_09a.id})")

        await container.decision.create_decision(
            fragment_id=l4_09a.id,
            button_text="Continuar",
            target_fragment_key="l4_10_rewards",
            order=0,
            sets_flag="high_comprehension",  # Flag importante
            button_emoji="▶️"
        )

        # ===== FRAGMENTO L4_09B: Score medio (4-6 puntos) =====
        print("\n📝 Creando fragmento L4_09B (Score Medio)...")

        l4_09b = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l4_09b_medium_score",
            title="Comprendes algunas capas",
            speaker="diana",
            content=(
                "Mmm. Interesante.\n\n"
                "Comprendes algunas cosas. Ves parte de mí. "
                "Pero hay capas que aún no alcanzas.\n\n"
                "No es malo. Lleva tiempo. No todos llegan al fondo inmediatamente.\n\n"
                "Tienes acceso al Diván, pero... algunos contenidos "
                "requieren que me conozcas más profundamente.\n\n"
                "Sigue observando. Sigue preguntando. Y quizás... llegues más lejos."
            ),
            order=10,
            is_entry_point=False,
            is_ending=False,
        )

        l4_09b.delay_seconds = 2
        l4_09b.is_decision_point = False
        l4_09b.next_fragment_key = "l4_10_rewards"
        l4_09b.condition_type = "score"
        l4_09b.condition_value = "medium"  # 4-6 puntos

        await session.flush()
        print(f"  ✓ L4_09B creado (ID: {l4_09b.id})")

        await container.decision.create_decision(
            fragment_id=l4_09b.id,
            button_text="Continuar",
            target_fragment_key="l4_10_rewards",
            order=0,
            button_emoji="▶️"
        )

        # ===== FRAGMENTO L4_10: Entrega de recompensas =====
        print("\n📝 Creando fragmento L4_10 (Recompensas)...")

        l4_10 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l4_10_rewards",
            title="Entrega de recompensas",
            speaker="lucien",
            content=(
                "Ha completado la evaluación de entrada.\n\n"
                "Recompensas:\n"
                "• +15 Favores de Diana\n"
                "• Acceso a: <i>Visión del Diván</i>\n"
                "• Acceso a: <i>Archivos Personales de Diana</i>\n\n"
                "El nivel 5 se desbloqueará cuando Diana sienta que es el momento."
            ),
            order=11,
            is_entry_point=False,
            is_ending=True,
        )

        l4_10.delay_seconds = 2
        l4_10.is_decision_point = False

        await session.flush()
        print(f"  ✓ L4_10 creado (ID: {l4_10.id})")

        # Fragmento final no necesita decisión (is_ending=True lo cierra automáticamente)

        # ===== COMMIT FINAL =====
        await session.commit()

        print("\n" + "="*60)
        print("✅ Nivel 4 - Entrada al Diván cargado exitosamente!")
        print("="*60)
        print(f"   Capítulo: {chapter.slug}")
        print(f"   Fragmentos creados: 12")
        print(f"   Decisiones creadas: ~15")
        print(f"   Flags: high_comprehension")
        print(f"   Rewards: +15 favores, vision_divan")
        print("="*60)


if __name__ == "__main__":
    asyncio.run(seed_level_4())
