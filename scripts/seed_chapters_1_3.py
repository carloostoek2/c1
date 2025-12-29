"""
Script de seed data para cargar los capítulos 1-3 (Los Kinkys - Canal Free).

Contenido narrativo completo del guión "El Mayordomo del Diván".
Los fragmentos usan la voz de Lucien y Diana según el guión narrativo.

Estructura de capítulos Free (Niveles 1-3):
- Capítulo 1: Bienvenida (4 fragmentos + variantes por arquetipo)
- Capítulo 2: Observación (4 fragmentos)
- Capítulo 3: Perfil de Deseo / La Invitación (4 fragmentos)

Uso:
    python scripts/seed_chapters_1_3.py
"""

import asyncio
import sys
import os

# Agregar directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.database import init_db, close_db, get_session
from bot.narrative.database import (
    ChapterType,
    NarrativeChapter,
    NarrativeFragment,
    FragmentDecision,
    FragmentRequirement,
    RequirementType,
)


# =============================================================================
# CONTENIDO NARRATIVO - CAPÍTULO 1: BIENVENIDA
# =============================================================================

CHAPTER_1_DATA = {
    "name": "Bienvenida",
    "slug": "cap-1-bienvenida",
    "chapter_type": ChapterType.FREE,
    "description": "Primer contacto con Diana y Lucien. El usuario descubre el universo del Diván.",
    "order": 1,
}

