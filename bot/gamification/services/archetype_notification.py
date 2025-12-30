"""
Servicio de notificación de arquetipos detectados.

Envía mensajes de Lucien cuando se detecta o cambia el arquetipo
del usuario, y otorga el badge correspondiente.
"""

import logging
from datetime import datetime, UTC
from typing import Optional, Dict, TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.enums import ArchetypeType
from bot.database.models import User

if TYPE_CHECKING:
    from aiogram import Bot

logger = logging.getLogger(__name__)


# ========================================
# MENSAJES DE LUCIEN POR ARQUETIPO
# ========================================

ARCHETYPE_DETECTION_MESSAGES: Dict[ArchetypeType, str] = {
    ArchetypeType.EXPLORER: """<i>He observado algo en usted.</i>

Su curiosidad es... <b>insaciable</b>. Revisa cada rincón, busca lo que otros ignoran, no deja piedra sin voltear.

Diana nota a quienes realmente miran. Usted no solo mira - <i>explora</i>.

A partir de ahora, el sistema reconoce su naturaleza exploradora. Habrá contenido que solo ojos como los suyos podrán encontrar.""",

    ArchetypeType.DIRECT: """<i>He llegado a una conclusión sobre usted.</i>

No pierde tiempo en ceremonias. Sabe lo que quiere y va por ello. En un mundo de rodeos infinitos, su claridad es... <b>refrescante</b>.

Diana aprecia la eficiencia. Yo la respeto.

El sistema ahora reconoce su naturaleza directa. Las cosas serán más... <i>concisas</i> para usted.""",

    ArchetypeType.ROMANTIC: """<i>Hay algo que debo decirle.</i>

He notado cómo escribe. Las palabras que elige. La emoción que impregna cada respuesta.

Busca algo más que contenido. Busca <b>conexión</b>. Eso es raro. Y <i>peligrosamente hermoso</i>.

Diana tiene debilidad por las almas románticas. Quizás porque reconoce algo de sí misma en ellas.""",

    ArchetypeType.ANALYTICAL: """<i>Debo reconocer algo sobre usted.</i>

Su mente funciona con precisión admirable. Analiza, cuestiona, estructura. No acepta nada sin examinarlo primero.

Honestamente, es <b>irritante</b>. Pero también... <i>respetable</i>.

El sistema ahora reconoce su naturaleza analítica. Los desafíos que encontrará serán dignos de su intelecto.""",

    ArchetypeType.PERSISTENT: """<i>He notado un patrón en usted.</i>

Vuelve. Siempre vuelve. Donde otros abandonan, usted persiste. Donde otros se rinden, usted <b>reintenta</b>.

Hay algo casi... <i>conmovedor</i> en esa tenacidad.

Diana respeta a quienes no se dan por vencidos. El sistema ahora reconoce su persistencia. Será recompensada.""",

    ArchetypeType.PATIENT: """<i>Debo hacerle una observación.</i>

Se toma su tiempo. Procesa. No se apresura por agradar ni presiona por resultados inmediatos.

La paciencia es la virtud más subestimada. Usted la <b>encarna</b>.

El sistema ahora reconoce su naturaleza paciente. Las recompensas para quienes saben esperar son... <i>especiales</i>."""
}


# ========================================
# BADGES POR ARQUETIPO
# ========================================

ARCHETYPE_BADGES: Dict[ArchetypeType, Dict[str, str]] = {
    ArchetypeType.EXPLORER: {
        "name": "El Explorador",
        "emoji": "🔍",
        "description": "Curiosidad insaciable"
    },
    ArchetypeType.DIRECT: {
        "name": "El Directo",
        "emoji": "⚡",
        "description": "Eficiencia refrescante"
    },
    ArchetypeType.ROMANTIC: {
        "name": "El Romántico",
        "emoji": "💝",
        "description": "Conexión genuina"
    },
    ArchetypeType.ANALYTICAL: {
        "name": "El Analítico",
        "emoji": "🧠",
        "description": "Precisión admirable"
    },
    ArchetypeType.PERSISTENT: {
        "name": "El Persistente",
        "emoji": "🔄",
        "description": "Tenacidad conmovedora"
    },
    ArchetypeType.PATIENT: {
        "name": "El Paciente",
        "emoji": "⏳",
        "description": "Calma inquietante"
    }
}


