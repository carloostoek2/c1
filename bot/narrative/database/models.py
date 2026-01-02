"""
Modelos de base de datos para el módulo de narrativa.

Sistema de fragmentos narrativos con decisiones, requisitos y progreso de usuario.
"""
from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    BigInteger,
    String,
    Text,
    Boolean,
    Integer,
    Float,
    ForeignKey,
    Index,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database.base import Base
from bot.narrative.database.enums import ChapterType, RequirementType, ArchetypeType


class NarrativeChapter(Base):
    """
    Capítulo narrativo (contenedor de fragmentos).

    Un capítulo es un conjunto de fragmentos relacionados que forman
    una unidad narrativa (ej: "Los Kinkys", "El Diván").
    """

    __tablename__ = "narrative_chapters"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))  # "Los Kinkys"
    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True)  # "los-kinkys"
    chapter_type: Mapped[ChapterType] = mapped_column(default=ChapterType.FREE)
    order: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Fase 5: Sistema de niveles (1-6)
    level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-6

    # Fase 5: Requisitos de acceso
    requires_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    requires_chapter_completed: Mapped[Optional[int]] = mapped_column(
        ForeignKey("narrative_chapters.id"), nullable=True
    )
    requires_archetype: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Fase 5: Metadata del capítulo
    estimated_duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Fase 5: Recompensas al completar
    favor_reward: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    badge_reward: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    item_reward: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    fragments: Mapped[List["NarrativeFragment"]] = relationship(
        back_populates="chapter",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<NarrativeChapter(id={self.id}, name='{self.name}', slug='{self.slug}', level={self.level})>"


class NarrativeFragment(Base):
    """
    Fragmento narrativo (unidad mínima de historia).

    Un fragmento es una escena individual con contenido de Diana/Lucien,
    posibles decisiones del usuario, y requisitos para acceder.
    """

    __tablename__ = "narrative_fragments"

    id: Mapped[int] = mapped_column(primary_key=True)
    chapter_id: Mapped[int] = mapped_column(ForeignKey("narrative_chapters.id"))

    # Identificación
    fragment_key: Mapped[str] = mapped_column(
        String(50), unique=True, index=True
    )  # "scene_1", "scene_2a"
    title: Mapped[str] = mapped_column(String(200))  # "Bienvenida de Diana"

    # Contenido
    speaker: Mapped[str] = mapped_column(String(50))  # "diana", "lucien", "narrator"
    content: Mapped[str] = mapped_column(Text)  # Texto narrativo con formato HTML
    visual_hint: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )  # Descripción imagen
    media_file_id: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )  # Telegram file_id

    # Navegación
    order: Mapped[int] = mapped_column(default=0)
    is_entry_point: Mapped[bool] = mapped_column(default=False)  # Inicio de capítulo
    is_ending: Mapped[bool] = mapped_column(default=False)  # Fin de capítulo

    # Fase 5: Navegación y flujo
    delay_seconds: Mapped[int] = mapped_column(Integer, default=0)  # Pausa dramática antes de mostrar
    is_decision_point: Mapped[bool] = mapped_column(default=False)  # Tiene decisiones del usuario
    next_fragment_key: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Siguiente si lineal

    # Fase 5: Condiciones dinámicas
    condition_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # "archetype", "response_time", etc.
    condition_value: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Valor a evaluar

    # Estado
    is_active: Mapped[bool] = mapped_column(default=True)

    # Metadata adicional (JSON para información extra como grants_clue, etc.)
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Metadata de timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    chapter: Mapped["NarrativeChapter"] = relationship(back_populates="fragments")
    decisions: Mapped[List["FragmentDecision"]] = relationship(
        back_populates="fragment",
        cascade="all, delete-orphan"
    )
    requirements: Mapped[List["FragmentRequirement"]] = relationship(
        back_populates="fragment",
        cascade="all, delete-orphan"
    )

    # Índices
    __table_args__ = (
        Index("idx_chapter_order", "chapter_id", "order"),
        Index("idx_entry_points", "chapter_id", "is_entry_point"),
    )

    def __repr__(self):
        return f"<NarrativeFragment(id={self.id}, key='{self.fragment_key}', speaker='{self.speaker}')>"


