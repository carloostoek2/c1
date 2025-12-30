"""
Tests E2E para Fase 3 - Sistema de Arquetipos y Tracking de Comportamiento.

Prueba:
- F3.1: Modelo UserBehaviorSignals y campos de arquetipo en User
- F3.2: BehaviorTrackingService con registro de interacciones
"""

import pytest
from datetime import datetime, UTC, timedelta

from bot.database import get_session
from bot.database.models import User
from bot.database.enums import UserRole, ArchetypeType, InteractionType
from bot.gamification.database.models import (
    UserBehaviorSignals,
    BehaviorInteraction
)
from bot.gamification.services.behavior_tracking import BehaviorTrackingService
from bot.gamification.services.container import GamificationContainer


# ============================================================
# F3.1: TESTS DE MODELOS Y ENUMS
# ============================================================

class TestArchetypeEnums:
    """Tests para ArchetypeType enum."""

    def test_archetype_values(self):
        """Verifica que existen los 6 arquetipos definidos."""
        assert ArchetypeType.EXPLORER.value == "explorer"
        assert ArchetypeType.DIRECT.value == "direct"
        assert ArchetypeType.ROMANTIC.value == "romantic"
        assert ArchetypeType.ANALYTICAL.value == "analytical"
        assert ArchetypeType.PERSISTENT.value == "persistent"
        assert ArchetypeType.PATIENT.value == "patient"

    def test_archetype_display_names(self):
        """Verifica nombres legibles de arquetipos."""
        assert ArchetypeType.EXPLORER.display_name == "El Explorador"
        assert ArchetypeType.DIRECT.display_name == "El Directo"
        assert ArchetypeType.ROMANTIC.display_name == "El Romántico"
        assert ArchetypeType.ANALYTICAL.display_name == "El Analítico"
        assert ArchetypeType.PERSISTENT.display_name == "El Persistente"
        assert ArchetypeType.PATIENT.display_name == "El Paciente"

    def test_archetype_lucien_descriptions(self):
        """Verifica descripciones de Lucien para cada arquetipo."""
        assert ArchetypeType.EXPLORER.lucien_description == "Insaciablemente curioso"
        assert ArchetypeType.DIRECT.lucien_description == "Refrescantemente directo"
        assert ArchetypeType.ROMANTIC.lucien_description == "Peligrosamente sentimental"
        assert ArchetypeType.ANALYTICAL.lucien_description == "Irritantemente preciso"
        assert ArchetypeType.PERSISTENT.lucien_description == "Admirablemente terco"
        assert ArchetypeType.PATIENT.lucien_description == "Inquietantemente paciente"

    def test_archetype_keywords(self):
        """Verifica palabras clave de cada arquetipo."""
        assert ArchetypeType.EXPLORER.keyword == "Curiosidad"
        assert ArchetypeType.DIRECT.keyword == "Eficiencia"
        assert ArchetypeType.ROMANTIC.keyword == "Emoción"
        assert ArchetypeType.ANALYTICAL.keyword == "Lógica"
        assert ArchetypeType.PERSISTENT.keyword == "Tenacidad"
        assert ArchetypeType.PATIENT.keyword == "Calma"


class TestInteractionTypeEnum:
    """Tests para InteractionType enum."""

    def test_interaction_types_exist(self):
        """Verifica que existen todos los tipos de interacción."""
        expected_types = [
            "button_click", "text_response", "content_view", "content_complete",
            "quiz_answer", "decision_made", "menu_navigation", "easter_egg_found",
            "session_start", "session_end", "return_after_inactivity",
            "retry_action", "skip_action", "question_asked"
        ]
        actual_types = [t.value for t in InteractionType]
        for expected in expected_types:
            assert expected in actual_types, f"Missing: {expected}"


class TestUserArchetypeFields:
    """Tests para campos de arquetipo en modelo User."""

    @pytest.mark.asyncio
    async def test_user_archetype_fields_exist(self):
        """Verifica que User tiene campos de arquetipo."""
        async with get_session() as session:
            # Crear usuario
            user = User(
                user_id=12345,
                first_name="Test",
                role=UserRole.FREE
            )
            session.add(user)
            await session.commit()

            # Verificar campos por defecto
            assert user.archetype is None
            assert user.archetype_confidence is None
            assert user.archetype_scores is None
            assert user.archetype_detected_at is None
            # archetype_version tiene default=1
            assert user.archetype_version == 1

    @pytest.mark.asyncio
    async def test_user_archetype_assignment(self):
        """Verifica que se puede asignar arquetipo a User."""
        async with get_session() as session:
            user = User(
                user_id=12346,
                first_name="Test",
                role=UserRole.FREE,
                archetype=ArchetypeType.EXPLORER,
                archetype_confidence=0.85,
                archetype_scores={
                    "EXPLORER": 0.85,
                    "DIRECT": 0.10,
                    "ROMANTIC": 0.05
                },
                archetype_detected_at=datetime.now(UTC),
                archetype_version=1
            )
            session.add(user)
            await session.commit()

            # Verificar asignación
            assert user.archetype == ArchetypeType.EXPLORER
            assert user.archetype_confidence == 0.85
            assert "EXPLORER" in user.archetype_scores
            assert user.archetype_version == 1

    def test_user_archetype_properties(self):
        """Verifica propiedades helper de arquetipo en User."""
        user = User(
            user_id=12347,
            first_name="Test",
            role=UserRole.FREE
        )

        # Sin arquetipo
        assert user.has_archetype is False
        assert user.archetype_display == "Sin clasificar"
        assert user.archetype_description == ""

        # Con arquetipo
        user.archetype = ArchetypeType.ROMANTIC
        assert user.has_archetype is True
        assert user.archetype_display == "El Romántico"
        assert user.archetype_description == "Peligrosamente sentimental"


