# Plan de Implementación: CMS Journey para C1

## Resumen Ejecutivo

Implementar el sistema CMS Journey del proyecto viejo (bolt_ok/mybot) en el nuevo sistema C1, enfocándose en el **CMS de contenido multimedia (ContentSets)** con integración completa en los sistemas existentes de gamificación, narrativa y shop, aprovechando el wizard de configuración en cascada.

---

## 1. Arquitectura de Modelos

### 1.1 Modelo Principal: ContentSet

**Ubicación**: `c1/bot/shop/database/models.py` (extender módulo shop existente)

**Justificación**: Los ContentSets son productos digitales que se venden/regalan, similar a los ShopItems. Aprovechar la infraestructura existente del shop reduce duplicación.

**Modelo ContentSet**:

```python
class ContentSet(Base):
    __tablename__ = "content_sets"

    # Identificación
    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Clasificación
    content_type = Column(Enum(ContentType), nullable=False)  # photo_set, video, audio, mixed
    category = Column(String(50), nullable=True)  # teaser, welcome, milestone, gift
    tier = Column(Enum(ContentTier), default=ContentTier.FREE)  # free, vip, premium

    # Contenido multimedia (Telegram file_ids)
    file_ids = Column(JSON, default=list)  # ["file_id_1", "file_id_2", ...]
    file_metadata = Column(JSON, default=dict)  # {"file_id_1": {"type": "photo", "caption": "..."}}

    # Control de acceso
    is_active = Column(Boolean, default=True)
    requires_vip = Column(Boolean, default=False)

    # Metadatos
    created_by = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    shop_items = relationship("ShopItem", back_populates="content_set")
    narrative_fragments = relationship("NarrativeFragment", back_populates="content_set")
    user_content_access = relationship("UserContentAccess", back_populates="content_set")

    __table_args__ = (
        Index('idx_content_slug', 'slug'),
        Index('idx_content_type_tier', 'content_type', 'tier'),
        Index('idx_content_active', 'is_active'),
    )
```

**Enums Nuevos** en `c1/bot/shop/database/enums.py`:

```python
class ContentType(str, Enum):
    PHOTO_SET = "photo_set"
    VIDEO = "video"
    AUDIO = "audio"
    MIXED = "mixed"

class ContentTier(str, Enum):
    FREE = "free"
    VIP = "vip"
    PREMIUM = "premium"
    GIFT = "gift"
```

### 1.2 Modelo de Tracking: UserContentAccess

**Ubicación**: `c1/bot/shop/database/models.py`

**Propósito**: Auditoría de qué contenido se entregó a qué usuarios y cuándo.

```python
class UserContentAccess(Base):
    __tablename__ = "user_content_access"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    content_set_id = Column(Integer, ForeignKey("content_sets.id"), nullable=False)

    # Tracking
    accessed_at = Column(DateTime, default=func.now())
    delivery_context = Column(String(100), nullable=True)  # "shop_purchase", "reward_claim", "gift", "narrative"
    trigger_type = Column(String(50), nullable=True)  # "manual", "automatic", "achievement"

    # Relationships
    user = relationship("User", back_populates="content_access")
    content_set = relationship("ContentSet", back_populates="user_content_access")

    __table_args__ = (
        Index('idx_user_content', 'user_id', 'content_set_id'),
        Index('idx_accessed_at', 'accessed_at'),
    )
```

### 1.3 Extensión de ShopItem

**Ubicación**: `c1/bot/shop/database/models.py`

**Modificación**: Agregar relación con ContentSet

```python
class ShopItem(Base):
    # ... campos existentes ...

    # NUEVO: Vinculación con content set
    content_set_id = Column(Integer, ForeignKey("content_sets.id"), nullable=True)

    # NUEVO: Relationship
    content_set = relationship("ContentSet", back_populates="shop_items")
```

**ItemType Nuevo** en `c1/bot/shop/database/enums.py`:

```python
class ItemType(str, Enum):
    # ... existentes ...
    CONTENT_SET = "content_set"  # NUEVO
```

### 1.4 Extensión de NarrativeFragment

**Ubicación**: `c1/bot/narrative/database/models.py`

**Modificación**: Agregar vinculación con ContentSet

```python
class NarrativeFragment(Base):
    # ... campos existentes ...

    # NUEVO: Contenido multimedia opcional
    content_set_id = Column(Integer, ForeignKey("content_sets.id"), nullable=True)
    auto_send_content = Column(Boolean, default=True)  # Enviar automáticamente al navegar

    # NUEVO: Relationship
    content_set = relationship("ContentSet", back_populates="narrative_fragments")
```