class FragmentDecision(Base):
    """
    Decisión/botón dentro de un fragmento.

    Representa una opción que el usuario puede elegir para avanzar
    en la narrativa.
    """

    __tablename__ = "fragment_decisions"

    id: Mapped[int] = mapped_column(primary_key=True)
    fragment_id: Mapped[int] = mapped_column(ForeignKey("narrative_fragments.id"))

    # Botón
    button_text: Mapped[str] = mapped_column(String(100))  # "🚪 Descubrir más"
    button_emoji: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    order: Mapped[int] = mapped_column(default=0)

    # Fase 5: Texto adicional
    subtext: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)  # Texto pequeño debajo del botón

    # Destino
    target_fragment_key: Mapped[str] = mapped_column(String(50))  # "scene_2"

    # Costo opcional (en besitos)
    besitos_cost: Mapped[int] = mapped_column(default=0)

    # Efectos
    grants_besitos: Mapped[int] = mapped_column(default=0)
    affects_archetype: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # "impulsive"

    # Fase 5: Sistema de favores/flags
    favor_change: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Puede ser negativo
    sets_flag: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Flag a setear
    requires_flag: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Flag requerido para ver opción

    # Estado
    is_active: Mapped[bool] = mapped_column(default=True)

    # Relationship
    fragment: Mapped["NarrativeFragment"] = relationship(back_populates="decisions")

    # Índice
    __table_args__ = (Index("idx_fragment_order", "fragment_id", "order"),)

    def __repr__(self):
        return f"<FragmentDecision(id={self.id}, text='{self.button_text}', target='{self.target_fragment_key}')>"


class FragmentRequirement(Base):
    """
    Requisito para acceder a un fragmento.

    Define condiciones que el usuario debe cumplir para poder
    acceder a un fragmento específico.
    """

    __tablename__ = "fragment_requirements"

    id: Mapped[int] = mapped_column(primary_key=True)
    fragment_id: Mapped[int] = mapped_column(ForeignKey("narrative_fragments.id"))

    requirement_type: Mapped[RequirementType] = mapped_column()
    value: Mapped[str] = mapped_column(
        String(100)
    )  # "100" para besitos, "impulsive" para arquetipo

    # Mensaje si no cumple
    rejection_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationship
    fragment: Mapped["NarrativeFragment"] = relationship(back_populates="requirements")

    # Índice
    __table_args__ = (Index("idx_fragment_requirements", "fragment_id"),)

    def __repr__(self):
        return f"<FragmentRequirement(id={self.id}, type='{self.requirement_type.value}', value='{self.value}')>"


class UserNarrativeProgress(Base):
    """
    Progreso del usuario en la narrativa.

    Rastrea la posición actual del usuario, arquetipo detectado
    y estadísticas generales.
    """

    __tablename__ = "user_narrative_progress"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)

    # Posición actual
    current_chapter_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("narrative_chapters.id"), nullable=True
    )
    current_fragment_key: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )

    # Fase 5: Sistema de niveles (1-6)
    current_level: Mapped[int] = mapped_column(Integer, default=1)

    # Arquetipo detectado (sistema expandido de 6 arquetipos)
    detected_archetype: Mapped[ArchetypeType] = mapped_column(
        default=ArchetypeType.UNKNOWN
    )
    archetype_confidence: Mapped[float] = mapped_column(default=0.0)  # 0.0 - 1.0
    archetype_detected_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    archetype_signals: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Estadísticas
    total_decisions: Mapped[int] = mapped_column(default=0)
    chapters_completed: Mapped[int] = mapped_column(default=0)  # Legacy: contador simple

    # Fase 5: Historial detallado (JSON)
    chapters_completed_list: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Array de chapter_ids
    fragments_seen: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Array de fragment_keys
    decisions_made: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # {fragment_key: decision_key, ...}

    # Fase 5: Sistema de flags narrativos
    narrative_flags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # {flag_key: value, ...}

    # Fase 5: Misiones narrativas activas
    active_mission_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    mission_started_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    mission_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Datos de misión en curso

    # Timestamps
    started_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    last_interaction: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Fase 5: Timestamps por nivel completado
    level_1_completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    level_2_completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    level_3_completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    level_4_completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    level_5_completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    level_6_completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Índice único por usuario
    __table_args__ = (Index("idx_user_narrative", "user_id", unique=True),)

    def __repr__(self):
        return f"<UserNarrativeProgress(user_id={self.user_id}, level={self.current_level}, archetype='{self.detected_archetype.value}', decisions={self.total_decisions})>"


class UserDecisionHistory(Base):
    """
    Historial de decisiones del usuario.

    Registra cada decisión tomada por el usuario para análisis
    de arquetipos y tracking de progreso.
    """

    __tablename__ = "user_decision_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)

    # Qué decidió
    fragment_key: Mapped[str] = mapped_column(String(50))
    decision_id: Mapped[int] = mapped_column(ForeignKey("fragment_decisions.id"))

    # Cuándo
    decided_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Tiempo de respuesta (para arquetipo)
    response_time_seconds: Mapped[Optional[int]] = mapped_column(nullable=True)

    # Índice
    __table_args__ = (Index("idx_user_decisions", "user_id", "fragment_key"),)

    def __repr__(self):
        return f"<UserDecisionHistory(user_id={self.user_id}, fragment='{self.fragment_key}', decided_at={self.decided_at})>"
