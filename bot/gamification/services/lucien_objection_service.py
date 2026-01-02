"""Servicio de manejo de objeciones para el personaje de Lucien.

Este servicio proporciona respuestas contextuales a objeciones comunes
que los usuarios puedan levantar durante el proceso de conversión.
"""

import logging
from typing import Dict, List, Optional
from enum import Enum

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class ObjectionType(str, Enum):
    """
    Tipos de objeciones comunes que los usuarios pueden levantar.
    
    Categorías:
    - Precio: Objecciones relacionadas con costo
    - Valor: Objecciones relacionadas con valor percibido
    - Tiempo: Objecciones relacionadas con tiempo de inversión
    - Confianza: Objecciones relacionadas con seguridad y confianza
    - Alternativas: Objecciones relacionadas con otras opciones
    - Personal: Objecciones relacionadas con circunstancias personales
    """
    
    # Objecciones de precio
    TOO_EXPENSIVE = "too_expensive"                 # Demasiado caro
    UNAFFORDABLE = "unaffordable"                   # No puedo pagar ahora
    BETTER_DEAL = "better_deal"                     # Hay mejores ofertas
    UNFAIR_PRICE = "unfair_price"                   # Precio no justificado
    
    # Objecciones de valor
    NO_VALUE = "no_value"                          # No veo el valor
    NOT_INTERESTED = "not_interested"              # No me interesa
    SATISFIED_CURRENT = "satisfied_current"        # Estoy bien con lo que tengo
    SKEPTICAL_BENEFITS = "skeptical_benefits"     # Dudo de los beneficios
    
    # Objecciones de tiempo
    TOO_BUSY = "too_busy"                         # No tengo tiempo
    NOT_NOW = "not_now"                           # Tal vez más adelante
    TOO_MUCH_COMMITMENT = "too_much_commitment"    # Demasiado compromiso
    TIME_SENSITIVE = "time_sensitive"              # No puedo dedicarle tiempo
    
    # Objecciones de confianza
    TRUST_ISSUES = "trust_issues"                 # No confío en el producto
    NO_PROOF = "no_proof"                         # No hay pruebas de efectividad
    FEEDBACK_CONCERNS = "feedback_concerns"       # No he leído buenas reseñas
    RISK_CONCERN = "risk_concern"                 # Temo perder mi dinero
    
    # Objecciones de alternativas
    ALTERNATIVE_CHOICE = "alternative_choice"     # Estoy usando otra opción
    ALREADY_PAID_FOR = "already_paid_for"         # Ya pagué por algo similar
    FREE_OPTIONS = "free_options"                 # Hay opciones gratuitas
    UNCERTAIN_BETWEEN = "uncertain_between"       # No sé cuál elegir
    
    # Objecciones personales
    PERSONAL_CIRCUMSTANCES = "personal_circumstances"  # Circunstancias personales
    LACK_SUPPORT = "lack_support"                 # No tengo apoyo
    NOT_READY = "not_ready"                       # No estoy listo psicológicamente
    CONCERNS_ABOUT_OTHERS = "concerns_about_others"    # Preocupaciones por otros