### 1.5 Extensión de Reward

**Ubicación**: `c1/bot/gamification/database/models.py`

**Modificación**: Agregar soporte para content sets como recompensa

```python
class Reward(Base):
    # ... campos existentes ...

    # NUEVO: Vinculación con content set
    content_set_id = Column(Integer, ForeignKey("content_sets.id"), nullable=True)

    # NUEVO: Relationship
    content_set = relationship("ContentSet")
```

**RewardType Nuevo** en `c1/bot/gamification/database/enums.py`:

```python
class RewardType(str, Enum):
    # ... existentes ...
    CONTENT_SET = "content_set"  # NUEVO
```

---

## 2. Servicios

### 2.1 ContentService

**Ubicación**: `c1/bot/shop/services/content_service.py` (NUEVO)

**Responsabilidades**:
- CRUD de ContentSets
- Envío de contenido multimedia a usuarios
- Tracking de acceso
- Validación de permisos (VIP)

**Métodos Principales**:

```python
class ContentService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_content_set(
        self,
        slug: str,
        name: str,
        content_type: ContentType,
        file_ids: List[str],
        description: str = None,
        tier: ContentTier = ContentTier.FREE,
        created_by: int = None
    ) -> ContentSet

    async def get_content_set(self, set_id: int = None, slug: str = None) -> Optional[ContentSet]

    async def list_content_sets(
        self,
        tier: ContentTier = None,
        content_type: ContentType = None,
        is_active: bool = True
    ) -> List[ContentSet]

    async def send_content_set(
        self,
        user_id: int,
        content_set_id: int,
        bot: Bot,
        context_message: str = None,
        delivery_context: str = "manual",
        trigger_type: str = "manual"
    ) -> bool

    async def track_content_access(
        self,
        user_id: int,
        content_set_id: int,
        delivery_context: str,
        trigger_type: str
    ) -> UserContentAccess

    async def update_content_set(self, set_id: int, **kwargs) -> ContentSet

    async def delete_content_set(self, set_id: int, soft_delete: bool = True) -> bool
```

### 2.2 Extensión de ShopService

**Ubicación**: `c1/bot/shop/services/shop_service.py`

**Modificaciones**: Agregar lógica de entrega de content sets

```python
class ShopService:
    # ... métodos existentes ...

    async def _deliver_content_set(
        self,
        bot: Bot,
        user_id: int,
        item: ShopItem
    ) -> bool:
        """Entrega contenido multimedia al comprar item con content_set."""
        if not item.content_set_id:
            return False

        from bot.shop.services.content_service import ContentService
        content_service = ContentService(self.session)

        success = await content_service.send_content_set(
            user_id=user_id,
            content_set_id=item.content_set_id,
            bot=bot,
            context_message=f"🎁 ¡Gracias por tu compra de **{item.name}**!",
            delivery_context="shop_purchase",
            trigger_type="automatic"
        )

        return success
```

### 2.3 Extensión de FragmentService

**Ubicación**: `c1/bot/narrative/services/fragment_service.py`

**Modificaciones**: Enviar content sets al navegar fragmentos

```python
class FragmentService:
    # ... métodos existentes ...

    async def navigate_to_fragment(
        self,
        user_id: int,
        fragment_id: int,
        bot: Bot
    ) -> dict:
        """Navega a fragmento y envía content set si existe."""
        fragment = await self.get_fragment(fragment_id)

        # ... lógica existente de navegación ...

        # NUEVO: Enviar content set si existe
        if fragment.content_set_id and fragment.auto_send_content:
            from bot.shop.services.content_service import ContentService
            content_service = ContentService(self.session)

            await content_service.send_content_set(
                user_id=user_id,
                content_set_id=fragment.content_set_id,
                bot=bot,
                delivery_context="narrative",
                trigger_type="automatic"
            )

        return {...}
```

### 2.4 Extensión de RewardService

**Ubicación**: `c1/bot/gamification/services/reward_service.py`

**Modificaciones**: Manejar content sets como recompensas

```python
class RewardService:
    # ... métodos existentes ...

    async def claim_reward(
        self,
        user_id: int,
        reward_id: int,
        bot: Bot = None
    ) -> tuple[bool, str]:
        """Canjea recompensa, incluyendo content sets."""
        # ... validaciones existentes ...

        # NUEVO: Manejar content set
        if reward.reward_type == RewardType.CONTENT_SET and reward.content_set_id:
            if not bot:
                return (False, "Bot instance required for content delivery")

            from bot.shop.services.content_service import ContentService
            content_service = ContentService(self.session)

            success = await content_service.send_content_set(
                user_id=user_id,
                content_set_id=reward.content_set_id,
                bot=bot,
                delivery_context="reward_claim",
                trigger_type="automatic"
            )

            if not success:
                return (False, "Failed to deliver content")

        # ... resto de lógica ...
```

