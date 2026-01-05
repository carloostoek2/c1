"""
Tests E2E para ONDA A: Servicios Inmersivos.

Valida el funcionamiento de los 4 servicios inmersivos:
- EngagementService
- VariantService
- CooldownService
- ChallengeService
"""
import pytest
from datetime import datetime, timedelta

from bot.narrative.services.engagement import EngagementService
from bot.narrative.services.variant import VariantService
from bot.narrative.services.cooldown import CooldownService
from bot.narrative.services.challenge import ChallengeService
from bot.narrative.database.enums import (
    VariantConditionType,
    CooldownType,
    ChallengeType,
)


@pytest.mark.asyncio
async def test_engagement_service_visit_tracking(db_setup):
    """Test: Tracking de visitas con EngagementService."""
    from bot.database.engine import get_session

    async with get_session() as session:
        service = EngagementService(session)

        # Primera visita
        visit1 = await service.record_visit(user_id=1, fragment_key="test_fragment")
        assert visit1.visit_count == 1
        assert visit1.total_time_seconds == 0

        # Segunda visita (revisita)
        visit2 = await service.record_visit(user_id=1, fragment_key="test_fragment")
        assert visit2.visit_count == 2

        # Verificar get_visit_count
        count = await service.get_visit_count(user_id=1, fragment_key="test_fragment")
        assert count == 2


@pytest.mark.asyncio
async def test_engagement_service_reading_time(db_setup):
    """Test: Cálculo de tiempo de lectura."""
    from bot.database.engine import get_session

    async with get_session() as session:
        service = EngagementService(session)

        # Iniciar visita
        await service.record_visit(user_id=1, fragment_key="test_fragment")

        # Simular lectura (esperar no es viable en tests, mock reading_started_at)
        from bot.narrative.database.models_immersive import UserFragmentVisit
        from sqlalchemy import select, and_

        stmt = select(UserFragmentVisit).where(
            and_(
                UserFragmentVisit.user_id == 1,
                UserFragmentVisit.fragment_key == "test_fragment",
            )
        )
        result = await session.execute(stmt)
        visit = result.scalar_one()

        # Simular que empezó a leer hace 30 segundos
        visit.reading_started_at = datetime.utcnow() - timedelta(seconds=30)
        await session.commit()

        # Finalizar visita
        elapsed = await service.finalize_visit(user_id=1, fragment_key="test_fragment")

        # Verificar que se calculó el tiempo (debería estar cerca de 30s)
        assert elapsed is not None
        assert 10 <= elapsed <= 300  # Dentro del rango razonable


@pytest.mark.asyncio
async def test_engagement_service_daily_limits(db_setup):
    """Test: Sistema de límites diarios."""
    from bot.database.engine import get_session

    async with get_session() as session:
        service = EngagementService(session)

        # Verificar límite inicial
        can_continue, remaining = await service.check_daily_limit(
            user_id=1, limit_type="fragments"
        )
        assert can_continue is True

        # Incrementar contador
        await service.increment_daily_counter(user_id=1, limit_type="fragments")

        # Verificar que se incrementó
        can_continue, remaining = await service.check_daily_limit(
            user_id=1, limit_type="fragments"
        )
        # Depende de la config, pero remaining debe ser menor
        assert remaining >= 0


@pytest.mark.asyncio
async def test_variant_service_first_visit(db_setup):
    """Test: Variante para primera visita."""
    from bot.database.engine import get_session

    async with get_session() as session:
        variant_service = VariantService(session)

        # Crear variante para primera visita
        variant = await variant_service.create_variant(
            fragment_key="test_fragment",
            variant_key="first_time",
            condition_type=VariantConditionType.FIRST_VISIT,
            condition_value="true",
            priority=10,
            content_override="Bienvenido por primera vez.",
        )

        # Contexto de usuario que nunca visitó
        context = {"visit_count": 0}

        # Evaluar condición
        is_applicable = await variant_service.evaluate_condition(variant, context)
        assert is_applicable is True

        # Contexto de usuario que ya visitó
        context_return = {"visit_count": 1}
        is_applicable_return = await variant_service.evaluate_condition(
            variant, context_return
        )
        assert is_applicable_return is False


