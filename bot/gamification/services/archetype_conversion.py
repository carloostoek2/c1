"""
Servicio de conversión basado en arquetipos.

Proporciona triggers de conversión y mensajes personalizados
según el arquetipo del usuario para maximizar la efectividad
de las ofertas VIP.
"""

from dataclasses import dataclass
from typing import Optional, Dict, List
from bot.database.enums import ArchetypeType


@dataclass
class ConversionTrigger:
    """Trigger de conversión para un arquetipo."""
    archetype: ArchetypeType
    trigger_event: str
    description: str
    priority: int  # 1 = más alta


@dataclass
class ConversionOffer:
    """Oferta de conversión personalizada."""
    archetype: ArchetypeType
    message: str
    call_to_action: str


# ========================================
# TRIGGERS DE CONVERSIÓN POR ARQUETIPO
# ========================================

CONVERSION_TRIGGERS: Dict[ArchetypeType, ConversionTrigger] = {
    ArchetypeType.EXPLORER: ConversionTrigger(
        archetype=ArchetypeType.EXPLORER,
        trigger_event="easter_egg_requires_vip",
        description="Cuando encuentra easter egg que requiere VIP",
        priority=1
    ),
    ArchetypeType.DIRECT: ConversionTrigger(
        archetype=ArchetypeType.DIRECT,
        trigger_event="action_completed",
        description="Después de completar acción, sin dilación",
        priority=1
    ),
    ArchetypeType.ROMANTIC: ConversionTrigger(
        archetype=ArchetypeType.ROMANTIC,
        trigger_event="emotional_fragment_viewed",
        description="Después de fragmento narrativo emocional",
        priority=1
    ),
    ArchetypeType.ANALYTICAL: ConversionTrigger(
        archetype=ArchetypeType.ANALYTICAL,
        trigger_event="quiz_high_score",
        description="Después de evaluación con buen score",
        priority=1
    ),
    ArchetypeType.PERSISTENT: ConversionTrigger(
        archetype=ArchetypeType.PERSISTENT,
        trigger_event="return_after_inactivity",
        description="Cuando regresa después de inactividad",
        priority=1
    ),
    ArchetypeType.PATIENT: ConversionTrigger(
        archetype=ArchetypeType.PATIENT,
        trigger_event="streak_7_days",
        description="Después de completar racha de 7+ días",
        priority=1
    ),
}


# ========================================
# MENSAJES DE CONVERSIÓN POR ARQUETIPO
# ========================================

CONVERSION_MESSAGES: Dict[ArchetypeType, ConversionOffer] = {
    ArchetypeType.EXPLORER: ConversionOffer(
        archetype=ArchetypeType.EXPLORER,
        message=(
            "Hay {count} archivos en el Diván que sus ojos de explorador "
            "aún no han visto. Secretos que esperan ser descubiertos. "
            "Rincones que solo los VIP conocen."
        ),
        call_to_action="🔍 Explorar el Diván"
    ),
    ArchetypeType.DIRECT: ConversionOffer(
        archetype=ArchetypeType.DIRECT,
        message=(
            "VIP: Acceso completo. Sin rodeos. {price}."
        ),
        call_to_action="⚡ Obtener acceso"
    ),
    ArchetypeType.ROMANTIC: ConversionOffer(
        archetype=ArchetypeType.ROMANTIC,
        message=(
            "Diana reserva sus momentos más íntimos para el Diván. "
            "Momentos que solo comparte con quienes realmente quieren "
            "conocerla. ¿Será usted uno de ellos?"
        ),
        call_to_action="💝 Conectar con Diana"
    ),
    ArchetypeType.ANALYTICAL: ConversionOffer(
        archetype=ArchetypeType.ANALYTICAL,
        message=(
            "El Diván contiene {posts} publicaciones exclusivas, "
            "{monthly} nuevas cada mes. "
            "Valor estimado: {value}. Inversión: {price}."
        ),
        call_to_action="🧠 Ver análisis completo"
    ),
    ArchetypeType.PERSISTENT: ConversionOffer(
        archetype=ArchetypeType.PERSISTENT,
        message=(
            "Ha demostrado compromiso inusual. Ha vuelto {returns} veces. "
            "El siguiente paso natural es el Diván. "
            "Su persistencia merece ese acceso."
        ),
        call_to_action="🔄 Dar el siguiente paso"
    ),
    ArchetypeType.PATIENT: ConversionOffer(
        archetype=ArchetypeType.PATIENT,
        message=(
            "Ha esperado. Ha observado. Ha construido mérito durante "
            "{days} días. El Diván está listo cuando usted lo esté."
        ),
        call_to_action="⏳ Acceder ahora"
    ),
}


