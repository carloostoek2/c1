"""
Servicio avanzado de detección de arquetipos.

Expande el sistema básico de arquetipos con detección basada en 20+ métricas
de comportamiento del usuario, generando perfiles de personalidad más precisos.
"""
import logging
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from bot.narrative.database.enums import ArchetypeType

logger = logging.getLogger(__name__)


class AdvancedArchetypeService:
    """Servicio de detección avanzada de arquetipos con múltiples métricas."""

    # Pesos de métricas para cada arquetipo (suma debe ser ~1.0)
    ARCHETYPE_WEIGHTS = {
        "EXPLORER": {
            "content_explored_pct": 0.15,
            "easter_eggs_found": 0.10,
            "avg_time_per_fragment": 0.12,
            "revisits_content": 0.08,
            "uses_journal": 0.05,
        },
        "DIRECT": {
            "decision_speed": 0.15,
            "skips_optional_content": 0.10,
            "prefers_short_sessions": 0.08,
            "quick_responses": 0.12,
        },
        "ROMANTIC": {
            "emotional_response_rate": 0.12,
            "time_on_emotional_fragments": 0.10,
            "revisits_emotional_scenes": 0.10,
            "reaction_to_intimate_content": 0.08,
        },
        "ANALYTICAL": {
            "comprehensive_reading": 0.12,
            "decision_deliberation": 0.10,
            "completes_challenges": 0.10,
            "low_failure_rate": 0.08,
        },
        "PERSISTENT": {
            "retries_challenges": 0.15,
            "completes_difficult_missions": 0.10,
            "comeback_rate": 0.08,
            "streak_recovery": 0.07,
        },
        "PATIENT": {
            "long_session_duration": 0.12,
            "deep_processing_time": 0.10,
            "time_between_actions": 0.08,
            "completion_rate": 0.10,
        },
    }

    # Umbrales mínimos de confianza
    MIN_CONFIDENCE = 0.6
    MIN_DECISIONS_FOR_DETECTION = 5

    def __init__(self, session: AsyncSession):
        """
        Inicializa el servicio.

        Args:
            session: Sesión async de SQLAlchemy
        """
        self.session = session

    async def calculate_archetype_scores(
        self, user_id: int
    ) -> Dict[str, float]:
        """
        Calcula scores para todos los arquetipos basándose en múltiples métricas.

        Args:
            user_id: ID del usuario

        Returns:
            dict: Scores por arquetipo (0.0-1.0)
                {"EXPLORER": 0.75, "ROMANTIC": 0.60, ...}
        """
        # Obtener métricas del usuario
        metrics = await self._collect_user_metrics(user_id)

        # Calcular score para cada arquetipo
        scores = {}

        for archetype, weights in self.ARCHETYPE_WEIGHTS.items():
            score = 0.0
            for metric_name, weight in weights.items():
                metric_value = metrics.get(metric_name, 0.0)
                score += metric_value * weight

            scores[archetype] = min(1.0, max(0.0, score))

        logger.debug(f"Archetype scores for user {user_id}: {scores}")

        return scores

    async def get_dominant_archetype(
        self, user_id: int
    ) -> Tuple[ArchetypeType, float]:
        """
        Obtiene el arquetipo dominante del usuario y su confianza.

        Args:
            user_id: ID del usuario

        Returns:
            Tuple[ArchetypeType, float]: (arquetipo, confianza)
        """
        # Verificar si tiene suficientes datos
        has_sufficient_data = await self._has_sufficient_data(user_id)

        if not has_sufficient_data:
            return ArchetypeType.UNKNOWN, 0.0

        # Calcular scores
        scores = await self.calculate_archetype_scores(user_id)

        # Encontrar el máximo
        max_archetype = max(scores, key=scores.get)
        max_score = scores[max_archetype]

        # Convertir a enum
        archetype_enum = ArchetypeType[max_archetype]

        # Calcular confianza final
        confidence = await self._calculate_confidence(
            user_id, archetype_enum, max_score
        )

        logger.info(
            f"User {user_id} dominant archetype: {archetype_enum.value} (confidence: {confidence:.2f})"
        )

        return archetype_enum, confidence

    async def track_metric(
        self, user_id: int, metric_type: str, value: float
    ) -> None:
        """
        Trackea una métrica específica del usuario.

        Nota: En producción, esto debería almacenarse en una tabla
        dedicada (UserBehaviorMetrics). Por ahora, lo logging es suficiente.

        Args:
            user_id: ID del usuario
            metric_type: Tipo de métrica
            value: Valor de la métrica (0.0-1.0)
        """
        logger.debug(f"Metric tracked: user={user_id}, type={metric_type}, value={value}")
        # TODO: Almacenar en tabla UserBehaviorMetrics cuando se implemente

    async def get_archetype_profile(self, user_id: int) -> Dict:
        """
        Obtiene el perfil completo de arquetipos del usuario.

        Args:
            user_id: ID del usuario

        Returns:
            dict: Perfil completo
                - dominant: Arquetipo dominante
                - confidence: Confianza del arquetipo dominante
                - scores: Scores de todos los arquetipos
                - secondary: Segundo arquetipo más fuerte
                - metrics: Métricas recolectadas
        """
        scores = await self.calculate_archetype_scores(user_id)
        dominant, confidence = await self.get_dominant_archetype(user_id)

        # Encontrar segundo arquetipo
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        secondary = sorted_scores[1][0] if len(sorted_scores) > 1 else None

        metrics = await self._collect_user_metrics(user_id)

        return {
            "dominant": dominant.value,
            "confidence": confidence,
            "scores": scores,
            "secondary": secondary,
            "metrics": metrics,
        }

    async def should_recalculate(self, user_id: int) -> bool:
        """
        Determina si se debe recalcular el arquetipo del usuario.

        Recalcula si:
        - No tiene arquetipo asignado
        - Han pasado 7+ días desde última detección
        - Tiene 10+ nuevas decisiones desde última detección

        Args:
            user_id: ID del usuario

        Returns:
            bool: True si debe recalcular
        """
        # Obtener progreso narrativo del usuario
        from bot.narrative.services.progress import ProgressService

        progress_service = ProgressService(self.session)
        progress = await progress_service.get_or_create_progress(user_id)

        # Sin arquetipo detectado
        if not progress.detected_archetype:
            return True

        # Última actualización hace más de 7 días
        if progress.archetype_updated_at:
            days_since_update = (
                datetime.utcnow() - progress.archetype_updated_at
            ).days
            if days_since_update >= 7:
                return True

        # Decisiones significativas desde última actualización
        # (esto requeriría tracking de cuándo fue la última actualización)
        # Por simplicidad, siempre permitir recalculo después de 10 decisiones totales
        if progress.total_decisions >= 10:
            return True

        return False

    # ========================================
    # MÉTODOS PRIVADOS
    # ========================================

    async def _collect_user_metrics(self, user_id: int) -> Dict[str, float]:
        """
        Recopila todas las métricas relevantes del usuario.

        Returns:
            dict: Métricas normalizadas (0.0-1.0)
        """
        from bot.narrative.services.progress import ProgressService
        from bot.narrative.services.engagement import EngagementService
        from bot.narrative.services.decision import DecisionService
        from bot.gamification.services.mission import MissionService
        from bot.gamification.services.user_gamification import (
            UserGamificationService,
        )

        metrics = {}

        # Inicializar servicios
        progress_service = ProgressService(self.session)
        engagement_service = EngagementService(self.session)

        # Obtener datos base
        progress = await progress_service.get_or_create_progress(user_id)
        engagement_stats = await engagement_service.get_user_engagement_stats(
            user_id
        )

        # ========================================
        # MÉTRICAS EXPLORER
        # ========================================

        # Content explored percentage
        total_fragments = engagement_stats.get("total_fragments_visited", 0)
        metrics["content_explored_pct"] = min(1.0, total_fragments / 50.0)

        # Easter eggs found (placeholder - requiere tabla específica)
        metrics["easter_eggs_found"] = 0.0

        # Avg time per fragment
        avg_time = engagement_stats.get("avg_time_per_fragment", 0)
        metrics["avg_time_per_fragment"] = min(1.0, avg_time / 120.0)

        # Revisits content
        total_visits = engagement_stats.get("total_visits", 0)
        revisit_rate = (
            (total_visits - total_fragments) / total_visits
            if total_visits > 0
            else 0
        )
        metrics["revisits_content"] = revisit_rate

        # Uses journal (placeholder)
        metrics["uses_journal"] = 0.0

        # ========================================
        # MÉTRICAS DIRECT
        # ========================================

        # Decision speed (basado en tiempo de respuesta promedio)
        from bot.narrative.database.models import UserDecisionHistory

        stmt = select(
            func.avg(UserDecisionHistory.response_time_seconds)
        ).where(UserDecisionHistory.user_id == user_id)
        result = await self.session.execute(stmt)
        avg_response_time = result.scalar_one_or_none() or 30.0

        # Más rápido = más DIRECT (< 10s = 1.0, > 30s = 0.0)
        metrics["decision_speed"] = max(0.0, 1.0 - (avg_response_time / 30.0))

        # Prefers short sessions
        total_reading_time = engagement_stats.get("total_reading_time", 0)
        avg_session_time = (
            total_reading_time / total_fragments if total_fragments > 0 else 0
        )
        metrics["prefers_short_sessions"] = (
            1.0 if avg_session_time < 300 else 0.5
        )

        # Quick responses
        metrics["quick_responses"] = metrics["decision_speed"]

        # Skips optional content (placeholder)
        metrics["skips_optional_content"] = 0.0

        # ========================================
        # MÉTRICAS ROMANTIC
        # ========================================

        # Emotional response rate (placeholder - requiere análisis de texto)
        metrics["emotional_response_rate"] = 0.0
        metrics["time_on_emotional_fragments"] = 0.0
        metrics["revisits_emotional_scenes"] = 0.0
        metrics["reaction_to_intimate_content"] = 0.0

        # ========================================
        # MÉTRICAS ANALYTICAL
        # ========================================

        # Comprehensive reading
        metrics["comprehensive_reading"] = min(
            1.0, avg_time / 90.0
        )  # > 90s = completo

        # Decision deliberation
        metrics["decision_deliberation"] = (
            1.0 if avg_response_time > 20 else 0.5
        )

        # Completes challenges (placeholder)
        metrics["completes_challenges"] = 0.0
        metrics["low_failure_rate"] = 0.0

        # ========================================
        # MÉTRICAS PERSISTENT
        # ========================================

        # Retries challenges (placeholder)
        metrics["retries_challenges"] = 0.0

        # Completes difficult missions (placeholder)
        metrics["completes_difficult_missions"] = 0.0

        # Comeback rate (placeholder - requiere tracking de abandonos)
        metrics["comeback_rate"] = 0.0

        # Streak recovery (placeholder)
        metrics["streak_recovery"] = 0.0

        # ========================================
        # MÉTRICAS PATIENT
        # ========================================

        # Long session duration
        metrics["long_session_duration"] = (
            1.0 if avg_session_time > 600 else 0.5
        )

        # Deep processing time
        metrics["deep_processing_time"] = min(1.0, avg_time / 120.0)

        # Time between actions (placeholder)
        metrics["time_between_actions"] = 0.5

        # Completion rate
        chapters_completed = progress.chapters_completed or 0
        metrics["completion_rate"] = min(1.0, chapters_completed / 3.0)

        return metrics

    async def _has_sufficient_data(self, user_id: int) -> bool:
        """Verifica si el usuario tiene suficientes datos para detección."""
        from bot.narrative.services.progress import ProgressService

        progress_service = ProgressService(self.session)
        progress = await progress_service.get_or_create_progress(user_id)

        return progress.total_decisions >= self.MIN_DECISIONS_FOR_DETECTION

    async def _calculate_confidence(
        self, user_id: int, archetype: ArchetypeType, raw_score: float
    ) -> float:
        """
        Calcula la confianza del arquetipo detectado.

        Args:
            user_id: ID del usuario
            archetype: Arquetipo detectado
            raw_score: Score bruto del arquetipo

        Returns:
            float: Confianza (0.0-1.0)
        """
        from bot.narrative.services.progress import ProgressService

        progress_service = ProgressService(self.session)
        progress = await progress_service.get_or_create_progress(user_id)

        # Factor 1: Score base
        confidence = raw_score

        # Factor 2: Cantidad de decisiones (más datos = más confianza)
        decisions_factor = min(1.0, progress.total_decisions / 20.0)
        confidence *= decisions_factor

        # Factor 3: Separación con segundo arquetipo
        # (si el score del dominante está muy cerca del segundo, baja confianza)
        # TODO: Implementar si es necesario

        return min(1.0, max(0.0, confidence))