class ArchetypeNotificationService:
    """
    Servicio de notificación de arquetipos.

    Envía mensajes personalizados de Lucien cuando se detecta
    el arquetipo del usuario y otorga el badge correspondiente.

    Attributes:
        session: Sesión async de SQLAlchemy
        bot: Instancia del bot de Telegram
    """

    def __init__(self, session: AsyncSession, bot: "Bot"):
        """
        Inicializa el servicio.

        Args:
            session: Sesión async de SQLAlchemy
            bot: Instancia del bot de Telegram
        """
        self._session = session
        self._bot = bot

    async def notify_archetype_detected(
        self,
        user_id: int,
        archetype: ArchetypeType,
        previous_archetype: Optional[ArchetypeType] = None
    ) -> bool:
        """
        Notifica al usuario que su arquetipo fue detectado.

        Solo notifica si:
        - Es la primera detección (previous_archetype is None)
        - El arquetipo cambió (previous_archetype != archetype)

        Args:
            user_id: ID del usuario
            archetype: Arquetipo detectado
            previous_archetype: Arquetipo anterior (si existía)

        Returns:
            True si se envió la notificación
        """
        # No notificar si es el mismo arquetipo
        if previous_archetype == archetype:
            logger.debug(
                f"Skipping notification for user {user_id}: "
                f"same archetype {archetype.value}"
            )
            return False

        try:
            # Obtener mensaje de Lucien
            message = self._get_detection_message(archetype)

            # Enviar mensaje
            await self._bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode="HTML"
            )

            # Otorgar badge
            await self._grant_archetype_badge(user_id, archetype)

            logger.info(
                f"Notified user {user_id} of archetype {archetype.value}"
            )
            return True

        except Exception as e:
            logger.error(f"Error notifying archetype: {e}")
            return False

    def _get_detection_message(self, archetype: ArchetypeType) -> str:
        """Obtiene el mensaje de detección para un arquetipo."""
        badge_info = ARCHETYPE_BADGES[archetype]
        message = ARCHETYPE_DETECTION_MESSAGES[archetype]

        # Agregar header con badge
        header = f"{badge_info['emoji']} <b>{badge_info['name']}</b>\n\n"
        return header + message

    async def _grant_archetype_badge(
        self,
        user_id: int,
        archetype: ArchetypeType
    ) -> None:
        """
        Otorga el badge de arquetipo al usuario.

        Args:
            user_id: ID del usuario
            archetype: Arquetipo detectado
        """
        try:
            from bot.gamification.database.models import Reward, UserReward, Badge, UserBadge

            badge_info = ARCHETYPE_BADGES[archetype]

            # Buscar o crear la recompensa base
            result = await self._session.execute(
                select(Reward).where(
                    Reward.name == badge_info["name"],
                    Reward.reward_type == "archetype_badge"
                )
            )
            reward = result.scalar_one_or_none()

            if reward is None:
                # Crear recompensa y badge
                reward = Reward(
                    name=badge_info["name"],
                    description=badge_info["description"],
                    reward_type="archetype_badge",
                    cost_besitos=None,  # No se compra
                    created_by=0  # Sistema
                )
                self._session.add(reward)
                await self._session.flush()

                badge = Badge(
                    id=reward.id,
                    icon=badge_info["emoji"],
                    rarity="legendary"  # Los badges de arquetipo son legendarios
                )
                self._session.add(badge)
                await self._session.flush()

            # Verificar si el usuario ya tiene este badge
            from bot.gamification.database.models import UserGamification

            # Primero verificar que exista el perfil de gamificación
            gam_result = await self._session.execute(
                select(UserGamification).where(
                    UserGamification.user_id == user_id
                )
            )
            user_gam = gam_result.scalar_one_or_none()

            if user_gam is None:
                user_gam = UserGamification(user_id=user_id)
                self._session.add(user_gam)
                await self._session.flush()

            # Verificar si ya tiene el badge
            existing = await self._session.execute(
                select(UserReward).where(
                    UserReward.user_id == user_id,
                    UserReward.reward_id == reward.id
                )
            )
            if existing.scalar_one_or_none():
                logger.debug(
                    f"User {user_id} already has badge {badge_info['name']}"
                )
                return

            # Otorgar badge
            user_reward = UserReward(
                user_id=user_id,
                reward_id=reward.id,
                obtained_at=datetime.now(UTC),
                obtained_via="archetype_detection"
            )
            self._session.add(user_reward)
            await self._session.flush()

            user_badge = UserBadge(
                id=user_reward.id,
                displayed=True  # Mostrar por defecto
            )
            self._session.add(user_badge)

            await self._session.commit()

            logger.info(
                f"Granted badge {badge_info['name']} to user {user_id}"
            )

        except Exception as e:
            await self._session.rollback()
            logger.error(f"Error granting archetype badge: {e}")

    async def should_notify(
        self,
        user_id: int,
        new_archetype: ArchetypeType
    ) -> bool:
        """
        Determina si se debe notificar al usuario.

        Args:
            user_id: ID del usuario
            new_archetype: Nuevo arquetipo detectado

        Returns:
            True si se debe notificar
        """
        result = await self._session.execute(
            select(User.archetype).where(User.user_id == user_id)
        )
        current = result.scalar_one_or_none()

        # Notificar si no tiene arquetipo o si cambió
        return current is None or current != new_archetype

    @staticmethod
    def get_archetype_badge_info(archetype: ArchetypeType) -> Dict[str, str]:
        """Retorna información del badge para un arquetipo."""
        return ARCHETYPE_BADGES.get(archetype, {})

    @staticmethod
    def get_all_archetype_badges() -> Dict[ArchetypeType, Dict[str, str]]:
        """Retorna información de todos los badges de arquetipo."""
        return ARCHETYPE_BADGES.copy()