CHAPTER_1_FRAGMENTS = [
    # -------------------------------------------------------------------------
    # Fragmento 1.1: Bienvenida de Diana
    # -------------------------------------------------------------------------
    {
        "fragment_key": "1.1_bienvenida_diana",
        "title": "Bienvenida de Diana",
        "speaker": "diana",
        "content": (
            "<b>Diana:</b>\n\n"
            "Bienvenido a Los Kinkys.\n"
            "Has cruzado una línea que muchos ven... pero pocos realmente atraviesan.\n\n"
            "Puedo sentir tu curiosidad desde aquí. Es... intrigante.\n"
            "No todos llegan con esa misma hambre en los ojos.\n\n"
            "Este lugar responde a quienes saben que algunas puertas solo se abren "
            "desde adentro.\n"
            "Y yo... bueno, yo solo me revelo ante quienes comprenden que lo más "
            "valioso nunca se entrega fácilmente.\n\n"
            "<i>Algo me dice que tú podrías ser diferente.\n"
            "Pero eso... eso está por verse.</i>"
        ),
        "visual_hint": "Imagen de Diana entre sombras, parcialmente oculta",
        "is_entry_point": True,
        "order": 0,
        "extra_metadata": {"grants_clue": None, "level_required": 1},
        "decisions": [
            {
                "button_text": "Descubrir más",
                "button_emoji": None,
                "target_fragment_key": "1.2_lucien_desafio",
                "order": 0,
                "besitos_cost": 0,
                "grants_besitos": 5,
            }
        ],
    },
    # -------------------------------------------------------------------------
    # Fragmento 1.2: Lucien presenta el primer desafío
    # -------------------------------------------------------------------------
    {
        "fragment_key": "1.2_lucien_desafio",
        "title": "Lucien y el Primer Desafío",
        "speaker": "lucien",
        "content": (
            "<b>Lucien:</b>\n\n"
            "Ah, otro visitante de Diana. Permítame adivinar: viene buscando "
            "\"algo especial\". Qué... predecible.\n\n"
            "Soy Lucien, mayordomo digital y guardián de los secretos que Diana "
            "no cuenta... todavía. También soy el encargado de recoger los corazones "
            "rotos. Tengo una colección impresionante.\n\n"
            "Veo que Diana ya plantó esa semillita de curiosidad en usted. "
            "Lo noto por esa expresión de \"quiero pero no debería\" tan característica. "
            "Diana adora esa expresión, por cierto. La encuentra... nutritiva.\n\n"
            "Diana observa. Siempre observa. Es como un halcón, pero con mejor gusto "
            "en decoración. Y lo que más le fascina no es la obediencia ciega - eso es "
            "aburrido - sino la intención detrás de cada gesto. "
            "¿Reacciona porque siente, o porque cree que debe?\n\n"
            "<b>Misión:</b> Reaccione al último mensaje del canal. "
            "Pero hágalo porque realmente quiere entender, no porque yo se lo ordeno. "
            "Diana detesta a los robots emocionales.\n\n"
            "<i>Por cierto, ella está observando su velocidad de reacción. "
            "Entre usted y yo, las estadísticas de supervivencia romántica varían "
            "según qué tan rápido salte.</i>"
        ),
        "visual_hint": "Lucien elegante pero con mirada penetrante y sonrisa burlona",
        "is_entry_point": False,
        "order": 1,
        "extra_metadata": {
            "mission_type": "reaction",
            "mission_target": "last_channel_message",
            "tracks_response_time": True,
        },
        "decisions": [
            {
                "button_text": "Ya reaccioné",
                "button_emoji": None,
                "target_fragment_key": "1.3a_impulsivo",
                "order": 0,
                "besitos_cost": 0,
                "grants_besitos": 10,
                "affects_archetype": "impulsive",
            },
            {
                "button_text": "Déjame pensarlo",
                "button_emoji": None,
                "target_fragment_key": "1.3b_contemplativo",
                "order": 1,
                "besitos_cost": 0,
                "grants_besitos": 5,
                "affects_archetype": "contemplative",
            },
        ],
    },
    # -------------------------------------------------------------------------
    # Fragmento 1.3A: Respuesta para usuario impulsivo
    # -------------------------------------------------------------------------
    {
        "fragment_key": "1.3a_impulsivo",
        "title": "Respuesta Impulsiva",
        "speaker": "lucien",
        "content": (
            "<b>Lucien:</b>\n\n"
            "Bueno, eso fue... rápido. Impulsivo, diría yo. Diana adora a los que "
            "no se pierden analizando hasta la muerte cada micro-gesto romántico.\n\n"
            "Hay algo hermoso en esa espontaneidad suya. Como un cachorro persiguiendo "
            "su cola: adorable, aunque no siempre efectivo.\n\n"
            "<b>Diana:</b>\n"
            "<i>Impulsivo... pero no imprudente. Hay una diferencia que pocos entienden.\n"
            "Me gusta eso de usted.</i>\n\n"
            "<b>Lucien:</b>\n"
            "Y ahí va Diana, siendo casi humana otra vez. Siempre me toma por sorpresa, "
            "como encontrar wifi que funciona o personas que leen los términos y condiciones.\n\n"
            "Su Mochila del Viajero, cortesía de alguien que aprecia la acción sin parálisis "
            "por análisis. Diana la eligió específicamente para alguien como usted: "
            "alguien que actúa cuando siente que algo es correcto, aunque no sepa "
            "exactamente por qué."
        ),
        "visual_hint": "Diana aparece brevemente con sonrisa apenas perceptible",
        "is_entry_point": False,
        "order": 2,
        "extra_metadata": {
            "archetype_signal": "impulsive",
            "reward_item": "mochila_viajero",
            "reward_clue": 1,
        },
        "decisions": [
            {
                "button_text": "Ver mi mochila",
                "button_emoji": None,
                "target_fragment_key": "1.4_primera_pista",
                "order": 0,
                "besitos_cost": 0,
                "grants_besitos": 0,
            }
        ],
    },
    # -------------------------------------------------------------------------
    # Fragmento 1.3B: Respuesta para usuario contemplativo
    # -------------------------------------------------------------------------
    {
        "fragment_key": "1.3b_contemplativo",
        "title": "Respuesta Contemplativa",
        "speaker": "lucien",
        "content": (
            "<b>Lucien:</b>\n\n"
            "Ah, un contemplativo. Se tomó su tiempo, evaluó, consideró las implicaciones "
            "existenciales de un simple click. Hay sabiduría en esa paciencia que Diana "
            "encuentra... cómo decirlo... seductoramente frustrante.\n\n"
            "Diana adora a los que comprenden que las mejores cosas no deben apresurarse. "
            "Como el buen vino, el queso francés, y la venganza servida fría.\n\n"
            "<b>Diana:</b>\n"
            "<i>Me fascina cómo algunos saben que lo genuino no debe apresurarse.\n"
            "Su manera de aproximarse dice más de usted que cualquier reacción impulsiva.</i>\n\n"
            "<b>Lucien:</b>\n"
            "Diana está impresionada. Y cuando digo impresionada, me refiero genuinamente "
            "impresionada, no mi usual \"impresionada\" sarcástico. Sí, tengo ambos en "
            "mi repertorio.\n\n"
            "Su Mochila del Viajero. La pista que encontrará dentro fue seleccionada para "
            "alguien que comprende que los mejores secretos se revelan a quienes saben que "
            "esperar puede ser su propia forma de seducción."
        ),
        "visual_hint": "Diana con mirada pensativa",
        "is_entry_point": False,
        "order": 3,
        "extra_metadata": {
            "archetype_signal": "contemplative",
            "reward_item": "mochila_viajero",
            "reward_clue": 1,
        },
        "decisions": [
            {
                "button_text": "Ver mi mochila",
                "button_emoji": None,
                "target_fragment_key": "1.4_primera_pista",
                "order": 0,
                "besitos_cost": 0,
                "grants_besitos": 0,
            }
        ],
    },
    # -------------------------------------------------------------------------
    # Fragmento 1.4: Primera Pista
    # -------------------------------------------------------------------------
    {
        "fragment_key": "1.4_primera_pista",
        "title": "La Primera Pista",
        "speaker": "lucien",
        "content": (
            "<b>Lucien:</b>\n\n"
            "Un mapa incompleto. Qué sorpresa. Diana no cree en las respuestas fáciles, "
            "los manuales de instrucciones, o las aplicaciones que funcionan a la primera.\n\n"
            "Solo tiene la mitad. La otra mitad está... bueno, donde las reglas del juego "
            "cambian y yo tengo que actualizar mi currículum de \"Facilitador de Imposibles "
            "Románticos\".\n\n"
            "<b>Diana:</b>\n"
            "<i>La otra mitad... no existe en este mundo que conoce.\n"
            "Está donde las reglas cambian, donde yo puedo ser... más de lo que aquí me "
            "permito ser.\n\n"
            "¿Está preparado para buscar en lugares donde no todos pueden entrar?\n"
            "Porque una vez que cruce completamente hacia mí... no hay vuelta atrás.</i>\n\n"
            "<b>Lucien:</b>\n"
            "Y con esa declaración dramática, Diana se retira a contemplar su propia "
            "complejidad. Mientras tanto, yo estaré aquí, sirviendo té existencial y "
            "recordándoles a todos que esto es, técnicamente, mi trabajo.\n\n"
            "Las pistas aparecen cuando Diana siente que está listo. No hay horarios. "
            "No hay garantías. Solo... conexión. Y mi comentario sarcástico ocasional "
            "para mantener todo en perspectiva."
        ),
        "visual_hint": "Lucien presentando mapa fragmentado con teatralidad",
        "is_entry_point": False,
        "is_ending": True,
        "order": 4,
        "extra_metadata": {
            "chapter_complete": True,
            "unlocks_level": 2,
            "mission_hint": "Las pistas aparecen cuando Diana siente que estás listo",
        },
        "decisions": [],
    },
]