### 2.5 Extensión de ServiceContainer

**Ubicación**: `c1/bot/services/container.py`

**Modificación**: Agregar lazy loading de ContentService

```python
class ServiceContainer:
    # ... existente ...

    @property
    def content(self) -> ContentService:
        """Lazy-loaded ContentService."""
        if not hasattr(self, '_content'):
            from bot.shop.services.content_service import ContentService
            self._content = ContentService(self.session)
        return self._content
```

---

## 3. Wizard de Configuración

### 3.1 Wizard Inline de ContentSet

**Ubicación**: `c1/bot/gamification/handlers/admin/unified_wizard.py`

**Integración**: Agregar wizard inline para ContentSets (similar a wizard de capítulos)

**Estados Nuevos** en `c1/bot/gamification/states/admin.py`:

```python
class UnifiedWizardStates(StatesGroup):
    # ... estados existentes ...

    # NUEVOS: ContentSet wizard
    content_enter_slug = State()
    content_enter_name = State()
    content_enter_description = State()
    content_select_type = State()
    content_select_tier = State()
    content_upload_files = State()
    content_add_more_files = State()
    content_confirm = State()
```

**Handlers Nuevos** en `unified_wizard.py`:

```python
# Agregar botón en menú principal
async def _show_unified_menu(message: Message, is_edit: bool = False):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        # ... botones existentes ...
        [
            InlineKeyboardButton(
                text="🎬 Crear Content Set",
                callback_data="unified:create:content"
            )
        ],
        # ...
    ])

# Handler: Iniciar wizard
@router.callback_query(F.data == "unified:create:content")
async def start_content_wizard(callback: CallbackQuery, state: FSMContext):
    """Inicia wizard de creación de ContentSet."""
    await state.clear()
    await callback.message.edit_text(
        "🎬 <b>Wizard: Crear Content Set</b>\n\n"
        "Paso 1/7: Ingresa un slug único (ej: day-1-welcome)\n\n"
        "<i>Solo minúsculas, números y guiones</i>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Cancelar", callback_data="unified:wizard:menu")]
        ])
    )
    await state.set_state(UnifiedWizardStates.content_enter_slug)

# Pasos 2-6: Similar a wizard de capítulos
# ...

# Handler: Confirmar y crear
@router.callback_query(UnifiedWizardStates.content_confirm, F.data == "unified:content:confirm")
async def confirm_content_set(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Crea el ContentSet."""
    data = await state.get_data()

    try:
        from bot.shop.services.content_service import ContentService
        content_service = ContentService(session)

        content_set = await content_service.create_content_set(
            slug=data['content_slug'],
            name=data['content_name'],
            description=data.get('content_description'),
            content_type=ContentType(data['content_type']),
            tier=ContentTier(data['content_tier']),
            file_ids=data['file_ids'],
            created_by=callback.from_user.id
        )

        await callback.message.edit_text(
            f"✅ <b>Content Set Creado</b>\n\n"
            f"<b>{content_set.name}</b>\n"
            f"Slug: <code>{content_set.slug}</code>\n"
            f"Tipo: {content_set.content_type.value}\n"
            f"Tier: {content_set.tier.value}\n"
            f"Archivos: {len(content_set.file_ids)}\n\n"
            f"El content set está ahora disponible para vincularlo en:\n"
            f"• 🛒 Items de tienda\n"
            f"• 🎁 Recompensas\n"
            f"• 📖 Fragmentos narrativos",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Volver", callback_data="unified:wizard:menu")]
            ])
        )

        await session.commit()
        await state.clear()

    except Exception as e:
        logger.error(f"Error creating content set: {e}", exc_info=True)
        await callback.message.edit_text(
            f"❌ <b>Error al crear Content Set</b>\n\n{str(e)}",
            parse_mode="HTML"
        )
```

### 3.2 Integración con Mission Wizard

**Ubicación**: `c1/bot/gamification/handlers/admin/mission_wizard.py`

**Modificación**: Agregar opción de content set como recompensa

