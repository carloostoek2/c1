"""Modelos de base de datos para tracking de conversiones y eventos de ventas.

Define modelos para el sistema de tracking de conversiones (F6.7) y
eventos de ventas que permiten monitorear el flujo de usuarios desde
Free → VIP → Premium → Mapa del Deseo.
"""

import json
from typing import Optional, List
from datetime import datetime, UTC

from sqlalchemy import (
    BigInteger, String, Integer, Boolean, DateTime, ForeignKey, Index, Text, Float, Enum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database.base import Base


class ConversionEvent(Base):
    """
    Eventos de conversión y ventas para tracking de flujos comerciales.

    Registra cada paso en el proceso de conversión de usuarios:
    - Visualización de ofertas
    - Click en botones de conversión
    - Inicio de proceso de pago
    - Confirmación de pago
    - Activación de producto
    - Rechazo de pago
    - Objeciones manejadas
    - Cierre de venta

    Attributes:
        id: ID único del evento (PK)
        user_id: ID del usuario involucrado
        event_type: Tipo de evento (conversion_view, payment_initiated, etc.)
        product_type: Producto involucrado (vip, premium, mapa_del_deseo)
        product_id: ID específico del producto si aplica
        event_data: Datos adicionales del evento en formato JSON
        value: Valor monetario si aplica
        currency: Moneda del valor (default: USD)
        source: Origen del evento (botón, enlace, comando)
        referrer: Referencia o código promocional si aplica
        session_id: ID de sesión para agrupar eventos relacionados
        created_at: Timestamp del evento

    Tipos de eventos:
        - conversion_view: Usuario ve oferta de producto
        - conversion_click: Usuario hace click en botón de conversión
        - payment_initiated: Usuario inicia proceso de pago
        - payment_confirmed: Usuario confirma/envía pago
        - payment_approved: Admin aprueba pago manual
        - payment_rejected: Admin rechaza pago manual
        - product_activated: Producto activado para usuario
        - objection_raised: Usuario levanta objeción
        - objection_handled: Lucien maneja objeción
        - upsell_offered: Oferta de upsell presentada
        - upsell_accepted: Usuario acepta oferta de upsell
        - upsell_rejected: Usuario rechaza oferta de upsell
    """
    __tablename__ = "conversion_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.user_id"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    product_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    product_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    event_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    referrer: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), nullable=False
    )

    # Índices para optimización
    __table_args__ = (
        Index('idx_conversion_user_event', 'user_id', 'event_type'),
        Index('idx_conversion_event_created', 'event_type', 'created_at'),
        Index('idx_conversion_user_created', 'user_id', 'created_at'),
        Index('idx_conversion_product', 'product_type', 'product_id'),
    )

    @property
    def data(self) -> dict:
        """Retorna los datos del evento como diccionario."""
        if self.event_data:
            return json.loads(self.event_data)
        return {}

    @data.setter
    def data(self, value: dict) -> None:
        """Establece los datos del evento desde un diccionario."""
        self.event_data = json.dumps(value)

    def __repr__(self):
        return (
            f"<ConversionEvent(id={self.id}, user_id={self.user_id}, "
            f"event_type='{self.event_type}', product='{self.product_type}', "
            f"created_at='{self.created_at}')>"
        )


