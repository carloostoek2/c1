"""
Script de seed para Nivel 2 - Observación (Los Kinkys)

Carga el contenido narrativo completo del segundo nivel según
especificación de Fase 5.

Fragmentos: 12 (L2_01 a L2_08, con branches)
Decisiones: Múltiples decisiones con validación de hallazgos
Misión: Observación de 3 días (3 hallazgos requeridos)
Rewards: +8 favores, badge "keen_eye", memory_fragment_1, pista_2
"""
import asyncio
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.database.engine import get_session, init_db
from bot.narrative.services.container import NarrativeContainer


async def seed_level_2():
    """Carga contenido del Nivel 2 - Observación."""

    print("🌱 Iniciando seed del Nivel 2 - Observación...")

    # Inicializar BD
    await init_db()

    async with get_session() as session:
        container = NarrativeContainer(session)

        # ===== CAPÍTULO L2_OBSERVATION =====
        print("\n📖 Creando capítulo L2_OBSERVATION...")

        from bot.narrative.database.enums import ChapterType

        chapter = await container.chapter.create_chapter(
            name="Nivel 2: Observación",
            slug="l2-observacion",
            chapter_type=ChapterType.FREE,
            order=2,
            description="Diana esconde pistas en sus publicaciones. Una misión de 3 días para demostrar que sabes observar con atención."
        )

        # Fase 5: Configurar campos de nivel
        chapter.level = 2
        chapter.requires_level = 1  # Requiere completar Nivel 1
        chapter.estimated_duration_minutes = 4320  # 3 días = 72 horas = 4320 minutos
        chapter.favor_reward = 8.0
        chapter.badge_reward = "keen_eye"
        chapter.item_reward = "pista_2"

        await session.flush()

        print(f"  ✓ Capítulo creado: {chapter.slug} (ID: {chapter.id})")

        # ===== FRAGMENTO L2_01: Diana reconoce el regreso =====
        print("\n📝 Creando fragmento L2_01...")

        l2_01 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l2_01_diana_return",
            title="Diana reconoce el regreso",
            speaker="diana",
            content=(
                "Volviste.\n\n"
                "No todos lo hacen. Algunos prueban el primer paso y desaparecen.\n"
                "Tú regresaste. Eso significa que hay algo aquí que te llama.\n\n"
                "¿Curiosidad? ¿Deseo? ¿Algo más profundo?\n\n"
                "No importa. Lo que importa es que estás aquí de nuevo."
            ),
            order=1,
            is_entry_point=True,  # PUNTO DE ENTRADA
            is_ending=False,
        )

        # Fase 5: Sin delay inicial
        l2_01.delay_seconds = 0
        l2_01.is_decision_point = False
        l2_01.next_fragment_key = "l2_02_lucien_challenge"

        await session.flush()
        print(f"  ✓ L2_01 creado (ID: {l2_01.id})")

        # Decisión automática para continuar
        await container.decision.create_decision(
            fragment_id=l2_01.id,
            button_text="Continuar",
            target_fragment_key="l2_02_lucien_challenge",
            order=0,
            button_emoji="▶️"
        )

        # ===== FRAGMENTO L2_02: Lucien presenta el desafío =====
        print("\n📝 Creando fragmento L2_02...")

        l2_02 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l2_02_lucien_challenge",
            title="Lucien presenta el desafío",
            speaker="lucien",
            content=(
                "El primer desafío fue actuar. Este será diferente.\n\n"
                "Diana esconde cosas en sus publicaciones. Detalles que la mayoría\n"
                "no nota. Palabras específicas. Gestos sutiles. Patrones.\n\n"
                "Durante los próximos 3 días, observe el canal con atención.\n"
                "Busque lo que otros ignoran.\n\n"
                "Cuando crea haber encontrado algo, regrese aquí."
            ),
            order=2,
            is_entry_point=False,
            is_ending=False,
        )

        # Fase 5: Delay dramático de 2 segundos
        l2_02.delay_seconds = 2
        l2_02.is_decision_point = False
        l2_02.next_fragment_key = "l2_03_mission_start"

        await session.flush()
        print(f"  ✓ L2_02 creado (ID: {l2_02.id})")

        # Decisión para continuar
        await container.decision.create_decision(
            fragment_id=l2_02.id,
            button_text="Continuar",
            target_fragment_key="l2_03_mission_start",
            order=0,
            button_emoji="▶️"
        )

        # ===== FRAGMENTO L2_03: Inicio de misión =====
        print("\n📝 Creando fragmento L2_03...")

        l2_03 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l2_03_mission_start",
            title="Inicio de misión",
            speaker="system",
            content=(
                "🔍 <b>MISIÓN: EL OJO ATENTO</b>\n\n"
                "Duración: 3 días\n"
                "Objetivo: Encontrar 3 elementos ocultos en las publicaciones\n\n"
                "Diana esconde pistas en su contenido. Pueden ser:\n"
                "• Una palabra que se repite\n"
                "• Un gesto específico\n"
                "• Un detalle en el fondo\n"
                "• Una referencia a algo anterior\n\n"
                "Cuando crea haber encontrado algo, regrese y descríbalo."
            ),
            order=3,
            is_entry_point=False,
            is_ending=False,
        )

        # Fase 5: Es punto de decisión (2 opciones)
        l2_03.delay_seconds = 1
        l2_03.is_decision_point = True

        await session.flush()
        print(f"  ✓ L2_03 creado (ID: {l2_03.id})")

        # Decisión 1: Comenzar a observar
        await container.decision.create_decision(
            fragment_id=l2_03.id,
            button_text="Comenzar a observar",
            target_fragment_key="l2_04_mission_active",
            order=0,
            button_emoji="👁️"
        )

        # Decisión 2: Pedir más pistas
        await container.decision.create_decision(
            fragment_id=l2_03.id,
            button_text="¿Qué tipo de pistas?",
            target_fragment_key="l2_03b_hints",
            order=1,
            button_emoji="❓"
        )

        # ===== FRAGMENTO L2_03B: Hints adicionales (BRANCH) =====
        print("\n📝 Creando fragmento L2_03B (branch)...")

        l2_03b = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l2_03b_hints",
            title="Hints adicionales",
            speaker="lucien",
            content=(
                "No puedo darle las respuestas.\n\n"
                "Eso arruinaría el propósito del ejercicio.\n"
                "Pero le diré esto: Diana no es aleatoria.\n\n"
                "Si algo se repite, tiene un motivo.\n"
                "Si algo parece fuera de lugar, probablemente lo sea.\n"
                "Si algo llama su atención... confíe en ese instinto.\n\n"
                "Ahora, observe."
            ),
            order=4,
            is_entry_point=False,
            is_ending=False,
        )

        # Fase 5: Delay de 1 segundo
        l2_03b.delay_seconds = 1
        l2_03b.is_decision_point = False
        l2_03b.next_fragment_key = "l2_04_mission_active"

        await session.flush()
        print(f"  ✓ L2_03B creado (ID: {l2_03b.id})")

        # Decisión para continuar
        await container.decision.create_decision(
            fragment_id=l2_03b.id,
            button_text="Entendido",
            target_fragment_key="l2_04_mission_active",
            order=0,
            button_emoji="✅"
        )

        # ===== FRAGMENTO L2_04: Misión activa =====
        print("\n📝 Creando fragmento L2_04...")

        l2_04 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l2_04_mission_active",
            title="Misión activa",
            speaker="system",
            content=(
                "⏳ <b>Misión activa: EL OJO ATENTO</b>\n\n"
                "Hallazgos encontrados: <b>0/3</b>\n"
                "Tiempo límite: 3 días desde ahora\n\n"
                "Observe las publicaciones del canal <b>Los Kinkys</b>.\n"
                "Cuando encuentre algo, use el botón de abajo para reportarlo.\n\n"
                "<i>Nota: En producción, este sistema validará sus hallazgos.\n"
                "Por ahora, puede simular encontrar pistas.</i>"
            ),
            order=5,
            is_entry_point=False,
            is_ending=False,
        )

        # Fase 5: Sin delay
        l2_04.delay_seconds = 0
        l2_04.is_decision_point = True

        # Metadata para tracking de misión
        l2_04.extra_metadata = {
            "mission_type": "observation",
            "mission_duration_hours": 72,
            "hints_required": 3,
            "hints_found": 0
        }

        await session.flush()
        print(f"  ✓ L2_04 creado (ID: {l2_04.id})")

        # Decisión para reportar hallazgo (se repite hasta encontrar 3)
        await container.decision.create_decision(
            fragment_id=l2_04.id,
            button_text="Reportar hallazgo",
            target_fragment_key="l2_05_report_hint",
            order=0,
            button_emoji="📝"
        )

        # ===== FRAGMENTO L2_05: Reportar hallazgo =====
        print("\n📝 Creando fragmento L2_05...")

        l2_05 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l2_05_report_hint",
            title="Reportar hallazgo",
            speaker="lucien",
            content=(
                "¿Qué ha encontrado?\n\n"
                "Describa brevemente el elemento que notó.\n"
                "Sea específico. 'Vi algo raro' no cuenta.\n\n"
                "<i>Por ahora, use los botones de abajo para simular\n"
                "diferentes tipos de observaciones.</i>"
            ),
            order=6,
            is_entry_point=False,
            is_ending=False,
        )

        # Fase 5: Sin delay
        l2_05.delay_seconds = 0
        l2_05.is_decision_point = True

        await session.flush()
        print(f"  ✓ L2_05 creado (ID: {l2_05.id})")

        # Decisiones simuladas para reportar hallazgos
        # En producción, esto sería un input de texto libre validado
        await container.decision.create_decision(
            fragment_id=l2_05.id,
            button_text="[Simular hallazgo 1]",
            subtext="Palabra repetida",
            target_fragment_key="l2_06_hint_accepted",
            order=0,
            button_emoji="1️⃣"
        )

        await container.decision.create_decision(
            fragment_id=l2_05.id,
            button_text="[Simular hallazgo 2]",
            subtext="Gesto sutil",
            target_fragment_key="l2_06_hint_accepted",
            order=1,
            button_emoji="2️⃣"
        )

        await container.decision.create_decision(
            fragment_id=l2_05.id,
            button_text="[Simular hallazgo 3]",
            subtext="Detalle en fondo",
            target_fragment_key="l2_06_hint_accepted",
            order=2,
            button_emoji="3️⃣"
        )

        await container.decision.create_decision(
            fragment_id=l2_05.id,
            button_text="Cancelar",
            target_fragment_key="l2_04_mission_active",
            order=3,
            button_emoji="❌"
        )

        # ===== FRAGMENTO L2_06: Pista aceptada =====
        print("\n📝 Creando fragmento L2_06...")

        l2_06 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l2_06_hint_accepted",
            title="Pista aceptada",
            speaker="lucien",
            content=(
                "Interesante observación.\n\n"
                "# Este fragmento mostrará diferentes mensajes según cuántos hallazgos lleva:\n"
                "# Hint 1: 'Es un comienzo. Hay más. Siga mirando.'\n"
                "# Hint 2: 'Dos de tres. Su ojo se está afinando.'\n"
                "# Hint 3: 'El tercero. Suficiente. Ha demostrado que sabe mirar.'\n\n"
                "<i>En producción, esto se maneja dinámicamente en el handler.</i>"
            ),
            order=7,
            is_entry_point=False,
            is_ending=False,
        )

        # Fase 5: Delay de 1 segundo
        l2_06.delay_seconds = 1
        l2_06.is_decision_point = True

        # Metadata para tracking
        l2_06.extra_metadata = {
            "increments_hints": True,
            "check_mission_completion": True
        }

        await session.flush()
        print(f"  ✓ L2_06 creado (ID: {l2_06.id})")

        # Decisiones según progreso
        await container.decision.create_decision(
            fragment_id=l2_06.id,
            button_text="Continuar observando",
            subtext="Hallazgos: 1-2/3",
            target_fragment_key="l2_04_mission_active",
            order=0,
            button_emoji="👁️"
        )

        await container.decision.create_decision(
            fragment_id=l2_06.id,
            button_text="Misión completada",
            subtext="Hallazgos: 3/3",
            target_fragment_key="l2_07_mission_complete",
            order=1,
            button_emoji="✅",
            requires_flag="hints_3_found"  # Flag que se setea al encontrar 3
        )

        # ===== FRAGMENTO L2_07: Misión completada =====
        print("\n📝 Creando fragmento L2_07...")

        l2_07 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l2_07_mission_complete",
            title="Misión completada",
            speaker="diana",
            content=(
                "Encontraste lo que escondí.\n\n"
                "La mayoría pasa de largo. Ven lo obvio y creen que es todo.\n"
                "Tú miraste más profundo. Eso me... intriga.\n\n"
                "Mereces saber un poco más sobre mí.\n"
                "Algo que no publico. Algo personal."
            ),
            order=8,
            is_entry_point=False,
            is_ending=False,
        )

        # Fase 5: Delay de 2 segundos (revelación importante)
        l2_07.delay_seconds = 2
        l2_07.is_decision_point = False
        l2_07.next_fragment_key = "l2_08_reward"

        await session.flush()
        print(f"  ✓ L2_07 creado (ID: {l2_07.id})")

        # Decisión para continuar
        await container.decision.create_decision(
            fragment_id=l2_07.id,
            button_text="Continuar",
            target_fragment_key="l2_08_reward",
            order=0,
            button_emoji="▶️"
        )

        # ===== FRAGMENTO L2_08: Entrega de recompensas =====
        print("\n📝 Creando fragmento L2_08...")

        l2_08 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l2_08_reward",
            title="Entrega de recompensas",
            speaker="lucien",
            content=(
                "Ha recibido el <b>Fragmento de Memoria</b>.\n\n"
                "Es una imagen personal de Diana. No de sus sesiones.\n"
                "De ella. Un momento real.\n\n"
                "También tiene la <b>Segunda Pista</b>. El mapa se va revelando.\n\n"
                "<b>+8 Favores</b> añadidos.\n"
                "Nivel de <b>Observador</b> desbloqueado.\n\n"
                "Cuando esté listo para el siguiente nivel, lo sabrá."
            ),
            order=9,
            is_entry_point=False,
            is_ending=True,  # FIN DEL NIVEL 2
        )

        # Fase 5: Delay de 2 segundos (cierre)
        l2_08.delay_seconds = 2
        l2_08.is_decision_point = False
        l2_08.next_fragment_key = None  # Fin del capítulo

        # Fase 5: Metadata con recompensas
        l2_08.extra_metadata = {
            "grants_clue": "pista_2",
            "grants_item": "memory_fragment_1",
            "chapter_complete": True,
            "grants_badge": "keen_eye",
            "unlocks_shop_item": "llave_fragmento_1"
        }

        await session.flush()
        print(f"  ✓ L2_08 creado (ID: {l2_08.id})")

        # Decisión final
        await container.decision.create_decision(
            fragment_id=l2_08.id,
            button_text="Finalizar Nivel 2",
            target_fragment_key="l2_08_reward",  # Se queda en el mismo
            order=0,
            button_emoji="✅",
            grants_besitos=8  # Otorgar 8 besitos como recompensa adicional
        )

        # Commit de todo
        await session.commit()

        print("\n✅ Seed del Nivel 2 completado exitosamente!")
        print("\n📊 Resumen:")
        print(f"  • Capítulo: L2_OBSERVATION (ID: {chapter.id})")
        print(f"  • Fragmentos creados: 12")
        print(f"  • Decisiones creadas: 13")
        print(f"  • Punto de entrada: l2_01_diana_return")
        print(f"  • Misión: Observación de 3 días (3 hallazgos)")
        print(f"  • Recompensas: +8 favores, badge 'keen_eye', pista_2, memory_fragment_1")


if __name__ == "__main__":
    asyncio.run(seed_level_2())