class LucienObjectionService:
    """
    Servicio para manejo de objeciones con respuestas de Lucien.
    
    Proporciona respuestas personalizadas y contextuales basadas en:
    - Tipo de objeción
    - Arquetipo del usuario
    - Historial de interacciones
    - Progreso en la narrativa
    """
    
    def __init__(self, session: AsyncSession):
        """Inicializa el servicio."""
        self._session = session
        self._responses = self._load_default_responses()
    
    def _load_default_responses(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Carga respuestas predeterminadas para cada tipo de objeción.
        
        Returns:
            Diccionario con respuestas por tipo de objeción y estilo de personalidad
        """
        return {
            ObjectionType.TOO_EXPENSIVE: [
                {
                    "response": (
                        "Ah, querido/a, entiendo tu preocupación. ¿Sabes? No se trata de gastar, "
                        "sino de invertir. Esta experiencia no es un gasto, es un regalo para tu "
                        "mente y espíritu. Además, ¿has considerado que el verdadero lujo es el "
                        "tiempo que no recuperas? Y este, mi querido/a, es irreemplazable."
                    ),
                    "style": "elegant"
                },
                {
                    "response": (
                        "Permíteme preguntarte algo: ¿cuánto cuesta realmente no actuar? "
                        "A veces, el precio más alto es el de la inacción. Pero no te preocupes, "
                        "tengo algunas opciones flexibles que quizás se adapten mejor a tu situación."
                    ),
                    "style": "philosophical"
                }
            ],
            ObjectionType.UNAFFORDABLE: [
                {
                    "response": (
                        "Entiendo que cada persona tiene su momento financiero, y respeto eso. "
                        "Pero permíteme decirte que hay maneras de acceder a lo que quieres "
                        "incluso con recursos limitados. ¿Te gustaría que exploremos juntos "
                        "las opciones disponibles?"
                    ),
                    "style": "understanding"
                },
                {
                    "response": (
                        "Mi estimado/a, a veces no es que no tengamos dinero, es que no tenemos "
                        "prioridades claras. Permíteme preguntarte: ¿qué tan valiosa es para ti "
                        "la transformación que buscas?"
                    ),
                    "style": "challenging"
                }
            ],
            ObjectionType.NO_VALUE: [
                {
                    "response": (
                        "Ah, el valor... No siempre es evidente a simple vista. ¿Te has preguntado "
                        "cuánto vale un momento de claridad, de conexión con tu interior? "
                        "El valor no siempre es tangible, pero sus efectos sí lo son."
                    ),
                    "style": "insightful"
                },
                {
                    "response": (
                        "Permíteme ser franco: el valor no se mide solo en beneficios inmediatos, "
                        "sino en la transformación que experimentarás. ¿No has notado ya ciertos "
                        "cambios sutiles desde que comenzaste?"
                    ),
                    "style": "direct"
                }
            ],
            ObjectionType.TOO_BUSY: [
                {
                    "response": (
                        "Veo que tienes una agenda muy ocupada... interesante. ¿Sabes qué? "
                        "Justamente por eso eres un candidato perfecto. Esta experiencia está "
                        "diseñada para integrarse naturalmente en tu vida, no para complicarla."
                    ),
                    "style": "adaptive"
                },
                {
                    "response": (
                        "El tiempo, mi estimado/a, es el activo más valioso que posees. "
                        "Pero ¿no crees que mereces dedicarle un poco de tiempo a tu bienestar? "
                        "Además, no es tanto tiempo como crees, y los efectos duran mucho más."
                    ),
                    "style": "reassuring"
                }
            ],
            ObjectionType.TRUST_ISSUES: [
                {
                    "response": (
                        "La confianza se construye con el tiempo, y entiendo tu cautela. "
                        "Permíteme demostrarte a través de la experiencia, no solo con promesas. "
                        "Puedo ofrecerte una pequeña prueba para que experimentes por ti mismo/a."
                    ),
                    "style": "honest"
                },
                {
                    "response": (
                        "Entiendo tus reservas. ¿Y si empezamos con un compromiso pequeño, "
                        "suficiente para que veas el valor por ti mismo/a? Si no estás satisfecho/a, "
                        "no hay problema. Confío en que cambiarás de opinión una vez experimentes."
                    ),
                    "style": "flexible"
                }
            ],
            ObjectionType.NOT_NOW: [
                {
                    "response": (
                        "El 'ahora' es una ilusión, querido/a mío/a. Pero precisamente porque "
                        "sé que el momento perfecto rara vez llega, te ofrezco una oportunidad "
                        "que no dependerá del momento, sino de tu decisión."
                    ),
                    "style": "philosophical"
                },
                {
                    "response": (
                        "Entiendo tu prudencia. Pero dime, ¿cuántas veces has pospuesto algo "
                        "importante diciendo 'después'? A veces, 'ahora' es precisamente "
                        "el momento indicado para tomar acción."
                    ),
                    "style": "challenging"
                }
            ],
            ObjectionType.ALTERNATIVE_CHOICE: [
                {
                    "response": (
                        "Ah, veo que has explorado otras opciones. Interesante. ¿Puedo preguntarte "
                        "qué te ha faltado en ellas? Quizás sea precisamente lo que ofrecemos aquí, "
                        "pero de una manera más alineada con tu verdadera esencia."
                    ),
                    "style": "curious"
                },
                {
                    "response": (
                        "No soy mejor o peor que otras opciones, soy diferente. "
                        "Estoy aquí para personas que buscan algo más profundo, "
                        "más personal, más... real. ¿Eres tú una de esas personas?"
                    ),
                    "style": "exclusive"
                }
            ],
            ObjectionType.PERSONAL_CIRCUMSTANCES: [
                {
                    "response": (
                        "Las circunstancias personales son únicas para cada individuo. "
                        "Permíteme adaptarme a tu situación, no para convencerte, "
                        "sino para ofrecerte lo que realmente necesitas en este momento."
                    ),
                    "style": "adaptive"
                },
                {
                    "response": (
                        "Entiendo que cada vida tiene su complejidad. Pero justamente "
                        "en los momentos difíciles es cuando más necesitamos herramientas "
                        "que nos ayuden a navegar con elegancia."
                    ),
                    "style": "empathetic"
                }
            ]
        }
    
    async def handle_objection(
        self,
        user_id: int,
        objection_type: ObjectionType,
        user_context: Optional[Dict] = None
    ) -> str:
        """
        Maneja una objeción del usuario y devuelve la respuesta de Lucien.
        
        Args:
            user_id: ID del usuario que levantó la objeción
            objection_type: Tipo de objeción levantada
            user_context: Contexto adicional del usuario (arquetipo, historial, etc.)
            
        Returns:
            Mensaje de respuesta de Lucien
        """
        # Registrar la objeción para tracking
        from bot.gamification.services.conversion_tracking_service import ConversionTrackingService
        from bot.gamification.enums import ConversionEventType
        
        tracking_service = ConversionTrackingService(self._session)
        await tracking_service.track_conversion_event(
            user_id=user_id,
            event_type=ConversionEventType.OBJECTION_RAISED,
            event_data={
                "objection_type": objection_type.value,
                "context": user_context
            }
        )
        
        # Obtener respuesta adecuada
        response = await self._select_response(user_id, objection_type, user_context)
        
        # Registrar que la objeción fue manejada
        await tracking_service.track_conversion_event(
            user_id=user_id,
            event_type=ConversionEventType.OBJECTION_HANDLED,
            event_data={
                "objection_type": objection_type.value,
                "response_style": response.get("style", "default")
            }
        )
        
        logger.info(f"Lucien handled objection {objection_type.value} for user {user_id}")
        
        return response["response"]
    
    async def _select_response(
        self,
        user_id: int,
        objection_type: ObjectionType,
        user_context: Optional[Dict] = None
    ) -> Dict[str, str]:
        """
        Selecciona la mejor respuesta basada en contexto del usuario.
        
        Args:
            user_id: ID del usuario
            objection_type: Tipo de objeción
            user_context: Contexto adicional del usuario
            
        Returns:
            Diccionario con respuesta y estilo
        """
        # Obtener respuestas disponibles para esta objeción
        available_responses = self._responses.get(objection_type, [])
        
        if not available_responses:
            return {
                "response": (
                    "Interesante tu comentario, mi estimado/a. "
                    "Permíteme reflexionar sobre tu perspectiva y ver cómo puedo "
                    "ayudarte mejor en este camino."
                ),
                "style": "elegant"
            }
        
        # Si hay contexto del usuario, intentar personalizar la respuesta
        if user_context:
            archetype = user_context.get("archetype")
            # Basar la selección en el arquetipo del usuario
            if archetype:
                if "romantic" in str(archetype).lower():
                    # Para usuarios románticos, usar respuestas más emocionales
                    romantic_responses = [r for r in available_responses if r["style"] in ["elegant", "insightful", "empathetic"]]
                    if romantic_responses:
                        return romantic_responses[0]
                elif "analytical" in str(archetype).lower():
                    # Para usuarios analíticos, usar respuestas más lógicas
                    analytical_responses = [r for r in available_responses if r["style"] in ["philosophical", "direct", "honest"]]
                    if analytical_responses:
                        return analytical_responses[0]
                elif "direct" in str(archetype).lower():
                    # Para usuarios directos, ser más directo
                    direct_responses = [r for r in available_responses if r["style"] in ["direct", "challenging"]]
                    if direct_responses:
                        return direct_responses[0]
        
        # Por defecto, usar la primera respuesta disponible
        return available_responses[0]
    
    def get_available_objections(self) -> List[ObjectionType]:
        """Retorna lista de objeciones disponibles."""
        return list(ObjectionType)
    
    async def add_custom_response(
        self,
        objection_type: ObjectionType,
        response: str,
        style: str = "custom"
    ) -> None:
        """
        Añade una respuesta personalizada para un tipo de objeción.
        
        Args:
            objection_type: Tipo de objeción
            response: Texto de la respuesta
            style: Estilo de la respuesta
        """
        new_response = {"response": response, "style": style}
        
        if objection_type in self._responses:
            self._responses[objection_type].append(new_response)
        else:
            self._responses[objection_type] = [new_response]
        
        logger.info(f"Added custom response for objection {objection_type.value}")