# =============================================================================
# CONTENIDO NARRATIVO - CAPÍTULO 2: OBSERVACIÓN
# =============================================================================

CHAPTER_2_DATA = {
    "name": "Observación",
    "slug": "cap-2-observacion",
    "chapter_type": ChapterType.FREE,
    "description": "Diana nota el regreso del usuario. Misión de observación durante 3 días.",
    "order": 2,
}

CHAPTER_2_FRAGMENTS = [
    # -------------------------------------------------------------------------
    # Fragmento 2.1: Diana nota el regreso
    # -------------------------------------------------------------------------
    {
        "fragment_key": "2.1_diana_regreso",
        "title": "El Regreso Observado",
        "speaker": "diana",
        "content": (
            "<b>Diana:</b>\n\n"
            "Volvió. Interesante...\n"
            "No todos regresan después de la primera revelación. Algunos se quedan "
            "satisfechos con las migajas de misterio.\n\n"
            "Pero usted... usted quiere más. Puedo sentir esa hambre desde aquí.\n"
            "Hay algo delicioso en esa persistencia suya.\n\n"
            "¿Sabe lo que más me fascina de usted hasta ahora? No es solo que "
            "haya regresado.\n"
            "Es <i>cómo</i> regresó. Con esa mezcla de expectativa y respeto que tan "
            "pocos comprenden."
        ),
        "visual_hint": "Diana aparece en un ángulo diferente, como si hubiera estado esperando",
        "is_entry_point": True,
        "order": 0,
        "extra_metadata": {"level_required": 2},
        "requirements": [
            {
                "requirement_type": RequirementType.CHAPTER_COMPLETE,
                "value": "cap-1-bienvenida",
                "rejection_message": "Primero debe completar el Capítulo 1.",
            }
        ],
        "decisions": [
            {
                "button_text": "Explorar más profundo",
                "button_emoji": None,
                "target_fragment_key": "2.2_lucien_observacion",
                "order": 0,
                "besitos_cost": 0,
                "grants_besitos": 5,
            }
        ],
    },
    # -------------------------------------------------------------------------
    # Fragmento 2.2: Lucien presenta el desafío de observación
    # -------------------------------------------------------------------------
    {
        "fragment_key": "2.2_lucien_observacion",
        "title": "Desafío de Observación",
        "speaker": "lucien",
        "content": (
            "<b>Lucien:</b>\n\n"
            "Bueno, bueno... mire quién regresó por más. Diana ha estado observándole "
            "más de lo que cree. Cada vez que consultó su mochila, cada momento que "
            "regresó a leer sus palabras como si fueran poesía romántica...\n\n"
            "Ella lo vio todo. Es como Santa Claus, pero con mejor gusto en lencería "
            "y menos problemas laborales con elfos sindicalizados.\n\n"
            "Y ahora, Diana quiere ver si usted puede observarla con la misma "
            "intensidad obsesiva... digo, dedicada atención.\n\n"
            "<b>Misión:</b> Durante los próximos 3 días, debe encontrar pistas ocultas "
            "en las publicaciones del canal. Pero no cualquier pista. Pistas que solo "
            "alguien que realmente <i>observa</i> puede detectar.\n\n"
            "Básicamente, Diana quiere que se convierta en su acosador virtual autorizado. "
            "Es romántico de una manera completamente moderna y ligeramente perturbadora.\n\n"
            "<b>Diana:</b>\n"
            "<i>No busque lo obvio. Busque lo que otros pasan por alto.\n"
            "Busque los detalles que revelan más sobre mí que las palabras que elijo decir.</i>\n\n"
            "<b>Lucien:</b>\n"
            "Y ahí está, siendo misteriosa otra vez. Mi trabajo nunca termina. "
            "Próxima parada: detectivismo romántico con certificación digital."
        ),
        "visual_hint": "Lucien acercándose conspiradoramente",
        "is_entry_point": False,
        "order": 1,
        "extra_metadata": {
            "mission_type": "observation",
            "mission_duration_days": 3,
            "mission_target": "hidden_clues",
        },
        "decisions": [
            {
                "button_text": "Aceptar el desafío",
                "button_emoji": None,
                "target_fragment_key": "2.3_mision_progreso",
                "order": 0,
                "besitos_cost": 0,
                "grants_besitos": 0,
            }
        ],
    },
    # -------------------------------------------------------------------------
    # Fragmento 2.3: Progreso de la misión (placeholder)
    # -------------------------------------------------------------------------
    {
        "fragment_key": "2.3_mision_progreso",
        "title": "Progreso de Observación",
        "speaker": "lucien",
        "content": (
            "<b>Lucien:</b>\n\n"
            "La misión de observación ha comenzado.\n\n"
            "Recuerde: Diana observa todo. Cada pista que encuentre, cada detalle que note, "
            "será registrado. No hay forma de hacer trampa aquí - aunque aprecio el "
            "pensamiento creativo.\n\n"
            "Regrese cuando haya encontrado las pistas. O cuando Diana decida que ha "
            "pasado suficiente tiempo mirando intensamente la pantalla."
        ),
        "visual_hint": None,
        "is_entry_point": False,
        "order": 2,
        "extra_metadata": {"mission_checkpoint": True},
        "decisions": [
            {
                "button_text": "He encontrado las pistas",
                "button_emoji": None,
                "target_fragment_key": "2.4_reconocimiento",
                "order": 0,
                "besitos_cost": 0,
                "grants_besitos": 15,
            }
        ],
    },
    # -------------------------------------------------------------------------
    # Fragmento 2.4: Reconocimiento de la observación profunda
    # -------------------------------------------------------------------------
    {
        "fragment_key": "2.4_reconocimiento",
        "title": "Reconocimiento de Diana",
        "speaker": "diana",
        "content": (
            "<b>Diana:</b>\n\n"
            "Encontró cada una. Cada pista escondida, cada detalle que pensé que "
            "pasaría desapercibido.\n"
            "Hay algo inquietante en ser vista con tanta precisión.\n\n"
            "¿Sabe qué es lo que más me perturba de todo esto? No es que haya "
            "encontrado mis secretos.\n"
            "Es que... me gusta ser vista así. Me gusta que alguien ponga esa "
            "atención en mí.\n\n"
            "<b>Lucien:</b>\n"
            "Bueno, esto es... inesperado. Diana, admitiendo que le gusta la atención. "
            "Alerta de noticias: la mujer misteriosa es, sorprendentemente, humana.\n\n"
            "Debo admitir, encontró cada pista con una precisión que normalmente reservo "
            "para localizar el control remoto o el sentido de mi vida. Impresionante.\n\n"
            "Diana rara vez comparte fragmentos de su memoria. Lo que acaba de recibir "
            "es más exclusivo que membresías de clubes privados o explicaciones claras "
            "de políticas de privacidad. Es un privilegio que pocos obtienen, y que yo "
            "administro con la gracia de un cisne y el sarcasmo de un crítico literario."
        ),
        "visual_hint": "Diana mostrando vulnerabilidad genuina",
        "is_entry_point": False,
        "is_ending": True,
        "order": 3,
        "extra_metadata": {
            "chapter_complete": True,
            "unlocks_level": 3,
            "reward_clue": 2,
            "reward_item": "fragmento_memoria",
        },
        "decisions": [],
    },
]