# ============================================================
# F3.2: TESTS DE BEHAVIOR TRACKING SERVICE
# ============================================================

class TestUserBehaviorSignalsModel:
    """Tests para modelo UserBehaviorSignals."""

    @pytest.mark.asyncio
    async def test_create_behavior_signals(self):
        """Verifica creación de registro de señales."""
        async with get_session() as session:
            # Crear usuario primero
            user = User(
                user_id=22345,
                first_name="Test",
                role=UserRole.FREE
            )
            session.add(user)
            await session.flush()

            # Crear señales
            signals = UserBehaviorSignals(
                user_id=user.user_id,
                content_sections_visited=5,
                easter_eggs_found=2,
                avg_response_time=3.5,
                emotional_words_count=10
            )
            session.add(signals)
            await session.commit()

            # Verificar valores
            assert signals.content_sections_visited == 5
            assert signals.easter_eggs_found == 2
            assert signals.avg_response_time == 3.5
            assert signals.emotional_words_count == 10

    @pytest.mark.asyncio
    async def test_behavior_signals_defaults(self):
        """Verifica valores por defecto de señales."""
        async with get_session() as session:
            user = User(
                user_id=22346,
                first_name="Test",
                role=UserRole.FREE
            )
            session.add(user)
            await session.flush()

            signals = UserBehaviorSignals(user_id=user.user_id)
            session.add(signals)
            await session.commit()

            # Todos los contadores deben ser 0
            assert signals.content_sections_visited == 0
            assert signals.easter_eggs_found == 0
            assert signals.total_interactions == 0
            assert signals.quiz_avg_score == 0.0
            assert signals.button_vs_text_ratio == 0.0