```python
# En el paso de "choose_rewards", agregar botón
keyboard = InlineKeyboardMarkup(inline_keyboard=[
    # ... botones existentes ...
    [
        InlineKeyboardButton(
            text="🎬 Content Set",
            callback_data="wizard:content:start"
        )
    ],
    # ...
])

# Handler: Seleccionar content set
@router.callback_query(MissionWizardStates.choose_rewards, F.data == "wizard:content:start")
async def select_content_set_reward(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Muestra lista de content sets disponibles."""
    from bot.shop.services.content_service import ContentService
    content_service = ContentService(session)

    content_sets = await content_service.list_content_sets(is_active=True)

    keyboard_rows = []
    for cs in content_sets:
        keyboard_rows.append([
            InlineKeyboardButton(
                text=f"{cs.name} ({cs.tier.value})",
                callback_data=f"wizard:content:select:{cs.id}"
            )
        ])

    keyboard_rows.append([
        InlineKeyboardButton(text="🔙 Volver", callback_data="wizard:rewards:back")
    ])

    await callback.message.edit_text(
        "🎬 <b>Seleccionar Content Set</b>\n\n"
        "Elige el content set que se otorgará como recompensa:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    )

@router.callback_query(MissionWizardStates.choose_rewards, F.data.startswith("wizard:content:select:"))
async def confirm_content_set_reward(callback: CallbackQuery, state: FSMContext):
    """Confirma selección de content set."""
    content_set_id = int(callback.data.split(":")[-1])

    data = await state.get_data()
    rewards = data.get('rewards', [])
    rewards.append({
        'mode': 'create',
        'data': {
            'name': f"Content Set #{content_set_id}",
            'description': "Content multimedia exclusivo",
            'reward_type': RewardType.CONTENT_SET,
            'metadata': {
                'content_set_id': content_set_id
            }
        }
    })
    await state.update_data(rewards=rewards)

    # Volver a menú de recompensas
    # ...
```

### 3.3 Integración con Reward Wizard

**Ubicación**: `c1/bot/gamification/handlers/admin/reward_wizard.py`

**Modificación**: Agregar RewardType.CONTENT_SET como opción

```python
# En el paso de selección de tipo
keyboard = InlineKeyboardMarkup(inline_keyboard=[
    # ... tipos existentes ...
    [
        InlineKeyboardButton(
            text="🎬 Content Set",
            callback_data="reward:type:content_set"
        )
    ],
    # ...
])

# Si selecciona content_set, mostrar lista para elegir
```

### 3.4 Integración con Shop Item Wizard

**Ubicación**: `c1/bot/gamification/handlers/admin/unified_wizard.py`

**Modificación**: Agregar paso opcional para vincular content set

```python
# En el wizard de shop item, después de seleccionar tipo
@router.callback_query(UnifiedWizardStates.shop_item_select_type, F.data == "unified:item:type:content_set")
async def shop_item_type_content_set(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Usuario eligió tipo CONTENT_SET, mostrar lista."""
    await state.update_data(item_type=ItemType.CONTENT_SET)

    from bot.shop.services.content_service import ContentService
    content_service = ContentService(session)

    content_sets = await content_service.list_content_sets(is_active=True)

    keyboard_rows = []
    for cs in content_sets:
        keyboard_rows.append([
            InlineKeyboardButton(
                text=f"{cs.name} ({cs.tier.value})",
                callback_data=f"unified:item:content:{cs.id}"
            )
        ])

    await callback.message.edit_text(
        "🛒 <b>Wizard: Crear Item de Tienda</b>\n\n"
        "Paso 3/7: Selecciona el Content Set que otorgará este item:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    )
    await state.set_state(UnifiedWizardStates.shop_item_enter_name)
```

### 3.5 Integración con Chapter Wizard

**Ubicación**: `c1/bot/gamification/handlers/admin/unified_wizard.py`

**Modificación**: Agregar paso opcional para vincular content set a capítulos

```python
# Después de crear el capítulo, preguntar si quiere agregar content set
@router.callback_query(UnifiedWizardStates.chapter_confirm, F.data == "unified:chapter:add_content")
async def chapter_add_content_set(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Permite vincular content set al capítulo."""
    from bot.shop.services.content_service import ContentService
    content_service = ContentService(session)

    content_sets = await content_service.list_content_sets(is_active=True)

    # Mostrar lista similar a otros wizards
    # ...
```

---

## 4. Admin Handlers

### 4.1 Panel de Gestión de Content Sets

**Ubicación**: `c1/bot/shop/handlers/admin/content_admin.py` (NUEVO)

**Funcionalidades**:
- Listar content sets (con paginación)
- Ver detalles de content set
- Editar content set
- Eliminar content set (soft delete)
- Enviar content set a usuario (testing)
- Estadísticas de uso

**Handler Principal**:

