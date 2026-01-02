"""
Detector de Arquetipos Expandido.

Analiza patrones de comportamiento del usuario para determinar su arquetipo
entre los 6 arquetipos del universo narrativo de El Mayordomo del Diván.

Arquetipos:
- EXPLORER: Busca cada detalle, revisa todo
- DIRECT: Va al grano, respuestas concisas
- ROMANTIC: Poético, busca conexión emocional
- ANALYTICAL: Reflexivo, busca comprensión
- PERSISTENT: No se rinde, múltiples intentos
- PATIENT: Toma tiempo, procesa profundamente
"""

import logging
import json
from datetime import datetime, UTC, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from bot.narrative.database.enums import ArchetypeType

logger = logging.getLogger(__name__)


# ================================================================
# CONFIGURACIÓN DE DETECCIÓN
# ================================================================

# Umbral mínimo para asignar arquetipo (60%)
ASSIGNMENT_THRESHOLD = 0.6

# Palabras emocionales para detectar ROMANTIC
EMOTIONAL_WORDS = {
    "amor", "sentir", "corazón", "alma", "emoción", "pasión",
    "deseo", "anhelo", "sueño", "fantasía", "intimidad", "conexión",
    "profundo", "intenso", "hermoso", "especial", "único", "mágico",
    "adorar", "querer", "necesitar", "extrañar", "abrazar", "besar"
}

# Intervalo de re-evaluación
REEVALUATION_DAYS = 7
REEVALUATION_INTERACTIONS = 10


# ================================================================
# SEÑALES DE ARQUETIPO
# ================================================================