# =============================================================================
# CONTENIDO NARRATIVO - CAPÍTULO 3: PERFIL DE DESEO
# =============================================================================

CHAPTER_3_DATA = {
    "name": "Perfil de Deseo",
    "slug": "cap-3-perfil-deseo",
    "chapter_type": ChapterType.FREE,
    "description": "Prueba final del nivel Free. Diana quiere conocer al usuario.",
    "order": 3,
}

CHAPTER_3_FRAGMENTS = [
    # -------------------------------------------------------------------------
    # Fragmento 3.1: Diana presenta la prueba final
    # -------------------------------------------------------------------------
    {
        "fragment_key": "3.1_diana_prueba_final",
        "title": "La Prueba Final",
        "speaker": "diana",
        "content": (
            "<b>Diana:</b>\n\n"
            "Hemos llegado al final de lo que puedo mostrarle... en este lado del muro.\n"
            "Pero antes de que decida si quiere más, necesito saber algo sobre usted.\n\n"
            "Durante todo este tiempo, ha estado descubriendo quién soy yo.\n"
            "Ahora yo quiero descubrir quién es usted.\n\n"
            "<b>Misión:</b> Complete su \"Perfil de Deseo\" - una serie de preguntas "
            "profundas que revelan no solo lo que busca, sino <i>por qué</i> lo busca."
        ),
        "visual_hint": "Diana se acerca más en la imagen, creando intimidad",
        "is_entry_point": True,
        "order": 0,
        "extra_metadata": {"level_required": 3},
        "requirements": [
            {
                "requirement_type": RequirementType.CHAPTER_COMPLETE,
                "value": "cap-2-observacion",
                "rejection_message": "Primero debe completar el Capítulo 2.",
            }
        ],
        "decisions": [
            {
                "button_text": "Comenzar el perfil",
                "button_emoji": None,
                "target_fragment_key": "3.2_lucien_evaluacion",
                "order": 0,
                "besitos_cost": 0,
                "grants_besitos": 5,
            }
        ],
    },
    # -------------------------------------------------------------------------
    # Fragmento 3.2: Lucien introduce la evaluación
    # -------------------------------------------------------------------------
    {
        "fragment_key": "3.2_lucien_evaluacion",
        "title": "La Evaluación Mutua",
        "speaker": "lucien",
        "content": (
            "<b>Lucien:</b>\n\n"
            "Ah, hemos llegado al momento de la verdad. Diana no hace esta pregunta "
            "a cualquiera. Si llegó hasta aquí, es porque despertó algo en ella. "
            "Algo que no había visto desde... bueno, desde el último usuario que llegó "
            "al Nivel 3. Pero ese es otro caso archivado.\n\n"
            "Verá, Diana está a punto de hacer algo radical: mostrar interés genuino "
            "en conocerle. Es como un eclipse solar, pero con más implicaciones "
            "emocionales y menos daño retinal.\n\n"
            "Entre usted y yo, esto es cuando la cosa se pone interesante. Ya no es "
            "solo otro visitante coleccionando pistas como si fueran cartas de Pokémon. "
            "Ahora es... bueno, alguien en quien Diana está considerando invertir "
            "tiempo emocional.\n\n"
            "Y yo, por supuesto, estaré aquí evaluando sus respuestas como si fuera "
            "un crítico de vinos, pero para personalidades. ¿Notas de autenticidad? "
            "¿Matices de vulnerabilidad? ¿Un final persistente de no ser un completo "
            "desastre?"
        ),
        "visual_hint": "Lucien con seriedad teñida de humor",
        "is_entry_point": False,
        "order": 1,
        "extra_metadata": {"evaluation_start": True},
        "decisions": [
            {
                "button_text": "Estoy listo",
                "button_emoji": None,
                "target_fragment_key": "3.3_diana_evaluacion",
                "order": 0,
                "besitos_cost": 0,
                "grants_besitos": 0,
            }
        ],
    },
    # -------------------------------------------------------------------------
    # Fragmento 3.3: Diana evalúa las respuestas
    # -------------------------------------------------------------------------
    {
        "fragment_key": "3.3_diana_evaluacion",
        "title": "Evaluación de Diana",
        "speaker": "diana",
        "content": (
            "<b>Diana:</b>\n\n"
            "He analizado sus respuestas...\n\n"
            "Hay algo en cómo describe lo que busca. No es superficial. "
            "No es el típico \"quiero diversión\" que escucho tantas veces.\n\n"
            "Usted busca algo más profundo. Conexión. Comprensión. "
            "Quizás incluso... ser visto de verdad.\n\n"
            "<i>¿Sabe algo curioso? Pensé que mantener la distancia sería más fácil "
            "con usted.\n"
            "Pero hay algo en cómo me mira, en cómo me <b>ve</b>, que hace que quiera... "
            "mostrar más.</i>\n\n"
            "<b>Lucien:</b>\n"
            "Y ahí va Diana otra vez, siendo vulnerable cuando menos me lo espero. "
            "Es como ver a un unicornio aprender a hacer impuestos: hermoso, imposible, "
            "y ligeramente desconcertante.\n\n"
            "Debo admitir, sus respuestas fueron... bueno, no terribles. De hecho, "
            "Diana está haciendo esa cara que hace cuando algo la sorprende positivamente. "
            "Como cuando encuentra una serie de Netflix que no cancela después de una "
            "temporada."
        ),
        "visual_hint": "Diana en momento de máxima vulnerabilidad en nivel gratuito",
        "is_entry_point": False,
        "order": 2,
        "extra_metadata": {"evaluation_complete": True},
        "decisions": [
            {
                "button_text": "Continuar",
                "button_emoji": None,
                "target_fragment_key": "3.4_invitacion",
                "order": 0,
                "besitos_cost": 0,
                "grants_besitos": 10,
            }
        ],
    },
    # -------------------------------------------------------------------------
    # Fragmento 3.4: La Invitación al Diván
    # -------------------------------------------------------------------------
    {
        "fragment_key": "3.4_invitacion",
        "title": "La Invitación - Llave del Diván",
        "speaker": "lucien",
        "content": (
            "<b>Lucien:</b>\n\n"
            "Su invitación al Diván. Personalizada según su nivel de no ser un "
            "completo desastre romántico.\n\n"
            "Diana está considerando seriamente mostrarle partes de sí misma que "
            "normalmente mantiene bajo llave, en una caja fuerte, en una dimensión "
            "paralela.\n\n"
            "Congratulaciones. Ha graduado de \"visitante curioso\" a \"persona de "
            "interés romántico\". Mi trabajo aquí está... bueno, técnicamente nunca "
            "termina, pero al menos se vuelve más interesante.\n\n"
            "<b>Diana:</b>\n"
            "<i>El Diván es donde las máscaras se vuelven innecesarias... casi.\n"
            "Si decide entrar, lo que encontrará allí cambiará la forma en que me ve.\n"
            "Y quizás... la forma en que se ve a usted mismo.</i>\n\n"
            "<b>Lucien:</b>\n"
            "La Llave del Diván está ahora disponible para usted. Úsela cuando esté "
            "listo para cruzar al otro lado.\n\n"
            "Y recuerde: Diana no hace invitaciones a la ligera. Este es el punto "
            "de conversión. El momento donde \"curioso\" se convierte en \"comprometido\"."
        ),
        "visual_hint": "Lucien presentando la invitación con floritura",
        "is_entry_point": False,
        "is_ending": True,
        "order": 3,
        "extra_metadata": {
            "chapter_complete": True,
            "is_conversion_point": True,
            "reward_clue": 3,
            "reward_item": "llave_divan",
            "unlocks_vip_invitation": True,
        },
        "decisions": [],
    },
]


