"""
Servicio de tracking de comportamiento para detección de arquetipos.

Este servicio registra interacciones del usuario y calcula métricas
que son utilizadas por el algoritmo de clasificación de arquetipos.
Lucien observa estas señales para entender el comportamiento.
"""

import json
import logging
import re
from datetime import datetime, UTC, timedelta
from typing import Optional, Dict, Any, List

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.enums import InteractionType
from bot.gamification.database.models import (
    UserBehaviorSignals,
    BehaviorInteraction
)
from bot.gamification.utils.emotional_words import (
    EMOTIONAL_WORDS,
    has_emotional_content,
    is_diana_question,
)

logger = logging.getLogger(__name__)


class BehaviorTrackingService:
    """
    Servicio de tracking de comportamiento de usuarios.

    Registra interacciones y calcula métricas para determinar
    el arquetipo del usuario basándose en su comportamiento.

    Attributes:
        session: Sesión async de SQLAlchemy

    Métodos principales:
        track_interaction: Registra una interacción
        update_metrics: Recalcula métricas derivadas
        get_behavior_signals: Obtiene señales de comportamiento
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el servicio.

        Args:
            session: Sesión async de SQLAlchemy
        """
        self._session = session

    # ========================================
    # TRACKING DE INTERACCIONES
    # ========================================

    async def track_interaction(
        self,
        user_id: int,
        interaction_type: InteractionType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Registra una interacción del usuario.

        Crea un registro de la interacción y actualiza métricas
        básicas de forma incremental.

        Args:
            user_id: ID del usuario
            interaction_type: Tipo de interacción (InteractionType enum)
            metadata: Datos específicos del tipo de interacción

        Examples:
            >>> await service.track_interaction(
            ...     user_id=123,
            ...     interaction_type=InteractionType.BUTTON_CLICK,
            ...     metadata={"button_id": "menu_main", "time_to_click": 2.5}
            ... )
        """
        try:
            # Crear registro de interacción
            interaction = BehaviorInteraction(
                user_id=user_id,
                interaction_type=interaction_type.value,
                interaction_data=json.dumps(metadata) if metadata else None,
                created_at=datetime.now(UTC)
            )
            self._session.add(interaction)

            # Obtener o crear señales del usuario
            signals = await self._get_or_create_signals(user_id)

            # Actualizar contador total
            signals.total_interactions += 1

            # Establecer primera interacción si no existe
            if signals.first_interaction_at is None:
                signals.first_interaction_at = datetime.now(UTC)

            # Actualización incremental según tipo
            await self._update_incremental_metrics(
                signals, interaction_type, metadata
            )

            await self._session.commit()

            logger.debug(
                f"Tracked {interaction_type.value} for user {user_id}"
            )

        except Exception as e:
            await self._session.rollback()
            logger.error(f"Error tracking interaction: {e}")
            raise

    async def _get_or_create_signals(
        self,
        user_id: int
    ) -> UserBehaviorSignals:
        """
        Obtiene o crea registro de señales para un usuario.

        Args:
            user_id: ID del usuario

        Returns:
            UserBehaviorSignals del usuario
        """
        result = await self._session.execute(
            select(UserBehaviorSignals).where(
                UserBehaviorSignals.user_id == user_id
            )
        )
        signals = result.scalar_one_or_none()

        if signals is None:
            signals = UserBehaviorSignals(user_id=user_id)
            self._session.add(signals)
            await self._session.flush()

        return signals

    async def _update_incremental_metrics(
        self,
        signals: UserBehaviorSignals,
        interaction_type: InteractionType,
        metadata: Optional[Dict[str, Any]]
    ) -> None:
        """
        Actualiza métricas de forma incremental según el tipo de interacción.

        Args:
            signals: Registro de señales del usuario
            interaction_type: Tipo de interacción
            metadata: Datos de la interacción
        """
        meta = metadata or {}

        if interaction_type == InteractionType.BUTTON_CLICK:
            # Incrementa ratio de botones
            total = signals.total_interactions
            current_ratio = signals.button_vs_text_ratio
            signals.button_vs_text_ratio = (
                (current_ratio * (total - 1) + 1.0) / total
            )

            # Actualiza tiempo promedio de decisión
            if "time_to_click" in meta:
                self._update_average(
                    signals, "avg_decision_time",
                    meta["time_to_click"]
                )

        elif interaction_type == InteractionType.TEXT_RESPONSE:
            # Decrementa ratio de botones
            total = signals.total_interactions
            current_ratio = signals.button_vs_text_ratio
            signals.button_vs_text_ratio = (
                (current_ratio * (total - 1) + 0.0) / total
            )

            # Actualiza longitud promedio de respuesta
            if "word_count" in meta:
                self._update_average(
                    signals, "avg_response_length",
                    meta["word_count"]
                )

                # Detecta respuestas largas (>50 palabras)
                if meta["word_count"] > 50:
                    signals.long_responses_count += 1

            # Detecta palabras emocionales
            if meta.get("has_emotional_words", False):
                signals.emotional_words_count += 1

            # Detecta preguntas
            if meta.get("has_questions", False):
                signals.question_count += 1

            # Detecta respuestas estructuradas
            if meta.get("is_structured", False):
                signals.structured_responses += 1

            # Actualiza tiempo de respuesta
            if "response_time" in meta:
                self._update_average(
                    signals, "avg_response_time",
                    meta["response_time"]
                )

        elif interaction_type == InteractionType.CONTENT_VIEW:
            # Actualiza tiempo en contenido
            if "time_spent" in meta:
                self._update_average(
                    signals, "avg_time_on_content",
                    meta["time_spent"]
                )

            # Detecta revisitas
            if meta.get("is_revisit", False):
                signals.revisits_old_content += 1

            # Actualiza tasa de completación
            if "completion" in meta:
                self._update_average(
                    signals, "content_completion_rate",
                    meta["completion"]
                )

        elif interaction_type == InteractionType.EASTER_EGG_FOUND:
            signals.easter_eggs_found += 1

        elif interaction_type == InteractionType.QUIZ_ANSWER:
            # Actualiza score promedio
            if "is_correct" in meta:
                score = 100.0 if meta["is_correct"] else 0.0
                self._update_average(
                    signals, "quiz_avg_score", score
                )

        elif interaction_type == InteractionType.DECISION_MADE:
            # Actualiza tiempo de decisión
            if "time_to_decide" in meta:
                self._update_average(
                    signals, "avg_decision_time",
                    meta["time_to_decide"]
                )

        elif interaction_type == InteractionType.MENU_NAVIGATION:
            # Incrementa secciones visitadas
            signals.content_sections_visited += 1

        elif interaction_type == InteractionType.RETURN_AFTER_INACTIVITY:
            signals.return_after_inactivity += 1

        elif interaction_type == InteractionType.RETRY_ACTION:
            signals.retry_failed_actions += 1

        elif interaction_type == InteractionType.SKIP_ACTION:
            signals.skip_actions_used += 1

        elif interaction_type == InteractionType.QUESTION_ASKED:
            signals.question_count += 1

            # Detecta preguntas sobre Diana
            if self._is_diana_question(meta.get("question_text", "")):
                signals.personal_questions_about_diana += 1

    def _update_average(
        self,
        signals: UserBehaviorSignals,
        field_name: str,
        new_value: float
    ) -> None:
        """
        Actualiza un promedio usando media móvil.

        Args:
            signals: Registro de señales
            field_name: Nombre del campo a actualizar
            new_value: Nuevo valor a promediar
        """
        current = getattr(signals, field_name)
        count = signals.total_interactions
        if count <= 1:
            setattr(signals, field_name, new_value)
        else:
            new_avg = ((current * (count - 1)) + new_value) / count
            setattr(signals, field_name, new_avg)

    def _is_diana_question(self, text: str) -> bool:
        """
        Detecta si el texto es una pregunta sobre Diana.

        Args:
            text: Texto a analizar

        Returns:
            True si parece ser una pregunta sobre Diana
        """
        return is_diana_question(text)

    # ========================================
    # ANÁLISIS DE TEXTO
    # ========================================

    @staticmethod
    def analyze_text_response(text: str) -> Dict[str, Any]:
        """
        Analiza un texto de respuesta del usuario.

        Detecta características relevantes para clasificación:
        - Cantidad de palabras
        - Presencia de palabras emocionales
        - Presencia de preguntas
        - Estructura (listas, enumeraciones)

        Args:
            text: Texto a analizar

        Returns:
            Dict con métricas del texto:
                word_count: int
                has_emotional_words: bool
                has_questions: bool
                is_structured: bool

        Examples:
            >>> metrics = BehaviorTrackingService.analyze_text_response(
            ...     "Me encanta lo que haces, Diana. Es muy especial."
            ... )
            >>> metrics["has_emotional_words"]
            True
        """
        words = text.split()
        word_count = len(words)

        # Detectar palabras emocionales usando módulo centralizado
        has_emotional, _ = has_emotional_content(text)

        # Detectar preguntas
        has_questions = "?" in text

        # Detectar estructura (listas, enumeraciones)
        is_structured = bool(
            re.search(r"^\d+\.", text, re.MULTILINE) or  # 1. 2. 3.
            re.search(r"^[-*•]", text, re.MULTILINE) or  # - * •
            re.search(r":\s*\n", text)  # Headers con :
        )

        return {
            "word_count": word_count,
            "has_emotional_words": has_emotional,
            "has_questions": has_questions,
            "is_structured": is_structured
        }

    # ========================================
    # ACTUALIZACIÓN DE MÉTRICAS
    # ========================================

    async def update_metrics(self, user_id: int) -> None:
        """
        Recalcula todas las métricas derivadas para un usuario.

        Este método realiza un recálculo completo basándose en
        el historial de interacciones. Usar periódicamente o
        cuando se sospeche de inconsistencias.

        Args:
            user_id: ID del usuario

        Note:
            Este método es costoso. Para actualizaciones frecuentes,
            track_interaction actualiza de forma incremental.
        """
        try:
            signals = await self._get_or_create_signals(user_id)

            # Obtener todas las interacciones del usuario
            result = await self._session.execute(
                select(BehaviorInteraction).where(
                    BehaviorInteraction.user_id == user_id
                ).order_by(BehaviorInteraction.created_at)
            )
            interactions = result.scalars().all()

            if not interactions:
                return

            # Reiniciar contadores
            self._reset_counters(signals)
            signals.total_interactions = len(interactions)
            signals.first_interaction_at = interactions[0].created_at

            # Procesar cada interacción
            button_clicks = 0
            text_responses = 0
            response_times: List[float] = []
            response_lengths: List[float] = []
            content_times: List[float] = []
            decision_times: List[float] = []
            quiz_scores: List[float] = []

            for interaction in interactions:
                itype = interaction.interaction_type
                meta = json.loads(interaction.interaction_data) if interaction.interaction_data else {}

                if itype == InteractionType.BUTTON_CLICK.value:
                    button_clicks += 1
                    if "time_to_click" in meta:
                        decision_times.append(meta["time_to_click"])

                elif itype == InteractionType.TEXT_RESPONSE.value:
                    text_responses += 1
                    if "word_count" in meta:
                        response_lengths.append(meta["word_count"])
                        if meta["word_count"] > 50:
                            signals.long_responses_count += 1
                    if meta.get("has_emotional_words"):
                        signals.emotional_words_count += 1
                    if meta.get("has_questions"):
                        signals.question_count += 1
                    if meta.get("is_structured"):
                        signals.structured_responses += 1
                    if "response_time" in meta:
                        response_times.append(meta["response_time"])

                elif itype == InteractionType.CONTENT_VIEW.value:
                    if "time_spent" in meta:
                        content_times.append(meta["time_spent"])
                    if meta.get("is_revisit"):
                        signals.revisits_old_content += 1

                elif itype == InteractionType.EASTER_EGG_FOUND.value:
                    signals.easter_eggs_found += 1

                elif itype == InteractionType.QUIZ_ANSWER.value:
                    if "is_correct" in meta:
                        quiz_scores.append(100.0 if meta["is_correct"] else 0.0)

                elif itype == InteractionType.DECISION_MADE.value:
                    if "time_to_decide" in meta:
                        decision_times.append(meta["time_to_decide"])

                elif itype == InteractionType.MENU_NAVIGATION.value:
                    signals.content_sections_visited += 1

                elif itype == InteractionType.RETURN_AFTER_INACTIVITY.value:
                    signals.return_after_inactivity += 1

                elif itype == InteractionType.RETRY_ACTION.value:
                    signals.retry_failed_actions += 1

                elif itype == InteractionType.SKIP_ACTION.value:
                    signals.skip_actions_used += 1

                elif itype == InteractionType.QUESTION_ASKED.value:
                    signals.question_count += 1
                    if self._is_diana_question(meta.get("question_text", "")):
                        signals.personal_questions_about_diana += 1

            # Calcular promedios
            total_clicks_text = button_clicks + text_responses
            if total_clicks_text > 0:
                signals.button_vs_text_ratio = button_clicks / total_clicks_text

            if response_times:
                signals.avg_response_time = sum(response_times) / len(response_times)

            if response_lengths:
                signals.avg_response_length = sum(response_lengths) / len(response_lengths)

            if content_times:
                signals.avg_time_on_content = sum(content_times) / len(content_times)

            if decision_times:
                signals.avg_decision_time = sum(decision_times) / len(decision_times)

            if quiz_scores:
                signals.quiz_avg_score = sum(quiz_scores) / len(quiz_scores)

            await self._session.commit()

            logger.info(f"Updated metrics for user {user_id}")

        except Exception as e:
            await self._session.rollback()
            logger.error(f"Error updating metrics: {e}")
            raise

    def _reset_counters(self, signals: UserBehaviorSignals) -> None:
        """Reinicia todos los contadores de señales."""
        signals.content_sections_visited = 0
        signals.content_completion_rate = 0.0
        signals.easter_eggs_found = 0
        signals.avg_time_on_content = 0.0
        signals.revisits_old_content = 0
        signals.avg_response_time = 0.0
        signals.avg_response_length = 0.0
        signals.button_vs_text_ratio = 0.0
        signals.avg_decision_time = 0.0
        signals.actions_per_session = 0.0
        signals.emotional_words_count = 0
        signals.question_count = 0
        signals.long_responses_count = 0
        signals.personal_questions_about_diana = 0
        signals.quiz_avg_score = 0.0
        signals.structured_responses = 0
        signals.error_reports = 0
        signals.return_after_inactivity = 0
        signals.retry_failed_actions = 0
        signals.incomplete_flows_completed = 0
        signals.skip_actions_used = 0

    # ========================================
    # CONSULTAS
    # ========================================

    async def get_behavior_signals(
        self,
        user_id: int
    ) -> Optional[UserBehaviorSignals]:
        """
        Obtiene las señales de comportamiento de un usuario.

        Args:
            user_id: ID del usuario

        Returns:
            UserBehaviorSignals o None si no existe
        """
        result = await self._session.execute(
            select(UserBehaviorSignals).where(
                UserBehaviorSignals.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def get_interaction_count(
        self,
        user_id: int,
        interaction_type: Optional[InteractionType] = None,
        since: Optional[datetime] = None
    ) -> int:
        """
        Cuenta interacciones de un usuario.

        Args:
            user_id: ID del usuario
            interaction_type: Filtrar por tipo (opcional)
            since: Desde cuándo contar (opcional)

        Returns:
            Cantidad de interacciones
        """
        query = select(func.count(BehaviorInteraction.id)).where(
            BehaviorInteraction.user_id == user_id
        )

        if interaction_type:
            query = query.where(
                BehaviorInteraction.interaction_type == interaction_type.value
            )

        if since:
            query = query.where(BehaviorInteraction.created_at >= since)

        result = await self._session.execute(query)
        return result.scalar() or 0

    async def get_recent_interactions(
        self,
        user_id: int,
        limit: int = 50,
        interaction_type: Optional[InteractionType] = None
    ) -> List[BehaviorInteraction]:
        """
        Obtiene interacciones recientes de un usuario.

        Args:
            user_id: ID del usuario
            limit: Máximo de resultados
            interaction_type: Filtrar por tipo (opcional)

        Returns:
            Lista de BehaviorInteraction ordenadas por fecha DESC
        """
        query = select(BehaviorInteraction).where(
            BehaviorInteraction.user_id == user_id
        ).order_by(BehaviorInteraction.created_at.desc()).limit(limit)

        if interaction_type:
            query = query.where(
                BehaviorInteraction.interaction_type == interaction_type.value
            )

        result = await self._session.execute(query)
        return list(result.scalars().all())

    # ========================================
    # SINCRONIZACIÓN CON STREAKS
    # ========================================

    async def sync_streak_metrics(
        self,
        user_id: int,
        current_streak: int,
        best_streak: int
    ) -> None:
        """
        Sincroniza métricas de racha desde el sistema de rachas.

        Este método es llamado por el sistema de rachas (F2.3)
        para mantener las métricas de paciencia actualizadas.

        Args:
            user_id: ID del usuario
            current_streak: Racha actual
            best_streak: Mejor racha histórica
        """
        try:
            signals = await self._get_or_create_signals(user_id)
            signals.current_streak = current_streak
            signals.best_streak = max(signals.best_streak, best_streak)
            await self._session.commit()

        except Exception as e:
            await self._session.rollback()
            logger.error(f"Error syncing streak metrics: {e}")
            raise

    # ========================================
    # LIMPIEZA
    # ========================================

    async def cleanup_old_interactions(
        self,
        days_old: int = 90
    ) -> int:
        """
        Elimina interacciones antiguas para mantener el tamaño de BD.

        Las métricas en UserBehaviorSignals se mantienen ya que
        son acumulativas. Solo se eliminan los registros de detalle.

        Args:
            days_old: Eliminar interacciones más antiguas de N días

        Returns:
            Cantidad de registros eliminados
        """
        try:
            cutoff_date = datetime.now(UTC) - timedelta(days=days_old)

            result = await self._session.execute(
                select(func.count(BehaviorInteraction.id)).where(
                    BehaviorInteraction.created_at < cutoff_date
                )
            )
            count = result.scalar() or 0

            if count > 0:
                await self._session.execute(
                    BehaviorInteraction.__table__.delete().where(
                        BehaviorInteraction.created_at < cutoff_date
                    )
                )
                await self._session.commit()
                logger.info(f"Cleaned up {count} old interactions")

            return count

        except Exception as e:
            await self._session.rollback()
            logger.error(f"Error cleaning up interactions: {e}")
            raise
