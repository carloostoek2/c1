"""
Servicio de gestión de variantes de contenido.

Evalúa condiciones de contexto del usuario para determinar qué variante
de contenido debe mostrarse en un fragmento narrativo.
"""
import logging
from datetime import datetime
from typing import Optional, List, Dict

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from bot.narrative.database.models_immersive import FragmentVariant
from bot.narrative.database.enums import VariantConditionType, ArchetypeType

logger = logging.getLogger(__name__)


class VariantService:
    """Servicio de selección de variantes de contenido basada en contexto."""

    def __init__(self, session: AsyncSession):
        """
        Inicializa el servicio.

        Args:
            session: Sesión async de SQLAlchemy
        """
        self.session = session

    async def get_applicable_variant(
        self, fragment_key: str, user_context: Dict
    ) -> Optional[FragmentVariant]:
        """
        Obtiene la variante aplicable para un fragmento según el contexto del usuario.

        Evalúa todas las variantes del fragmento por prioridad (mayor a menor)
        y retorna la primera cuya condición se cumpla.

        Args:
            fragment_key: Clave del fragmento
            user_context: Contexto del usuario (ver build_user_context)

        Returns:
            FragmentVariant: Variante aplicable, o None si ninguna aplica
        """
        # Obtener variantes ordenadas por prioridad (mayor primero)
        variants = await self.get_variants_for_fragment(fragment_key)

        if not variants:
            return None

        # Evaluar cada variante en orden de prioridad
        for variant in variants:
            if await self.evaluate_condition(variant, user_context):
                logger.info(
                    f"Variante '{variant.variant_key}' aplicable para fragmento '{fragment_key}' (condición: {variant.condition_type.value})"
                )
                return variant

        logger.debug(
            f"Ninguna variante aplicable para fragmento '{fragment_key}', usar contenido original"
        )
        return None

    async def evaluate_condition(
        self, variant: FragmentVariant, user_context: Dict
    ) -> bool:
        """
        Evalúa si la condición de una variante se cumple.

        Args:
            variant: Variante a evaluar
            user_context: Contexto del usuario

        Returns:
            bool: True si la condición se cumple
        """
        condition_type = variant.condition_type
        condition_value = variant.condition_value

        try:
            if condition_type == VariantConditionType.FIRST_VISIT:
                # Primera visita al fragmento
                visit_count = user_context.get("visit_count", 0)
                return visit_count == 0

            elif condition_type == VariantConditionType.RETURN_VISIT:
                # Visita de retorno (>= 2)
                visit_count = user_context.get("visit_count", 0)
                return visit_count >= 2

            elif condition_type == VariantConditionType.VISIT_COUNT:
                # Número específico de visitas (ej: ">=3")
                visit_count = user_context.get("visit_count", 0)
                return self._evaluate_numeric_condition(
                    visit_count, condition_value
                )

            elif condition_type == VariantConditionType.HAS_CLUE:
                # Usuario tiene pista específica
                clues = user_context.get("clues", [])
                return condition_value in clues

            elif condition_type == VariantConditionType.ARCHETYPE:
                # Usuario tiene arquetipo específico
                archetype = user_context.get("archetype", "unknown")
                return archetype == condition_value

            elif condition_type == VariantConditionType.TIME_OF_DAY:
                # Hora del día (morning, afternoon, evening, night)
                current_time = datetime.utcnow().hour
                time_windows = {
                    "morning": (6, 12),
                    "afternoon": (12, 18),
                    "evening": (18, 22),
                    "night": (22, 6),
                }
                window = time_windows.get(condition_value)
                if not window:
                    return False

                start, end = window
                if start < end:
                    return start <= current_time < end
                else:
                    # Ventana cruza medianoche (ej: night 22-6)
                    return current_time >= start or current_time < end

            elif condition_type == VariantConditionType.DAYS_SINCE_START:
                # Días desde que inició la historia (ej: ">=7")
                days_since_start = user_context.get("days_since_start", 0)
                return self._evaluate_numeric_condition(
                    days_since_start, condition_value
                )

            elif condition_type == VariantConditionType.DECISION_TAKEN:
                # Tomó decisión específica (formato: "fragment_key:decision_id")
                decisions_taken = user_context.get("decisions_taken", [])
                return condition_value in decisions_taken

            elif condition_type == VariantConditionType.CHAPTER_COMPLETE:
                # Completó capítulo específico
                chapters_completed = user_context.get("chapters_completed", [])
                return condition_value in chapters_completed

            else:
                logger.warning(
                    f"Tipo de condición no reconocido: {condition_type.value}"
                )
                return False

        except Exception as e:
            logger.error(
                f"Error evaluando condición de variante {variant.id}: {e}",
                exc_info=True,
            )
            return False

    def _evaluate_numeric_condition(
        self, value: int, condition: str
    ) -> bool:
        """
        Evalúa una condición numérica (ej: ">=3", "==5", "<10").

        Args:
            value: Valor actual
            condition: Condición a evaluar (formato: operator+number)

        Returns:
            bool: True si se cumple la condición
        """
        try:
            if condition.startswith(">="):
                threshold = int(condition[2:])
                return value >= threshold
            elif condition.startswith("<="):
                threshold = int(condition[2:])
                return value <= threshold
            elif condition.startswith(">"):
                threshold = int(condition[1:])
                return value > threshold
            elif condition.startswith("<"):
                threshold = int(condition[1:])
                return value < threshold
            elif condition.startswith("=="):
                threshold = int(condition[2:])
                return value == threshold
            else:
                # Asumir igualdad directa
                threshold = int(condition)
                return value == threshold
        except ValueError:
            logger.warning(f"Condición numérica inválida: {condition}")
            return False

    async def create_variant(
        self,
        fragment_key: str,
        variant_key: str,
        condition_type: VariantConditionType,
        condition_value: str,
        priority: int = 0,
        content_override: Optional[str] = None,
        speaker_override: Optional[str] = None,
        visual_hint_override: Optional[str] = None,
        media_file_id_override: Optional[str] = None,
        additional_decisions: Optional[list] = None,
    ) -> FragmentVariant:
        """
        Crea una nueva variante de contenido para un fragmento.

        Args:
            fragment_key: Clave del fragmento padre
            variant_key: Identificador único de la variante
            condition_type: Tipo de condición
            condition_value: Valor de la condición
            priority: Prioridad de evaluación (mayor = primero)
            content_override: Contenido alternativo
            speaker_override: Speaker alternativo
            visual_hint_override: Visual hint alternativo
            media_file_id_override: Media file ID alternativo
            additional_decisions: Decisiones adicionales (JSON)

        Returns:
            FragmentVariant: Variante creada
        """
        variant = FragmentVariant(
            fragment_key=fragment_key,
            variant_key=variant_key,
            priority=priority,
            condition_type=condition_type,
            condition_value=condition_value,
            content_override=content_override,
            speaker_override=speaker_override,
            visual_hint_override=visual_hint_override,
            media_file_id_override=media_file_id_override,
            additional_decisions=additional_decisions,
            is_active=True,
        )

        self.session.add(variant)
        await self.session.commit()
        await self.session.refresh(variant)

        logger.info(
            f"Variante '{variant_key}' creada para fragmento '{fragment_key}'"
        )

        return variant

    async def get_variants_for_fragment(
        self, fragment_key: str
    ) -> List[FragmentVariant]:
        """
        Obtiene todas las variantes activas de un fragmento ordenadas por prioridad.

        Args:
            fragment_key: Clave del fragmento

        Returns:
            List[FragmentVariant]: Lista de variantes ordenadas por prioridad (mayor primero)
        """
        stmt = (
            select(FragmentVariant)
            .where(
                and_(
                    FragmentVariant.fragment_key == fragment_key,
                    FragmentVariant.is_active == True,
                )
            )
            .order_by(FragmentVariant.priority.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def build_user_context(
        self, user_id: int, fragment_key: str
    ) -> Dict:
        """
        Construye el contexto del usuario para evaluar variantes.

        Este método recopila toda la información relevante del usuario
        que podría afectar qué variante mostrar.

        Args:
            user_id: ID del usuario
            fragment_key: Clave del fragmento actual

        Returns:
            dict: Contexto del usuario con campos:
                - visit_count: Veces que visitó este fragmento
                - clues: Lista de slugs de pistas que posee
                - archetype: Arquetipo detectado del usuario
                - days_since_start: Días desde que inició la historia
                - decisions_taken: Lista de "fragment_key:decision_id" tomadas
                - chapters_completed: Lista de chapter_slugs completados
        """
        from bot.narrative.services.progress import ProgressService
        from bot.narrative.services.engagement import EngagementService
        from bot.narrative.services.clue import ClueService
        from bot.narrative.services.archetype import ArchetypeService
        from bot.narrative.database.models import UserDecisionHistory
        from bot.narrative.database.models_immersive import ChapterCompletion

        # Inicializar servicios
        progress_service = ProgressService(self.session)
        engagement_service = EngagementService(self.session)
        clue_service = ClueService(self.session)
        archetype_service = ArchetypeService(self.session)

        # Visit count para este fragmento
        visit_count = await engagement_service.get_visit_count(
            user_id, fragment_key
        )

        # Pistas del usuario
        user_clues = await clue_service.get_user_clues(user_id)
        clue_slugs = [clue["item_slug"] for clue in user_clues]

        # Arquetipo
        archetype = await archetype_service.get_archetype(user_id)

        # Días desde que inició (primera decisión o fragmento visitado)
        progress = await progress_service.get_or_create_progress(user_id)
        if progress.started_at:
            days_since_start = (
                datetime.utcnow() - progress.started_at
            ).days
        else:
            days_since_start = 0

        # Decisiones tomadas
        stmt_decisions = select(UserDecisionHistory).where(
            UserDecisionHistory.user_id == user_id
        )
        result = await self.session.execute(stmt_decisions)
        decisions = result.scalars().all()
        decisions_taken = [
            f"{d.fragment_key}:{d.decision_id}" for d in decisions
        ]

        # Capítulos completados
        stmt_chapters = select(ChapterCompletion.chapter_slug).where(
            ChapterCompletion.user_id == user_id
        )
        result = await self.session.execute(stmt_chapters)
        chapters_completed = list(result.scalars().all())

        context = {
            "visit_count": visit_count,
            "clues": clue_slugs,
            "archetype": archetype.value if archetype else "unknown",
            "days_since_start": days_since_start,
            "decisions_taken": decisions_taken,
            "chapters_completed": chapters_completed,
        }

        logger.debug(
            f"Contexto construido para user {user_id} en fragmento '{fragment_key}': {context}"
        )

        return context

    async def update_variant(
        self, variant_id: int, **updates
    ) -> Optional[FragmentVariant]:
        """
        Actualiza una variante existente.

        Args:
            variant_id: ID de la variante
            **updates: Campos a actualizar

        Returns:
            FragmentVariant: Variante actualizada, o None si no existe
        """
        stmt = select(FragmentVariant).where(FragmentVariant.id == variant_id)
        result = await self.session.execute(stmt)
        variant = result.scalar_one_or_none()

        if not variant:
            return None

        for key, value in updates.items():
            if hasattr(variant, key):
                setattr(variant, key, value)

        await self.session.commit()
        await self.session.refresh(variant)

        logger.info(f"Variante {variant_id} actualizada")

        return variant

    async def delete_variant(self, variant_id: int) -> bool:
        """
        Elimina una variante.

        Args:
            variant_id: ID de la variante

        Returns:
            bool: True si se eliminó, False si no existía
        """
        stmt = select(FragmentVariant).where(FragmentVariant.id == variant_id)
        result = await self.session.execute(stmt)
        variant = result.scalar_one_or_none()

        if not variant:
            return False

        await self.session.delete(variant)
        await self.session.commit()

        logger.info(f"Variante {variant_id} eliminada")

        return True
