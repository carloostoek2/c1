"""
Script de seed para Nivel 3 - Perfil de Deseo (Los Kinkys)

Carga el contenido narrativo completo del tercer nivel según
especificación de Fase 5.

Fragmentos: 20 (L3_01 a L3_11, con 6 variantes por arquetipo)
Decisiones: Cuestionario de 5 preguntas + variantes por arquetipo
Flags: Sistema completo de flags narrativos
Rewards: +10 favores, badge "desire_profiled", pista_3, invitation_to_divan
"""
import asyncio
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.database.engine import get_session, init_db
from bot.narrative.services.container import NarrativeContainer


async def seed_level_3():
    """Carga contenido del Nivel 3 - Perfil de Deseo."""

    print("🌱 Iniciando seed del Nivel 3 - Perfil de Deseo...")

    # Inicializar BD
    await init_db()

    async with get_session() as session:
        container = NarrativeContainer(session)

        # ===== CAPÍTULO L3_DESIRE_PROFILE =====
        print("\n📖 Creando capítulo L3_DESIRE_PROFILE...")

        from bot.narrative.database.enums import ChapterType

        chapter = await container.chapter.create_chapter(
            name="Nivel 3: Perfil de Deseo",
            slug="l3-perfil-de-deseo",
            chapter_type=ChapterType.FREE,
            order=3,
            description="Diana quiere saber quién eres realmente. Un cuestionario profundo que revela motivaciones y define tu arquetipo."
        )

        # Fase 5: Configurar campos de nivel
        chapter.level = 3
        chapter.requires_level = 2  # Requiere completar Nivel 2
        chapter.estimated_duration_minutes = 30
        chapter.favor_reward = 10.0
        chapter.badge_reward = "desire_profiled"
        chapter.item_reward = "pista_3"

        await session.flush()

        print(f"  ✓ Capítulo creado: {chapter.slug} (ID: {chapter.id})")

        # ===== FRAGMENTO L3_01: Diana solicita el perfil =====
        print("\n📝 Creando fragmento L3_01...")

        l3_01 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l3_01_diana_request",
            title="Diana solicita el perfil",
            speaker="diana",
            content=(
                "Has llegado más lejos que la mayoría.\n\n"
                "Actuaste cuando otros solo miraban.\n"
                "Observaste lo que otros ignoraban.\n\n"
                "Ahora quiero saber algo más difícil: quiero saber por qué.\n\n"
                "¿Por qué estás aquí? ¿Qué buscas realmente?\n"
                "No la respuesta fácil. La verdadera."
            ),
            order=1,
            is_entry_point=True,
            is_ending=False,
        )

        l3_01.delay_seconds = 0
        l3_01.is_decision_point = False
        l3_01.next_fragment_key = "l3_02_lucien_explains"

        await session.flush()
        print(f"  ✓ L3_01 creado (ID: {l3_01.id})")

        await container.decision.create_decision(
            fragment_id=l3_01.id,
            button_text="Continuar",
            target_fragment_key="l3_02_lucien_explains",
            order=0,
            button_emoji="▶️"
        )

        # ===== FRAGMENTO L3_02: Lucien explica el proceso =====
        print("\n📝 Creando fragmento L3_02...")

        l3_02 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l3_02_lucien_explains",
            title="Lucien explica el proceso",
            speaker="lucien",
            content=(
                "Lo que viene es el Perfil de Deseo.\n\n"
                "Son preguntas. Algunas simples. Otras... menos.\n"
                "No hay respuestas correctas o incorrectas. Pero hay respuestas\n"
                "honestas y respuestas performativas.\n\n"
                "Diana sabrá la diferencia. Yo también.\n\n"
                "Tómese el tiempo que necesite. Pero sea sincero.\n"
                "La mentira aquí no sirve de nada."
            ),
            order=2,
            is_entry_point=False,
            is_ending=False,
        )

        l3_02.delay_seconds = 2
        l3_02.is_decision_point = False
        l3_02.next_fragment_key = "l3_03_question_1"

        await session.flush()
        print(f"  ✓ L3_02 creado (ID: {l3_02.id})")

        await container.decision.create_decision(
            fragment_id=l3_02.id,
            button_text="Estoy listo",
            target_fragment_key="l3_03_question_1",
            order=0,
            button_emoji="✅"
        )

        # ===== FRAGMENTO L3_03: Pregunta 1 =====
        print("\n📝 Creando fragmento L3_03 (Pregunta 1)...")

        l3_03 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l3_03_question_1",
            title="Pregunta 1: Qué te atrajo",
            speaker="diana",
            content=(
                "<b>Primera pregunta.</b>\n\n"
                "¿Qué te atrajo a este lugar inicialmente?\n"
                "Antes de conocerme. Antes de entender qué era esto.\n"
                "El primer impulso."
            ),
            order=3,
            is_entry_point=False,
            is_ending=False,
        )

        l3_03.delay_seconds = 2
        l3_03.is_decision_point = True

        await session.flush()
        print(f"  ✓ L3_03 creado (ID: {l3_03.id})")

        # Decisiones de Pregunta 1 (setean flags)
        await container.decision.create_decision(
            fragment_id=l3_03.id,
            button_text="Curiosidad pura",
            subtext="Quería saber qué había aquí",
            target_fragment_key="l3_04_question_2",
            order=0,
            button_emoji="🔍",
            sets_flag="curious"
        )

        await container.decision.create_decision(
            fragment_id=l3_03.id,
            button_text="Atracción",
            subtext="Algo en ti me llamó",
            target_fragment_key="l3_04_question_2",
            order=1,
            button_emoji="💫",
            sets_flag="attracted"
        )

        await container.decision.create_decision(
            fragment_id=l3_03.id,
            button_text="Buscaba conexión",
            subtext="Algo específico",
            target_fragment_key="l3_04_question_2",
            order=2,
            button_emoji="🔗",
            sets_flag="seeking"
        )

        await container.decision.create_decision(
            fragment_id=l3_03.id,
            button_text="No lo sé",
            subtext="Algo me trajo",
            target_fragment_key="l3_04_question_2",
            order=3,
            button_emoji="🤷",
            sets_flag="intuitive"
        )

        # ===== FRAGMENTO L3_04: Pregunta 2 =====
        print("\n📝 Creando fragmento L3_04 (Pregunta 2)...")

        l3_04 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l3_04_question_2",
            title="Pregunta 2: Qué te importa más",
            speaker="diana",
            content=(
                "<b>Segunda pregunta.</b>\n\n"
                "Cuando ves mi contenido, ¿qué te importa más?\n"
                "¿Lo visual? ¿Lo que digo? ¿Lo que no digo?\n"
                "¿O algo completamente diferente?"
            ),
            order=4,
            is_entry_point=False,
            is_ending=False,
        )

        l3_04.delay_seconds = 1
        l3_04.is_decision_point = True

        await session.flush()
        print(f"  ✓ L3_04 creado (ID: {l3_04.id})")

        # Decisiones de Pregunta 2
        await container.decision.create_decision(
            fragment_id=l3_04.id,
            button_text="Lo visual",
            subtext="La estética, cómo te presentas",
            target_fragment_key="l3_05_question_3",
            order=0,
            button_emoji="👁️",
            sets_flag="visual"
        )

        await container.decision.create_decision(
            fragment_id=l3_04.id,
            button_text="Tus palabras",
            subtext="Lo que expresas, cómo piensas",
            target_fragment_key="l3_05_question_3",
            order=1,
            button_emoji="💬",
            sets_flag="verbal"
        )

        await container.decision.create_decision(
            fragment_id=l3_04.id,
            button_text="El misterio",
            subtext="Lo que ocultas me atrae más",
            target_fragment_key="l3_05_question_3",
            order=2,
            button_emoji="🔮",
            sets_flag="mystery"
        )

        await container.decision.create_decision(
            fragment_id=l3_04.id,
            button_text="La persona detrás",
            subtext="Diana, no Kinky",
            target_fragment_key="l3_05_question_3",
            order=3,
            button_emoji="💖",
            sets_flag="personal"
        )

        # ===== FRAGMENTO L3_05: Pregunta 3 =====
        print("\n📝 Creando fragmento L3_05 (Pregunta 3)...")

        l3_05 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l3_05_question_3",
            title="Pregunta 3: Si no soy lo que parece",
            speaker="diana",
            content=(
                "<b>Tercera pregunta.</b>\n\n"
                "¿Qué harías si te dijera que no soy lo que parece?\n"
                "Que la Kinky que ves es una construcción.\n"
                "Que Diana es diferente. Más complicada. Menos perfecta."
            ),
            order=5,
            is_entry_point=False,
            is_ending=False,
        )

        l3_05.delay_seconds = 1
        l3_05.is_decision_point = True

        await session.flush()
        print(f"  ✓ L3_05 creado (ID: {l3_05.id})")

        # Decisiones de Pregunta 3
        await container.decision.create_decision(
            fragment_id=l3_05.id,
            button_text="Me intrigaría más",
            subtext="La imperfección es interesante",
            target_fragment_key="l3_06_question_4",
            order=0,
            button_emoji="✨",
            sets_flag="depth"
        )

        await container.decision.create_decision(
            fragment_id=l3_05.id,
            button_text="Tengo límites",
            subtext="Depende de qué tan diferente",
            target_fragment_key="l3_06_question_4",
            order=1,
            button_emoji="⚖️",
            sets_flag="cautious"
        )

        await container.decision.create_decision(
            fragment_id=l3_05.id,
            button_text="Ya lo sospechaba",
            subtext="Nadie es solo una cosa",
            target_fragment_key="l3_06_question_4",
            order=2,
            button_emoji="🎭",
            sets_flag="perceptive"
        )

        await container.decision.create_decision(
            fragment_id=l3_05.id,
            button_text="Me decepcionaría",
            subtext="Vine por lo que muestras",
            target_fragment_key="l3_06_question_4",
            order=3,
            button_emoji="😔",
            sets_flag="surface"
        )

        # ===== FRAGMENTO L3_06: Pregunta 4 =====
        print("\n📝 Creando fragmento L3_06 (Pregunta 4)...")

        l3_06 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l3_06_question_4",
            title="Pregunta 4: Qué esperas obtener",
            speaker="diana",
            content=(
                "<b>Cuarta pregunta.</b>\n\n"
                "¿Qué esperas obtener de estar aquí?\n"
                "Al final del camino. Cuando hayas visto todo lo que hay que ver.\n"
                "¿Qué habrá valido la pena?"
            ),
            order=6,
            is_entry_point=False,
            is_ending=False,
        )

        l3_06.delay_seconds = 1
        l3_06.is_decision_point = True

        await session.flush()
        print(f"  ✓ L3_06 creado (ID: {l3_06.id})")

        # Decisiones de Pregunta 4
        await container.decision.create_decision(
            fragment_id=l3_06.id,
            button_text="Entretenimiento",
            subtext="Momentos de placer",
            target_fragment_key="l3_07_question_5",
            order=0,
            button_emoji="🎪",
            sets_flag="pleasure"
        )

        await container.decision.create_decision(
            fragment_id=l3_06.id,
            button_text="Conexión",
            subtext="No ser solo un número",
            target_fragment_key="l3_07_question_5",
            order=1,
            button_emoji="🤝",
            sets_flag="connection"
        )

        await container.decision.create_decision(
            fragment_id=l3_06.id,
            button_text="Conocimiento",
            subtext="Entender algo nuevo",
            target_fragment_key="l3_07_question_5",
            order=2,
            button_emoji="📚",
            sets_flag="understanding"
        )

        await container.decision.create_decision(
            fragment_id=l3_06.id,
            button_text="No lo sé aún",
            subtext="Descubriendo sobre la marcha",
            target_fragment_key="l3_07_question_5",
            order=3,
            button_emoji="🧭",
            sets_flag="open"
        )

        # ===== FRAGMENTO L3_07: Pregunta 5 (texto libre) =====
        print("\n📝 Creando fragmento L3_07 (Pregunta 5 - texto libre)...")

        l3_07 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l3_07_question_5",
            title="Pregunta 5: Una cosa sobre ti",
            speaker="diana",
            content=(
                "<b>Última pregunta.</b> Y esta no tiene opciones.\n\n"
                "Si pudieras decirme una cosa. Solo una.\n"
                "Algo que quisieras que yo supiera sobre ti.\n"
                "¿Qué sería?\n\n"
                "<i>En producción, aquí esperaríamos input de texto libre.\n"
                "Por ahora, use el botón de abajo para continuar.</i>"
            ),
            order=7,
            is_entry_point=False,
            is_ending=False,
        )

        l3_07.delay_seconds = 1
        l3_07.is_decision_point = False
        l3_07.next_fragment_key = "l3_08_analysis"

        # Metadata para indicar que requiere input de texto
        l3_07.extra_metadata = {
            "requires_text_input": True,
            "min_characters": 20,
            "max_characters": 500,
            "save_response_as": "personal_statement"
        }

        await session.flush()
        print(f"  ✓ L3_07 creado (ID: {l3_07.id})")

        await container.decision.create_decision(
            fragment_id=l3_07.id,
            button_text="[Simular respuesta]",
            subtext="En producción: texto libre",
            target_fragment_key="l3_08_analysis",
            order=0,
            button_emoji="📝"
        )

        # ===== FRAGMENTO L3_08: Análisis (delay dramático) =====
        print("\n📝 Creando fragmento L3_08 (Análisis)...")

        l3_08 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l3_08_analysis",
            title="Análisis de respuestas",
            speaker="system",
            content=(
                "⏳ Diana está revisando tus respuestas...\n\n"
                "<i>Analizando flags narrativos...</i>\n"
                "<i>Determinando arquetipo dominante...</i>\n"
                "<i>Generando respuesta personalizada...</i>"
            ),
            order=8,
            is_entry_point=False,
            is_ending=False,
        )

        l3_08.delay_seconds = 3  # Delay dramático
        l3_08.is_decision_point = True  # Ramificación según arquetipo

        # Metadata para procesamiento
        l3_08.extra_metadata = {
            "analyze_flags": True,
            "determine_archetype": True,
            "generate_personalized_response": True
        }

        await session.flush()
        print(f"  ✓ L3_08 creado (ID: {l3_08.id})")

        # Decisiones hacia variantes por arquetipo
        # En producción, el handler determinaría automáticamente cuál mostrar
        await container.decision.create_decision(
            fragment_id=l3_08.id,
            button_text="[→ Explorador]",
            target_fragment_key="l3_09_explorer",
            order=0,
            button_emoji="🗺️",
            requires_flag="curious"
        )

        await container.decision.create_decision(
            fragment_id=l3_08.id,
            button_text="[→ Romántico]",
            target_fragment_key="l3_09_romantic",
            order=1,
            button_emoji="💕",
            requires_flag="connection"
        )

        await container.decision.create_decision(
            fragment_id=l3_08.id,
            button_text="[→ Analítico]",
            target_fragment_key="l3_09_analytical",
            order=2,
            button_emoji="🧠",
            requires_flag="understanding"
        )

        await container.decision.create_decision(
            fragment_id=l3_08.id,
            button_text="[→ Directo]",
            target_fragment_key="l3_09_direct",
            order=3,
            button_emoji="🎯",
            requires_flag="pleasure"
        )

        await container.decision.create_decision(
            fragment_id=l3_08.id,
            button_text="[→ Paciente]",
            target_fragment_key="l3_09_patient",
            order=4,
            button_emoji="🌱",
            requires_flag="open"
        )

        await container.decision.create_decision(
            fragment_id=l3_08.id,
            button_text="[→ Persistente]",
            target_fragment_key="l3_09_persistent",
            order=5,
            button_emoji="💪",
            # Sin flag específico, es el default
        )

        # ===== VARIANTES POR ARQUETIPO (L3_09) =====
        print("\n📝 Creando variantes por arquetipo (L3_09)...")

        # L3_09_EXPLORER
        l3_09_explorer = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l3_09_explorer",
            title="Respuesta para Exploradores",
            speaker="diana",
            content=(
                "Tu curiosidad es casi... hambrienta.\n\n"
                "Quieres verlo todo. Saberlo todo. No por coleccionar,\n"
                "sino por ese impulso de no dejar nada sin descubrir.\n\n"
                "Me reconozco en eso. Es agotador. Y adictivo.\n\n"
                "El Diván tiene cosas que ni Lucien ha visto.\n"
                "Quizás tú las encuentres."
            ),
            order=9,
            is_entry_point=False,
            is_ending=False,
        )
        l3_09_explorer.delay_seconds = 2
        l3_09_explorer.next_fragment_key = "l3_10_invitation"
        await session.flush()

        # L3_09_ROMANTIC
        l3_09_romantic = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l3_09_romantic",
            title="Respuesta para Románticos",
            speaker="diana",
            content=(
                "Buscas algo real.\n\n"
                "No viniste por el contenido. Viniste por la persona.\n"
                "Quieres conexión, no transacción. Intimidad, no producto.\n\n"
                "Es hermoso. Y peligroso.\n"
                "Porque puedo darte momentos de eso. Pero no puedo prometerte todo.\n\n"
                "Aun así... el Diván es donde me permito ser más vulnerable."
            ),
            order=10,
            is_entry_point=False,
            is_ending=False,
        )
        l3_09_romantic.delay_seconds = 2
        l3_09_romantic.next_fragment_key = "l3_10_invitation"
        await session.flush()

        # L3_09_ANALYTICAL
        l3_09_analytical = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l3_09_analytical",
            title="Respuesta para Analíticos",
            speaker="diana",
            content=(
                "Analizas todo, ¿verdad?\n\n"
                "Cada palabra. Cada gesto. Buscando patrones. Lógica.\n"
                "Tratando de entender cómo funciona esto. Cómo funciono yo.\n\n"
                "No sé si me descifrarás. Ni yo me he descifrado.\n"
                "Pero el intento... tiene su propio valor.\n\n"
                "El Diván tiene capas que apreciarás."
            ),
            order=11,
            is_entry_point=False,
            is_ending=False,
        )
        l3_09_analytical.delay_seconds = 2
        l3_09_analytical.next_fragment_key = "l3_10_invitation"
        await session.flush()

        # L3_09_DIRECT
        l3_09_direct = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l3_09_direct",
            title="Respuesta para Directos",
            speaker="diana",
            content=(
                "Sabes lo que quieres.\n\n"
                "Sin rodeos. Sin justificaciones complicadas.\n"
                "Viniste por algo, y no te avergüenzas de ello.\n\n"
                "Eso es refrescante. La mayoría finge motivaciones más 'nobles'.\n\n"
                "El Diván tiene lo que buscas. Sin filtros innecesarios."
            ),
            order=12,
            is_entry_point=False,
            is_ending=False,
        )
        l3_09_direct.delay_seconds = 2
        l3_09_direct.next_fragment_key = "l3_10_invitation"
        await session.flush()

        # L3_09_PATIENT
        l3_09_patient = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l3_09_patient",
            title="Respuesta para Pacientes",
            speaker="diana",
            content=(
                "Te tomas tu tiempo.\n\n"
                "No apresuras. No presionas. Dejas que las cosas se revelen\n"
                "cuando están listas. Eso es... raro aquí.\n\n"
                "La mayoría quiere todo inmediatamente.\n"
                "Tú entiendes que lo valioso se construye despacio.\n\n"
                "El Diván recompensa esa paciencia."
            ),
            order=13,
            is_entry_point=False,
            is_ending=False,
        )
        l3_09_patient.delay_seconds = 2
        l3_09_patient.next_fragment_key = "l3_10_invitation"
        await session.flush()

        # L3_09_PERSISTENT
        l3_09_persistent = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l3_09_persistent",
            title="Respuesta para Persistentes",
            speaker="diana",
            content=(
                "Sigues aquí.\n\n"
                "Has pasado por todo esto sin rendirte. Sin abandonar.\n"
                "Cada vez que el camino se complicó, seguiste adelante.\n\n"
                "Esa persistencia... me conmueve más de lo que admitiré.\n\n"
                "El Diván tiene recompensas para quienes no se rinden."
            ),
            order=14,
            is_entry_point=False,
            is_ending=False,
        )
        l3_09_persistent.delay_seconds = 2
        l3_09_persistent.next_fragment_key = "l3_10_invitation"
        await session.flush()

        print(f"  ✓ 6 variantes creadas (Explorer, Romantic, Analytical, Direct, Patient, Persistent)")

        # Decisiones de todas las variantes hacia L3_10
        for variant_frag in [l3_09_explorer, l3_09_romantic, l3_09_analytical,
                             l3_09_direct, l3_09_patient, l3_09_persistent]:
            await container.decision.create_decision(
                fragment_id=variant_frag.id,
                button_text="Continuar",
                target_fragment_key="l3_10_invitation",
                order=0,
                button_emoji="▶️"
            )

        # ===== FRAGMENTO L3_10: La Invitación =====
        print("\n📝 Creando fragmento L3_10 (La Invitación)...")

        l3_10 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l3_10_invitation",
            title="La Invitación",
            speaker="diana",
            content=(
                "Has completado el Perfil de Deseo.\n\n"
                "Ahora te conozco un poco más. Y quizás tú te conoces mejor también.\n\n"
                "Hay una puerta. El Diván. Mi espacio más íntimo.\n"
                "No todos llegan hasta ella. Tú llegaste.\n\n"
                "La invitación está sobre la mesa.\n"
                "La decisión es tuya."
            ),
            order=15,
            is_entry_point=False,
            is_ending=False,
        )

        l3_10.delay_seconds = 3  # Delay dramático antes del pitch VIP
        l3_10.is_decision_point = False
        l3_10.next_fragment_key = "l3_11_lucien_vip"

        await session.flush()
        print(f"  ✓ L3_10 creado (ID: {l3_10.id})")

        await container.decision.create_decision(
            fragment_id=l3_10.id,
            button_text="Continuar",
            target_fragment_key="l3_11_lucien_vip",
            order=0,
            button_emoji="▶️"
        )

        # ===== FRAGMENTO L3_11: Lucien presenta la Llave del Diván =====
        print("\n📝 Creando fragmento L3_11 (Llave del Diván)...")

        l3_11 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l3_11_lucien_vip",
            title="Lucien presenta la Llave del Diván",
            speaker="lucien",
            content=(
                "Ha llegado al final del camino gratuito.\n\n"
                "Lo que viene después... requiere compromiso.\n"
                "La Llave del Diván no es solo un pago. Es una declaración.\n\n"
                "Dice: 'Estoy listo para ver más. Para conocer más. Para ser parte de esto.'\n\n"
                "No hay presión. Pero la puerta está ahí.\n"
                "Y Diana está del otro lado.\n\n"
                "<b>+10 Favores</b> han sido añadidos.\n"
                "Has recibido la <b>Tercera Pista</b> y la <b>Invitación al Diván</b>."
            ),
            order=16,
            is_entry_point=False,
            is_ending=True,  # FIN DEL NIVEL 3 (y del contenido FREE)
        )

        l3_11.delay_seconds = 2
        l3_11.is_decision_point = False
        l3_11.next_fragment_key = None  # Fin del capítulo

        # Metadata con recompensas y trigger de conversión
        l3_11.extra_metadata = {
            "grants_clue": "pista_3",
            "grants_item": "invitation_to_divan",
            "chapter_complete": True,
            "grants_badge": "desire_profiled",
            "trigger_vip_conversion": True,  # IMPORTANTE: Trigger de conversión
            "show_vip_shop_item": "llave_divan"
        }

        await session.flush()
        print(f"  ✓ L3_11 creado (ID: {l3_11.id})")

        # Decisión final
        await container.decision.create_decision(
            fragment_id=l3_11.id,
            button_text="Finalizar Nivel 3",
            target_fragment_key="l3_11_lucien_vip",
            order=0,
            button_emoji="✅",
            grants_besitos=10
        )

        # Commit de todo
        await session.commit()

        print("\n✅ Seed del Nivel 3 completado exitosamente!")
        print("\n📊 Resumen:")
        print(f"  • Capítulo: L3_DESIRE_PROFILE (ID: {chapter.id})")
        print(f"  • Fragmentos creados: 20 (incluyendo 6 variantes por arquetipo)")
        print(f"  • Decisiones creadas: ~30")
        print(f"  • Punto de entrada: l3_01_diana_request")
        print(f"  • Cuestionario: 5 preguntas (4 opciones múltiples, 1 texto libre)")
        print(f"  • Arquetipos: 6 variantes (Explorer, Romantic, Analytical, Direct, Patient, Persistent)")
        print(f"  • Flags narrativos: curious, attracted, seeking, intuitive, visual, verbal, mystery, personal, etc.")
        print(f"  • Recompensas: +10 favores, badge 'desire_profiled', pista_3, invitation_to_divan")
        print(f"  • Trigger: Conversión VIP activada")


if __name__ == "__main__":
    asyncio.run(seed_level_3())