```python
router = Router(name="content_admin")
router.message.middleware(DatabaseMiddleware())
router.message.middleware(AdminAuthMiddleware())
router.callback_query.middleware(DatabaseMiddleware())
router.callback_query.middleware(AdminAuthMiddleware())

@router.callback_query(F.data == "admin:content")
async def show_content_menu(callback: CallbackQuery, session: AsyncSession):
    """Muestra menú principal de gestión de content sets."""
    from bot.shop.services.content_service import ContentService
    content_service = ContentService(session)

    content_sets = await content_service.list_content_sets()
    total_active = len([cs for cs in content_sets if cs.is_active])

    text = (
        "🎬 <b>Gestión de Content Sets</b>\n\n"
        f"📊 <b>Total:</b> {len(content_sets)}\n"
        f"✅ <b>Activos:</b> {total_active}\n\n"
        "Selecciona una opción:"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Listar Content Sets", callback_data="admin:content:list:1")],
        [InlineKeyboardButton(text="➕ Crear Content Set", callback_data="unified:create:content")],
        [InlineKeyboardButton(text="📊 Estadísticas", callback_data="admin:content:stats")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:main")]
    ])

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)

# Handlers adicionales para listar, editar, eliminar, etc.
```

---

## 5. Migraciones de Base de Datos

### 5.1 Migración: Crear Tablas de Content Sets

**Ubicación**: `c1/migrations/add_content_sets.py` (NUEVO)

```python
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

def upgrade():
    # Crear tabla content_sets
    op.create_table(
        'content_sets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('content_type', sa.String(20), nullable=False),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('tier', sa.String(20), nullable=False),
        sa.Column('file_ids', sa.JSON(), nullable=False),
        sa.Column('file_metadata', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('requires_vip', sa.Boolean(), default=False),
        sa.Column('created_by', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.Index('idx_content_slug', 'slug'),
        sa.Index('idx_content_type_tier', 'content_type', 'tier'),
        sa.Index('idx_content_active', 'is_active'),
    )

    # Crear tabla user_content_access
    op.create_table(
        'user_content_access',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('content_set_id', sa.Integer(), nullable=False),
        sa.Column('accessed_at', sa.DateTime(), nullable=False),
        sa.Column('delivery_context', sa.String(100), nullable=True),
        sa.Column('trigger_type', sa.String(50), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['content_set_id'], ['content_sets.id']),
        sa.Index('idx_user_content', 'user_id', 'content_set_id'),
        sa.Index('idx_accessed_at', 'accessed_at'),
    )

    # Extender shop_items
    op.add_column('shop_items', sa.Column('content_set_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_shop_item_content_set', 'shop_items', 'content_sets', ['content_set_id'], ['id'])

    # Extender narrative_fragments
    op.add_column('narrative_fragments', sa.Column('content_set_id', sa.Integer(), nullable=True))
    op.add_column('narrative_fragments', sa.Column('auto_send_content', sa.Boolean(), default=True))
    op.create_foreign_key('fk_fragment_content_set', 'narrative_fragments', 'content_sets', ['content_set_id'], ['id'])

    # Extender rewards
    op.add_column('rewards', sa.Column('content_set_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_reward_content_set', 'rewards', 'content_sets', ['content_set_id'], ['id'])

def downgrade():
    # Rollback inverso
    op.drop_constraint('fk_reward_content_set', 'rewards')
    op.drop_column('rewards', 'content_set_id')

    op.drop_constraint('fk_fragment_content_set', 'narrative_fragments')
    op.drop_column('narrative_fragments', 'auto_send_content')
    op.drop_column('narrative_fragments', 'content_set_id')

    op.drop_constraint('fk_shop_item_content_set', 'shop_items')
    op.drop_column('shop_items', 'content_set_id')

    op.drop_table('user_content_access')
    op.drop_table('content_sets')
```

---

## 6. Estructura de Archivos (Resumen)

