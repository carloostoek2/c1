"""
Script de seed para Nivel 1 - Bienvenida (Los Kinkys)

Carga el contenido narrativo completo del primer nivel según
especificación de Fase 5.

Fragmentos: 9 (L1_01 a L1_07, con branches L1_03B y L1_05A/L1_05B)
Decisiones: 4
Flags: first_reaction_fast, first_reaction_slow
Rewards: +5 favores, badge "first_step", pista_1
"""
import asyncio
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.database.engine import get_session, init_db
from bot.narrative.services.container import NarrativeContainer


async def seed_level_1():
    """Carga contenido del Nivel 1 - Bienvenida."""

    print("🌱 Iniciando seed del Nivel 1 - Bienvenida...")

    # Inicializar BD
    await init_db()

    async with get_session() as session:
        container = NarrativeContainer(session)

        # ===== CAPÍTULO L1_WELCOME =====
        print("\n📖 Creando capítulo L1_WELCOME...")

        from bot.narrative.database.enums import ChapterType

        chapter = await container.chapter.create_chapter(
            name="Nivel 1: Bienvenida",
            slug="l1-bienvenida",
            chapter_type=ChapterType.FREE,
            order=1,
            description="El primer contacto con Diana y Lucien. Un desafío simple: demostrar que puedes actuar."
        )

        # Fase 5: Configurar campos de nivel
        chapter.level = 1
        chapter.estimated_duration_minutes = 10
        chapter.favor_reward = 5.0
        chapter.badge_reward = "first_step"
        chapter.item_reward = "pista_1"

        await session.flush()

        print(f"  ✓ Capítulo creado: {chapter.slug} (ID: {chapter.id})")

        # ===== FRAGMENTO L1_01: Primera aparición de Diana =====
        print("\n📝 Creando fragmento L1_01...")

        l1_01 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l1_01_diana_appears",
            title="Primera aparición de Diana",
            speaker="diana",
            content=(
                "Así que has llegado.\n\n"
                "No sé cómo encontraste este lugar. No sé qué buscas exactamente.\n"
                "Pero estás aquí. Y eso ya dice algo sobre ti.\n\n"
                "Soy Diana. O Kinky. O ninguna de las dos.\n"
                "Depende de qué parte de mí decidas ver.\n\n"
                "Antes de continuar... hay alguien que quiere conocerte."
            ),
            order=1,
            is_entry_point=True,  # PUNTO DE ENTRADA
            is_ending=False,
        )

        # Fase 5: Sin delay inicial
        l1_01.delay_seconds = 0
        l1_01.is_decision_point = False
        l1_01.next_fragment_key = "l1_02_lucien_intro"

        await session.flush()
        print(f"  ✓ L1_01 creado (ID: {l1_01.id})")

        # Decisión automática para continuar
        await container.decision.create_decision(
            fragment_id=l1_01.id,
            button_text="Continuar",
            target_fragment_key="l1_02_lucien_intro",
            order=0,
            button_emoji="▶️"
        )

        # ===== FRAGMENTO L1_02: Lucien se presenta =====
        print("\n📝 Creando fragmento L1_02...")

        l1_02 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l1_02_lucien_intro",
            title="Lucien se presenta",
            speaker="lucien",
            content=(
                "Permítame presentarme.\n\n"
                "Soy Lucien. Administro el acceso al universo de Diana.\n"
                "No soy su secretario. No soy su guardaespaldas.\n"
                "Soy... el filtro. El que determina quién merece llegar más lejos.\n\n"
                "Diana no recibe a cualquiera. Mi trabajo es asegurarme de que\n"
                "quienes la conocen sean dignos del privilegio."
            ),
            order=2,
            is_entry_point=False,
            is_ending=False,
        )

        # Fase 5: Delay dramático de 2 segundos
        l1_02.delay_seconds = 2
        l1_02.is_decision_point = False
        l1_02.next_fragment_key = "l1_03_first_challenge"

        await session.flush()
        print(f"  ✓ L1_02 creado (ID: {l1_02.id})")

        # Decisión para continuar
        await container.decision.create_decision(
            fragment_id=l1_02.id,
            button_text="Continuar",
            target_fragment_key="l1_03_first_challenge",
            order=0,
            button_emoji="▶️"
        )

        # ===== FRAGMENTO L1_03: El primer desafío =====
        print("\n📝 Creando fragmento L1_03...")

        l1_03 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l1_03_first_challenge",
            title="El primer desafío",
            speaker="lucien",
            content=(
                "Ahora, una prueba simple.\n\n"
                "Diana ha publicado algo recientemente en el canal.\n"
                "Quiero ver si usted es de los que actúan... o de los que solo miran.\n\n"
                "Vaya al canal. Encuentre la última publicación. Reaccione.\n\n"
                "Cualquier reacción sirve. Lo que importa es que lo haga.\n"
                "Estaré observando."
            ),
            order=3,
            is_entry_point=False,
            is_ending=False,
        )

        # Fase 5: Es punto de decisión (2 opciones)
        l1_03.delay_seconds = 2
        l1_03.is_decision_point = True

        await session.flush()
        print(f"  ✓ L1_03 creado (ID: {l1_03.id})")

        # Decisión 1: Aceptar el desafío
        await container.decision.create_decision(
            fragment_id=l1_03.id,
            button_text="Entendido, voy ahora",
            target_fragment_key="l1_04_waiting",
            order=0,
            button_emoji="✅"
        )

        # Decisión 2: Desafiar a Lucien
        await container.decision.create_decision(
            fragment_id=l1_03.id,
            button_text="¿Por qué debería hacerlo?",
            target_fragment_key="l1_03b_challenge_response",
            order=1,
            button_emoji="❓"
        )

        # ===== FRAGMENTO L1_03B: Respuesta al desafiante (BRANCH) =====
        print("\n📝 Creando fragmento L1_03B (branch)...")

        l1_03b = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l1_03b_challenge_response",
            title="Respuesta al desafiante",
            speaker="lucien",
            content=(
                "¿Por qué?\n\n"
                "Porque Diana nota a quienes actúan. Ignora a quienes solo observan.\n"
                "Porque cada paso aquí es una evaluación.\n"
                "Porque si no puede hacer algo tan simple... el resto será imposible.\n\n"
                "Pero si prefiere quedarse en la puerta, es su elección.\n"
                "Yo no insisto. Solo informo."
            ),
            order=4,
            is_entry_point=False,
            is_ending=False,
        )

        # Fase 5: Delay de 1 segundo
        l1_03b.delay_seconds = 1
        l1_03b.is_decision_point = False
        l1_03b.next_fragment_key = "l1_04_waiting"

        await session.flush()
        print(f"  ✓ L1_03B creado (ID: {l1_03b.id})")

        # Decisión para continuar
        await container.decision.create_decision(
            fragment_id=l1_03b.id,
            button_text="Está bien, lo haré",
            target_fragment_key="l1_04_waiting",
            order=0,
            button_emoji="✅"
        )

        # ===== FRAGMENTO L1_04: Esperando reacción =====
        print("\n📝 Creando fragmento L1_04...")

        l1_04 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l1_04_waiting",
            title="Esperando reacción",
            speaker="system",
            content=(
                "⏳ <b>Esperando su reacción en el canal...</b>\n\n"
                "Cuando haya reaccionado a una publicación del canal Los Kinkys,\n"
                "esta conversación continuará automáticamente.\n\n"
                "<i>Nota: Este es un placeholder. En producción, un background task\n"
                "detectará la reacción y continuará el flujo.</i>"
            ),
            order=5,
            is_entry_point=False,
            is_ending=False,
        )

        # Fase 5: Sin delay
        l1_04.delay_seconds = 0
        l1_04.is_decision_point = True  # 2 rutas según tiempo de reacción

        await session.flush()
        print(f"  ✓ L1_04 creado (ID: {l1_04.id})")

        # Decisión simulada: Reacción rápida (<2 min)
        await container.decision.create_decision(
            fragment_id=l1_04.id,
            button_text="[Simular reacción rápida]",
            subtext="< 2 minutos",
            target_fragment_key="l1_05a_fast_reaction",
            order=0,
            button_emoji="⚡",
            sets_flag="first_reaction_fast"  # Fase 5: SETEA FLAG
        )

        # Decisión simulada: Reacción pausada (>2 min)
        await container.decision.create_decision(
            fragment_id=l1_04.id,
            button_text="[Simular reacción pausada]",
            subtext="> 2 minutos",
            target_fragment_key="l1_05b_slow_reaction",
            order=1,
            button_emoji="🤔",
            sets_flag="first_reaction_slow"  # Fase 5: SETEA FLAG
        )

        # ===== FRAGMENTO L1_05A: Reacción rápida =====
        print("\n📝 Creando fragmento L1_05A...")

        l1_05a = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l1_05a_fast_reaction",
            title="Reacción rápida",
            speaker="lucien",
            content=(
                "Rápido. Muy rápido.\n\n"
                "Apenas di la instrucción y ya actuó. Eso dice algo.\n"
                "Impulsivo, quizás. O simplemente... decidido.\n\n"
                "Diana nota a los que no dudan. Pero también nota\n"
                "a los que actúan sin pensar. Veremos cuál es usted."
            ),
            order=6,
            is_entry_point=False,
            is_ending=False,
        )

        # Fase 5: Delay de 1 segundo
        l1_05a.delay_seconds = 1
        l1_05a.is_decision_point = False
        l1_05a.next_fragment_key = "l1_06_diana_reward"

        await session.flush()
        print(f"  ✓ L1_05A creado (ID: {l1_05a.id})")

        # Decisión para continuar
        await container.decision.create_decision(
            fragment_id=l1_05a.id,
            button_text="Continuar",
            target_fragment_key="l1_06_diana_reward",
            order=0,
            button_emoji="▶️"
        )

        # ===== FRAGMENTO L1_05B: Reacción pausada =====
        print("\n📝 Creando fragmento L1_05B...")

        l1_05b = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l1_05b_slow_reaction",
            title="Reacción pausada",
            speaker="lucien",
            content=(
                "Se tomó su tiempo.\n\n"
                "No saltó inmediatamente. Procesó. Quizás leyó el contenido\n"
                "antes de reaccionar. O quizás dudó.\n\n"
                "La paciencia es una virtud subestimada. Pero también puede ser\n"
                "una máscara para la indecisión. El tiempo dirá."
            ),
            order=7,
            is_entry_point=False,
            is_ending=False,
        )

        # Fase 5: Delay de 1 segundo
        l1_05b.delay_seconds = 1
        l1_05b.is_decision_point = False
        l1_05b.next_fragment_key = "l1_06_diana_reward"

        await session.flush()
        print(f"  ✓ L1_05B creado (ID: {l1_05b.id})")

        # Decisión para continuar
        await container.decision.create_decision(
            fragment_id=l1_05b.id,
            button_text="Continuar",
            target_fragment_key="l1_06_diana_reward",
            order=0,
            button_emoji="▶️"
        )

        # ===== FRAGMENTO L1_06: Entrega de recompensas (Diana) =====
        print("\n📝 Creando fragmento L1_06...")

        l1_06 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l1_06_diana_reward",
            title="Entrega de recompensas",
            speaker="diana",
            content=(
                "Bien. Diste el primer paso.\n\n"
                "No es mucho, pero es más de lo que la mayoría hace.\n"
                "La mayoría mira desde lejos. Tú actuaste.\n\n"
                "Te he dejado algo. Una especie de... mochila para el viaje.\n"
                "Y la primera pista de algo más grande.\n\n"
                "Lucien te explicará."
            ),
            order=8,
            is_entry_point=False,
            is_ending=False,
        )

        # Fase 5: Delay de 2 segundos (revelación importante)
        l1_06.delay_seconds = 2
        l1_06.is_decision_point = False
        l1_06.next_fragment_key = "l1_07_lucien_closure"

        await session.flush()
        print(f"  ✓ L1_06 creado (ID: {l1_06.id})")

        # Decisión para continuar
        await container.decision.create_decision(
            fragment_id=l1_06.id,
            button_text="Continuar",
            target_fragment_key="l1_07_lucien_closure",
            order=0,
            button_emoji="▶️"
        )

        # ===== FRAGMENTO L1_07: Explicación de Lucien + Cierre =====
        print("\n📝 Creando fragmento L1_07...")

        l1_07 = await container.fragment.create_fragment(
            chapter_id=chapter.id,
            fragment_key="l1_07_lucien_closure",
            title="Explicación de Lucien + Cierre",
            speaker="lucien",
            content=(
                "Ha recibido la Mochila del Viajero.\n"
                "Es simbólica, pero lo que contiene es real.\n\n"
                "También tiene la Primera Pista. Hay un mapa que Diana\n"
                "ha escondido en este universo. Las pistas lo revelarán.\n\n"
                "Por ahora, explore. Observe. Reaccione cuando sienta que debe.\n"
                "Cuando esté listo para el siguiente paso, lo sabrá.\n\n"
                "<b>+5 Favores</b> han sido añadidos a su cuenta.\n"
                "Diana lo notará."
            ),
            order=9,
            is_entry_point=False,
            is_ending=True,  # FIN DEL NIVEL 1
        )

        # Fase 5: Delay de 2 segundos (cierre)
        l1_07.delay_seconds = 2
        l1_07.is_decision_point = False
        l1_07.next_fragment_key = None  # Fin del capítulo

        # Fase 5: Metadata con recompensas
        l1_07.extra_metadata = {
            "grants_clue": "pista_1",
            "chapter_complete": True,
            "grants_badge": "first_step"
        }

        await session.flush()
        print(f"  ✓ L1_07 creado (ID: {l1_07.id})")

        # Decisión final
        await container.decision.create_decision(
            fragment_id=l1_07.id,
            button_text="Finalizar Nivel 1",
            target_fragment_key="l1_07_lucien_closure",  # Se queda en el mismo
            order=0,
            button_emoji="✅",
            grants_besitos=5  # Otorgar 5 besitos como recompensa adicional
        )

        # Commit de todo
        await session.commit()

        print("\n✅ Seed del Nivel 1 completado exitosamente!")
        print("\n📊 Resumen:")
        print(f"  • Capítulo: L1_WELCOME (ID: {chapter.id})")
        print(f"  • Fragmentos creados: 9")
        print(f"  • Decisiones creadas: 11")
        print(f"  • Punto de entrada: l1_01_diana_appears")
        print(f"  • Flags configurados: first_reaction_fast, first_reaction_slow")
        print(f"  • Recompensas: +5 favores, badge 'first_step', pista_1")


if __name__ == "__main__":
    asyncio.run(seed_level_1())
