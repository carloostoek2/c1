"""
Servicio de detección de arquetipos basado en comportamiento.

Este servicio analiza las señales de comportamiento del usuario
y determina su arquetipo usando un algoritmo de scoring ponderado.
Lucien "observa" estos patrones para clasificar al usuario.

Arquetipos detectables:
    - EXPLORER: Curiosidad insaciable
    - DIRECT: Eficiencia y rapidez
    - ROMANTIC: Conexión emocional
    - ANALYTICAL: Precisión lógica
    - PERSISTENT: Tenacidad
    - PATIENT: Calma y constancia
"""

import logging
from dataclasses import dataclass
from datetime import datetime, UTC, timedelta
from typing import Optional, Dict, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.enums import ArchetypeType
from bot.database.models import User
from bot.gamification.database.models import UserBehaviorSignals

logger = logging.getLogger(__name__)


# ========================================
# CONFIGURACIÓN
# ========================================

# Umbrales de detección
MIN_INTERACTIONS_FOR_DETECTION = 20
MIN_CONFIDENCE_THRESHOLD = 0.35

# Re-evaluación
REEVALUATION_DAYS = 7
REEVALUATION_INTERACTIONS = 50

# Versión del algoritmo (incrementar al cambiar fórmulas)
ALGORITHM_VERSION = 1


@dataclass
class ArchetypeResult:
    """Resultado de la detección de arquetipo."""

    archetype: Optional[ArchetypeType]
    confidence: float
    scores: Dict[str, float]
    reason: str

    @property
    def is_detected(self) -> bool:
        """Retorna True si se detectó un arquetipo."""
        return self.archetype is not None


@dataclass
class ArchetypeInsights:
    """Información detallada del arquetipo para UI."""

    current_archetype: Optional[ArchetypeType]
    confidence: float
    top_archetypes: list  # [(ArchetypeType, score), ...]
    key_behaviors: list  # Comportamientos que más influyen
    detected_at: Optional[datetime]
    total_interactions: int