# ========================================
# SERVICIO DE CONVERSIÓN
# ========================================

class ArchetypeConversionService:
    """
    Servicio de conversión basado en arquetipos.

    Determina el momento óptimo y el mensaje adecuado
    para ofrecer VIP a cada usuario según su arquetipo.
    """

    @staticmethod
    def get_trigger(archetype: ArchetypeType) -> ConversionTrigger:
        """
        Obtiene el trigger de conversión para un arquetipo.

        Args:
            archetype: Arquetipo del usuario

        Returns:
            ConversionTrigger para ese arquetipo
        """
        return CONVERSION_TRIGGERS.get(archetype)

    @staticmethod
    def get_conversion_message(
        archetype: ArchetypeType,
        **format_args
    ) -> ConversionOffer:
        """
        Obtiene el mensaje de conversión personalizado.

        Args:
            archetype: Arquetipo del usuario
            **format_args: Argumentos para formatear el mensaje

        Returns:
            ConversionOffer con mensaje formateado
        """
        offer = CONVERSION_MESSAGES.get(archetype)
        if offer is None:
            # Mensaje genérico si no hay arquetipo
            return ConversionOffer(
                archetype=archetype,
                message="El Diván VIP te espera. Acceso exclusivo a todo el contenido.",
                call_to_action="Obtener VIP"
            )

        # Formatear mensaje con argumentos
        try:
            formatted_message = offer.message.format(**format_args)
        except KeyError:
            formatted_message = offer.message

        return ConversionOffer(
            archetype=archetype,
            message=formatted_message,
            call_to_action=offer.call_to_action
        )

    @staticmethod
    def should_show_offer(
        archetype: ArchetypeType,
        event: str,
        context: Dict = None
    ) -> bool:
        """
        Determina si se debe mostrar la oferta de conversión.

        Args:
            archetype: Arquetipo del usuario
            event: Evento actual
            context: Contexto adicional

        Returns:
            True si es el momento óptimo para mostrar oferta
        """
        trigger = CONVERSION_TRIGGERS.get(archetype)
        if trigger is None:
            return False

        # Verificar si el evento coincide con el trigger
        if event == trigger.trigger_event:
            return True

        # Triggers adicionales por contexto
        context = context or {}

        # Explorer: cualquier contenido bloqueado
        if archetype == ArchetypeType.EXPLORER:
            if context.get("blocked_content"):
                return True

        # Analytical: después de quiz con score > 70
        if archetype == ArchetypeType.ANALYTICAL:
            if event == "quiz_completed" and context.get("score", 0) > 70:
                return True

        # Patient: después de streak milestone
        if archetype == ArchetypeType.PATIENT:
            if event == "streak_milestone" and context.get("streak", 0) >= 7:
                return True

        return False

    @staticmethod
    def get_optimal_timing(archetype: ArchetypeType) -> str:
        """
        Describe el timing óptimo para mostrar oferta.

        Args:
            archetype: Arquetipo del usuario

        Returns:
            Descripción del momento óptimo
        """
        timing = {
            ArchetypeType.EXPLORER: "Cuando encuentra contenido bloqueado o easter egg VIP",
            ArchetypeType.DIRECT: "Inmediatamente después de completar cualquier acción",
            ArchetypeType.ROMANTIC: "Después de un fragmento narrativo emocional",
            ArchetypeType.ANALYTICAL: "Después de completar evaluación con score > 70%",
            ArchetypeType.PERSISTENT: "Cuando regresa después de período de inactividad",
            ArchetypeType.PATIENT: "Después de alcanzar racha de 7+ días",
        }
        return timing.get(archetype, "En cualquier momento apropiado")

    @staticmethod
    def get_all_triggers() -> List[ConversionTrigger]:
        """Retorna todos los triggers de conversión."""
        return list(CONVERSION_TRIGGERS.values())

    @staticmethod
    def get_all_offers() -> List[ConversionOffer]:
        """Retorna todas las ofertas de conversión."""
        return list(CONVERSION_MESSAGES.values())
