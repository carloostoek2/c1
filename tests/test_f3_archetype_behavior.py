"""
Tests E2E para Fase 3 - Sistema de Arquetipos y Tracking de Comportamiento.

Prueba:
- F3.1: Modelo UserBehaviorSignals y campos de arquetipo en User
- F3.2: BehaviorTrackingService con registro de interacciones
- F3.3: ArchetypeDetectionService con algoritmo de scoring
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
from bot.gamification.services.archetype_detection import (
    ArchetypeDetectionService,
    ArchetypeResult,
    ArchetypeInsights,
    MIN_INTERACTIONS_FOR_DETECTION,
    MIN_CONFIDENCE_THRESHOLD,
)
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


# ============================================================
# F3.3: TESTS DE ARCHETYPE DETECTION SERVICE
# ============================================================

class TestArchetypeDetectionNormalize:
    """Tests para función normalize."""

    def test_normalize_in_range(self):
        """Verifica normalización de valor dentro del rango."""
        result = ArchetypeDetectionService.normalize(50, 0, 100)
        assert result == 0.5

    def test_normalize_below_min(self):
        """Verifica normalización de valor menor al mínimo."""
        result = ArchetypeDetectionService.normalize(-10, 0, 100)
        assert result == 0.0

    def test_normalize_above_max(self):
        """Verifica normalización de valor mayor al máximo."""
        result = ArchetypeDetectionService.normalize(150, 0, 100)
        assert result == 1.0

    def test_normalize_at_min(self):
        """Verifica normalización exactamente en el mínimo."""
        result = ArchetypeDetectionService.normalize(0, 0, 100)
        assert result == 0.0

    def test_normalize_at_max(self):
        """Verifica normalización exactamente en el máximo."""
        result = ArchetypeDetectionService.normalize(100, 0, 100)
        assert result == 1.0


class TestArchetypeDetectionScoring:
    """Tests para cálculo de scores de arquetipos."""

    @pytest.mark.asyncio
    async def test_explorer_score_calculation(self):
        """Verifica cálculo de score para EXPLORER."""
        async with get_session() as session:
            user = User(
                user_id=62345,
                first_name="Explorer",
                role=UserRole.FREE
            )
            session.add(user)
            await session.flush()

            # Crear señales con comportamiento explorador
            signals = UserBehaviorSignals(
                user_id=user.user_id,
                content_completion_rate=0.8,  # Alto completado
                easter_eggs_found=5,  # Encuentra secretos
                avg_time_on_content=60.0,  # Tiempo moderado
                revisits_old_content=10,  # Revisita contenido
                content_sections_visited=15,  # Muchas secciones
                total_interactions=25
            )
            session.add(signals)
            await session.commit()

            service = ArchetypeDetectionService(session)
            score = service._calculate_explorer_score(signals)

            # Score alto para comportamiento explorador
            assert score > 0.5

    @pytest.mark.asyncio
    async def test_direct_score_calculation(self):
        """Verifica cálculo de score para DIRECT."""
        async with get_session() as session:
            user = User(
                user_id=62346,
                first_name="Direct",
                role=UserRole.FREE
            )
            session.add(user)
            await session.flush()

            # Crear señales con comportamiento directo
            signals = UserBehaviorSignals(
                user_id=user.user_id,
                avg_response_time=3.0,  # Muy rápido
                avg_response_length=8.0,  # Respuestas cortas
                button_vs_text_ratio=0.9,  # Usa muchos botones
                avg_decision_time=2.0,  # Decisiones rápidas
                actions_per_session=15.0,  # Muchas acciones
                total_interactions=25
            )
            session.add(signals)
            await session.commit()

            service = ArchetypeDetectionService(session)
            score = service._calculate_direct_score(signals)

            # Score alto para comportamiento directo
            assert score > 0.5

    @pytest.mark.asyncio
    async def test_romantic_score_calculation(self):
        """Verifica cálculo de score para ROMANTIC."""
        async with get_session() as session:
            user = User(
                user_id=62347,
                first_name="Romantic",
                role=UserRole.FREE
            )
            session.add(user)
            await session.flush()

            # Crear señales con comportamiento romántico
            signals = UserBehaviorSignals(
                user_id=user.user_id,
                emotional_words_count=30,  # Muchas palabras emocionales
                long_responses_count=12,  # Respuestas largas
                personal_questions_about_diana=7,  # Preguntas personales
                avg_response_length=60.0,  # Respuestas elaboradas
                question_count=20,
                total_interactions=25
            )
            session.add(signals)
            await session.commit()

            service = ArchetypeDetectionService(session)
            score = service._calculate_romantic_score(signals)

            # Score alto para comportamiento romántico
            assert score > 0.5

    @pytest.mark.asyncio
    async def test_analytical_score_calculation(self):
        """Verifica cálculo de score para ANALYTICAL."""
        async with get_session() as session:
            user = User(
                user_id=62348,
                first_name="Analytical",
                role=UserRole.FREE
            )
            session.add(user)
            await session.flush()

            # Crear señales con comportamiento analítico
            signals = UserBehaviorSignals(
                user_id=user.user_id,
                quiz_avg_score=85.0,  # Alto rendimiento
                question_count=25,  # Muchas preguntas
                structured_responses=10,  # Respuestas estructuradas
                error_reports=3,  # Reporta errores
                total_interactions=25
            )
            session.add(signals)
            await session.commit()

            service = ArchetypeDetectionService(session)
            score = service._calculate_analytical_score(signals)

            # Score alto para comportamiento analítico
            assert score > 0.5

    @pytest.mark.asyncio
    async def test_persistent_score_calculation(self):
        """Verifica cálculo de score para PERSISTENT."""
        async with get_session() as session:
            user = User(
                user_id=62349,
                first_name="Persistent",
                role=UserRole.FREE
            )
            session.add(user)
            await session.flush()

            # Crear señales con comportamiento persistente
            signals = UserBehaviorSignals(
                user_id=user.user_id,
                return_after_inactivity=4,  # Vuelve después de ausencia
                retry_failed_actions=8,  # Reintenta acciones
                incomplete_flows_completed=3,  # Completa flujos
                first_interaction_at=datetime.now(UTC) - timedelta(days=60),  # Cuenta antigua
                total_interactions=25
            )
            session.add(signals)
            await session.commit()

            service = ArchetypeDetectionService(session)
            score = service._calculate_persistent_score(signals)

            # Score alto para comportamiento persistente
            assert score > 0.5

    @pytest.mark.asyncio
    async def test_patient_score_calculation(self):
        """Verifica cálculo de score para PATIENT."""
        async with get_session() as session:
            user = User(
                user_id=62350,
                first_name="Patient",
                role=UserRole.FREE
            )
            session.add(user)
            await session.flush()

            # Crear señales con comportamiento paciente extremo
            signals = UserBehaviorSignals(
                user_id=user.user_id,
                avg_response_time=90.0,  # Respuestas muy lentas/pensadas
                skip_actions_used=0,  # Nunca salta
                current_streak=50,  # Racha muy larga
                best_streak=70,  # Mejor racha excelente
                avg_session_duration=1500.0,  # Sesiones largas
                total_interactions=25
            )
            session.add(signals)
            await session.commit()

            service = ArchetypeDetectionService(session)
            score = service._calculate_patient_score(signals)

            # Score alto para comportamiento paciente
            assert score > 0.5


class TestArchetypeDetection:
    """Tests para detección de arquetipos."""

    @pytest.mark.asyncio
    async def test_detect_insufficient_data(self):
        """Verifica que no detecta con pocas interacciones."""
        async with get_session() as session:
            user = User(
                user_id=72345,
                first_name="New",
                role=UserRole.FREE
            )
            session.add(user)
            await session.flush()

            # Pocas interacciones
            signals = UserBehaviorSignals(
                user_id=user.user_id,
                total_interactions=5  # < MIN_INTERACTIONS_FOR_DETECTION (20)
            )
            session.add(signals)
            await session.commit()

            service = ArchetypeDetectionService(session)
            result = await service.detect_archetype(user.user_id)

            assert result.archetype is None
            assert result.reason == "insufficient_data"
            assert not result.is_detected

    @pytest.mark.asyncio
    async def test_detect_no_signals(self):
        """Verifica manejo cuando no hay señales."""
        async with get_session() as session:
            user = User(
                user_id=72346,
                first_name="NoSignals",
                role=UserRole.FREE
            )
            session.add(user)
            await session.commit()

            service = ArchetypeDetectionService(session)
            result = await service.detect_archetype(user.user_id)

            assert result.archetype is None
            assert result.reason == "no_signals"

    @pytest.mark.asyncio
    async def test_detect_explorer_archetype(self):
        """Verifica detección de arquetipo EXPLORER."""
        async with get_session() as session:
            user = User(
                user_id=72347,
                first_name="Explorer",
                role=UserRole.FREE
            )
            session.add(user)
            await session.flush()

            # Señales fuertemente exploradoras
            signals = UserBehaviorSignals(
                user_id=user.user_id,
                total_interactions=50,
                content_completion_rate=0.9,
                easter_eggs_found=8,
                avg_time_on_content=80.0,
                revisits_old_content=15,
                content_sections_visited=18,
                # Otros arquetipos con valores bajos
                avg_response_time=20.0,
                avg_response_length=20.0,
                button_vs_text_ratio=0.5,
                emotional_words_count=3,
                quiz_avg_score=50.0,
                return_after_inactivity=1,
                current_streak=5,
                first_interaction_at=datetime.now(UTC) - timedelta(days=30)
            )
            session.add(signals)
            await session.commit()

            service = ArchetypeDetectionService(session)
            result = await service.detect_archetype(user.user_id)

            # Debe detectar EXPLORER con alta confianza
            assert result.is_detected
            assert result.archetype == ArchetypeType.EXPLORER
            assert result.confidence >= MIN_CONFIDENCE_THRESHOLD

    @pytest.mark.asyncio
    async def test_detect_saves_to_user(self):
        """Verifica que la detección se guarda en el usuario."""
        async with get_session() as session:
            user = User(
                user_id=72348,
                first_name="Test",
                role=UserRole.FREE
            )
            session.add(user)
            await session.flush()

            # Señales para DIRECT
            signals = UserBehaviorSignals(
                user_id=user.user_id,
                total_interactions=30,
                avg_response_time=2.0,
                avg_response_length=5.0,
                button_vs_text_ratio=0.95,
                avg_decision_time=1.5,
                actions_per_session=18.0,
                # Otros bajos
                content_completion_rate=0.2,
                easter_eggs_found=0,
                emotional_words_count=1,
                quiz_avg_score=40.0,
                return_after_inactivity=0,
                current_streak=2,
                first_interaction_at=datetime.now(UTC) - timedelta(days=10)
            )
            session.add(signals)
            await session.commit()

            service = ArchetypeDetectionService(session)
            result = await service.detect_archetype(user.user_id)

            # Refrescar usuario
            await session.refresh(user)

            # Verificar que se guardó
            assert user.archetype is not None
            assert user.archetype_confidence is not None
            assert user.archetype_scores is not None
            assert user.archetype_detected_at is not None

    @pytest.mark.asyncio
    async def test_get_archetype_without_recalculate(self):
        """Verifica get_archetype retorna sin recalcular."""
        async with get_session() as session:
            user = User(
                user_id=72349,
                first_name="Cached",
                role=UserRole.FREE,
                archetype=ArchetypeType.ROMANTIC,
                archetype_confidence=0.75
            )
            session.add(user)
            await session.commit()

            service = ArchetypeDetectionService(session)
            archetype = await service.get_archetype(user.user_id)

            assert archetype == ArchetypeType.ROMANTIC

    @pytest.mark.asyncio
    async def test_get_archetype_scores(self):
        """Verifica obtención de scores guardados."""
        async with get_session() as session:
            scores = {
                "explorer": 0.7,
                "direct": 0.3,
                "romantic": 0.5,
            }
            user = User(
                user_id=72350,
                first_name="WithScores",
                role=UserRole.FREE,
                archetype_scores=scores
            )
            session.add(user)
            await session.commit()

            service = ArchetypeDetectionService(session)
            result = await service.get_archetype_scores(user.user_id)

            assert result == scores


class TestArchetypeReevaluation:
    """Tests para lógica de re-evaluación."""

    @pytest.mark.asyncio
    async def test_should_reevaluate_no_archetype(self):
        """Verifica que re-evalúa si no tiene arquetipo."""
        async with get_session() as session:
            user = User(
                user_id=82345,
                first_name="NoArchetype",
                role=UserRole.FREE,
                archetype=None
            )
            session.add(user)
            await session.commit()

            service = ArchetypeDetectionService(session)
            should = await service.should_reevaluate(user.user_id)

            assert should is True

    @pytest.mark.asyncio
    async def test_should_reevaluate_old_detection(self):
        """Verifica que re-evalúa si la detección es antigua."""
        async with get_session() as session:
            user = User(
                user_id=82346,
                first_name="OldDetection",
                role=UserRole.FREE,
                archetype=ArchetypeType.EXPLORER,
                archetype_confidence=0.8,
                archetype_detected_at=datetime.now(UTC) - timedelta(days=10),  # > 7 días
                archetype_version=1
            )
            session.add(user)
            await session.commit()

            service = ArchetypeDetectionService(session)
            should = await service.should_reevaluate(user.user_id)

            assert should is True

    @pytest.mark.asyncio
    async def test_should_not_reevaluate_recent(self):
        """Verifica que no re-evalúa si la detección es reciente."""
        async with get_session() as session:
            user = User(
                user_id=82347,
                first_name="RecentDetection",
                role=UserRole.FREE,
                archetype=ArchetypeType.DIRECT,
                archetype_confidence=0.8,
                archetype_detected_at=datetime.now(UTC) - timedelta(days=2),  # < 7 días
                archetype_version=1
            )
            session.add(user)
            await session.commit()

            service = ArchetypeDetectionService(session)
            should = await service.should_reevaluate(user.user_id)

            assert should is False

    @pytest.mark.asyncio
    async def test_force_reevaluation(self):
        """Verifica que force_reevaluation recalcula."""
        async with get_session() as session:
            user = User(
                user_id=82348,
                first_name="ForceReval",
                role=UserRole.FREE,
                archetype=ArchetypeType.EXPLORER,
                archetype_confidence=0.5
            )
            session.add(user)
            await session.flush()

            # Cambiar señales a PATIENT
            signals = UserBehaviorSignals(
                user_id=user.user_id,
                total_interactions=40,
                avg_response_time=90.0,
                skip_actions_used=0,
                current_streak=50,
                best_streak=60,
                avg_session_duration=1200.0,
                # Otros bajos
                content_completion_rate=0.2,
                easter_eggs_found=0,
                emotional_words_count=1,
                quiz_avg_score=40.0,
                button_vs_text_ratio=0.5,
                first_interaction_at=datetime.now(UTC) - timedelta(days=90)
            )
            session.add(signals)
            await session.commit()

            service = ArchetypeDetectionService(session)
            result = await service.force_reevaluation(user.user_id)

            # Debe cambiar de EXPLORER a PATIENT
            assert result.is_detected
            assert result.archetype == ArchetypeType.PATIENT


class TestArchetypeInsights:
    """Tests para ArchetypeInsights."""

    @pytest.mark.asyncio
    async def test_get_insights_with_archetype(self):
        """Verifica obtención de insights con arquetipo."""
        async with get_session() as session:
            user = User(
                user_id=92345,
                first_name="WithInsights",
                role=UserRole.FREE,
                archetype=ArchetypeType.ANALYTICAL,
                archetype_confidence=0.85,
                archetype_scores={
                    "analytical": 0.85,
                    "explorer": 0.45,
                    "direct": 0.30,
                    "romantic": 0.20,
                    "persistent": 0.15,
                    "patient": 0.10
                },
                archetype_detected_at=datetime.now(UTC)
            )
            session.add(user)
            await session.flush()

            signals = UserBehaviorSignals(
                user_id=user.user_id,
                total_interactions=100,
                quiz_avg_score=90.0,
                structured_responses=12,
                question_count=25
            )
            session.add(signals)
            await session.commit()

            service = ArchetypeDetectionService(session)
            insights = await service.get_archetype_insights(user.user_id)

            assert insights.current_archetype == ArchetypeType.ANALYTICAL
            assert insights.confidence == 0.85
            assert len(insights.top_archetypes) == 3
            assert insights.total_interactions == 100
            assert len(insights.key_behaviors) > 0

    @pytest.mark.asyncio
    async def test_get_insights_no_archetype(self):
        """Verifica insights cuando no hay arquetipo."""
        async with get_session() as session:
            user = User(
                user_id=92346,
                first_name="NoInsights",
                role=UserRole.FREE
            )
            session.add(user)
            await session.commit()

            service = ArchetypeDetectionService(session)
            insights = await service.get_archetype_insights(user.user_id)

            assert insights.current_archetype is None
            assert insights.confidence == 0.0
            assert len(insights.top_archetypes) == 0


class TestArchetypeDistribution:
    """Tests para estadísticas de distribución."""

    @pytest.mark.asyncio
    async def test_get_distribution(self):
        """Verifica obtención de distribución de arquetipos."""
        async with get_session() as session:
            # Crear usuarios con diferentes arquetipos
            users = [
                User(user_id=102345, first_name="E1", role=UserRole.FREE, archetype=ArchetypeType.EXPLORER),
                User(user_id=102346, first_name="E2", role=UserRole.FREE, archetype=ArchetypeType.EXPLORER),
                User(user_id=102347, first_name="D1", role=UserRole.FREE, archetype=ArchetypeType.DIRECT),
                User(user_id=102348, first_name="R1", role=UserRole.FREE, archetype=ArchetypeType.ROMANTIC),
                User(user_id=102349, first_name="N1", role=UserRole.FREE, archetype=None),
            ]
            for u in users:
                session.add(u)
            await session.commit()

            service = ArchetypeDetectionService(session)
            distribution = await service.get_archetype_distribution()

            assert distribution["explorer"] == 2
            assert distribution["direct"] == 1
            assert distribution["romantic"] == 1
            # Sin arquetipo no cuenta
            assert distribution["analytical"] == 0

    @pytest.mark.asyncio
    async def test_get_unclassified_count(self):
        """Verifica conteo de usuarios sin clasificar."""
        async with get_session() as session:
            users = [
                User(user_id=112345, first_name="C1", role=UserRole.FREE, archetype=ArchetypeType.EXPLORER),
                User(user_id=112346, first_name="U1", role=UserRole.FREE, archetype=None),
                User(user_id=112347, first_name="U2", role=UserRole.FREE, archetype=None),
            ]
            for u in users:
                session.add(u)
            await session.commit()

            service = ArchetypeDetectionService(session)
            count = await service.get_unclassified_count()

            assert count >= 2  # Al menos los 2 que creamos


class TestArchetypeContainerIntegration:
    """Tests de integración con GamificationContainer."""

    @pytest.mark.asyncio
    async def test_archetype_detection_via_container(self):
        """Verifica acceso a ArchetypeDetectionService via container."""
        async with get_session() as session:
            container = GamificationContainer(session)

            # Verificar que el servicio está disponible
            service = container.archetype_detection
            assert service is not None
            assert isinstance(service, ArchetypeDetectionService)

            # Verificar lazy loading (misma instancia)
            service2 = container.archetype_detection
            assert service is service2

    @pytest.mark.asyncio
    async def test_container_tracks_archetype_service(self):
        """Verifica que container reporta archetype_detection como cargado."""
        async with get_session() as session:
            container = GamificationContainer(session)

            # Antes de acceder
            loaded = container.get_loaded_services()
            assert "archetype_detection" not in loaded

            # Acceder al servicio
            _ = container.archetype_detection

            # Después de acceder
            loaded = container.get_loaded_services()
            assert "archetype_detection" in loaded