```
c1/
├── bot/
│   ├── shop/
│   │   ├── database/
│   │   │   ├── models.py (MODIFICAR: +ContentSet, +UserContentAccess)
│   │   │   └── enums.py (MODIFICAR: +ContentType, +ContentTier)
│   │   ├── services/
│   │   │   ├── content_service.py (NUEVO)
│   │   │   └── shop_service.py (MODIFICAR: +_deliver_content_set)
│   │   └── handlers/
│   │       └── admin/
│   │           └── content_admin.py (NUEVO)
│   │
│   ├── narrative/
│   │   ├── database/
│   │   │   └── models.py (MODIFICAR: NarrativeFragment +content_set_id)
│   │   └── services/
│   │       └── fragment_service.py (MODIFICAR: +envío de content sets)
│   │
│   ├── gamification/
│   │   ├── database/
│   │   │   ├── models.py (MODIFICAR: Reward +content_set_id)
│   │   │   └── enums.py (MODIFICAR: RewardType +CONTENT_SET)
│   │   ├── services/
│   │   │   └── reward_service.py (MODIFICAR: +manejo de content sets)
│   │   ├── handlers/
│   │   │   └── admin/
│   │   │       ├── unified_wizard.py (MODIFICAR: +wizard inline de ContentSet)
│   │   │       ├── mission_wizard.py (MODIFICAR: +opción content set)
│   │   │       └── reward_wizard.py (MODIFICAR: +tipo content set)
│   │   └── states/
│   │       └── admin.py (MODIFICAR: +estados ContentSet)
│   │
│   ├── services/
│   │   └── container.py (MODIFICAR: +lazy loading ContentService)
│   │
│   └── database/
│       └── models.py (MODIFICAR: User +relationship content_access)
│
├── migrations/
│   └── add_content_sets.py (NUEVO)
│
└── tests/
    └── test_content_service.py (NUEVO)
```

---

## 7. Plan de Implementación por Fases

### FASE 1: Modelos y Migraciones (2-3 horas)

**Archivos**:
- `c1/bot/shop/database/models.py`
- `c1/bot/shop/database/enums.py`
- `c1/bot/narrative/database/models.py`
- `c1/bot/gamification/database/models.py`
- `c1/bot/gamification/database/enums.py`
- `c1/migrations/add_content_sets.py`

**Tareas**:
1. Crear modelo `ContentSet`
2. Crear modelo `UserContentAccess`
3. Agregar enums `ContentType` y `ContentTier`
4. Extender `ShopItem` con `content_set_id`
5. Extender `NarrativeFragment` con `content_set_id`
6. Extender `Reward` con `content_set_id`
7. Agregar `RewardType.CONTENT_SET` y `ItemType.CONTENT_SET`
8. Crear migración
9. Ejecutar migración

**Validación**:
- Tablas creadas correctamente
- Foreign keys funcionando
- Índices creados

---

### FASE 2: Servicios Core (3-4 horas)

**Archivos**:
- `c1/bot/shop/services/content_service.py` (NUEVO)
- `c1/bot/services/container.py`

**Tareas**:
1. Implementar `ContentService` completo:
   - `create_content_set()`
   - `get_content_set()`
   - `list_content_sets()`
   - `send_content_set()` (lógica de envío multimedia)
   - `track_content_access()`
   - `update_content_set()`
   - `delete_content_set()`
2. Agregar `content` property a `ServiceContainer`
3. Escribir tests unitarios

**Validación**:
- CRUD funcional
- Envío de multimedia funciona (photo_set, video, audio, mixed)
- Tracking correcto

---

### FASE 3: Wizard de Creación (4-5 horas)

**Archivos**:
- `c1/bot/gamification/states/admin.py`
- `c1/bot/gamification/handlers/admin/unified_wizard.py`

**Tareas**:
1. Agregar estados FSM para ContentSet wizard
2. Agregar botón "Crear Content Set" en menú unificado
3. Implementar wizard inline (7 pasos):
   - Paso 1: Slug
   - Paso 2: Nombre
   - Paso 3: Descripción
   - Paso 4: Tipo (photo_set/video/audio/mixed)
   - Paso 5: Tier (free/vip/premium)
   - Paso 6: Upload archivos (soporte múltiples)
   - Paso 7: Confirmación
4. Manejar upload de archivos multimedia
5. Almacenar file_ids de Telegram

**Validación**:
- Wizard funciona end-to-end
- Archivos se suben correctamente
- file_ids se guardan en BD

---

### FASE 4: Integración con Shop (2-3 horas)

**Archivos**:
- `c1/bot/shop/services/shop_service.py`
- `c1/bot/gamification/handlers/admin/unified_wizard.py` (wizard de shop item)

**Tareas**:
1. Implementar `_deliver_content_set()` en ShopService
2. Integrar en `purchase_item()` para entregar content sets
3. Extender wizard de shop item para soportar tipo CONTENT_SET
4. Agregar selección de content set al crear item de tienda

**Validación**:
- Comprar item con content set entrega multimedia
- Tracking de acceso funciona
- User ve el contenido

---

### FASE 5: Integración con Narrativa (2-3 horas)

**Archivos**:
- `c1/bot/narrative/services/fragment_service.py`
- `c1/bot/gamification/handlers/admin/unified_wizard.py` (wizard de chapter)

