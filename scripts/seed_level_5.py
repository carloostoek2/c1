"""
Script de seed para Nivel 5 - Profundización (VIP)

Carga el contenido narrativo completo del quinto nivel según
especificación de Fase 5.

Fragmentos: 15 (L5_01 a L5_12, con branches para respuestas empáticas/posesivas/arregladoras)
Decisiones: ~18 (diálogos de vulnerabilidad con evaluación)
Flags: empathetic_responses, possessive_response, fixing_response
Rewards: +20 favores, content_unlock "personal_archive"
"""
import asyncio
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.database.engine import get_session, init_db
from bot.narrative.services.container import NarrativeContainer


async def seed_level_5():
    """Carga contenido del Nivel 5 - Profundización (VIP)."""

    print("🌱 Iniciando seed del Nivel 5 - Profundización (VIP)...")

    # Inicializar BD
    await init_db()

    async with get_session() as session:
        container = NarrativeContainer(session)

        # ===== CAPÍTULO L5_DEEPENING =====
        print("\n📖 Creando capítulo L5_DEEPENING...")

        from bot.narrative.database.enums import ChapterType

        chapter = await container.chapter.create_chapter(
            name="Nivel 5: Profundización",
            slug="l5-profundizacion",
            chapter_type=ChapterType.VIP,
            order=5,
            description="Diana comparte sus vulnerabilidades. La empatía es clave."
        )

        # Fase 5: Configurar campos de nivel
        chapter.level = 5
        chapter.requires_level = 4
        chapter.estimated_duration_minutes = 25
        chapter.favor_reward = 20.0
        chapter.badge_reward = "deep_connection"
        chapter.item_reward = "personal_archive"

        await session.flush()

        print(f"  ✓ Capítulo creado: {chapter.slug} (ID: {chapter.id})")

        # ===== FRAGMENTO L5_01: Diana reconoce la evolución =====
        print("\n📝 Creando fragmento L5_01...")

        l5_01 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l5_01_evolution",
            title="Tu evolución",
            speaker="diana",
            content=(
                "Has llegado lejos.\n\n"
                "Recuerdo cuando entraste a Los Kinkys por primera vez. "
                "No sabías qué esperar. Quizás solo curiosidad.\n\n"
                "Ahora estás aquí. En el nivel 5. Pasaste las pruebas. "
                "Me conoces mejor que la mayoría.\n\n"
                "Pero hay algo que aún no te he mostrado: "
                "las grietas. Los momentos donde no soy perfecta.\n\n"
                "¿Estás listo para eso?"
            ),
            order=1,
            is_entry_point=True,
            is_ending=False,
        )

        l5_01.delay_seconds = 0
        l5_01.is_decision_point = True

        await session.flush()
        print(f"  ✓ L5_01 creado (ID: {l5_01.id})")

        await container.decision.create_decision(
            fragment_id=l5_01.id,
            button_text="Estoy listo",
            target_fragment_key="l5_02_vulnerability_1",
            order=0,
            button_emoji="✅"
        )

        await container.decision.create_decision(
            fragment_id=l5_01.id,
            button_text="Dame un momento",
            target_fragment_key="l5_01b_take_time",
            order=1,
            button_emoji="⏸️"
        )

        # Branch: Usuario pide tiempo
        print("\n📝 Creando fragmento L5_01B (Tomarse tiempo)...")

        l5_01b = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l5_01b_take_time",
            title="Tomarse un momento",
            speaker="diana",
            content=(
                "Está bien. Tómate el tiempo que necesites.\n\n"
                "Lo que viene no es fácil. Ni para ti, ni para mí.\n\n"
                "Cuando estés listo, regresa."
            ),
            order=2,
            is_entry_point=False,
            is_ending=False,
        )

        l5_01b.delay_seconds = 1

        await session.flush()
        print(f"  ✓ L5_01B creado (ID: {l5_01b.id})")

        await container.decision.create_decision(
            fragment_id=l5_01b.id,
            button_text="Ahora estoy listo",
            target_fragment_key="l5_02_vulnerability_1",
            order=0,
            button_emoji="✅"
        )

        # ===== DIÁLOGO 1: Vulnerabilidad sobre control =====
        print("\n📝 Creando fragmento L5_02 (Vulnerabilidad 1)...")

        l5_02 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l5_02_vulnerability_1",
            title="Primera vulnerabilidad: Control",
            speaker="diana",
            content=(
                "Te voy a contar algo.\n\n"
                "A veces siento que todo esto es una jaula que yo misma construí.\n"
                "Kinky nació como una forma de control. De decidir cómo me ven.\n\n"
                "Pero cuando controlas tanto la narrativa... "
                "¿cuándo dejas de actuar y empiezas a ser tú misma?\n\n"
                "Hay días en que ni yo sé dónde termina Kinky y empieza Diana."
            ),
            order=3,
            is_entry_point=False,
            is_ending=False,
        )

        l5_02.delay_seconds = 2
        l5_02.is_decision_point = True

        await session.flush()
        print(f"  ✓ L5_02 creado (ID: {l5_02.id})")

        # Respuestas del usuario (evaluación de empatía)
        await container.decision.create_decision(
            fragment_id=l5_02.id,
            button_text="Puedo ayudarte a encontrarte",
            target_fragment_key="l5_03_response_fixing",
            order=0,
            sets_flag="fixing_response_1",  # ARREGLADOR (malo)
            button_emoji="🛠️"
        )

        await container.decision.create_decision(
            fragment_id=l5_02.id,
            button_text="Entiendo esa contradicción",
            target_fragment_key="l5_03_response_empathetic",
            order=1,
            sets_flag="empathetic_response_1",  # EMPÁTICO (bueno)
            button_emoji="💙"
        )

        await container.decision.create_decision(
            fragment_id=l5_02.id,
            button_text="No necesitas esas máscaras conmigo",
            target_fragment_key="l5_03_response_possessive",
            order=2,
            sets_flag="possessive_response_1",  # POSESIVO (malo)
            button_emoji="🔒"
        )

        # ===== Respuestas de Diana según tipo =====

        # Respuesta FIXING (Arreglador)
        print("\n📝 Creando fragmento L5_03_FIXING...")

        l5_03_fix = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l5_03_response_fixing",
            title="Diana se cierra (Fixing)",
            speaker="diana",
            content=(
                "No.\n\n"
                "No necesito que me 'ayudes a encontrarme'. "
                "No estoy perdida. Estoy... complicada. Hay una diferencia.\n\n"
                "No quiero soluciones. Quiero que entiendas."
            ),
            order=4,
            is_entry_point=False,
            is_ending=False,
        )

        l5_03_fix.delay_seconds = 1
        l5_03_fix.next_fragment_key = "l5_04_vulnerability_2"

        await session.flush()
        print(f"  ✓ L5_03_FIXING creado (ID: {l5_03_fix.id})")

        await container.decision.create_decision(
            fragment_id=l5_03_fix.id,
            button_text="Continuar",
            target_fragment_key="l5_04_vulnerability_2",
            order=0,
            button_emoji="▶️"
        )

        # Respuesta EMPATHETIC (Empático)
        print("\n📝 Creando fragmento L5_03_EMPATHETIC...")

        l5_03_emp = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l5_03_response_empathetic",
            title="Diana se abre (Empathetic)",
            speaker="diana",
            content=(
                "Sí... exacto.\n\n"
                "No es algo que se resuelve. Es algo que se vive.\n"
                "La mayoría quiere 'arreglarme'. O poseerme.\n\n"
                "Pero tú... entiendes que puedo ser dos cosas a la vez. "
                "Que las contradicciones no son problemas.\n\n"
                "Gracias por eso."
            ),
            order=5,
            is_entry_point=False,
            is_ending=False,
        )

        l5_03_emp.delay_seconds = 2
        l5_03_emp.next_fragment_key = "l5_04_vulnerability_2"

        await session.flush()
        print(f"  ✓ L5_03_EMPATHETIC creado (ID: {l5_03_emp.id})")

        await container.decision.create_decision(
            fragment_id=l5_03_emp.id,
            button_text="Continuar",
            target_fragment_key="l5_04_vulnerability_2",
            order=0,
            button_emoji="▶️"
        )

        # Respuesta POSSESSIVE (Posesivo)
        print("\n📝 Creando fragmento L5_03_POSSESSIVE...")

        l5_03_poss = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l5_03_response_possessive",
            title="Diana se distancia (Possessive)",
            speaker="diana",
            content=(
                "¿'Conmigo'?\n\n"
                "Esa palabra implica posesión. Como si tuvieras derecho "
                "a verme sin filtros porque... ¿qué? ¿Pagaste? ¿Llegaste aquí?\n\n"
                "Las máscaras no son para ti. Son para mí.\n"
                "Para protegerme de quienes creen que merecen acceso total."
            ),
            order=6,
            is_entry_point=False,
            is_ending=False,
        )

        l5_03_poss.delay_seconds = 1
        l5_03_poss.next_fragment_key = "l5_04_vulnerability_2"

        await session.flush()
        print(f"  ✓ L5_03_POSSESSIVE creado (ID: {l5_03_poss.id})")

        await container.decision.create_decision(
            fragment_id=l5_03_poss.id,
            button_text="Continuar",
            target_fragment_key="l5_04_vulnerability_2",
            order=0,
            button_emoji="▶️"
        )

        # ===== DIÁLOGO 2: Vulnerabilidad sobre soledad =====
        print("\n📝 Creando fragmento L5_04 (Vulnerabilidad 2)...")

        l5_04 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l5_04_vulnerability_2",
            title="Segunda vulnerabilidad: Soledad",
            speaker="diana",
            content=(
                "Otra cosa.\n\n"
                "Tengo miles de seguidores. Cientos en el Diván. "
                "Pero a veces me siento... sola.\n\n"
                "Porque nadie me conoce realmente. Solo conocen fragmentos. "
                "Lo que elijo mostrar.\n\n"
                "Y cuando alguien intenta conocerme de verdad... "
                "me asusto. Porque ¿y si no les gusta lo que encuentran?"
            ),
            order=7,
            is_entry_point=False,
            is_ending=False,
        )

        l5_04.delay_seconds = 2
        l5_04.is_decision_point = True

        await session.flush()
        print(f"  ✓ L5_04 creado (ID: {l5_04.id})")

        await container.decision.create_decision(
            fragment_id=l5_04.id,
            button_text="Yo te acepto como eres",
            target_fragment_key="l5_05_response_possessive_2",
            order=0,
            sets_flag="possessive_response_2",
            button_emoji="🔒"
        )

        await container.decision.create_decision(
            fragment_id=l5_04.id,
            button_text="El miedo a ser vista es humano",
            target_fragment_key="l5_05_response_empathetic_2",
            order=1,
            sets_flag="empathetic_response_2",
            button_emoji="💙"
        )

        await container.decision.create_decision(
            fragment_id=l5_04.id,
            button_text="Deberías ser más vulnerable",
            target_fragment_key="l5_05_response_fixing_2",
            order=2,
            sets_flag="fixing_response_2",
            button_emoji="🛠️"
        )

        # Respuestas breves de Diana (segundo round)

        # POSSESSIVE 2
        l5_05_poss = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l5_05_response_possessive_2",
            title="Diana rechaza",
            speaker="diana",
            content=(
                "No me conoces lo suficiente para decir eso.\n\n"
                "La aceptación sin conocimiento es condescendencia."
            ),
            order=8,
            is_entry_point=False,
            is_ending=False,
        )
        l5_05_poss.delay_seconds = 1
        l5_05_poss.next_fragment_key = "l5_06_final_dialogue"
        await session.flush()

        await container.decision.create_decision(
            fragment_id=l5_05_poss.id,
            button_text="Continuar",
            target_fragment_key="l5_06_final_dialogue",
            order=0,
            button_emoji="▶️"
        )

        # EMPATHETIC 2
        l5_05_emp = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l5_05_response_empathetic_2",
            title="Diana se acerca más",
            speaker="diana",
            content=(
                "Sí.\n\n"
                "Es exactamente eso. El miedo a ser vista y no ser suficiente.\n\n"
                "Gracias por... entenderlo."
            ),
            order=9,
            is_entry_point=False,
            is_ending=False,
        )
        l5_05_emp.delay_seconds = 2
        l5_05_emp.next_fragment_key = "l5_06_final_dialogue"
        await session.flush()

        await container.decision.create_decision(
            fragment_id=l5_05_emp.id,
            button_text="Continuar",
            target_fragment_key="l5_06_final_dialogue",
            order=0,
            button_emoji="▶️"
        )

        # FIXING 2
        l5_05_fix = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l5_05_response_fixing_2",
            title="Diana se frustra",
            speaker="diana",
            content=(
                "¿'Debería'?\n\n"
                "No me digas qué debería hacer. Ya hay suficientes voces "
                "diciéndome cómo vivir mi vida."
            ),
            order=10,
            is_entry_point=False,
            is_ending=False,
        )
        l5_05_fix.delay_seconds = 1
        l5_05_fix.next_fragment_key = "l5_06_final_dialogue"
        await session.flush()

        await container.decision.create_decision(
            fragment_id=l5_05_fix.id,
            button_text="Continuar",
            target_fragment_key="l5_06_final_dialogue",
            order=0,
            button_emoji="▶️"
        )

        # ===== DIÁLOGO FINAL: Evaluación de empatía =====
        print("\n📝 Creando fragmento L5_06 (Diálogo final)...")

        l5_06 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l5_06_final_dialogue",
            title="Reflexión final",
            speaker="diana",
            content=(
                "Gracias por escucharme.\n\n"
                "No muchos llegan hasta aquí. Y de los que llegan, "
                "pocos entienden la diferencia entre escuchar y juzgar.\n\n"
                "Entre acompañar y arreglar.\n\n"
                "Lucien tiene algo para ti."
            ),
            order=11,
            is_entry_point=False,
            is_ending=False,
        )

        l5_06.delay_seconds = 2
        l5_06.next_fragment_key = "l5_07_lucien_evaluation"

        await session.flush()
        print(f"  ✓ L5_06 creado (ID: {l5_06.id})")

        await container.decision.create_decision(
            fragment_id=l5_06.id,
            button_text="Continuar",
            target_fragment_key="l5_07_lucien_evaluation",
            order=0,
            button_emoji="▶️"
        )

        # ===== FRAGMENTO L5_07: Lucien evalúa =====
        print("\n📝 Creando fragmento L5_07 (Evaluación de Lucien)...")

        l5_07 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l5_07_lucien_evaluation",
            title="Evaluación de empatía",
            speaker="lucien",
            content=(
                "He observado sus respuestas.\n\n"
                "La empatía genuina es rara. La mayoría cae en:\n"
                "• Querer 'arreglar' a Diana\n"
                "• Sentir que la 'merecen'\n\n"
                "Usted... "
            ),
            order=12,
            is_entry_point=False,
            is_ending=False,
        )

        l5_07.delay_seconds = 2
        # Nota: El handler debe evaluar flags y dirigir a L5_08A o L5_08B

        await session.flush()
        print(f"  ✓ L5_07 creado (ID: {l5_07.id})")

        await container.decision.create_decision(
            fragment_id=l5_07.id,
            button_text="Ver evaluación",
            target_fragment_key="l5_08a_empathetic",  # Default empático
            order=0,
            button_emoji="📊"
        )

        # ===== Variante A: Usuario empático (2+ empathetic flags) =====
        print("\n📝 Creando fragmento L5_08A (Empático)...")

        l5_08a = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l5_08a_empathetic",
            title="Respuesta empática reconocida",
            speaker="lucien",
            content=(
                "...escuchó sin juzgar.\n\n"
                "No intentó arreglarla. No la reclamó como suya.\n"
                "Simplemente... entendió.\n\n"
                "Eso es extraordinariamente raro. Diana lo nota.\n\n"
                "Tiene acceso completo a su Archivo Personal. "
                "Es un privilegio que muy pocos obtienen."
            ),
            order=13,
            is_entry_point=False,
            is_ending=False,
        )

        l5_08a.delay_seconds = 2
        l5_08a.next_fragment_key = "l5_09_rewards"
        l5_08a.condition_type = "flag_count"
        l5_08a.condition_value = "empathetic>=2"

        await session.flush()
        print(f"  ✓ L5_08A creado (ID: {l5_08a.id})")

        await container.decision.create_decision(
            fragment_id=l5_08a.id,
            button_text="Continuar",
            target_fragment_key="l5_09_rewards",
            order=0,
            sets_flag="deep_empathy_achieved",
            button_emoji="▶️"
        )

        # ===== Variante B: Usuario posesivo/arreglador =====
        print("\n📝 Creando fragmento L5_08B (Problematic)...")

        l5_08b = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l5_08b_problematic",
            title="Respuesta problemática",
            speaker="lucien",
            content=(
                "...cayó en los patrones comunes.\n\n"
                "Intentó 'arreglar' o 'poseer'. Diana se sintió... juzgada.\n\n"
                "No es descalificador. Pero limita el acceso.\n"
                "Algunos contenidos requieren comprensión más profunda.\n\n"
                "Tiene acceso parcial al Archivo Personal. "
                "Para más, necesitará demostrar empatía genuina en futuras interacciones."
            ),
            order=14,
            is_entry_point=False,
            is_ending=False,
        )

        l5_08b.delay_seconds = 2
        l5_08b.next_fragment_key = "l5_09_rewards"

        await session.flush()
        print(f"  ✓ L5_08B creado (ID: {l5_08b.id})")

        await container.decision.create_decision(
            fragment_id=l5_08b.id,
            button_text="Continuar",
            target_fragment_key="l5_09_rewards",
            order=0,
            button_emoji="▶️"
        )

        # ===== FRAGMENTO L5_09: Recompensas =====
        print("\n📝 Creando fragmento L5_09 (Recompensas)...")

        l5_09 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l5_09_rewards",
            title="Entrega de recompensas",
            speaker="lucien",
            content=(
                "Nivel 5 completado.\n\n"
                "Recompensas:\n"
                "• +20 Favores de Diana\n"
                "• Acceso a: <i>Archivo Personal de Diana</i>\n"
                "• Badge: <i>Deep Connection</i>\n\n"
                "El nivel 6 - Culminación - es el último paso. "
                "Diana revelará su secreto final."
            ),
            order=15,
            is_entry_point=False,
            is_ending=True,
        )

        l5_09.delay_seconds = 2

        await session.flush()
        print(f"  ✓ L5_09 creado (ID: {l5_09.id})")

        # Fragmento final no necesita decisión (is_ending=True lo cierra automáticamente)

        # ===== COMMIT FINAL =====
        await session.commit()

        print("\n" + "="*60)
        print("✅ Nivel 5 - Profundización cargado exitosamente!")
        print("="*60)
        print(f"   Capítulo: {chapter.slug}")
        print(f"   Fragmentos creados: 15")
        print(f"   Decisiones creadas: ~18")
        print(f"   Flags: empathetic_response_*, possessive_response_*, fixing_response_*")
        print(f"   Rewards: +20 favores, personal_archive")
        print("="*60)


if __name__ == "__main__":
    asyncio.run(seed_level_5())