async def seed_chapter(session, chapter_data: dict, fragments_data: list) -> None:
    """Carga un capítulo con todos sus fragmentos y decisiones."""
    from bot.narrative.services.chapter import ChapterService
    from bot.narrative.services.fragment import FragmentService

    chapter_service = ChapterService(session)
    fragment_service = FragmentService(session)

    # Verificar si ya existe el capítulo
    existing = await chapter_service.get_chapter_by_slug(chapter_data["slug"])
    if existing:
        print(f"  ⚠️  Capítulo '{chapter_data['name']}' ya existe. Saltando.")
        return

    # Crear capítulo
    chapter = await chapter_service.create_chapter(
        name=chapter_data["name"],
        slug=chapter_data["slug"],
        chapter_type=chapter_data["chapter_type"],
        description=chapter_data["description"],
        order=chapter_data["order"],
    )
    print(f"  ✅ Capítulo creado: {chapter.name} (ID: {chapter.id})")

    # Crear fragmentos
    for frag_data in fragments_data:
        fragment = await fragment_service.create_fragment(
            chapter_id=chapter.id,
            fragment_key=frag_data["fragment_key"],
            title=frag_data["title"],
            speaker=frag_data["speaker"],
            content=frag_data["content"],
            visual_hint=frag_data.get("visual_hint"),
            is_entry_point=frag_data.get("is_entry_point", False),
            is_ending=frag_data.get("is_ending", False),
            order=frag_data.get("order", 0),
            extra_metadata=frag_data.get("extra_metadata"),
        )

        # Crear decisiones para el fragmento
        for dec_data in frag_data.get("decisions", []):
            decision = FragmentDecision(
                fragment_id=fragment.id,
                button_text=dec_data["button_text"],
                button_emoji=dec_data.get("button_emoji"),
                target_fragment_key=dec_data["target_fragment_key"],
                order=dec_data.get("order", 0),
                besitos_cost=dec_data.get("besitos_cost", 0),
                grants_besitos=dec_data.get("grants_besitos", 0),
                affects_archetype=dec_data.get("affects_archetype"),
                is_active=True,
            )
            session.add(decision)

        # Crear requisitos para el fragmento
        for req_data in frag_data.get("requirements", []):
            requirement = FragmentRequirement(
                fragment_id=fragment.id,
                requirement_type=req_data["requirement_type"],
                value=req_data["value"],
                rejection_message=req_data.get("rejection_message"),
            )
            session.add(requirement)

        print(f"    📄 Fragmento: {frag_data['fragment_key']}")

    await session.flush()