class TestBehaviorTrackingService:
    """Tests para BehaviorTrackingService."""

    @pytest.mark.asyncio
    async def test_track_button_click(self):
        """Verifica tracking de click en botón."""
        async with get_session() as session:
            user = User(
                user_id=32345,
                first_name="Test",
                role=UserRole.FREE
            )
            session.add(user)
            await session.commit()

            service = BehaviorTrackingService(session)

            await service.track_interaction(
                user_id=user.user_id,
                interaction_type=InteractionType.BUTTON_CLICK,
                metadata={
                    "button_id": "menu_main",
                    "context": "start_handler",
                    "time_to_click": 2.5
                }
            )

            # Verificar señales actualizadas
            signals = await service.get_behavior_signals(user.user_id)
            assert signals is not None
            assert signals.total_interactions == 1
            assert signals.button_vs_text_ratio == 1.0  # Solo un click de botón

    @pytest.mark.asyncio
    async def test_track_text_response(self):
        """Verifica tracking de respuesta de texto."""
        async with get_session() as session:
            user = User(
                user_id=32346,
                first_name="Test",
                role=UserRole.FREE
            )
            session.add(user)
            await session.commit()

            service = BehaviorTrackingService(session)

            await service.track_interaction(
                user_id=user.user_id,
                interaction_type=InteractionType.TEXT_RESPONSE,
                metadata={
                    "word_count": 25,
                    "has_emotional_words": True,
                    "has_questions": True,
                    "is_structured": False,
                    "response_time": 5.0
                }
            )

            signals = await service.get_behavior_signals(user.user_id)
            assert signals.total_interactions == 1
            assert signals.emotional_words_count == 1
            assert signals.question_count == 1
            assert signals.avg_response_length == 25.0
            assert signals.avg_response_time == 5.0

    @pytest.mark.asyncio
    async def test_track_long_response(self):
        """Verifica detección de respuestas largas (>50 palabras)."""
        async with get_session() as session:
            user = User(
                user_id=32347,
                first_name="Test",
                role=UserRole.FREE
            )
            session.add(user)
            await session.commit()

            service = BehaviorTrackingService(session)

            await service.track_interaction(
                user_id=user.user_id,
                interaction_type=InteractionType.TEXT_RESPONSE,
                metadata={
                    "word_count": 75,  # >50 = respuesta larga
                    "has_emotional_words": False,
                    "has_questions": False,
                    "is_structured": False
                }
            )

            signals = await service.get_behavior_signals(user.user_id)
            assert signals.long_responses_count == 1

    @pytest.mark.asyncio
    async def test_track_easter_egg(self):
        """Verifica tracking de easter egg encontrado."""
        async with get_session() as session:
            user = User(
                user_id=32348,
                first_name="Test",
                role=UserRole.FREE
            )
            session.add(user)
            await session.commit()

            service = BehaviorTrackingService(session)

            await service.track_interaction(
                user_id=user.user_id,
                interaction_type=InteractionType.EASTER_EGG_FOUND,
                metadata={"easter_egg_id": "secret_1"}
            )

            signals = await service.get_behavior_signals(user.user_id)
            assert signals.easter_eggs_found == 1

    @pytest.mark.asyncio
    async def test_track_multiple_interactions(self):
        """Verifica tracking de múltiples interacciones."""
        async with get_session() as session:
            user = User(
                user_id=32349,
                first_name="Test",
                role=UserRole.FREE
            )
            session.add(user)
            await session.commit()

            service = BehaviorTrackingService(session)

            # Simular 3 clicks de botón, 2 respuestas de texto
            for _ in range(3):
                await service.track_interaction(
                    user_id=user.user_id,
                    interaction_type=InteractionType.BUTTON_CLICK,
                    metadata={"button_id": "test", "time_to_click": 1.0}
                )

            for _ in range(2):
                await service.track_interaction(
                    user_id=user.user_id,
                    interaction_type=InteractionType.TEXT_RESPONSE,
                    metadata={"word_count": 10}
                )

            signals = await service.get_behavior_signals(user.user_id)
            assert signals.total_interactions == 5
            # Ratio: 3 botones / 5 total = 0.6
            assert abs(signals.button_vs_text_ratio - 0.6) < 0.01

    @pytest.mark.asyncio
    async def test_track_quiz_answer(self):
        """Verifica tracking de respuestas a quiz."""
        async with get_session() as session:
            user = User(
                user_id=32350,
                first_name="Test",
                role=UserRole.FREE
            )
            session.add(user)
            await session.commit()

            service = BehaviorTrackingService(session)

            # Respuesta correcta
            await service.track_interaction(
                user_id=user.user_id,
                interaction_type=InteractionType.QUIZ_ANSWER,
                metadata={"quiz_id": "q1", "is_correct": True}
            )

            # Respuesta incorrecta
            await service.track_interaction(
                user_id=user.user_id,
                interaction_type=InteractionType.QUIZ_ANSWER,
                metadata={"quiz_id": "q2", "is_correct": False}
            )

            signals = await service.get_behavior_signals(user.user_id)
            # Promedio: (100 + 0) / 2 = 50
            assert signals.quiz_avg_score == 50.0

    @pytest.mark.asyncio
    async def test_track_return_after_inactivity(self):
        """Verifica tracking de retorno después de inactividad."""
        async with get_session() as session:
            user = User(
                user_id=32351,
                first_name="Test",
                role=UserRole.FREE
            )
            session.add(user)
            await session.commit()

            service = BehaviorTrackingService(session)

            await service.track_interaction(
                user_id=user.user_id,
                interaction_type=InteractionType.RETURN_AFTER_INACTIVITY,
                metadata={"days_inactive": 5}
            )

            signals = await service.get_behavior_signals(user.user_id)
            assert signals.return_after_inactivity == 1


class TestBehaviorTextAnalysis:
    """Tests para análisis de texto del BehaviorTrackingService."""

    def test_analyze_emotional_text(self):
        """Verifica detección de palabras emocionales."""
        text = "Me encanta lo que haces, es muy especial y lleno de amor."
        result = BehaviorTrackingService.analyze_text_response(text)

        assert result["has_emotional_words"] is True
        assert result["word_count"] == 12

    def test_analyze_question(self):
        """Verifica detección de preguntas."""
        text = "Como es tu vida? Me gustaria saber mas."
        result = BehaviorTrackingService.analyze_text_response(text)

        assert result["has_questions"] is True

    def test_analyze_structured_text(self):
        """Verifica detección de texto estructurado."""
        text = """1. Primer punto
2. Segundo punto
3. Tercer punto"""
        result = BehaviorTrackingService.analyze_text_response(text)

        assert result["is_structured"] is True

    def test_analyze_plain_text(self):
        """Verifica análisis de texto simple sin características especiales."""
        text = "Hola, como estas hoy."
        result = BehaviorTrackingService.analyze_text_response(text)

        assert result["has_emotional_words"] is False
        assert result["has_questions"] is False
        assert result["is_structured"] is False
        assert result["word_count"] == 4


