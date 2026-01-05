"""
Servicio avanzado de detección de arquetipos.

Expande el sistema básico de arquetipos con detección basada en métricas
de comportamiento observable del usuario (clicks, tiempos, decisiones).

IMPORTANTE: Este algoritmo NO usa análisis de texto de mensajes del usuario.
Todas las métricas se basan en interacciones medibles (botones, tiempos, patrones).
"""
import logging
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from bot.narrative.database.enums import ArchetypeType

logger = logging.getLogger(__name__)


class AdvancedArchetypeService:
    """Servicio de detección avanzada de arquetipos con métricas observables."""

    # Pesos de métricas para cada arquetipo
    # Solo incluye métricas VIABLES (sin análisis de texto)
    ARCHETYPE_WEIGHTS = {
        "EXPLORER": {
            "content_explored_pct": 0.25,      # % de fragmentos visitados
            "revisit_rate": 0.15,              # Cuánto revisita contenido
            "avg_time_per_fragment": 0.15,    # Tiempo de lectura
            "variety_in_decisions": 0.20,     # Diversidad de elecciones
            "hidden_content_found": 0.15,     # Fragmentos opcionales encontrados
            "completion_thoroughness": 0.10,  # Completa todo antes de avanzar
        },
        "DIRECT": {
            "decision_speed": 0.30,           # Velocidad de decisiones
            "low_revisit_rate": 0.20,         # NO revisita (inverso)
            "short_sessions": 0.20,           # Sesiones cortas
            "linear_progression": 0.15,       # Avanza linealmente
            "skip_optional_rate": 0.15,       # Salta contenido opcional
        },
        "ROMANTIC": {
            "time_on_intimate_fragments": 0.25,  # Tiempo en fragmentos íntimos
            "revisit_intimate_scenes": 0.25,     # Revisita contenido emocional
            "reaction_to_emotional": 0.20,       # Reacciona a contenido emocional
            "slow_deliberation": 0.15,           # Toma tiempo en decisiones íntimas
            "completion_of_emotional_arcs": 0.15, # Completa arcos emocionales
        },
        "ANALYTICAL": {
            "comprehensive_reading": 0.25,    # Lee todo (tiempo alto)
            "decision_deliberation": 0.20,    # Toma tiempo en decisiones
            "challenge_success_rate": 0.20,   # Alta tasa de éxito en challenges
            "low_hint_usage": 0.15,           # No usa hints
            "systematic_exploration": 0.20,   # Explora ordenadamente
        },
        "PERSISTENT": {
            "challenge_retry_rate": 0.30,     # Reintenta challenges fallidos
            "comeback_after_abandonment": 0.25, # Vuelve después de inactividad
            "streak_recovery_rate": 0.20,     # Recupera streaks rotos
            "mission_completion_rate": 0.15,  # Completa misiones difíciles
            "never_gives_up": 0.10,           # No abandona fragmentos
        },
        "PATIENT": {
            "long_session_duration": 0.25,    # Sesiones largas
            "deep_processing_time": 0.20,     # Tiempo alto por fragmento
            "time_between_actions": 0.15,     # Pausas entre acciones
            "high_completion_rate": 0.20,     # Completa lo que empieza
            "low_abandonment_rate": 0.20,     # No abandona contenido
        },
    }

    # Umbrales
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
        Calcula scores para todos los arquetipos basándose en métricas observables.

        Args:
            user_id: ID del usuario

        Returns:
            dict: Scores por arquetipo (0.0-1.0)
        """
        # Obtener métricas del usuario
        metrics = await self._collect_user_metrics(user_id)

        # Calcular score para cada arquetipo
        scores = {}

        for archetype, weights in self.ARCHETYPE_WEIGHTS.items():
            score = 0.0
            total_weight = 0.0  # Para normalizar si faltan métricas

            for metric_name, weight in weights.items():
                if metric_name in metrics:
                    metric_value = metrics[metric_name]
                    score += metric_value * weight
                    total_weight += weight

            # Normalizar score si algunas métricas no están disponibles
            if total_weight > 0:
                score = score / total_weight

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

        Args:
            user_id: ID del usuario

        Returns:
            bool: True si debe recalcular
        """
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

        # 10+ nuevas decisiones
        if progress.total_decisions >= 10:
            return True

        return False

    # ========================================
    # MÉTODOS PRIVADOS - RECOLECCIÓN DE MÉTRICAS
    # ========================================

    async def _collect_user_metrics(self, user_id: int) -> Dict[str, float]:
        """
        Recopila SOLO métricas viables basadas en datos observables.

        Returns:
            dict: Métricas normalizadas (0.0-1.0)
        """
        from bot.narrative.services.progress import ProgressService
        from bot.narrative.services.engagement import EngagementService
        from bot.narrative.database.models import UserDecisionHistory
        from bot.narrative.database.models_immersive import (
            UserChallengeAttempt,
            FragmentChallenge,
        )
        from bot.gamification.database.models import UserStreak

        metrics = {}

        # Servicios
        progress_service = ProgressService(self.session)
        engagement_service = EngagementService(self.session)

        # Datos base
        progress = await progress_service.get_or_create_progress(user_id)
        engagement_stats = await engagement_service.get_user_engagement_stats(user_id)

        # ========================================
        # MÉTRICAS EXPLORER
        # ========================================

        # Content explored percentage (fragmentos únicos / estimado total)
        total_fragments = engagement_stats.get("total_fragments_visited", 0)
        metrics["content_explored_pct"] = min(1.0, total_fragments / 50.0)

        # Revisit rate (cuánto revisita contenido)
        total_visits = engagement_stats.get("total_visits", 0)
        revisit_rate = (
            (total_visits - total_fragments) / total_visits
            if total_visits > 0
            else 0
        )
        metrics["revisit_rate"] = revisit_rate

        # Avg time per fragment (tiempo promedio de lectura)
        avg_time = engagement_stats.get("avg_time_per_fragment", 0)
        metrics["avg_time_per_fragment"] = min(1.0, avg_time / 120.0)

        # Variety in decisions (diversidad de elecciones)
        # Calculado como: decisiones únicas / fragmentos visitados
        stmt = select(func.count(func.distinct(UserDecisionHistory.decision_id))).where(
            UserDecisionHistory.user_id == user_id
        )
        result = await self.session.execute(stmt)
        unique_decisions = result.scalar_one()
        variety = (
            unique_decisions / total_fragments if total_fragments > 0 else 0
        )
        metrics["variety_in_decisions"] = min(1.0, variety * 2)  # Escalar

        # Hidden content found (fragmentos no-entry point visitados)
        # TODO: Requiere campo is_optional en fragmentos
        metrics["hidden_content_found"] = 0.5  # Placeholder medio

        # Completion thoroughness
        chapters_completed = progress.chapters_completed or 0
        metrics["completion_thoroughness"] = min(1.0, chapters_completed / 3.0)

        # ========================================
        # MÉTRICAS DIRECT
        # ========================================

        # Decision speed (velocidad promedio)
        stmt = select(func.avg(UserDecisionHistory.response_time_seconds)).where(
            UserDecisionHistory.user_id == user_id
        )
        result = await self.session.execute(stmt)
        avg_response_time = result.scalar_one_or_none() or 30.0

        # < 10s = 1.0, > 30s = 0.0
        metrics["decision_speed"] = max(0.0, 1.0 - (avg_response_time / 30.0))

        # Low revisit rate (inverso de revisit_rate)
        metrics["low_revisit_rate"] = 1.0 - revisit_rate

        # Short sessions (sesiones < 5 min)
        total_reading_time = engagement_stats.get("total_reading_time", 0)
        avg_session_time = (
            total_reading_time / total_fragments if total_fragments > 0 else 0
        )
        metrics["short_sessions"] = 1.0 if avg_session_time < 300 else 0.3

        # Linear progression (fragmentos visitados en orden)
        # TODO: Requiere análisis de secuencia de visitas
        metrics["linear_progression"] = 0.5  # Placeholder medio

        # Skip optional rate
        # TODO: Requiere tracking de fragmentos opcionales omitidos
        metrics["skip_optional_rate"] = 0.5  # Placeholder medio

        # ========================================
        # MÉTRICAS ROMANTIC
        # ========================================

        # Time on intimate fragments
        # Requiere metadata: fragment.tags contiene "intimate" o "emotional"
        # Por ahora, aproximar con fragmentos que tienen tiempo alto de lectura
        most_revisited = engagement_stats.get("most_revisited")
        if most_revisited and most_revisited["visit_count"] >= 3:
            # Si revisita mucho UN fragmento, podría ser emocional para él
            metrics["time_on_intimate_fragments"] = 0.7
        else:
            metrics["time_on_intimate_fragments"] = 0.3

        # Revisit intimate scenes (similar lógica)
        metrics["revisit_intimate_scenes"] = (
            0.8 if revisit_rate > 0.3 else 0.2
        )

        # Reaction to emotional (basado en custom reactions)
        # TODO: Implementar cuando se agregue metadata a fragmentos
        metrics["reaction_to_emotional"] = 0.5  # Placeholder

        # Slow deliberation on intimate decisions
        metrics["slow_deliberation"] = (
            1.0 if avg_response_time > 25 else 0.4
        )

        # Completion of emotional arcs
        metrics["completion_of_emotional_arcs"] = (
            0.8 if chapters_completed >= 2 else 0.3
        )

        # ========================================
        # MÉTRICAS ANALYTICAL
        # ========================================

        # Comprehensive reading (tiempo alto = lectura completa)
        metrics["comprehensive_reading"] = min(1.0, avg_time / 90.0)

        # Decision deliberation (tiempo de pensamiento)
        metrics["decision_deliberation"] = (
            1.0 if avg_response_time > 20 else 0.5
        )

        # Challenge success rate (éxito en challenges)
        stmt_success = select(func.count(UserChallengeAttempt.id)).where(
            and_(
                UserChallengeAttempt.user_id == user_id,
                UserChallengeAttempt.is_correct == True,
            )
        )
        stmt_total = select(func.count(UserChallengeAttempt.id)).where(
            UserChallengeAttempt.user_id == user_id
        )
        result_success = await self.session.execute(stmt_success)
        result_total = await self.session.execute(stmt_total)
        success_count = result_success.scalar_one()
        total_attempts = result_total.scalar_one()

        success_rate = (
            success_count / total_attempts if total_attempts > 0 else 0.5
        )
        metrics["challenge_success_rate"] = success_rate

        # Low hint usage (no usa hints)
        stmt_hints = select(func.avg(UserChallengeAttempt.hints_used)).where(
            UserChallengeAttempt.user_id == user_id
        )
        result = await self.session.execute(stmt_hints)
        avg_hints = result.scalar_one_or_none() or 0
        metrics["low_hint_usage"] = max(0.0, 1.0 - (avg_hints / 2.0))

        # Systematic exploration (visita fragmentos ordenadamente)
        metrics["systematic_exploration"] = 0.5  # Placeholder

        # ========================================
        # MÉTRICAS PERSISTENT
        # ========================================

        # Challenge retry rate (reintenta challenges)
        stmt_retries = select(func.count(UserChallengeAttempt.id)).where(
            and_(
                UserChallengeAttempt.user_id == user_id,
                UserChallengeAttempt.attempt_number > 1,
            )
        )
        result = await self.session.execute(stmt_retries)
        retry_count = result.scalar_one()
        retry_rate = (
            retry_count / total_attempts if total_attempts > 0 else 0
        )
        metrics["challenge_retry_rate"] = retry_rate

        # Comeback after abandonment (vuelve después de inactividad)
        # Detectar si tuvo periodos de inactividad y volvió
        if progress.started_at:
            days_since_start = (datetime.utcnow() - progress.started_at).days
            if days_since_start > 7 and total_fragments > 5:
                # Ha estado activo por varios días = volvió
                metrics["comeback_after_abandonment"] = 0.8
            else:
                metrics["comeback_after_abandonment"] = 0.3
        else:
            metrics["comeback_after_abandonment"] = 0.3

        # Streak recovery rate (recupera streaks)
        stmt_streak = select(UserStreak).where(UserStreak.user_id == user_id)
        result = await self.session.execute(stmt_streak)
        user_streak = result.scalar_one_or_none()

        if user_streak and user_streak.longest_streak > user_streak.current_streak:
            # Tuvo streak más largo antes = lo perdió pero sigue intentando
            metrics["streak_recovery_rate"] = 0.7
        else:
            metrics["streak_recovery_rate"] = 0.3

        # Mission completion rate
        # TODO: Integrar con gamification cuando esté disponible
        metrics["mission_completion_rate"] = 0.5

        # Never gives up (no abandona fragmentos)
        # Aproximar con: fragmentos visitados vs decisiones tomadas
        total_decisions = progress.total_decisions or 0
        decision_rate = (
            total_decisions / total_fragments if total_fragments > 0 else 0
        )
        metrics["never_gives_up"] = min(1.0, decision_rate * 1.5)

        # ========================================
        # MÉTRICAS PATIENT
        # ========================================

        # Long session duration (sesiones > 10 min)
        metrics["long_session_duration"] = (
            1.0 if avg_session_time > 600 else 0.4
        )

        # Deep processing time (tiempo alto por fragmento)
        metrics["deep_processing_time"] = min(1.0, avg_time / 120.0)

        # Time between actions (pausas entre decisiones)
        # Calcular tiempo promedio entre decisiones consecutivas
        stmt_times = select(
            UserDecisionHistory.decided_at
        ).where(
            UserDecisionHistory.user_id == user_id
        ).order_by(UserDecisionHistory.decided_at.asc())
        result = await self.session.execute(stmt_times)
        decision_times = list(result.scalars().all())

        if len(decision_times) >= 2:
            intervals = []
            for i in range(1, len(decision_times)):
                interval = (decision_times[i] - decision_times[i-1]).total_seconds()
                intervals.append(interval)
            avg_interval = sum(intervals) / len(intervals)
            # > 60s entre acciones = patient
            metrics["time_between_actions"] = min(1.0, avg_interval / 120.0)
        else:
            metrics["time_between_actions"] = 0.5

        # High completion rate (completa lo que empieza)
        metrics["high_completion_rate"] = min(1.0, chapters_completed / 2.0)

        # Low abandonment rate (no abandona contenido)
        # Inverso de: fragmentos visitados pero sin decisión
        metrics["low_abandonment_rate"] = min(1.0, decision_rate * 1.2)

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
        scores = await self.calculate_archetype_scores(user_id)
        sorted_scores = sorted(scores.values(), reverse=True)
        if len(sorted_scores) >= 2:
            first_score = sorted_scores[0]
            second_score = sorted_scores[1]
            separation = first_score - second_score
            # Si hay mucha separación (> 0.2), aumentar confianza
            if separation > 0.2:
                confidence *= 1.1

        return min(1.0, max(0.0, confidence))