@dataclass
class ArchetypeSignals:
    """Señales detectadas para clasificación de arquetipo."""

    # EXPLORER
    content_viewed_percentage: float = 0.0  # % contenido visto
    easter_eggs_found: int = 0
    avg_content_time_seconds: float = 0.0

    # DIRECT
    avg_response_words: float = 0.0
    avg_decision_time_seconds: float = 0.0
    button_vs_text_ratio: float = 0.0  # % de acciones por botón

    # ROMANTIC
    emotional_word_count: int = 0
    emotional_content_interactions: int = 0

    # ANALYTICAL
    quiz_score_avg: float = 0.0
    questions_asked: int = 0
    structured_responses: int = 0

    # PERSISTENT
    return_after_inactivity_count: int = 0
    challenge_retry_count: int = 0
    failed_action_retries: int = 0

    # PATIENT
    avg_response_time_seconds: float = 0.0
    skip_actions_used: int = 0
    current_streak_days: int = 0

    # Metadata
    total_interactions: int = 0
    last_evaluated: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convierte a diccionario para almacenamiento JSON."""
        data = asdict(self)
        if data['last_evaluated']:
            data['last_evaluated'] = data['last_evaluated'].isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'ArchetypeSignals':
        """Crea instancia desde diccionario."""
        if data.get('last_evaluated'):
            data['last_evaluated'] = datetime.fromisoformat(data['last_evaluated'])
        return cls(**data)


# ================================================================
# DETECTOR DE ARQUETIPOS
# ================================================================

class ArchetypeDetector:
    """
    Detector de arquetipos expandido.

    Evalúa señales de comportamiento y asigna uno de los 6 arquetipos
    del universo narrativo basado en reglas de detección.
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def detect(
        self,
        user_id: int,
        signals: Optional[ArchetypeSignals] = None,
        force: bool = False
    ) -> Tuple[Optional[ArchetypeType], float, ArchetypeSignals]:
        """
        Detecta arquetipo del usuario basado en señales.

        Args:
            user_id: ID del usuario
            signals: Señales pre-calculadas (opcional, se calculan si no se proveen)
            force: Forzar re-evaluación aunque no sea necesario

        Returns:
            Tupla (arquetipo, confianza, señales)
            - arquetipo: None si ninguno supera umbral
            - confianza: 0.0-1.0
            - señales: Señales utilizadas para detección
        """
        # Obtener o calcular señales
        if signals is None:
            signals = await self._gather_signals(user_id)

        # Verificar si necesita re-evaluación
        if not force and not self._needs_reevaluation(signals):
            logger.debug(f"Usuario {user_id} no requiere re-evaluación de arquetipo")
            # Retornar resultado anterior si existe
            return None, 0.0, signals

        # Calcular scores por arquetipo
        scores = self._calculate_scores(signals)

        # Encontrar mejor match
        best_archetype = None
        best_score = 0.0

        for archetype, score in scores.items():
            if score > best_score:
                best_score = score
                best_archetype = archetype

        # Verificar si supera umbral
        if best_score < ASSIGNMENT_THRESHOLD:
            logger.debug(
                f"Usuario {user_id}: ningún arquetipo supera umbral "
                f"(mejor: {best_archetype}={best_score:.2f})"
            )
            return None, best_score, signals

        logger.info(
            f"Arquetipo detectado para usuario {user_id}: "
            f"{best_archetype.value} (score={best_score:.2f})"
        )

        # Actualizar timestamp
        signals.last_evaluated = datetime.now(UTC)

        return best_archetype, best_score, signals

    def _calculate_scores(self, signals: ArchetypeSignals) -> Dict[ArchetypeType, float]:
        """
        Calcula score de cumplimiento para cada arquetipo.

        Cada arquetipo tiene 3 condiciones. El score es el % de condiciones cumplidas.

        Returns:
            Dict mapeando arquetipo a score (0.0-1.0)
        """
        scores = {}

        # EXPLORER: cumplir 2+ de 3
        explorer_conditions = [
            signals.content_viewed_percentage > 0.8,  # >80% contenido visto
            signals.easter_eggs_found >= 1,            # Al menos 1 easter egg
            signals.avg_content_time_seconds > 30      # >30s promedio en contenido
        ]
        scores[ArchetypeType.EXPLORER] = sum(explorer_conditions) / 3

        # DIRECT: cumplir 2+ de 3
        direct_conditions = [
            signals.avg_response_words < 15 and signals.avg_response_words > 0,
            signals.avg_decision_time_seconds < 5 and signals.avg_decision_time_seconds > 0,
            signals.button_vs_text_ratio > 0.8        # >80% usa botones
        ]
        scores[ArchetypeType.DIRECT] = sum(direct_conditions) / 3

        # ROMANTIC: cumplir 2+ de 3
        romantic_conditions = [
            signals.emotional_word_count >= 5,         # 5+ palabras emocionales
            signals.avg_response_words > 30,           # Respuestas largas
            signals.emotional_content_interactions >= 3  # Interactúa con contenido emocional
        ]
        scores[ArchetypeType.ROMANTIC] = sum(romantic_conditions) / 3

        # ANALYTICAL: cumplir 2+ de 3
        analytical_conditions = [
            signals.quiz_score_avg > 0.8,             # >80% en quizzes
            signals.questions_asked >= 2,              # Hace preguntas
            signals.structured_responses >= 3          # Respuestas estructuradas
        ]
        scores[ArchetypeType.ANALYTICAL] = sum(analytical_conditions) / 3

        # PERSISTENT: cumplir 2+ de 3
        persistent_conditions = [
            signals.return_after_inactivity_count >= 2,  # Retornó 2+ veces
            signals.challenge_retry_count >= 2,          # Reintenta desafíos
            signals.failed_action_retries >= 2           # Reintenta acciones fallidas
        ]
        scores[ArchetypeType.PERSISTENT] = sum(persistent_conditions) / 3

        # PATIENT: cumplir 2+ de 3
        patient_conditions = [
            signals.avg_response_time_seconds > 30,   # >30s promedio respuesta
            signals.skip_actions_used == 0,            # No usa skip
            signals.current_streak_days >= 7           # Racha 7+ días
        ]
        scores[ArchetypeType.PATIENT] = sum(patient_conditions) / 3

        return scores

    def _needs_reevaluation(self, signals: ArchetypeSignals) -> bool:
        """
        Verifica si el usuario necesita re-evaluación de arquetipo.

        Re-evalúa si:
        - Nunca fue evaluado
        - Han pasado 7+ días desde última evaluación
        - Ha tenido 10+ interacciones desde última evaluación
        """
        if signals.last_evaluated is None:
            return True

        # Asegurar timezone
        last_eval = signals.last_evaluated
        if last_eval.tzinfo is None:
            last_eval = last_eval.replace(tzinfo=UTC)

        days_since = (datetime.now(UTC) - last_eval).days
        if days_since >= REEVALUATION_DAYS:
            return True

        # TODO: Comparar interacciones desde última evaluación
        # Por ahora, re-evaluar si tiene suficientes interacciones
        if signals.total_interactions >= REEVALUATION_INTERACTIONS:
            return True

        return False

    async def _gather_signals(self, user_id: int) -> ArchetypeSignals:
        """
        Recolecta señales de comportamiento del usuario.

        Consulta múltiples tablas para construir el perfil de señales.
        """
        signals = ArchetypeSignals()

        # Obtener datos de gamificación
        try:
            from bot.gamification.database.models import UserGamification, UserStreak

            user_gamif = await self._session.get(UserGamification, user_id)
            if user_gamif:
                signals.total_interactions = user_gamif.besitos_earned or 0

            user_streak = await self._session.get(UserStreak, user_id)
            if user_streak:
                signals.current_streak_days = user_streak.current_streak or 0

        except Exception as e:
            logger.warning(f"Error obteniendo datos de gamificación: {e}")

        # Obtener datos de narrativa
        try:
            from bot.narrative.database import UserDecisionHistory

            # Tiempos de respuesta
            stmt = select(
                func.avg(UserDecisionHistory.response_time_seconds),
                func.count(UserDecisionHistory.id)
            ).where(UserDecisionHistory.user_id == user_id)
            result = await self._session.execute(stmt)
            row = result.one()

            if row[0]:
                signals.avg_response_time_seconds = float(row[0])
                signals.avg_decision_time_seconds = float(row[0])

        except Exception as e:
            logger.warning(f"Error obteniendo datos de narrativa: {e}")

        return signals

    def count_emotional_words(self, text: str) -> int:
        """Cuenta palabras emocionales en un texto."""
        if not text:
            return 0
        words = text.lower().split()
        return sum(1 for word in words if word in EMOTIONAL_WORDS)

    def is_structured_response(self, text: str) -> bool:
        """Detecta si una respuesta es estructurada (usa listas, puntos, etc.)."""
        if not text:
            return False
        indicators = [
            "1.", "2.", "3.",
            "- ", "• ",
            "primero", "segundo", "tercero",
            "por un lado", "por otro lado",
            "en primer lugar", "en segundo lugar"
        ]
        text_lower = text.lower()
        return any(ind in text_lower for ind in indicators)

    def detect_from_narrative_flags(
        self,
        narrative_flags: Dict[str, any]
    ) -> Tuple[Optional[ArchetypeType], float]:
        """
        Detecta arquetipo basándose en flags narrativos del cuestionario Nivel 3.

        Analiza las respuestas del cuestionario de Perfil de Deseo para determinar
        el arquetipo dominante del usuario.

        Args:
            narrative_flags: Diccionario con flags seteados durante el cuestionario
                           (curious, attracted, seeking, visual, verbal, etc.)

        Returns:
            Tupla (arquetipo, confianza)
            - arquetipo: None si no hay suficientes datos
            - confianza: 0.0-1.0

        Flags por arquetipo:
        - EXPLORER: curious + mystery (búsqueda, exploración)
        - ROMANTIC: connection + personal (conexión emocional)
        - ANALYTICAL: understanding + perceptive (comprensión profunda)
        - DIRECT: pleasure + visual (directo, lo que ve)
        - PATIENT: open + cautious (abierto, paciente)
        - PERSISTENT: (fallback si no hay match claro)
        """
        if not narrative_flags:
            logger.debug("No hay flags narrativos para analizar")
            return None, 0.0

        # Contar flags por arquetipo
        archetype_scores: Dict[ArchetypeType, int] = {
            ArchetypeType.EXPLORER: 0,
            ArchetypeType.ROMANTIC: 0,
            ArchetypeType.ANALYTICAL: 0,
            ArchetypeType.DIRECT: 0,
            ArchetypeType.PATIENT: 0,
            ArchetypeType.PERSISTENT: 0,
        }

        # EXPLORER: curious, mystery, seeking (exploración)
        if narrative_flags.get("curious"):
            archetype_scores[ArchetypeType.EXPLORER] += 2
        if narrative_flags.get("mystery"):
            archetype_scores[ArchetypeType.EXPLORER] += 2
        if narrative_flags.get("seeking"):
            archetype_scores[ArchetypeType.EXPLORER] += 1

        # ROMANTIC: connection, personal, attracted (conexión emocional)
        if narrative_flags.get("connection"):
            archetype_scores[ArchetypeType.ROMANTIC] += 2
        if narrative_flags.get("personal"):
            archetype_scores[ArchetypeType.ROMANTIC] += 2
        if narrative_flags.get("attracted"):
            archetype_scores[ArchetypeType.ROMANTIC] += 1

        # ANALYTICAL: understanding, perceptive, verbal (comprensión)
        if narrative_flags.get("understanding"):
            archetype_scores[ArchetypeType.ANALYTICAL] += 2
        if narrative_flags.get("perceptive"):
            archetype_scores[ArchetypeType.ANALYTICAL] += 2
        if narrative_flags.get("verbal"):
            archetype_scores[ArchetypeType.ANALYTICAL] += 1

        # DIRECT: pleasure, visual, surface (directo)
        if narrative_flags.get("pleasure"):
            archetype_scores[ArchetypeType.DIRECT] += 2
        if narrative_flags.get("visual"):
            archetype_scores[ArchetypeType.DIRECT] += 2
        if narrative_flags.get("surface"):
            archetype_scores[ArchetypeType.DIRECT] += 1

        # PATIENT: open, cautious, depth (paciente, reflexivo)
        if narrative_flags.get("open"):
            archetype_scores[ArchetypeType.PATIENT] += 2
        if narrative_flags.get("cautious"):
            archetype_scores[ArchetypeType.PATIENT] += 2
        if narrative_flags.get("depth"):
            archetype_scores[ArchetypeType.PATIENT] += 1

        # PERSISTENT: intuitive (fallback, no específico)
        if narrative_flags.get("intuitive"):
            archetype_scores[ArchetypeType.PERSISTENT] += 1

        # Encontrar mejor match
        best_archetype = None
        best_score = 0

        for archetype, score in archetype_scores.items():
            if score > best_score:
                best_score = score
                best_archetype = archetype

        # Si ninguno tiene score, es PERSISTENT (default)
        if best_score == 0:
            logger.debug("No hay flags suficientes, asignando PERSISTENT como default")
            return ArchetypeType.PERSISTENT, 0.3

        # Calcular confianza (score/max_score_posible)
        # Max score posible es 5 (2+2+1 para un arquetipo)
        confidence = min(best_score / 5.0, 1.0)

        logger.info(
            f"Arquetipo detectado desde flags narrativos: "
            f"{best_archetype.value} (score={best_score}, confidence={confidence:.2f})"
        )
        logger.debug(f"Scores por arquetipo: {archetype_scores}")
        logger.debug(f"Flags analizados: {narrative_flags}")

        return best_archetype, confidence


# ================================================================
# FUNCIONES DE UTILIDAD
# ================================================================

def get_archetype_description(archetype: ArchetypeType) -> str:
    """Retorna descripción del arquetipo para mostrar al usuario."""
    descriptions = {
        ArchetypeType.EXPLORER: (
            "Explorador - Busca cada detalle y quiere ver todo lo que hay detrás de cada puerta."
        ),
        ArchetypeType.DIRECT: (
            "Directo - Va al grano sin rodeos. Sabe lo que quiere y no pierde tiempo."
        ),
        ArchetypeType.ROMANTIC: (
            "Romántico - Busca conexión emocional. Le importa la historia, no solo el resultado."
        ),
        ArchetypeType.ANALYTICAL: (
            "Analítico - Reflexivo y metódico. Estudia, calcula y busca comprensión."
        ),
        ArchetypeType.PERSISTENT: (
            "Persistente - No se rinde ante el primer obstáculo. Vuelve a intentar."
        ),
        ArchetypeType.PATIENT: (
            "Paciente - Toma su tiempo para procesar. No reacciona por impulso."
        ),
    }
    return descriptions.get(archetype, "Arquetipo desconocido")