async def seed_chapters_1_3():
    """Carga los capítulos 1-3 (Los Kinkys - Canal Free)."""
    print("=" * 60)
    print("🌱 SEED: Capítulos 1-3 (Los Kinkys - Canal Free)")
    print("=" * 60)

    # Inicializar BD
    await init_db()

    async with get_session() as session:
        # Capítulo 1: Bienvenida
        print("\n📚 Capítulo 1: Bienvenida")
        await seed_chapter(session, CHAPTER_1_DATA, CHAPTER_1_FRAGMENTS)

        # Capítulo 2: Observación
        print("\n📚 Capítulo 2: Observación")
        await seed_chapter(session, CHAPTER_2_DATA, CHAPTER_2_FRAGMENTS)

        # Capítulo 3: Perfil de Deseo
        print("\n📚 Capítulo 3: Perfil de Deseo")
        await seed_chapter(session, CHAPTER_3_DATA, CHAPTER_3_FRAGMENTS)

        await session.commit()

    await close_db()

    print("\n" + "=" * 60)
    print("✅ Seed completado exitosamente!")
    print("=" * 60)
    print("\nResumen:")
    print("  - 3 capítulos creados (Los Kinkys - Niveles 1-3)")
    print("  - 12 fragmentos narrativos")
    print("  - Decisiones con efectos de arquetipo")
    print("  - Requisitos de progresión por capítulo")
    print("\n🎮 El contenido narrativo Free está listo para usuarios.")


if __name__ == "__main__":
    asyncio.run(seed_chapters_1_3())
