"""Servicio de tracking de conversiones para el sistema de ventas.

Este servicio registra eventos de conversión y mantiene métricas
de seguimiento del embudo de ventas para análisis posterior.
"""

import json
import logging
from datetime import datetime, UTC
from typing import Optional, Dict, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.gamification.database.conversion_models import (
    ConversionEvent,
    ConversionFunnel,
    LeadQualification
)

logger = logging.getLogger(__name__)


class ConversionTrackingService:
    """
    Servicio de tracking de conversiones y ventas.

    Registra eventos de conversión, mantiene métricas del embudo
    y califica leads basado en comportamiento de conversión.

    Attributes:
        session: Sesión async de SQLAlchemy
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el servicio.

        Args:
            session: Sesión async de SQLAlchemy
        """
        self._session = session

    # ========================================
    # REGISTRO DE EVENTOS DE CONVERSIÓN
    # ========================================

    async def track_conversion_event(
        self,
        user_id: int,
        event_type: str,
        product_type: Optional[str] = None,
        product_id: Optional[int] = None,
        event_data: Optional[Dict[str, Any]] = None,
        value: Optional[float] = None,
        currency: str = "USD",
        source: Optional[str] = None,
        referrer: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> ConversionEvent:
        """
        Registra un evento de conversión.

        Args:
            user_id: ID del usuario
            event_type: Tipo de evento (conversion_view, payment_initiated, etc.)
            product_type: Tipo de producto (vip, premium, mapa_del_deseo)
            product_id: ID específico del producto si aplica
            event_data: Datos adicionales del evento
            value: Valor monetario si aplica
            currency: Moneda del valor (default: USD)
            source: Origen del evento
            referrer: Referencia o código promocional
            session_id: ID de sesión para agrupar eventos

        Returns:
            ConversionEvent registrado
        """
        try:
            event = ConversionEvent(
                user_id=user_id,
                event_type=event_type,
                product_type=product_type,
                product_id=product_id,
                event_data=json.dumps(event_data) if event_data else None,
                value=value,
                currency=currency,
                source=source,
                referrer=referrer,
                session_id=session_id,
                created_at=datetime.now(UTC)
            )
            self._session.add(event)
            await self._session.flush()

            # Actualizar métricas del embudo
            await self._update_conversion_funnel(user_id, event_type, product_type)

            # Actualizar calificación del lead
            await self._update_lead_qualification(user_id, event_type, value, product_type)

            await self._session.commit()

            logger.debug(
                f"Conversion event tracked: {event_type} for user {user_id}"
            )

            return event

        except Exception as e:
            await self._session.rollback()
            logger.error(f"Error tracking conversion event: {e}")
            raise

    # ========================================
    # MANTENIMIENTO DE EMBUDO DE CONVERSIÓN
    # ========================================

    async def _update_conversion_funnel(
        self,
        user_id: int,
        event_type: str,
        product_type: Optional[str]
    ) -> None:
        """
        Actualiza las métricas del embudo de conversión para un usuario.

        Args:
            user_id: ID del usuario
            event_type: Tipo de evento registrado
            product_type: Tipo de producto involucrado
        """
        # Obtener o crear registro del embudo
        funnel = await self._get_or_create_conversion_funnel(user_id)

        # Actualizar contadores según tipo de evento
        if event_type == "conversion_view":
            funnel.increment_attempts(product_type or "unknown")
        elif event_type == "payment_initiated":
            funnel.payment_initiated_count += 1
        elif event_type == "payment_confirmed":
            funnel.payment_confirmed_count += 1
        elif event_type == "payment_approved":
            funnel.payment_approved_count += 1
        elif event_type == "objection_raised":
            funnel.objections_raised += 1
        elif event_type == "objection_handled":
            funnel.objections_handled += 1

        # Actualizar último paso
        funnel.update_last_step(event_type)

        await self._session.flush()

    async def _get_or_create_conversion_funnel(
        self,
        user_id: int
    ) -> ConversionFunnel:
        """
        Obtiene o crea registro de embudo de conversión para un usuario.

        Args:
            user_id: ID del usuario

        Returns:
            ConversionFunnel del usuario
        """
        result = await self._session.execute(
            select(ConversionFunnel).where(
                ConversionFunnel.user_id == user_id
            )
        )
        funnel = result.scalar_one_or_none()

        if funnel is None:
            funnel = ConversionFunnel(user_id=user_id)
            self._session.add(funnel)
            await self._session.flush()

        return funnel

    # ========================================
    # CALIFICACIÓN DE LEADS
    # ========================================

    async def _update_lead_qualification(
        self,
        user_id: int,
        event_type: str,
        value: Optional[float],
        product_type: Optional[str]
    ) -> None:
        """
        Actualiza la calificación del lead basado en eventos de conversión.

        Args:
            user_id: ID del usuario
            event_type: Tipo de evento registrado
            value: Valor monetario si aplica
            product_type: Tipo de producto involucrado
        """
        # Obtener o crear registro de calificación
        qualification = await self._get_or_create_lead_qualification(user_id)

        # Actualizar métricas según tipo de evento
        if event_type == "conversion_view":
            qualification.engagement_score = min(1.0, qualification.engagement_score + 0.05)
        elif event_type == "payment_initiated":
            qualification.engagement_score = min(1.0, qualification.engagement_score + 0.1)
            qualification.intent_score = min(1.0, qualification.intent_score + 0.15)
        elif event_type == "payment_confirmed":
            qualification.engagement_score = min(1.0, qualification.engagement_score + 0.15)
            qualification.intent_score = min(1.0, qualification.intent_score + 0.25)
        elif event_type == "payment_approved":
            qualification.engagement_score = min(1.0, qualification.engagement_score + 0.2)
            qualification.intent_score = min(1.0, qualification.intent_score + 0.3)
        elif event_type == "objection_raised":
            # Una objeción puede indicar interés pero también dudas
            qualification.intent_score = min(1.0, qualification.intent_score + 0.05)
        elif event_type == "objection_handled":
            # Resolver objeciones incrementa intención
            qualification.intent_score = min(1.0, qualification.intent_score + 0.1)

        # Actualizar valor potencial si aplica
        if value:
            qualification.conversion_value += value

        # Recalcular score de conversión global
        qualification.conversion_score = (
            qualification.engagement_score * 0.4 +
            qualification.intent_score * 0.6
        )

        # Determinar nivel de calificación
        if qualification.conversion_score >= 0.7:
            qualification.qualification_level = "hot"
        elif qualification.conversion_score >= 0.4:
            qualification.qualification_level = "warm"
        elif qualification.conversion_score >= 0.1:
            qualification.qualification_level = "cold"
        else:
            qualification.qualification_level = "none"

        qualification.last_scored_at = datetime.now(UTC)

        await self._session.flush()

    async def _get_or_create_lead_qualification(
        self,
        user_id: int
    ) -> LeadQualification:
        """
        Obtiene o crea registro de calificación de lead para un usuario.

        Args:
            user_id: ID del usuario

        Returns:
            LeadQualification del usuario
        """
        result = await self._session.execute(
            select(LeadQualification).where(
                LeadQualification.user_id == user_id
            )
        )
        qualification = result.scalar_one_or_none()

        if qualification is None:
            qualification = LeadQualification(user_id=user_id)
            self._session.add(qualification)
            await self._session.flush()

        return qualification

    # ========================================
    # MÉTODOS DE CONSULTA
    # ========================================

    async def get_conversion_funnel(
        self,
        user_id: int
    ) -> Optional[ConversionFunnel]:
        """
        Obtiene el embudo de conversión de un usuario.

        Args:
            user_id: ID del usuario

        Returns:
            ConversionFunnel o None si no existe
        """
        result = await self._session.execute(
            select(ConversionFunnel).where(
                ConversionFunnel.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def get_lead_qualification(
        self,
        user_id: int
    ) -> Optional[LeadQualification]:
        """
        Obtiene la calificación de lead de un usuario.

        Args:
            user_id: ID del usuario

        Returns:
            LeadQualification o None si no existe
        """
        result = await self._session.execute(
            select(LeadQualification).where(
                LeadQualification.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def get_conversion_events(
        self,
        user_id: int,
        event_type: Optional[str] = None,
        limit: int = 50
    ) -> list[ConversionEvent]:
        """
        Obtiene eventos de conversión de un usuario.

        Args:
            user_id: ID del usuario
            event_type: Filtrar por tipo de evento (opcional)
            limit: Límite de resultados (default: 50)

        Returns:
            Lista de ConversionEvent
        """
        query = select(ConversionEvent).where(
            ConversionEvent.user_id == user_id
        ).order_by(ConversionEvent.created_at.desc()).limit(limit)

        if event_type:
            query = query.where(ConversionEvent.event_type == event_type)

        result = await self._session.execute(query)
        return list(result.scalars().all())