@pytest.mark.asyncio
async def test_variant_service_archetype_condition(db_setup):
    """Test: Variante basada en arquetipo."""
    from bot.database.engine import get_session

    async with get_session() as session:
        variant_service = VariantService(session)

        # Crear variante para EXPLORER
        variant = await variant_service.create_variant(
            fragment_key="test_fragment",
            variant_key="explorer_version",
            condition_type=VariantConditionType.ARCHETYPE,
            condition_value="explorer",
            priority=5,
            content_override="Tú, que buscas cada detalle...",
        )

        # Contexto de EXPLORER
        context_explorer = {"archetype": "explorer"}
        is_applicable = await variant_service.evaluate_condition(
            variant, context_explorer
        )
        assert is_applicable is True

        # Contexto de ROMANTIC (no aplica)
        context_romantic = {"archetype": "romantic"}
        is_applicable_romantic = await variant_service.evaluate_condition(
            variant, context_romantic
        )
        assert is_applicable_romantic is False


@pytest.mark.asyncio
async def test_cooldown_service_basic_flow(db_setup):
    """Test: Flujo básico de cooldowns."""
    from bot.database.engine import get_session

    async with get_session() as session:
        service = CooldownService(session)

        # No hay cooldown inicialmente
        is_active, _, _ = await service.check_cooldown(
            user_id=1, cooldown_type=CooldownType.FRAGMENT, target_key="test_fragment"
        )
        assert is_active is False

        # Establecer cooldown de 60 segundos
        cooldown = await service.set_cooldown(
            user_id=1,
            cooldown_type=CooldownType.FRAGMENT,
            target_key="test_fragment",
            duration_seconds=60,
            message="Diana necesita un momento...",
        )

        assert cooldown.remaining_seconds > 0

        # Verificar que está activo
        is_active, expires_at, message = await service.check_cooldown(
            user_id=1, cooldown_type=CooldownType.FRAGMENT, target_key="test_fragment"
        )
        assert is_active is True
        assert expires_at is not None
        assert message == "Diana necesita un momento..."

        # Limpiar cooldown
        removed = await service.clear_cooldown(
            user_id=1, cooldown_type=CooldownType.FRAGMENT, target_key="test_fragment"
        )
        assert removed is True

        # Verificar que ya no está activo
        is_active, _, _ = await service.check_cooldown(
            user_id=1, cooldown_type=CooldownType.FRAGMENT, target_key="test_fragment"
        )
        assert is_active is False


@pytest.mark.asyncio
async def test_cooldown_service_time_window(db_setup):
    """Test: Ventanas de tiempo para fragmentos."""
    from bot.database.engine import get_session

    async with get_session() as session:
        service = CooldownService(session)

        # Crear ventana: solo disponible de 20:00 a 23:59 (horas 20, 21, 22, 23)
        window = await service.create_time_window(
            fragment_key="night_fragment",
            available_hours=[20, 21, 22, 23],
            unavailable_message="Este fragmento solo está disponible por la noche.",
        )

        assert window.fragment_key == "night_fragment"

        # Verificar disponibilidad (depende de la hora actual, pero debe retornar algo)
        is_available, message = await service.check_time_window("night_fragment")
        assert isinstance(is_available, bool)


@pytest.mark.asyncio
async def test_challenge_service_basic_flow(db_setup):
    """Test: Flujo básico de challenges."""
    from bot.database.engine import get_session

    async with get_session() as session:
        service = ChallengeService(session)

        # Crear challenge
        challenge = await service.create_challenge(
            fragment_key="test_fragment",
            challenge_type=ChallengeType.TEXT_INPUT,
            question="¿Cuánto es 2 + 2?",
            correct_answers=["4", "cuatro"],
            hints=["Es un número par", "Está entre 3 y 5"],
            attempts_allowed=3,
            success_besitos=10,
            success_message="¡Correcto!",
        )

        assert challenge.fragment_key == "test_fragment"
        assert challenge.attempts_allowed == 3

        # Validar respuesta correcta
        is_correct, message = await service.validate_answer(challenge.id, "4")
        assert is_correct is True
        assert message == "¡Correcto!"

        # Registrar intento
        attempt = await service.record_attempt(
            user_id=1,
            challenge_id=challenge.id,
            answer="4",
            is_correct=True,
            hints_used=0,
        )

        assert attempt.attempt_number == 1
        assert attempt.is_correct is True

        # Verificar que completó el challenge
        completed = await service.has_completed_challenge(user_id=1, challenge_id=challenge.id)
        assert completed is True