class TestBehaviorTrackingContainerIntegration:
    """Tests de integración con GamificationContainer."""

    @pytest.mark.asyncio
    async def test_behavior_tracking_via_container(self):
        """Verifica acceso a BehaviorTrackingService via container."""
        async with get_session() as session:
            container = GamificationContainer(session)

            # Verificar que el servicio está disponible
            service = container.behavior_tracking
            assert service is not None
            assert isinstance(service, BehaviorTrackingService)

            # Verificar que se reutiliza la instancia (lazy loading)
            service2 = container.behavior_tracking
            assert service is service2

    @pytest.mark.asyncio
    async def test_container_tracks_loaded_services(self):
        """Verifica que container reporta behavior_tracking como cargado."""
        async with get_session() as session:
            container = GamificationContainer(session)

            # Antes de acceder
            loaded = container.get_loaded_services()
            assert "behavior_tracking" not in loaded

            # Acceder al servicio
            _ = container.behavior_tracking

            # Después de acceder
            loaded = container.get_loaded_services()
            assert "behavior_tracking" in loaded


class TestSyncStreakMetrics:
    """Tests para sincronización de métricas de racha."""

    @pytest.mark.asyncio
    async def test_sync_streak(self):
        """Verifica sincronización de métricas de racha."""
        async with get_session() as session:
            user = User(
                user_id=42345,
                first_name="Test",
                role=UserRole.FREE
            )
            session.add(user)
            await session.commit()

            service = BehaviorTrackingService(session)

            # Sincronizar racha
            await service.sync_streak_metrics(
                user_id=user.user_id,
                current_streak=7,
                best_streak=14
            )

            signals = await service.get_behavior_signals(user.user_id)
            assert signals.current_streak == 7
            assert signals.best_streak == 14

    @pytest.mark.asyncio
    async def test_sync_streak_preserves_best(self):
        """Verifica que sync preserva el mejor streak histórico."""
        async with get_session() as session:
            user = User(
                user_id=42346,
                first_name="Test",
                role=UserRole.FREE
            )
            session.add(user)
            await session.commit()

            service = BehaviorTrackingService(session)

            # Primera sincronización
            await service.sync_streak_metrics(
                user_id=user.user_id,
                current_streak=10,
                best_streak=10
            )

            # Segunda sincronización con streak menor pero best mayor
            await service.sync_streak_metrics(
                user_id=user.user_id,
                current_streak=3,
                best_streak=5  # Menor que el anterior
            )

            signals = await service.get_behavior_signals(user.user_id)
            assert signals.current_streak == 3
            # Best debe ser el máximo histórico
            assert signals.best_streak == 10


class TestInteractionCounts:
    """Tests para conteo de interacciones."""

    @pytest.mark.asyncio
    async def test_get_interaction_count(self):
        """Verifica conteo de interacciones."""
        async with get_session() as session:
            user = User(
                user_id=52345,
                first_name="Test",
                role=UserRole.FREE
            )
            session.add(user)
            await session.commit()

            service = BehaviorTrackingService(session)

            # Registrar interacciones
            for _ in range(5):
                await service.track_interaction(
                    user_id=user.user_id,
                    interaction_type=InteractionType.BUTTON_CLICK,
                    metadata={}
                )

            for _ in range(3):
                await service.track_interaction(
                    user_id=user.user_id,
                    interaction_type=InteractionType.TEXT_RESPONSE,
                    metadata={}
                )

            # Contar todas
            total = await service.get_interaction_count(user.user_id)
            assert total == 8

            # Contar solo botones
            buttons = await service.get_interaction_count(
                user.user_id,
                interaction_type=InteractionType.BUTTON_CLICK
            )
            assert buttons == 5

            # Contar solo texto
            text = await service.get_interaction_count(
                user.user_id,
                interaction_type=InteractionType.TEXT_RESPONSE
            )
            assert text == 3

    @pytest.mark.asyncio
    async def test_get_recent_interactions(self):
        """Verifica obtención de interacciones recientes."""
        async with get_session() as session:
            user = User(
                user_id=52346,
                first_name="Test",
                role=UserRole.FREE
            )
            session.add(user)
            await session.commit()

            service = BehaviorTrackingService(session)

            # Registrar interacciones
            for i in range(10):
                await service.track_interaction(
                    user_id=user.user_id,
                    interaction_type=InteractionType.MENU_NAVIGATION,
                    metadata={"menu": f"menu_{i}"}
                )

            # Obtener últimas 5
            recent = await service.get_recent_interactions(
                user.user_id,
                limit=5
            )
            assert len(recent) == 5

            # Verificar orden (más reciente primero)
            for i in range(len(recent) - 1):
                assert recent[i].created_at >= recent[i + 1].created_at