**Tareas**:
1. Modificar `navigate_to_fragment()` para enviar content sets
2. Extender wizard de capítulos para vincular content sets
3. Agregar toggle `auto_send_content` en fragmentos

**Validación**:
- Navegar fragmento envía content set automáticamente
- Opción de desactivar auto-envío funciona

---

### FASE 6: Integración con Gamificación (3-4 horas)

**Archivos**:
- `c1/bot/gamification/services/reward_service.py`
- `c1/bot/gamification/handlers/admin/reward_wizard.py`
- `c1/bot/gamification/handlers/admin/mission_wizard.py`

**Tareas**:
1. Modificar `claim_reward()` para entregar content sets
2. Agregar tipo CONTENT_SET en reward wizard
3. Agregar opción de content set en mission wizard (paso recompensas)
4. Implementar selección de content set existente

**Validación**:
- Canjear recompensa de content set entrega multimedia
- Crear misión con content set como recompensa funciona
- Completar misión otorga content set

---

### FASE 7: Admin Panel (2-3 horas)

**Archivos**:
- `c1/bot/shop/handlers/admin/content_admin.py` (NUEVO)
- `c1/bot/handlers/admin/main.py`

**Tareas**:
1. Crear router `content_admin_router`
2. Implementar menú principal de gestión
3. Listar content sets con paginación
4. Ver detalles de content set
5. Editar content set (nombre, descripción, tier)
6. Eliminar content set (soft delete)
7. Enviar content set a usuario (testing)
8. Estadísticas de uso

**Validación**:
- Admin puede gestionar todos los content sets
- Paginación funciona
- Testing de envío funciona

---

### FASE 8: Testing y Refinamiento (2-3 horas)

**Archivos**:
- `c1/tests/test_content_service.py` (NUEVO)
- Todos los archivos modificados

**Tareas**:
1. Tests unitarios de `ContentService`
2. Tests de integración (shop, narrative, gamification)
3. Tests E2E de wizards
4. Optimizaciones de queries
5. Agregar logging apropiado
6. Documentación inline (docstrings)
7. Testing manual completo

**Validación**:
- Todos los tests pasan
- No hay regressions en funcionalidades existentes
- Performance aceptable

---

## 8. Consideraciones Técnicas

### 8.1 Manejo de Archivos Multimedia

**Telegram file_ids**:
- Al subir archivo, Telegram retorna `file_id` único
- `file_id` es permanente y reutilizable
- Guardar `file_id` en array JSON en `ContentSet.file_ids`
- Opcional: guardar metadata (tipo, caption) en `file_metadata`

**Ejemplo de almacenamiento**:
```json
{
  "file_ids": [
    "AgACAgIAAxkBAAIB...",
    "AgACAgIAAxkBAAIB...",
    "BAACAgIAAxkBAAIC..."
  ],
  "file_metadata": {
    "AgACAgIAAxkBAAIB...": {
      "type": "photo",
      "caption": "Primera escena",
      "order": 1
    },
    "BAACAgIAAxkBAAIC...": {
      "type": "video",
      "caption": "Video exclusivo",
      "order": 2
    }
  }
}
```

### 8.2 Envío de Multimedia

**Lógica en `send_content_set()`**:

```python
async def send_content_set(self, user_id: int, content_set_id: int, bot: Bot, ...):
    content_set = await self.get_content_set(content_set_id)

    # Validar permisos VIP
    if content_set.requires_vip:
        user = await self.session.get(User, user_id)
        if user.role != "vip":
            return False

    # Enviar mensaje de contexto (opcional)
    if context_message:
        await bot.send_message(user_id, context_message, parse_mode="HTML")

    # Enviar archivos según tipo
    if content_set.content_type == ContentType.PHOTO_SET:
        for file_id in content_set.file_ids:
            await bot.send_photo(user_id, file_id)
            await asyncio.sleep(0.3)  # Anti rate-limit

    elif content_set.content_type == ContentType.VIDEO:
        await bot.send_video(user_id, content_set.file_ids[0])

    elif content_set.content_type == ContentType.AUDIO:
        await bot.send_audio(user_id, content_set.file_ids[0])

    elif content_set.content_type == ContentType.MIXED:
        # Detectar tipo por metadata o intentar enviar
        for file_id in content_set.file_ids:
            metadata = content_set.file_metadata.get(file_id, {})
            file_type = metadata.get('type', 'photo')

            if file_type == 'photo':
                await bot.send_photo(user_id, file_id)
            elif file_type == 'video':
                await bot.send_video(user_id, file_id)
            # ...

            await asyncio.sleep(0.3)

    # Tracking
    await self.track_content_access(user_id, content_set_id, delivery_context, trigger_type)

    return True
```

