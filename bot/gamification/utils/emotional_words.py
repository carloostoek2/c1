"""
Diccionario de palabras emocionales para detección de arquetipo ROMANTIC.

Este módulo contiene las palabras y frases que indican contenido
emocional en las respuestas del usuario. Lucien usa estas señales
para identificar a los románticos.
"""

from typing import Tuple
import re


# ========================================
# PALABRAS EMOCIONALES
# ========================================

EMOTIONAL_WORDS = {
    # Positivas intensas
    "amor", "amo", "quiero", "adoro", "deseo", "anhelo", "sueño",
    "pasión", "corazón", "alma", "sentir", "siento",

    # Conexión
    "conexión", "conectar", "especial", "único", "única", "íntimo",
    "cercano", "profundo", "verdadero", "auténtico", "genuino",

    # Vulnerabilidad
    "miedo", "temo", "vulnerable", "abierto", "honesto", "sincero",
    "confiar", "confianza", "entrega", "rendirme",

    # Intensidad
    "intenso", "increíble", "maravilloso", "hermoso", "perfecto",
    "mágico", "extraordinario", "inolvidable",

    # Relacionales
    "nosotros", "juntos", "compartir", "unir", "pertenecer",
    "acompañar", "entender", "comprender",

    # Afecto
    "cariño", "ternura", "dulzura", "calidez", "abrazo", "beso",
    "abrazar", "besar", "susurrar", "acariciar",

    # Admiración
    "admirar", "fascinación", "encanto", "encantar", "fascinar",
    "cautivar", "hipnotizar", "seducir",

    # Nostalgia/Anhelo
    "extrañar", "necesitar", "anhelar", "soñar", "añorar",
    "recordar", "memoria", "recuerdo",

    # Relacionadas con Diana
    "diana", "bella", "hermosa", "perfecta", "diosa", "reina",
    "señorita", "dueña", "ama",

    # Devoción
    "devoción", "dedicación", "lealtad", "fidelidad", "entrega",
    "sometimiento", "obediencia", "servir",

    # Emociones
    "feliz", "felicidad", "alegría", "emoción", "emocionado",
    "conmovido", "tocado", "impactado",

    # Deseo
    "desear", "querer", "necesitar", "ansiar", "morir por",
}

# ========================================
# FRASES EMOCIONALES
# ========================================

EMOTIONAL_PHRASES = [
    "me haces sentir",
    "no puedo dejar de",
    "significa mucho",
    "desde el corazón",
    "en el fondo",
    "lo que siento",
    "me encanta",
    "me fascina",
    "me cautiva",
    "me enamora",
    "con todo mi",
    "te admiro",
    "te adoro",
    "contigo es",
    "a tu lado",
    "por ti",
    "para ti",
    "eres especial",
    "eres única",
    "no hay nadie como",
    "nunca había sentido",
    "me hace feliz",
]

# ========================================
# PATRONES DE PREGUNTAS SOBRE DIANA
# ========================================

DIANA_QUESTION_PATTERNS = [
    r"\b(diana|ella)\b.*\?",
    r"\bquién es\b",
    r"\bcómo es\b.*\bpersona\b",
    r"\bqué le gusta\b",
    r"\bcuántos años\b",
    r"\bdónde vive\b",
    r"\bvida\b.*\bpersonal\b",
    r"\bcómo empezó\b",
    r"\bqué significa\b.*\bpara ti\b",
    r"\bcuéntame\b.*\bsobre\b",
    r"\bme gustaría saber\b",
    r"\bquisiera conocer\b",
]


def has_emotional_content(text: str) -> Tuple[bool, int]:
    """
    Detecta si el texto contiene contenido emocional.

    Analiza el texto buscando palabras y frases emocionales
    definidas en los diccionarios del módulo.

    Args:
        text: Texto a analizar

    Returns:
        Tupla (tiene_contenido_emocional, cantidad_palabras_emocionales)

    Examples:
        >>> has_emotional_content("Me encanta lo que haces, Diana")
        (True, 2)
        >>> has_emotional_content("Ok, entendido")
        (False, 0)
    """
    text_lower = text.lower()
    count = 0

    # Contar palabras emocionales
    for word in EMOTIONAL_WORDS:
        if word in text_lower:
            count += 1

    # Contar frases emocionales (pesan más)
    for phrase in EMOTIONAL_PHRASES:
        if phrase in text_lower:
            count += 2

    return (count > 0, count)


def is_diana_question(text: str) -> bool:
    """
    Detecta si el texto es una pregunta sobre Diana.

    Args:
        text: Texto a analizar

    Returns:
        True si parece ser una pregunta personal sobre Diana

    Examples:
        >>> is_diana_question("¿Cómo es Diana en persona?")
        True
        >>> is_diana_question("¿Cuánto cuesta?")
        False
    """
    text_lower = text.lower()
    for pattern in DIANA_QUESTION_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False


def get_emotional_intensity(text: str) -> str:
    """
    Determina la intensidad emocional del texto.

    Args:
        text: Texto a analizar

    Returns:
        Nivel de intensidad: "none", "low", "medium", "high"
    """
    has_emotional, count = has_emotional_content(text)

    if not has_emotional:
        return "none"
    elif count <= 2:
        return "low"
    elif count <= 5:
        return "medium"
    else:
        return "high"
