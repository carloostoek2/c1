"""
Servicio de gestión de desafíos interactivos.

Administra challenges (acertijos, puzzles) asociados a fragmentos narrativos,
validación de respuestas, sistema de hints y tracking de intentos.
"""
import logging
from datetime import datetime
from typing import Optional, Tuple, List, Dict

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from bot.narrative.database.models_immersive import (
    FragmentChallenge,
    UserChallengeAttempt,
)
from bot.narrative.database.enums import ChallengeType
from bot.narrative.config import NarrativeConfig

logger = logging.getLogger(__name__)


class ChallengeService:
    """Servicio de gestión de desafíos interactivos."""

    def __init__(self, session: AsyncSession):
        """
        Inicializa el servicio.

        Args:
            session: Sesión async de SQLAlchemy
        """
        self.session = session

    async def get_challenge(
        self, fragment_key: str
    ) -> Optional[FragmentChallenge]:
        """
        Obtiene el challenge asociado a un fragmento.

        Args:
            fragment_key: Clave del fragmento

        Returns:
            FragmentChallenge: Challenge del fragmento, o None si no tiene
        """
        stmt = select(FragmentChallenge).where(
            and_(
                FragmentChallenge.fragment_key == fragment_key,
                FragmentChallenge.is_active == True,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_challenge_by_id(
        self, challenge_id: int
    ) -> Optional[FragmentChallenge]:
        """
        Obtiene un challenge por su ID.

        Args:
            challenge_id: ID del challenge

        Returns:
            FragmentChallenge: Challenge, o None si no existe
        """
        stmt = select(FragmentChallenge).where(
            FragmentChallenge.id == challenge_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def validate_answer(
        self, challenge_id: int, user_answer: str
    ) -> Tuple[bool, str]:
        """
        Valida si la respuesta del usuario es correcta.

        Args:
            challenge_id: ID del challenge
            user_answer: Respuesta dada por el usuario

        Returns:
            Tuple[bool, str]: (es_correcta, mensaje_feedback)
        """
        challenge = await self.get_challenge_by_id(challenge_id)

        if not challenge:
            return False, "Challenge no encontrado."

        # Normalizar respuesta del usuario (lowercase, sin espacios extras)
        user_answer_normalized = user_answer.strip().lower()

        # Verificar contra todas las respuestas correctas
        correct_answers = challenge.correct_answers
        for correct_answer in correct_answers:
            correct_normalized = str(correct_answer).strip().lower()
            if user_answer_normalized == correct_normalized:
                logger.info(
                    f"Challenge {challenge_id}: respuesta correcta '{user_answer}'"
                )
                return True, challenge.success_message or "¡Correcto!"

        logger.debug(
            f"Challenge {challenge_id}: respuesta incorrecta '{user_answer}'"
        )
        return False, "Respuesta incorrecta. Intenta de nuevo."

    async def record_attempt(
        self,
        user_id: int,
        challenge_id: int,
        answer: str,
        is_correct: bool,
        hints_used: int = 0,
        response_time_seconds: Optional[int] = None,
    ) -> UserChallengeAttempt:
        """
        Registra un intento de challenge del usuario.

        Args:
            user_id: ID del usuario
            challenge_id: ID del challenge
            answer: Respuesta dada
            is_correct: Si fue correcta
            hints_used: Número de hints usados
            response_time_seconds: Tiempo de respuesta en segundos

        Returns:
            UserChallengeAttempt: Intento registrado
        """
        # Obtener número de intento
        attempt_number = await self._get_next_attempt_number(
            user_id, challenge_id
        )

        attempt = UserChallengeAttempt(
            user_id=user_id,
            challenge_id=challenge_id,
            attempt_number=attempt_number,
            answer_given=answer[:200],  # Limitar longitud
            is_correct=is_correct,
            hints_used=hints_used,
            attempted_at=datetime.utcnow(),
            response_time_seconds=response_time_seconds,
        )

        self.session.add(attempt)
        await self.session.commit()
        await self.session.refresh(attempt)

        logger.info(
            f"User {user_id} intento #{attempt_number} en challenge {challenge_id}: {'correcto' if is_correct else 'incorrecto'}"
        )

        return attempt

    async def get_remaining_attempts(
        self, user_id: int, challenge_id: int
    ) -> int:
        """
        Obtiene los intentos restantes del usuario para un challenge.

        Args:
            user_id: ID del usuario
            challenge_id: ID del challenge

        Returns:
            int: Intentos restantes (9999 si ilimitados)
        """
        challenge = await self.get_challenge_by_id(challenge_id)

        if not challenge:
            return 0

        # Si attempts_allowed es 0, significa ilimitados
        if challenge.attempts_allowed == 0:
            return 9999

        # Contar intentos del usuario
        stmt = select(func.count(UserChallengeAttempt.id)).where(
            and_(
                UserChallengeAttempt.user_id == user_id,
                UserChallengeAttempt.challenge_id == challenge_id,
            )
        )
        result = await self.session.execute(stmt)
        attempts_made = result.scalar_one()

        remaining = challenge.attempts_allowed - attempts_made
        return max(0, remaining)

    async def has_completed_challenge(
        self, user_id: int, challenge_id: int
    ) -> bool:
        """
        Verifica si el usuario completó exitosamente un challenge.

        Args:
            user_id: ID del usuario
            challenge_id: ID del challenge

        Returns:
            bool: True si completó exitosamente
        """
        stmt = select(UserChallengeAttempt).where(
            and_(
                UserChallengeAttempt.user_id == user_id,
                UserChallengeAttempt.challenge_id == challenge_id,
                UserChallengeAttempt.is_correct == True,
            )
        )
        result = await self.session.execute(stmt)
        success = result.scalar_one_or_none()

        return success is not None

    async def get_available_hints(
        self, user_id: int, challenge_id: int
    ) -> List[str]:
        """
        Obtiene los hints disponibles para el usuario.

        Retorna solo los hints que aún no ha usado (hasta el siguiente sin usar).

        Args:
            user_id: ID del usuario
            challenge_id: ID del challenge

        Returns:
            List[str]: Lista de hints disponibles (vacía si no hay más)
        """
        challenge = await self.get_challenge_by_id(challenge_id)

        if not challenge or not challenge.hints:
            return []

        # Obtener cuántos hints ya usó
        hints_used = await self._get_hints_used_count(user_id, challenge_id)

        # Limitar al máximo configurado
        max_hints = min(
            len(challenge.hints), NarrativeConfig.MAX_HINTS_PER_CHALLENGE
        )

        if hints_used >= max_hints:
            return []

        # Retornar el siguiente hint disponible
        return [challenge.hints[hints_used]]

    async def use_hint(
        self, user_id: int, challenge_id: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Usa un hint para el usuario en un challenge.

        Args:
            user_id: ID del usuario
            challenge_id: ID del challenge

        Returns:
            Tuple[bool, Optional[str]]: (pudo_usar, texto_hint)
        """
        available_hints = await self.get_available_hints(
            user_id, challenge_id
        )

        if not available_hints:
            return False, None

        hint_text = available_hints[0]

        # Registrar que usó un hint (incrementar contador en último intento o crear flag)
        hints_used = await self._get_hints_used_count(user_id, challenge_id)
        hints_used += 1

        # Actualizar contador en último intento
        await self._update_hints_used(user_id, challenge_id, hints_used)

        logger.info(
            f"User {user_id} usó hint #{hints_used} en challenge {challenge_id}"
        )

        return True, hint_text

    async def create_challenge(
        self,
        fragment_key: str,
        challenge_type: ChallengeType,
        question: str,
        correct_answers: List[str],
        hints: Optional[List[str]] = None,
        attempts_allowed: int = 3,
        timeout_seconds: Optional[int] = None,
        failure_redirect_key: Optional[str] = None,
        failure_message: Optional[str] = None,
        success_redirect_key: Optional[str] = None,
        success_clue_slug: Optional[str] = None,
        success_besitos: int = 0,
        success_message: Optional[str] = None,
        question_image_file_id: Optional[str] = None,
    ) -> FragmentChallenge:
        """
        Crea un nuevo challenge para un fragmento.

        Args:
            fragment_key: Clave del fragmento
            challenge_type: Tipo de challenge
            question: Pregunta o instrucción
            correct_answers: Lista de respuestas correctas
            hints: Lista de pistas progresivas
            attempts_allowed: Intentos permitidos (0 = ilimitados)
            timeout_seconds: Timeout para challenges cronometrados
            failure_redirect_key: Fragmento a donde redirigir si falla
            failure_message: Mensaje si falla
            success_redirect_key: Fragmento a donde redirigir si tiene éxito
            success_clue_slug: Pista a otorgar si tiene éxito
            success_besitos: Besitos a otorgar si tiene éxito
            success_message: Mensaje si tiene éxito
            question_image_file_id: ID de imagen de la pregunta

        Returns:
            FragmentChallenge: Challenge creado
        """
        challenge = FragmentChallenge(
            fragment_key=fragment_key,
            challenge_type=challenge_type,
            question=question,
            question_image_file_id=question_image_file_id,
            correct_answers=correct_answers,
            hints=hints or [],
            attempts_allowed=attempts_allowed,
            timeout_seconds=timeout_seconds,
            failure_redirect_key=failure_redirect_key,
            failure_message=failure_message,
            success_redirect_key=success_redirect_key,
            success_clue_slug=success_clue_slug,
            success_besitos=success_besitos,
            success_message=success_message,
            is_active=True,
        )

        self.session.add(challenge)
        await self.session.commit()
        await self.session.refresh(challenge)

        logger.info(
            f"Challenge creado para fragmento '{fragment_key}' (tipo: {challenge_type.value})"
        )

        return challenge

    async def get_user_attempts(
        self, user_id: int, challenge_id: int
    ) -> List[UserChallengeAttempt]:
        """
        Obtiene todos los intentos del usuario en un challenge.

        Args:
            user_id: ID del usuario
            challenge_id: ID del challenge

        Returns:
            List[UserChallengeAttempt]: Lista de intentos ordenados por fecha
        """
        stmt = (
            select(UserChallengeAttempt)
            .where(
                and_(
                    UserChallengeAttempt.user_id == user_id,
                    UserChallengeAttempt.challenge_id == challenge_id,
                )
            )
            .order_by(UserChallengeAttempt.attempted_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_challenge_stats(
        self, challenge_id: int
    ) -> Dict:
        """
        Obtiene estadísticas de un challenge.

        Args:
            challenge_id: ID del challenge

        Returns:
            dict: Estadísticas del challenge
                - total_attempts: Total de intentos
                - unique_users: Usuarios únicos que intentaron
                - success_rate: Tasa de éxito (0-1)
                - avg_attempts_to_success: Promedio de intentos para éxito
        """
        # Total de intentos
        stmt_total = select(func.count(UserChallengeAttempt.id)).where(
            UserChallengeAttempt.challenge_id == challenge_id
        )
        result = await self.session.execute(stmt_total)
        total_attempts = result.scalar_one()

        # Usuarios únicos
        stmt_users = select(
            func.count(func.distinct(UserChallengeAttempt.user_id))
        ).where(UserChallengeAttempt.challenge_id == challenge_id)
        result = await self.session.execute(stmt_users)
        unique_users = result.scalar_one()

        # Intentos exitosos
        stmt_success = select(func.count(UserChallengeAttempt.id)).where(
            and_(
                UserChallengeAttempt.challenge_id == challenge_id,
                UserChallengeAttempt.is_correct == True,
            )
        )
        result = await self.session.execute(stmt_success)
        successful_attempts = result.scalar_one()

        # Tasa de éxito
        success_rate = (
            successful_attempts / total_attempts if total_attempts > 0 else 0
        )

        return {
            "total_attempts": total_attempts,
            "unique_users": unique_users,
            "successful_attempts": successful_attempts,
            "success_rate": success_rate,
        }

    async def update_challenge(
        self, challenge_id: int, **updates
    ) -> Optional[FragmentChallenge]:
        """
        Actualiza un challenge existente.

        Args:
            challenge_id: ID del challenge
            **updates: Campos a actualizar

        Returns:
            FragmentChallenge: Challenge actualizado, o None si no existe
        """
        stmt = select(FragmentChallenge).where(
            FragmentChallenge.id == challenge_id
        )
        result = await self.session.execute(stmt)
        challenge = result.scalar_one_or_none()

        if not challenge:
            return None

        for key, value in updates.items():
            if hasattr(challenge, key):
                setattr(challenge, key, value)

        await self.session.commit()
        await self.session.refresh(challenge)

        logger.info(f"Challenge {challenge_id} actualizado")

        return challenge

    async def delete_challenge(self, challenge_id: int) -> bool:
        """
        Elimina un challenge.

        Args:
            challenge_id: ID del challenge

        Returns:
            bool: True si se eliminó, False si no existía
        """
        stmt = select(FragmentChallenge).where(
            FragmentChallenge.id == challenge_id
        )
        result = await self.session.execute(stmt)
        challenge = result.scalar_one_or_none()

        if not challenge:
            return False

        await self.session.delete(challenge)
        await self.session.commit()

        logger.info(f"Challenge {challenge_id} eliminado")

        return True

    # ========================================
    # MÉTODOS PRIVADOS
    # ========================================

    async def _get_next_attempt_number(
        self, user_id: int, challenge_id: int
    ) -> int:
        """Obtiene el número del próximo intento."""
        stmt = select(func.max(UserChallengeAttempt.attempt_number)).where(
            and_(
                UserChallengeAttempt.user_id == user_id,
                UserChallengeAttempt.challenge_id == challenge_id,
            )
        )
        result = await self.session.execute(stmt)
        max_attempt = result.scalar_one_or_none()

        return (max_attempt or 0) + 1

    async def _get_hints_used_count(
        self, user_id: int, challenge_id: int
    ) -> int:
        """Obtiene cuántos hints usó el usuario."""
        stmt = select(func.max(UserChallengeAttempt.hints_used)).where(
            and_(
                UserChallengeAttempt.user_id == user_id,
                UserChallengeAttempt.challenge_id == challenge_id,
            )
        )
        result = await self.session.execute(stmt)
        hints_used = result.scalar_one_or_none()

        return hints_used or 0

    async def _update_hints_used(
        self, user_id: int, challenge_id: int, hints_count: int
    ) -> None:
        """Actualiza el contador de hints usados en el último intento."""
        stmt = (
            select(UserChallengeAttempt)
            .where(
                and_(
                    UserChallengeAttempt.user_id == user_id,
                    UserChallengeAttempt.challenge_id == challenge_id,
                )
            )
            .order_by(UserChallengeAttempt.attempted_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        last_attempt = result.scalar_one_or_none()

        if last_attempt:
            last_attempt.hints_used = hints_count
            await self.session.commit()