### 8.3 Optimización para Termux

**Lazy Loading**:
- ContentService solo se carga cuando se usa (ServiceContainer)
- Queries optimizadas con índices
- Paginación en listas largas (PAGE_SIZE=5)

**Memoria**:
- No cargar archivos en memoria, solo file_ids
- Telegram maneja el almacenamiento de archivos

### 8.4 Convenciones de Código

**Async/Await**: Todos los métodos async
**Type Hints**: Obligatorio en todas las signatures
**Docstrings**: Google style en todos los métodos públicos
**Logging**: Logger en cada módulo, niveles apropiados
**Error Handling**: Try-except en handlers, logging de errores

---

## 9. Archivos Críticos a Modificar

### Archivos Nuevos:
1. `c1/bot/shop/services/content_service.py`
2. `c1/bot/shop/handlers/admin/content_admin.py`
3. `c1/migrations/add_content_sets.py`
4. `c1/tests/test_content_service.py`

### Archivos a Modificar:
1. `c1/bot/shop/database/models.py` - Agregar ContentSet, UserContentAccess, extender ShopItem
2. `c1/bot/shop/database/enums.py` - Agregar ContentType, ContentTier, ItemType.CONTENT_SET
3. `c1/bot/shop/services/shop_service.py` - Agregar _deliver_content_set()
4. `c1/bot/narrative/database/models.py` - Extender NarrativeFragment
5. `c1/bot/narrative/services/fragment_service.py` - Envío de content sets
6. `c1/bot/gamification/database/models.py` - Extender Reward
7. `c1/bot/gamification/database/enums.py` - Agregar RewardType.CONTENT_SET
8. `c1/bot/gamification/services/reward_service.py` - Manejo de content sets
9. `c1/bot/gamification/states/admin.py` - Agregar estados ContentSet
10. `c1/bot/gamification/handlers/admin/unified_wizard.py` - Wizard inline ContentSet
11. `c1/bot/gamification/handlers/admin/mission_wizard.py` - Opción content set
12. `c1/bot/gamification/handlers/admin/reward_wizard.py` - Tipo content set
13. `c1/bot/services/container.py` - Lazy loading ContentService
14. `c1/bot/database/models.py` - Relationship en User (opcional)

---

## 10. Estimación de Tiempo

| Fase | Tiempo Estimado | Complejidad |
|------|----------------|-------------|
| Fase 1: Modelos y Migraciones | 2-3 horas | Media |
| Fase 2: Servicios Core | 3-4 horas | Media-Alta |
| Fase 3: Wizard de Creación | 4-5 horas | Alta |
| Fase 4: Integración Shop | 2-3 horas | Media |
| Fase 5: Integración Narrativa | 2-3 horas | Media |
| Fase 6: Integración Gamificación | 3-4 horas | Media-Alta |
| Fase 7: Admin Panel | 2-3 horas | Media |
| Fase 8: Testing y Refinamiento | 2-3 horas | Media |
| **TOTAL** | **20-28 horas** | - |

---

## 11. Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Telegram file_ids inválidos tras tiempo | Baja | Alto | Validar file_ids antes de usar, manejar errores gracefully |
| Rate limiting de Telegram | Media | Medio | Agregar delays entre envíos (asyncio.sleep) |
| Tamaño de archivos grandes | Baja | Medio | Validar tamaño en upload, rechazar si >20MB |
| Conflictos con migraciones existentes | Media | Alto | Revisar migraciones antes, usar alembic stamp |
| Complejidad del wizard | Media | Medio | Seguir patrón existente de capítulos |
| Performance en listas largas | Baja | Bajo | Paginación desde el inicio |

---

## 12. Criterios de Éxito

✅ **Funcionales**:
- Admin puede crear content sets desde wizard
- Content sets se pueden vincular a shop items, recompensas, fragmentos
- Comprar item con content set entrega multimedia automáticamente
- Canjear recompensa de content set entrega multimedia
- Navegar fragmento con content set envía contenido
- Admin puede gestionar content sets (listar, editar, eliminar)

✅ **Técnicos**:
- Todos los tests unitarios pasan
- No hay regressions en funcionalidades existentes
- Queries optimizadas (< 100ms)
- Memoria controlada (lazy loading)
- Código sigue convenciones de c1

✅ **UX**:
- Wizard intuitivo y consistente
- Mensajes de error claros
- Paginación fluida
- Confirmaciones antes de acciones destructivas

---

## Fin del Plan