class ConversionFunnel(Base):
    """
    Seguimiento de embudo de conversión por usuario.

    Mantiene métricas acumuladas del proceso de conversión de cada usuario
    para analizar su progreso a través del embudo de ventas.

    Attributes:
        user_id: ID del usuario (PK, 1-to-1 con users)
        last_conversion_step: Último paso de conversión alcanzado
        conversion_attempts: Intentos totales de conversión
        vip_attempts: Intentos de conversión a VIP
        premium_attempts: Intentos de conversión a Premium
        mapa_attempts: Intentos de conversión a Mapa del Deseo
        objections_raised: Total de objeciones levantadas
        objections_handled: Total de objeciones manejadas por Lucien
        payment_initiated_count: Veces que inició proceso de pago
        payment_confirmed_count: Veces que confirmó pago
        payment_approved_count: Veces que pago fue aprobado
        conversion_value: Valor total potencial de conversiones en proceso
        conversion_currency: Moneda del valor (default: USD)
        last_interaction_at: Última interacción en proceso de conversión
        first_interaction_at: Primera interacción en proceso de conversión
        created_at: Fecha de creación del registro
        updated_at: Fecha de última actualización
    """
    __tablename__ = "conversion_funnels"

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.user_id"), primary_key=True
    )
    last_conversion_step: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    conversion_attempts: Mapped[int] = mapped_column(Integer, default=0)
    vip_attempts: Mapped[int] = mapped_column(Integer, default=0)
    premium_attempts: Mapped[int] = mapped_column(Integer, default=0)
    mapa_attempts: Mapped[int] = mapped_column(Integer, default=0)
    objections_raised: Mapped[int] = mapped_column(Integer, default=0)
    objections_handled: Mapped[int] = mapped_column(Integer, default=0)
    payment_initiated_count: Mapped[int] = mapped_column(Integer, default=0)
    payment_confirmed_count: Mapped[int] = mapped_column(Integer, default=0)
    payment_approved_count: Mapped[int] = mapped_column(Integer, default=0)
    conversion_value: Mapped[float] = mapped_column(Float, default=0.0)
    conversion_currency: Mapped[str] = mapped_column(String(10), default="USD")
    last_interaction_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    first_interaction_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False
    )

    # Índices para optimización
    __table_args__ = (
        Index('idx_conversion_funnel_step', 'last_conversion_step'),
        Index('idx_conversion_funnel_updated', 'updated_at'),
    )

    def increment_attempts(self, product_type: str) -> None:
        """Incrementa el contador de intentos para un tipo de producto."""
        if product_type == 'vip':
            self.vip_attempts += 1
        elif product_type == 'premium':
            self.premium_attempts += 1
        elif product_type == 'mapa_del_deseo':
            self.mapa_attempts += 1
        self.conversion_attempts += 1

    def update_last_step(self, step: str) -> None:
        """Actualiza el último paso de conversión."""
        self.last_conversion_step = step
        self.last_interaction_at = datetime.now(UTC)
        if not self.first_interaction_at:
            self.first_interaction_at = datetime.now(UTC)

    def __repr__(self):
        return (
            f"<ConversionFunnel(user_id={self.user_id}, "
            f"last_step='{self.last_conversion_step}', "
            f"attempts={self.conversion_attempts})>"
        )


class LeadQualification(Base):
    """
    Calificación de leads/probabilidad de conversión.

    Mantiene un score basado en el comportamiento del usuario que
    indica la probabilidad de que realice una conversión.

    Attributes:
        user_id: ID del usuario (PK, 1-to-1 con users)
        conversion_score: Score de probabilidad de conversión (0.0-1.0)
        qualification_level: Nivel de calificación (hot, warm, cold, none)
        last_scored_at: Última actualización del score
        engagement_score: Puntaje de engagement (0.0-1.0)
        intent_score: Puntaje de intención de compra (0.0-1.0)
        budget_indicator: Indicador de capacidad de pago (low, medium, high, unknown)
        created_at: Fecha de creación
        updated_at: Fecha de última actualización
    """
    __tablename__ = "lead_qualifications"

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.user_id"), primary_key=True
    )
    conversion_score: Mapped[float] = mapped_column(Float, default=0.0)  # 0.0-1.0
    qualification_level: Mapped[str] = mapped_column(String(20), default="none")  # hot, warm, cold, none
    last_scored_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    engagement_score: Mapped[float] = mapped_column(Float, default=0.0)  # 0.0-1.0
    intent_score: Mapped[float] = mapped_column(Float, default=0.0)  # 0.0-1.0
    budget_indicator: Mapped[str] = mapped_column(String(20), default="unknown")  # low, medium, high, unknown
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False
    )

    # Índices para optimización
    __table_args__ = (
        Index('idx_lead_qualification_score', 'conversion_score'),
        Index('idx_lead_qualification_level', 'qualification_level'),
    )

    @property
    def is_hot_lead(self) -> bool:
        """Verifica si es un lead caliente."""
        return self.qualification_level == "hot"

    @property
    def is_warm_lead(self) -> bool:
        """Verifica si es un lead tibio."""
        return self.qualification_level == "warm"

    @property
    def is_cold_lead(self) -> bool:
        """Verifica si es un lead frío."""
        return self.qualification_level == "cold"

    def __repr__(self):
        return (
            f"<LeadQualification(user_id={self.user_id}, "
            f"score={self.conversion_score:.2f}, "
            f"level='{self.qualification_level}')>"
        )