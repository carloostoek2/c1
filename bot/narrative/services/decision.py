"""
Servicio de procesamiento de decisiones del usuario.

Maneja la lógica de tomar decisiones, validaciones, costos/recompensas,
y registro en historial.
"""
import logging
from typing import List, Tuple, Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.narrative.database import (
    FragmentDecision,
    UserDecisionHistory,
    NarrativeFragment,
)

logger = logging.getLogger(__name__)


class DecisionService:
    """
    Servicio de procesamiento de decisiones.

    Métodos CRUD:
    - create_decision: Crear nueva decisión
    - update_decision: Actualizar decisión existente
    - delete_decision: Eliminar decisión (soft delete)
    - get_decision_by_id: Obtener decisión por ID
    - get_decisions_by_fragment: Obtener decisiones de un fragmento

    Métodos de Procesamiento:
    - get_available_decisions: Obtener decisiones disponibles
    - process_decision: Procesar decisión del usuario
    - record_decision: Registrar decisión en historial
    - can_afford_decision: Verificar si usuario puede pagar decisión
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa servicio.

        Args:
            session: Sesión async de SQLAlchemy
        """
        self._session = session

    async def get_available_decisions(
        self,
        fragment_key: str,
        user_id: Optional[int] = None
    ) -> List[FragmentDecision]:
        """
        Obtiene decisiones disponibles para un fragmento.

        Filtra decisiones basadas en:
        - Estado activo
        - Flags requeridos (requires_flag) - Fase 5

        Args:
            fragment_key: Key del fragmento
            user_id: ID del usuario (para validar besitos y flags si aplica)

        Returns:
            Lista de decisiones disponibles
        """
        from bot.narrative.services.fragment import FragmentService

        fragment_service = FragmentService(self._session)
        fragment = await fragment_service.get_fragment(
            fragment_key,
            load_decisions=True
        )

        if not fragment:
            logger.warning(f"⚠️ Fragmento no encontrado: {fragment_key}")
            return []

        # Filtrar decisiones activas
        decisions = [d for d in fragment.decisions if d.is_active]

        # Fase 5: Filtrar por flags requeridos
        if user_id:
            from bot.narrative.services.progress import ProgressService
            progress_service = ProgressService(self._session)

            filtered_decisions = []
            for decision in decisions:
                # Si requiere flag, verificar que el usuario lo tenga
                if decision.requires_flag:
                    has_required_flag = await progress_service.has_flag(
                        user_id,
                        decision.requires_flag
                    )
                    if not has_required_flag:
                        logger.debug(
                            f"⛔ Decisión {decision.id} oculta: requiere flag '{decision.requires_flag}'"
                        )
                        continue

                filtered_decisions.append(decision)

            decisions = filtered_decisions

        # Ordenar por order
        decisions.sort(key=lambda d: d.order)

        logger.debug(
            f"📋 Decisiones disponibles para {fragment_key}: {len(decisions)}"
        )

        return decisions

    async def process_decision(
        self,
        user_id: int,
        decision_id: int,
        response_time: Optional[int] = None
    ) -> Tuple[bool, str, Optional[NarrativeFragment]]:
        """
        Procesa decisión del usuario.

        Este método:
        1. Valida que la decisión existe
        2. Verifica si hay costo en besitos (y si usuario puede pagar)
        3. Cobra besitos si aplica
        4. Otorga besitos si aplica
        5. Registra decisión en historial
        6. Actualiza progreso del usuario
        7. Retorna fragmento destino

        Args:
            user_id: ID del usuario
            decision_id: ID de la decisión tomada
            response_time: Tiempo de respuesta en segundos (para arquetipos)

        Returns:
            Tupla (success, message, next_fragment)
        """
        # Obtener decisión
        decision = await self.get_decision_by_id(decision_id)
        if not decision:
            return False, "❌ Decisión no válida", None

        # Verificar si está activa
        if not decision.is_active:
            return False, "❌ Esta decisión no está disponible", None

        # Verificar costo en besitos
        if decision.besitos_cost > 0:
            can_afford, balance = await self.can_afford_decision(user_id, decision)
            if not can_afford:
                return (
                    False,
                    f"❌ Necesitas {decision.besitos_cost} besitos (tienes {balance})",
                    None
                )

            # Cobrar besitos
            await self._deduct_besitos(user_id, decision.besitos_cost)
            logger.info(
                f"💰 Usuario {user_id} pagó {decision.besitos_cost} besitos"
            )

        # Otorgar besitos si aplica
        if decision.grants_besitos > 0:
            await self._grant_besitos(user_id, decision.grants_besitos)
            logger.info(
                f"💝 Usuario {user_id} recibió {decision.grants_besitos} besitos"
            )

        # Fase 5: Setear flag si aplica
        from bot.narrative.services.progress import ProgressService

        progress_service = ProgressService(self._session)

        if decision.sets_flag:
            await progress_service.set_flag(user_id, decision.sets_flag, True)
            logger.info(
                f"🏴 Flag '{decision.sets_flag}' seteado para usuario {user_id}"
            )

        # Registrar decisión en historial
        await self.record_decision(
            user_id=user_id,
            decision=decision,
            response_time=response_time
        )

        # Actualizar progreso
        from bot.narrative.services.fragment import FragmentService

        await progress_service.increment_decisions(user_id)

        # Obtener fragmento destino
        fragment_service = FragmentService(self._session)
        next_fragment = await fragment_service.get_fragment(
            decision.target_fragment_key,
            load_decisions=True
        )

        if not next_fragment:
            return (
                False,
                f"❌ Error: fragmento destino '{decision.target_fragment_key}' no existe",
                None
            )

        # Avanzar usuario al nuevo fragmento
        await progress_service.advance_to(
            user_id=user_id,
            fragment_key=next_fragment.fragment_key,
            chapter_id=next_fragment.chapter_id
        )

        logger.info(
            f"✅ Usuario {user_id} procesó decisión {decision_id} "
            f"→ {next_fragment.fragment_key}"
        )

        return True, "✅ Decisión procesada", next_fragment

    async def record_decision(
        self,
        user_id: int,
        decision: FragmentDecision,
        response_time: Optional[int] = None
    ) -> UserDecisionHistory:
        """
        Registra decisión en historial.

        Args:
            user_id: ID del usuario
            decision: Decisión tomada
            response_time: Tiempo de respuesta en segundos

        Returns:
            Registro de historial creado
        """
        # Obtener fragment_key del fragmento padre
        from bot.narrative.database import NarrativeFragment

        stmt = select(NarrativeFragment).where(
            NarrativeFragment.id == decision.fragment_id
        )
        result = await self._session.execute(stmt)
        fragment = result.scalar_one()

        history = UserDecisionHistory(
            user_id=user_id,
            fragment_key=fragment.fragment_key,
            decision_id=decision.id,
            response_time_seconds=response_time
        )

        self._session.add(history)
        await self._session.flush()
        await self._session.refresh(history)

        logger.debug(
            f"📝 Decisión registrada: user={user_id}, "
            f"fragment={fragment.fragment_key}, time={response_time}s"
        )

        return history

    async def get_decision_by_id(
        self,
        decision_id: int
    ) -> Optional[FragmentDecision]:
        """
        Obtiene decisión por ID.

        Args:
            decision_id: ID de la decisión

        Returns:
            Decisión o None si no existe
        """
        stmt = select(FragmentDecision).where(
            FragmentDecision.id == decision_id
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def can_afford_decision(
        self,
        user_id: int,
        decision: FragmentDecision
    ) -> Tuple[bool, int]:
        """
        Verifica si usuario puede pagar decisión.

        Args:
            user_id: ID del usuario
            decision: Decisión a validar

        Returns:
            Tupla (puede_pagar, balance_actual)
        """
        if decision.besitos_cost == 0:
            return True, 0

        # Obtener balance de besitos del usuario
        balance = await self._get_besitos_balance(user_id)

        can_afford = balance >= decision.besitos_cost

        return can_afford, balance

    async def _get_besitos_balance(self, user_id: int) -> int:
        """
        Obtiene balance de besitos del usuario.

        Args:
            user_id: ID del usuario

        Returns:
            Balance de besitos
        """
        try:
            from bot.gamification.services.container import get_container

            gamification = get_container()
            user_gamif = await gamification.user_gamification.get_or_create(user_id)
            return user_gamif.total_besitos
        except Exception as e:
            logger.error(f"❌ Error obteniendo balance de besitos: {e}")
            return 0

    async def _deduct_besitos(self, user_id: int, amount: int) -> None:
        """
        Deduce besitos del usuario.

        Args:
            user_id: ID del usuario
            amount: Cantidad a deducir
        """
        try:
            from bot.gamification.services.container import get_container
            from bot.gamification.database.enums import TransactionType

            gamification = get_container()
            await gamification.besito.deduct_besitos(
                user_id=user_id,
                amount=amount,
                reason="Decisión narrativa",
                transaction_type=TransactionType.PURCHASE
            )
        except Exception as e:
            logger.error(f"❌ Error deduciendo besitos: {e}")

    async def _grant_besitos(self, user_id: int, amount: int) -> None:
        """
        Otorga besitos al usuario.

        Args:
            user_id: ID del usuario
            amount: Cantidad a otorgar
        """
        try:
            from bot.gamification.services.container import get_container
            from bot.gamification.database.enums import TransactionType

            gamification = get_container()
            await gamification.besito.grant_besitos(
                user_id=user_id,
                amount=amount,
                reason="Recompensa de decisión narrativa",
                transaction_type=TransactionType.ADMIN_GRANT
            )
        except Exception as e:
            logger.error(f"❌ Error otorgando besitos: {e}")

    # ========================================
    # MÉTODOS CRUD
    # ========================================

    async def create_decision(
        self,
        fragment_id: int,
        button_text: str,
        target_fragment_key: str,
        order: int = 0,
        button_emoji: Optional[str] = None,
        subtext: Optional[str] = None,
        besitos_cost: int = 0,
        grants_besitos: int = 0,
        affects_archetype: Optional[str] = None,
        favor_change: Optional[float] = None,
        sets_flag: Optional[str] = None,
        requires_flag: Optional[str] = None
    ) -> FragmentDecision:
        """
        Crea nueva decisión para un fragmento.

        Args:
            fragment_id: ID del fragmento padre
            button_text: Texto del botón
            target_fragment_key: Key del fragmento destino
            order: Orden de presentación (default 0)
            button_emoji: Emoji opcional para el botón
            subtext: Texto pequeño debajo del botón (Fase 5)
            besitos_cost: Costo en besitos (default 0)
            grants_besitos: Besitos a otorgar (default 0)
            affects_archetype: Arquetipo afectado (opcional)
            favor_change: Cambio en favores (Fase 5, puede ser negativo)
            sets_flag: Flag a setear cuando se toma esta decisión (Fase 5)
            requires_flag: Flag requerido para ver esta opción (Fase 5)

        Returns:
            Decisión creada
        """
        decision = FragmentDecision(
            fragment_id=fragment_id,
            button_text=button_text,
            target_fragment_key=target_fragment_key,
            order=order,
            button_emoji=button_emoji,
            subtext=subtext,
            besitos_cost=besitos_cost,
            grants_besitos=grants_besitos,
            affects_archetype=affects_archetype,
            favor_change=favor_change,
            sets_flag=sets_flag,
            requires_flag=requires_flag,
            is_active=True
        )

        self._session.add(decision)
        await self._session.flush()
        await self._session.refresh(decision)

        logger.info(
            f"✅ Decisión creada: '{button_text}' → {target_fragment_key}"
        )

        return decision

    async def update_decision(
        self,
        decision_id: int,
        button_text: Optional[str] = None,
        target_fragment_key: Optional[str] = None,
        order: Optional[int] = None,
        button_emoji: Optional[str] = None,
        subtext: Optional[str] = None,
        besitos_cost: Optional[int] = None,
        grants_besitos: Optional[int] = None,
        affects_archetype: Optional[str] = None,
        favor_change: Optional[float] = None,
        sets_flag: Optional[str] = None,
        requires_flag: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Optional[FragmentDecision]:
        """
        Actualiza decisión existente.

        Args:
            decision_id: ID de la decisión
            button_text: Nuevo texto del botón
            target_fragment_key: Nuevo fragmento destino
            order: Nuevo orden
            button_emoji: Nuevo emoji
            subtext: Nuevo subtext (Fase 5)
            besitos_cost: Nuevo costo
            grants_besitos: Nuevos besitos a otorgar
            affects_archetype: Nuevo arquetipo afectado
            favor_change: Nuevo cambio en favores (Fase 5)
            sets_flag: Nuevo flag a setear (Fase 5)
            requires_flag: Nuevo flag requerido (Fase 5)
            is_active: Nuevo estado activo

        Returns:
            Decisión actualizada o None si no existe
        """
        decision = await self.get_decision_by_id(decision_id)
        if not decision:
            logger.warning(f"⚠️ Decisión no encontrada: {decision_id}")
            return None

        if button_text is not None:
            decision.button_text = button_text
        if target_fragment_key is not None:
            decision.target_fragment_key = target_fragment_key
        if order is not None:
            decision.order = order
        if button_emoji is not None:
            decision.button_emoji = button_emoji if button_emoji != "" else None
        if subtext is not None:
            decision.subtext = subtext if subtext != "" else None
        if besitos_cost is not None:
            decision.besitos_cost = besitos_cost
        if grants_besitos is not None:
            decision.grants_besitos = grants_besitos
        if affects_archetype is not None:
            decision.affects_archetype = affects_archetype if affects_archetype != "" else None
        if favor_change is not None:
            decision.favor_change = favor_change
        if sets_flag is not None:
            decision.sets_flag = sets_flag if sets_flag != "" else None
        if requires_flag is not None:
            decision.requires_flag = requires_flag if requires_flag != "" else None
        if is_active is not None:
            decision.is_active = is_active

        await self._session.flush()
        await self._session.refresh(decision)

        logger.info(f"✅ Decisión actualizada: ID={decision_id}")

        return decision

    async def delete_decision(self, decision_id: int) -> bool:
        """
        Elimina decisión (soft delete).

        Args:
            decision_id: ID de la decisión

        Returns:
            True si se eliminó, False si no existía
        """
        decision = await self.get_decision_by_id(decision_id)
        if not decision:
            logger.warning(f"⚠️ Decisión no encontrada: {decision_id}")
            return False

        decision.is_active = False
        await self._session.flush()

        logger.info(f"🗑️ Decisión eliminada (soft): ID={decision_id}")

        return True

    async def get_decisions_by_fragment(
        self,
        fragment_id: int,
        active_only: bool = True
    ) -> List[FragmentDecision]:
        """
        Obtiene todas las decisiones de un fragmento.

        Args:
            fragment_id: ID del fragmento
            active_only: Si True, solo retorna decisiones activas

        Returns:
            Lista de decisiones ordenadas por order
        """
        stmt = select(FragmentDecision).where(
            FragmentDecision.fragment_id == fragment_id
        )

        if active_only:
            stmt = stmt.where(FragmentDecision.is_active == True)

        stmt = stmt.order_by(FragmentDecision.order)

        result = await self._session.execute(stmt)
        decisions = list(result.scalars().all())

        logger.debug(
            f"📋 Decisiones para fragment_id={fragment_id}: {len(decisions)}"
        )

        return decisions