class ArchetypeDetectionService:
    """
    Servicio de detección automática de arquetipos.

    Analiza las señales de comportamiento del usuario y determina
    su arquetipo dominante usando un algoritmo de scoring ponderado.

    Attributes:
        session: Sesión async de SQLAlchemy

    Métodos principales:
        detect_archetype: Ejecuta detección completa
        get_archetype: Consulta arquetipo actual (sin recalcular)
        should_reevaluate: Determina si es momento de re-evaluar
        force_reevaluation: Fuerza re-evaluación
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el servicio.

        Args:
            session: Sesión async de SQLAlchemy
        """
        self._session = session

    # ========================================
    # FUNCIÓN DE NORMALIZACIÓN
    # ========================================

    @staticmethod
    def normalize(value: float, min_val: float, max_val: float) -> float:
        """
        Normaliza un valor al rango 0-1.

        Args:
            value: Valor a normalizar
            min_val: Valor mínimo del rango
            max_val: Valor máximo del rango

        Returns:
            Valor normalizado entre 0.0 y 1.0

        Examples:
            >>> ArchetypeDetectionService.normalize(50, 0, 100)
            0.5
            >>> ArchetypeDetectionService.normalize(150, 0, 100)
            1.0
            >>> ArchetypeDetectionService.normalize(-10, 0, 100)
            0.0
        """
        if value <= min_val:
            return 0.0
        if value >= max_val:
            return 1.0
        return (value - min_val) / (max_val - min_val)

    # ========================================
    # CÁLCULO DE SCORES POR ARQUETIPO
    # ========================================

    def _calculate_explorer_score(self, signals: UserBehaviorSignals) -> float:
        """
        Calcula score para arquetipo EXPLORER.

        Comportamientos característicos:
        - Alta tasa de completación de contenido
        - Encuentra easter eggs
        - Tiempo alto en contenido (lee todo)
        - Revisita contenido antiguo
        - Visita múltiples secciones
        """
        score = (
            (signals.content_completion_rate * 0.25) +
            (self.normalize(signals.easter_eggs_found, 0, 10) * 0.20) +
            (self.normalize(signals.avg_time_on_content, 20, 120) * 0.20) +
            (self.normalize(signals.revisits_old_content, 0, 20) * 0.15) +
            (self.normalize(signals.content_sections_visited, 0, 20) * 0.20)
        )
        return min(1.0, score)

    def _calculate_direct_score(self, signals: UserBehaviorSignals) -> float:
        """
        Calcula score para arquetipo DIRECT.

        Comportamientos característicos:
        - Tiempo de respuesta rápido
        - Respuestas cortas
        - Usa botones más que texto
        - Decisiones rápidas
        - Muchas acciones por sesión
        """
        # Invertir normalizaciones (menos tiempo/longitud = más directo)
        score = (
            (1 - self.normalize(signals.avg_response_time, 5, 60)) * 0.25 +
            (1 - self.normalize(signals.avg_response_length, 5, 50)) * 0.20 +
            (signals.button_vs_text_ratio * 0.25) +
            (1 - self.normalize(signals.avg_decision_time, 3, 30)) * 0.15 +
            (self.normalize(signals.actions_per_session, 5, 20) * 0.15)
        )
        return min(1.0, max(0.0, score))

    def _calculate_romantic_score(self, signals: UserBehaviorSignals) -> float:
        """
        Calcula score para arquetipo ROMANTIC.

        Comportamientos característicos:
        - Usa palabras emocionales
        - Respuestas largas
        - Preguntas personales sobre Diana
        - Alto promedio de palabras por respuesta
        """
        score = (
            (self.normalize(signals.emotional_words_count, 0, 50) * 0.25) +
            (self.normalize(signals.long_responses_count, 0, 20) * 0.20) +
            (self.normalize(signals.personal_questions_about_diana, 0, 10) * 0.25) +
            (self.normalize(signals.avg_response_length, 20, 100) * 0.15) +
            (self.normalize(signals.question_count, 0, 30) * 0.15)
        )
        return min(1.0, score)

    def _calculate_analytical_score(self, signals: UserBehaviorSignals) -> float:
        """
        Calcula score para arquetipo ANALYTICAL.

        Comportamientos característicos:
        - Alto score en evaluaciones
        - Hace preguntas
        - Respuestas estructuradas
        - Reporta errores
        """
        score = (
            (signals.quiz_avg_score / 100 * 0.30) +
            (self.normalize(signals.question_count, 0, 30) * 0.20) +
            (self.normalize(signals.structured_responses, 0, 15) * 0.20) +
            (self.normalize(signals.error_reports, 0, 5) * 0.10) +
            # Bonus por combinar preguntas con estructura
            (0.20 if signals.structured_responses > 5 and signals.question_count > 10 else 0.10)
        )
        return min(1.0, score)

    def _calculate_persistent_score(self, signals: UserBehaviorSignals) -> float:
        """
        Calcula score para arquetipo PERSISTENT.

        Comportamientos característicos:
        - Regresa después de inactividad
        - Reintenta acciones fallidas
        - Completa flujos abandonados
        - Antigüedad de cuenta
        """
        # Factor de antigüedad basado en primera interacción
        account_age_factor = 0.0
        if signals.first_interaction_at:
            days_old = (datetime.now(UTC) - signals.first_interaction_at).days
            account_age_factor = self.normalize(days_old, 0, 90)

        score = (
            (self.normalize(signals.return_after_inactivity, 0, 5) * 0.30) +
            (self.normalize(signals.retry_failed_actions, 0, 10) * 0.25) +
            (self.normalize(signals.incomplete_flows_completed, 0, 5) * 0.25) +
            (account_age_factor * 0.20)
        )
        return min(1.0, score)

    def _calculate_patient_score(self, signals: UserBehaviorSignals) -> float:
        """
        Calcula score para arquetipo PATIENT.

        Comportamientos característicos:
        - Tiempo de respuesta >30 segundos
        - No usa opciones de skip
        - Rachas largas y consistentes
        - Sesiones regulares
        """
        # Bonus por no usar skip
        skip_bonus = 1 - self.normalize(signals.skip_actions_used, 0, 10)

        score = (
            (self.normalize(signals.avg_response_time, 30, 120) * 0.20) +
            (skip_bonus * 0.20) +
            (self.normalize(signals.current_streak, 7, 60) * 0.25) +
            (self.normalize(signals.best_streak, 7, 100) * 0.15) +
            (self.normalize(signals.avg_session_duration, 300, 1800) * 0.20)
        )
        return min(1.0, score)

    def _calculate_all_scores(
        self,
        signals: UserBehaviorSignals
    ) -> Dict[str, float]:
        """
        Calcula scores para todos los arquetipos.

        Args:
            signals: Señales de comportamiento del usuario

        Returns:
            Dict con scores por arquetipo
        """
        return {
            ArchetypeType.EXPLORER.value: self._calculate_explorer_score(signals),
            ArchetypeType.DIRECT.value: self._calculate_direct_score(signals),
            ArchetypeType.ROMANTIC.value: self._calculate_romantic_score(signals),
            ArchetypeType.ANALYTICAL.value: self._calculate_analytical_score(signals),
            ArchetypeType.PERSISTENT.value: self._calculate_persistent_score(signals),
            ArchetypeType.PATIENT.value: self._calculate_patient_score(signals),
        }

    # ========================================
    # DETECCIÓN PRINCIPAL
    # ========================================

    async def detect_archetype(self, user_id: int) -> ArchetypeResult:
        """
        Ejecuta detección completa de arquetipo.

        Analiza las señales de comportamiento y determina el arquetipo
        dominante. Actualiza el campo archetype en el usuario si
        se detecta con suficiente confianza.

        Args:
            user_id: ID del usuario

        Returns:
            ArchetypeResult con el resultado de la detección

        Examples:
            >>> result = await service.detect_archetype(123)
            >>> if result.is_detected:
            ...     print(f"Arquetipo: {result.archetype.display_name}")
        """
        try:
            # Obtener señales
            signals = await self._get_signals(user_id)

            if signals is None:
                return ArchetypeResult(
                    archetype=None,
                    confidence=0.0,
                    scores={},
                    reason="no_signals"
                )

            # Verificar mínimo de interacciones
            if signals.total_interactions < MIN_INTERACTIONS_FOR_DETECTION:
                return ArchetypeResult(
                    archetype=None,
                    confidence=0.0,
                    scores={},
                    reason="insufficient_data"
                )

            # Calcular scores
            scores = self._calculate_all_scores(signals)

            # Ordenar por score
            sorted_scores = sorted(
                scores.items(),
                key=lambda x: x[1],
                reverse=True
            )

            top_archetype_value = sorted_scores[0][0]
            top_score = sorted_scores[0][1]
            second_score = sorted_scores[1][1]

            # Calcular confianza (diferencia con segundo + bonus por score alto)
            confidence = top_score - second_score + (top_score * 0.3)
            confidence = min(confidence, 1.0)

            # Verificar umbral de confianza
            if confidence < MIN_CONFIDENCE_THRESHOLD:
                return ArchetypeResult(
                    archetype=None,
                    confidence=confidence,
                    scores=scores,
                    reason="low_confidence"
                )

            # Convertir a enum
            top_archetype = ArchetypeType(top_archetype_value)

            # Guardar en usuario
            await self._save_archetype(
                user_id=user_id,
                archetype=top_archetype,
                confidence=confidence,
                scores=scores
            )

            logger.info(
                f"Detected archetype {top_archetype.value} for user {user_id} "
                f"with confidence {confidence:.2f}"
            )

            return ArchetypeResult(
                archetype=top_archetype,
                confidence=confidence,
                scores=scores,
                reason="detected"
            )

        except Exception as e:
            logger.error(f"Error detecting archetype for user {user_id}: {e}")
            raise

    async def _get_signals(self, user_id: int) -> Optional[UserBehaviorSignals]:
        """Obtiene señales de comportamiento del usuario."""
        result = await self._session.execute(
            select(UserBehaviorSignals).where(
                UserBehaviorSignals.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def _save_archetype(
        self,
        user_id: int,
        archetype: ArchetypeType,
        confidence: float,
        scores: Dict[str, float]
    ) -> None:
        """Guarda el arquetipo detectado en el usuario."""
        result = await self._session.execute(
            select(User).where(User.user_id == user_id)
        )
        user = result.scalar_one_or_none()

        if user:
            user.archetype = archetype
            user.archetype_confidence = confidence
            user.archetype_scores = scores
            user.archetype_detected_at = datetime.now(UTC)
            user.archetype_version = ALGORITHM_VERSION
            await self._session.commit()

    # ========================================
    # CONSULTAS
    # ========================================

    async def get_archetype(self, user_id: int) -> Optional[ArchetypeType]:
        """
        Retorna arquetipo actual del usuario (sin recalcular).

        Args:
            user_id: ID del usuario

        Returns:
            ArchetypeType o None si no hay arquetipo asignado
        """
        result = await self._session.execute(
            select(User.archetype).where(User.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_archetype_scores(self, user_id: int) -> Dict[str, float]:
        """
        Retorna scores de todos los arquetipos.

        Args:
            user_id: ID del usuario

        Returns:
            Dict con scores o dict vacío si no hay datos
        """
        result = await self._session.execute(
            select(User.archetype_scores).where(User.user_id == user_id)
        )
        scores = result.scalar_one_or_none()
        return scores or {}

    async def get_archetype_insights(self, user_id: int) -> ArchetypeInsights:
        """
        Retorna información detallada del arquetipo para UI.

        Args:
            user_id: ID del usuario

        Returns:
            ArchetypeInsights con información detallada
        """
        # Obtener usuario
        result = await self._session.execute(
            select(User).where(User.user_id == user_id)
        )
        user = result.scalar_one_or_none()

        # Obtener señales
        signals = await self._get_signals(user_id)
        total_interactions = signals.total_interactions if signals else 0

        if not user or not user.archetype_scores:
            return ArchetypeInsights(
                current_archetype=None,
                confidence=0.0,
                top_archetypes=[],
                key_behaviors=[],
                detected_at=None,
                total_interactions=total_interactions
            )

        # Top 3 arquetipos
        sorted_scores = sorted(
            user.archetype_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]

        top_archetypes = [
            (ArchetypeType(k), v) for k, v in sorted_scores
        ]

        # Comportamientos clave según arquetipo
        key_behaviors = self._get_key_behaviors(
            user.archetype,
            signals
        ) if signals and user.archetype else []

        return ArchetypeInsights(
            current_archetype=user.archetype,
            confidence=user.archetype_confidence or 0.0,
            top_archetypes=top_archetypes,
            key_behaviors=key_behaviors,
            detected_at=user.archetype_detected_at,
            total_interactions=total_interactions
        )

    def _get_key_behaviors(
        self,
        archetype: Optional[ArchetypeType],
        signals: UserBehaviorSignals
    ) -> list:
        """Retorna comportamientos clave según arquetipo."""
        if not archetype:
            return []

        behaviors = []

        if archetype == ArchetypeType.EXPLORER:
            if signals.easter_eggs_found > 0:
                behaviors.append(f"🔍 {signals.easter_eggs_found} easter eggs encontrados")
            if signals.revisits_old_content > 5:
                behaviors.append(f"📚 Revisita contenido frecuentemente")
            if signals.content_completion_rate > 0.5:
                behaviors.append(f"✅ {signals.content_completion_rate*100:.0f}% contenido explorado")

        elif archetype == ArchetypeType.DIRECT:
            if signals.avg_response_time < 10:
                behaviors.append(f"⚡ Respuestas rápidas ({signals.avg_response_time:.1f}s)")
            if signals.button_vs_text_ratio > 0.7:
                behaviors.append(f"🔘 Prefiere botones sobre texto")
            if signals.avg_response_length < 10:
                behaviors.append(f"✂️ Respuestas concisas")

        elif archetype == ArchetypeType.ROMANTIC:
            if signals.emotional_words_count > 10:
                behaviors.append(f"💝 Lenguaje emocional frecuente")
            if signals.long_responses_count > 5:
                behaviors.append(f"📝 Escribe respuestas elaboradas")
            if signals.personal_questions_about_diana > 2:
                behaviors.append(f"💭 Interés personal en Diana")

        elif archetype == ArchetypeType.ANALYTICAL:
            if signals.quiz_avg_score > 70:
                behaviors.append(f"🧠 Alto rendimiento en evaluaciones ({signals.quiz_avg_score:.0f}%)")
            if signals.structured_responses > 5:
                behaviors.append(f"📋 Respuestas estructuradas")
            if signals.question_count > 15:
                behaviors.append(f"❓ Muchas preguntas ({signals.question_count})")

        elif archetype == ArchetypeType.PERSISTENT:
            if signals.return_after_inactivity > 2:
                behaviors.append(f"🔄 Siempre regresa ({signals.return_after_inactivity} veces)")
            if signals.retry_failed_actions > 3:
                behaviors.append(f"💪 Reintenta acciones fallidas")
            if signals.incomplete_flows_completed > 0:
                behaviors.append(f"✅ Completa lo que empieza")

        elif archetype == ArchetypeType.PATIENT:
            if signals.current_streak > 7:
                behaviors.append(f"⏳ Racha de {signals.current_streak} días")
            if signals.skip_actions_used < 3:
                behaviors.append(f"🧘 Raramente usa 'saltar'")
            if signals.avg_response_time > 30:
                behaviors.append(f"⌛ Se toma su tiempo para responder")

        return behaviors[:3]  # Máximo 3 comportamientos

    # ========================================
    # RE-EVALUACIÓN
    # ========================================

    async def should_reevaluate(self, user_id: int) -> bool:
        """
        Determina si es momento de re-evaluar el arquetipo.

        Condiciones para re-evaluar:
        - Han pasado 7+ días desde última detección
        - Usuario ha tenido 50+ interacciones nuevas
        - Confianza actual < 0.5 y hay nuevos datos

        Args:
            user_id: ID del usuario

        Returns:
            True si debe re-evaluarse
        """
        result = await self._session.execute(
            select(User).where(User.user_id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            return False

        # Si no tiene arquetipo, evaluar
        if not user.archetype:
            return True

        # Si no tiene fecha de detección, evaluar
        if not user.archetype_detected_at:
            return True

        # Si cambió versión del algoritmo, evaluar
        if user.archetype_version != ALGORITHM_VERSION:
            return True

        # Si pasaron 7+ días
        days_since = (datetime.now(UTC) - user.archetype_detected_at).days
        if days_since >= REEVALUATION_DAYS:
            return True

        # Si confianza es baja y hay nuevas interacciones
        if user.archetype_confidence and user.archetype_confidence < 0.5:
            signals = await self._get_signals(user_id)
            if signals and signals.total_interactions >= REEVALUATION_INTERACTIONS:
                return True

        return False

    async def force_reevaluation(self, user_id: int) -> ArchetypeResult:
        """
        Fuerza re-evaluación del arquetipo ignorando caché.

        Útil para debugging o cuando el admin quiere actualizar
        manualmente la clasificación.

        Args:
            user_id: ID del usuario

        Returns:
            ArchetypeResult con nuevo resultado
        """
        logger.info(f"Forcing archetype reevaluation for user {user_id}")
        return await self.detect_archetype(user_id)

    # ========================================
    # UTILIDADES ADMIN
    # ========================================

    async def get_archetype_distribution(self) -> Dict[str, int]:
        """
        Retorna distribución de arquetipos entre todos los usuarios.

        Returns:
            Dict con conteo por arquetipo
        """
        from sqlalchemy import func

        result = await self._session.execute(
            select(
                User.archetype,
                func.count(User.user_id)
            ).where(
                User.archetype.isnot(None)
            ).group_by(User.archetype)
        )

        distribution = {
            ArchetypeType.EXPLORER.value: 0,
            ArchetypeType.DIRECT.value: 0,
            ArchetypeType.ROMANTIC.value: 0,
            ArchetypeType.ANALYTICAL.value: 0,
            ArchetypeType.PERSISTENT.value: 0,
            ArchetypeType.PATIENT.value: 0,
        }

        for archetype, count in result:
            if archetype:
                distribution[archetype.value] = count

        return distribution

    async def get_unclassified_count(self) -> int:
        """Retorna cantidad de usuarios sin arquetipo."""
        from sqlalchemy import func

        result = await self._session.execute(
            select(func.count(User.user_id)).where(
                User.archetype.is_(None)
            )
        )
        return result.scalar() or 0
