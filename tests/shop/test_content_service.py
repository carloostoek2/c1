"""
Tests para ContentService (CMS Journey).

Prueba la funcionalidad completa del servicio de gestión de Content Sets.
"""

import pytest
from datetime import datetime, UTC
from unittest.mock import AsyncMock, Mock

from bot.database import init_db, close_db, get_session
from bot.shop.services.content_service import ContentService
from bot.shop.database.enums import ContentType, ContentTier
from bot.database.models import User


@pytest.fixture(autouse=True)
async def setup_db():
    """Setup y teardown de BD para cada test."""
    await init_db()
    yield
    await close_db()


@pytest.fixture
async def session():
    """Proporciona sesión de BD."""
    async with get_session() as sess:
        yield sess


@pytest.fixture
def mock_bot():
    """Mock del bot de Telegram para ContentService."""
    bot = Mock()
    bot.send_message = AsyncMock()
    bot.send_photo = AsyncMock()
    bot.send_video = AsyncMock()
    bot.send_audio = AsyncMock()
    return bot


@pytest.fixture
def content_service(session, mock_bot):
    """Proporciona instancia de ContentService."""
    return ContentService(session, mock_bot)


@pytest.fixture
async def sample_content_set(content_service):
    """Crea un content set de prueba."""
    return await content_service.create_content_set(
        slug="test-gallery",
        name="Galería de Test",
        content_type=ContentType.PHOTO_SET,
        file_ids=["AgACAgIAAxkBAAI...", "AgACAgIAAxkBAAI..."],
        description="Galería para pruebas",
        tier=ContentTier.FREE,
        category="test",
        is_active=True,
        created_by=1
    )


@pytest.fixture
async def sample_user(session):
    """Crea usuario de prueba."""
    user = User(user_id=99999, username="test_content_user")
    session.add(user)
    await session.commit()
    return user


# ============================================================
# TESTS CRUD
# ============================================================

@pytest.mark.asyncio
async def test_create_content_set(content_service):
    """Test: Crear un content set nuevo."""
    content_set = await content_service.create_content_set(
        slug="my-gallery",
        name="Mi Galería",
        content_type=ContentType.PHOTO_SET,
        file_ids=["file1", "file2"],
        description="Fotos personales",
        tier=ContentTier.VIP,
        category="personal"
    )

    assert content_set is not None
    assert content_set.slug == "my-gallery"
    assert content_set.name == "Mi Galería"
    assert content_set.content_type == ContentType.PHOTO_SET.value
    assert content_set.tier == ContentTier.VIP.value
    assert content_set.file_ids == ["file1", "file2"]
    assert content_set.is_active is True


@pytest.mark.asyncio
async def test_create_content_set_duplicate_slug(content_service, sample_content_set):
    """Test: Error al crear con slug duplicado."""
    with pytest.raises(ValueError, match="Slug .* ya está en uso"):
        await content_service.create_content_set(
            slug="test-gallery",
            name="Otro Nombre",
            content_type=ContentType.VIDEO,
            file_ids=["file1"]
        )


@pytest.mark.asyncio
async def test_get_content_set_by_id(content_service, sample_content_set):
    """Test: Obtener content set por ID."""
    found = await content_service.get_content_set(set_id=sample_content_set.id)

    assert found is not None
    assert found.id == sample_content_set.id
    assert found.slug == "test-gallery"


@pytest.mark.asyncio
async def test_get_content_set_by_slug(content_service, sample_content_set):
    """Test: Obtener content set por slug."""
    found = await content_service.get_content_set(slug="test-gallery")

    assert found is not None
    assert found.slug == "test-gallery"


@pytest.mark.asyncio
async def test_get_content_set_not_found(content_service):
    """Test: Content set no encontrado."""
    result = await content_service.get_content_set(set_id=99999)
    assert result is None

    result = await content_service.get_content_set(slug="nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_list_content_sets_all(content_service):
    """Test: Listar todos los content sets."""
    await content_service.create_content_set("set1", "Set 1", ContentType.PHOTO_SET, ["f1"])
    await content_service.create_content_set("set2", "Set 2", ContentType.VIDEO, ["v1"])

    all_sets = await content_service.list_content_sets()

    assert len(all_sets) >= 3  # 2 nuevos + 1 del fixture


@pytest.mark.asyncio
async def test_update_content_set(content_service, sample_content_set):
    """Test: Actualizar content set."""
    updated = await content_service.update_content_set(
        sample_content_set.id,
        name="Nombre Actualizado"
    )

    assert updated.name == "Nombre Actualizado"
    assert updated.slug == "test-gallery"


@pytest.mark.asyncio
async def test_delete_content_set_soft(content_service, sample_content_set):
    """Test: Soft delete de content set."""
    result = await content_service.delete_content_set(
        sample_content_set.id,
        soft_delete=True
    )

    assert result is True

    deleted = await content_service.get_content_set(sample_content_set.id)
    assert deleted is not None
    assert deleted.is_active is False


@pytest.mark.asyncio
async def test_track_content_access(content_service, sample_content_set, sample_user):
    """Test: Registrar acceso de usuario a content set."""
    access = await content_service.track_content_access(
        user_id=sample_user.user_id,
        content_set_id=sample_content_set.id,
        delivery_context="shop_purchase",
        trigger_type="automatic"
    )

    assert access is not None
    assert access.user_id == sample_user.user_id
    assert access.content_set_id == sample_content_set.id


@pytest.mark.asyncio
async def test_get_content_set_stats(content_service, sample_content_set, sample_user):
    """Test: Obtener estadísticas de content set."""
    await content_service.track_content_access(
        sample_user.user_id,
        sample_content_set.id,
        "shop_purchase",
        "automatic"
    )

    stats = await content_service.get_content_set_stats(sample_content_set.id)

    assert stats["total_access"] == 1
    assert stats["content_set_id"] == sample_content_set.id


@pytest.mark.asyncio
async def test_add_file_to_content_set(content_service, sample_content_set):
    """Test: Agregar archivo a content set existente."""
    initial_count = len(sample_content_set.file_ids)

    result = await content_service.add_file_to_content_set(
        sample_content_set.id,
        "new_file_id"
    )

    assert result is True

    updated = await content_service.get_content_set(sample_content_set.id)
    assert len(updated.file_ids) == initial_count + 1


@pytest.mark.asyncio
async def test_content_set_lifecycle(content_service):
    """Test: Ciclo de vida completo de un content set."""
    # 1. Crear
    cs = await content_service.create_content_set(
        "lifecycle", "Lifecycle Test", ContentType.PHOTO_SET, ["f1"]
    )
    assert cs.is_active is True

    # 2. Soft delete
    await content_service.delete_content_set(cs.id, soft_delete=True)
    cs = await content_service.get_content_set(cs.id)
    assert cs.is_active is False

    # 3. Hard delete
    await content_service.delete_content_set(cs.id, soft_delete=False)
    cs = await content_service.get_content_set(cs.id)
    assert cs is None