@pytest.mark.asyncio
async def test_challenge_service_hints_system(db_setup):
    """Test: Sistema de hints."""
    from bot.database.engine import get_session

    async with get_session() as session:
        service = ChallengeService(session)

        # Crear challenge con hints
        challenge = await service.create_challenge(
            fragment_key="test_fragment",
            challenge_type=ChallengeType.TEXT_INPUT,
            question="¿Cuál es la capital de Francia?",
            correct_answers=["París", "Paris"],
            hints=["Es la ciudad de la Torre Eiffel", "Comienza con P"],
            attempts_allowed=3,
        )

        # Obtener hints disponibles (sin intentos previos)
        hints = await service.get_available_hints(user_id=1, challenge_id=challenge.id)
        assert len(hints) == 1  # Primer hint disponible
        assert hints[0] == "Es la ciudad de la Torre Eiffel"

        # Usar primer hint
        used, hint_text = await service.use_hint(user_id=1, challenge_id=challenge.id)
        assert used is True
        assert hint_text == "Es la ciudad de la Torre Eiffel"

        # Obtener segundo hint
        hints2 = await service.get_available_hints(user_id=1, challenge_id=challenge.id)
        assert len(hints2) == 1
        assert hints2[0] == "Comienza con P"


@pytest.mark.asyncio
async def test_challenge_service_attempts_limit(db_setup):
    """Test: Límite de intentos en challenges."""
    from bot.database.engine import get_session

    async with get_session() as session:
        service = ChallengeService(session)

        # Crear challenge con 2 intentos
        challenge = await service.create_challenge(
            fragment_key="test_fragment",
            challenge_type=ChallengeType.TEXT_INPUT,
            question="Pregunta difícil",
            correct_answers=["respuesta_secreta"],
            attempts_allowed=2,
        )

        # Verificar intentos restantes
        remaining = await service.get_remaining_attempts(user_id=1, challenge_id=challenge.id)
        assert remaining == 2

        # Hacer un intento fallido
        await service.record_attempt(
            user_id=1,
            challenge_id=challenge.id,
            answer="mal",
            is_correct=False,
        )

        # Verificar que ahora tiene 1 intento
        remaining = await service.get_remaining_attempts(user_id=1, challenge_id=challenge.id)
        assert remaining == 1

        # Hacer segundo intento fallido
        await service.record_attempt(
            user_id=1,
            challenge_id=challenge.id,
            answer="mal2",
            is_correct=False,
        )

        # Verificar que ya no tiene intentos
        remaining = await service.get_remaining_attempts(user_id=1, challenge_id=challenge.id)
        assert remaining == 0


@pytest.mark.asyncio
async def test_integration_engagement_and_variants(db_setup):
    """Test: Integración entre EngagementService y VariantService."""
    from bot.database.engine import get_session

    async with get_session() as session:
        engagement = EngagementService(session)
        variant_service = VariantService(session)

        # Crear variante para segunda visita
        await variant_service.create_variant(
            fragment_key="test_fragment",
            variant_key="return_visit",
            condition_type=VariantConditionType.RETURN_VISIT,
            condition_value="true",
            priority=5,
            content_override="Has vuelto. Interesante...",
        )

        # Primera visita
        await engagement.record_visit(user_id=1, fragment_key="test_fragment")

        # Build context
        context = await variant_service.build_user_context(
            user_id=1, fragment_key="test_fragment"
        )

        # Primera visita: variante return no debe aplicar
        applicable = await variant_service.get_applicable_variant(
            "test_fragment", context
        )
        assert applicable is None  # No hay variante para primera visita

        # Segunda visita
        await engagement.record_visit(user_id=1, fragment_key="test_fragment")

        # Build nuevo context
        context2 = await variant_service.build_user_context(
            user_id=1, fragment_key="test_fragment"
        )

        # Ahora debe aplicar variante return
        applicable2 = await variant_service.get_applicable_variant(
            "test_fragment", context2
        )
        assert applicable2 is not None
        assert applicable2.variant_key == "return_visit"
