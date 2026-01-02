"""Enums para el sistema de conversiones y ventas.

Define enumeraciones usadas en los modelos de tracking de conversiones.
"""

from enum import Enum


class ConversionEventType(str, Enum):
    """
    Tipos de eventos de conversión y ventas.

    Categorías:
        - Visualización: Eventos relacionados con ver ofertas
        - Interacción: Eventos de clicks y acciones
        - Pago: Eventos relacionados con el proceso de pago
        - Conversión: Eventos de activación de productos
        - Objecciones: Eventos relacionados con objecciones y respuestas
        - Upselling: Eventos de venta cruzada y upselling
    """

    # Visualización de ofertas
    CONVERSION_VIEW = "conversion_view"  # Usuario ve oferta
    OFFER_CLICKED = "offer_clicked"      # Usuario hace click en oferta
    PRODUCT_VIEW = "product_view"        # Usuario ve detalles de producto

    # Interacciones de conversión
    CONVERSION_CLICK = "conversion_click"     # Click en botón de conversión
    CTA_CLICKED = "cta_clicked"              # Click en call-to-action
    PAYMENT_INITIATED = "payment_initiated"   # Inicio de proceso de pago
    PAYMENT_CANCELLED = "payment_cancelled"   # Usuario cancela pago

    # Eventos de pago
    PAYMENT_CONFIRMED = "payment_confirmed"    # Usuario confirma/envía pago
    PAYMENT_APPROVED = "payment_approved"      # Admin aprueba pago manual
    PAYMENT_REJECTED = "payment_rejected"      # Admin rechaza pago manual
    PAYMENT_FAILED = "payment_failed"          # Falla en proceso de pago

    # Activación de productos
    PRODUCT_ACTIVATED = "product_activated"    # Producto activado para usuario
    VIP_ACTIVATED = "vip_activated"           # Activación de VIP
    PREMIUM_ACTIVATED = "premium_activated"   # Activación de Premium
    MAPA_ACTIVATED = "mapa_activated"         # Activación de Mapa del Deseo

    # Objecciones y respuestas
    OBJECTION_RAISED = "objection_raised"      # Usuario levanta objeción
    OBJECTION_HANDLED = "objection_handled"    # Lucien maneja objeción
    OBJECTION_OFFERED = "objection_offered"    # Oferta presentada como respuesta a objeción

    # Upselling y ventas cruzadas
    UPSELL_OFFERED = "upsell_offered"          # Oferta de upsell presentada
    UPSELL_ACCEPTED = "upsell_accepted"        # Usuario acepta oferta de upsell
    UPSELL_REJECTED = "upsell_rejected"        # Usuario rechaza oferta de upsell
    CROSS_SELL_OFFERED = "cross_sell_offered"  # Oferta de venta cruzada
    CROSS_SELL_ACCEPTED = "cross_sell_accepted"
    CROSS_SELL_REJECTED = "cross_sell_rejected"

    # Seguimiento de comportamiento post-venta
    POST_SALE_ENGAGEMENT = "post_sale_engagement"  # Compromiso post-venta
    RE_PURCHASE_INTENT = "re_purchase_intent"      # Indicador de intención de re-compra
    REFERRAL_GENERATED = "referral_generated"      # Generación de referido post-venta

    def __str__(self) -> str:
        """Retorna valor string del enum."""
        return self.value

    @property
    def display_name(self) -> str:
        """Retorna nombre legible del tipo de evento."""
        names = {
            ConversionEventType.CONVERSION_VIEW: "Visualización de conversión",
            ConversionEventType.OFFER_CLICKED: "Click en oferta",
            ConversionEventType.PRODUCT_VIEW: "Vista de producto",
            ConversionEventType.CONVERSION_CLICK: "Click de conversión",
            ConversionEventType.CTA_CLICKED: "Click en CTA",
            ConversionEventType.PAYMENT_INITIATED: "Pago iniciado",
            ConversionEventType.PAYMENT_CANCELLED: "Pago cancelado",
            ConversionEventType.PAYMENT_CONFIRMED: "Pago confirmado",
            ConversionEventType.PAYMENT_APPROVED: "Pago aprobado",
            ConversionEventType.PAYMENT_REJECTED: "Pago rechazado",
            ConversionEventType.PAYMENT_FAILED: "Pago fallido",
            ConversionEventType.PRODUCT_ACTIVATED: "Producto activado",
            ConversionEventType.VIP_ACTIVATED: "VIP activado",
            ConversionEventType.PREMIUM_ACTIVATED: "Premium activado",
            ConversionEventType.MAPA_ACTIVATED: "Mapa del Deseo activado",
            ConversionEventType.OBJECTION_RAISED: "Objeción levantada",
            ConversionEventType.OBJECTION_HANDLED: "Objeción manejada",
            ConversionEventType.OBJECTION_OFFERED: "Oferta por objeción",
            ConversionEventType.UPSELL_OFFERED: "Upsell ofrecido",
            ConversionEventType.UPSELL_ACCEPTED: "Upsell aceptado",
            ConversionEventType.UPSELL_REJECTED: "Upsell rechazado",
            ConversionEventType.CROSS_SELL_OFFERED: "Venta cruzada ofrecida",
            ConversionEventType.CROSS_SELL_ACCEPTED: "Venta cruzada aceptada",
            ConversionEventType.CROSS_SELL_REJECTED: "Venta cruzada rechazada",
            ConversionEventType.POST_SALE_ENGAGEMENT: "Compromiso post-venta",
            ConversionEventType.RE_PURCHASE_INTENT: "Intención de re-compra",
            ConversionEventType.REFERRAL_GENERATED: "Referido generado",
        }
        return names[self]

    @property
    def category(self) -> str:
        """Retorna la categoría del tipo de evento."""
        categories = {
            ConversionEventType.CONVERSION_VIEW: "view",
            ConversionEventType.OFFER_CLICKED: "interaction",
            ConversionEventType.PRODUCT_VIEW: "view",
            ConversionEventType.CONVERSION_CLICK: "interaction",
            ConversionEventType.CTA_CLICKED: "interaction",
            ConversionEventType.PAYMENT_INITIATED: "payment",
            ConversionEventType.PAYMENT_CANCELLED: "payment",
            ConversionEventType.PAYMENT_CONFIRMED: "payment",
            ConversionEventType.PAYMENT_APPROVED: "payment",
            ConversionEventType.PAYMENT_REJECTED: "payment",
            ConversionEventType.PAYMENT_FAILED: "payment",
            ConversionEventType.PRODUCT_ACTIVATED: "conversion",
            ConversionEventType.VIP_ACTIVATED: "conversion",
            ConversionEventType.PREMIUM_ACTIVATED: "conversion",
            ConversionEventType.MAPA_ACTIVATED: "conversion",
            ConversionEventType.OBJECTION_RAISED: "objection",
            ConversionEventType.OBJECTION_HANDLED: "objection",
            ConversionEventType.OBJECTION_OFFERED: "objection",
            ConversionEventType.UPSELL_OFFERED: "upsell",
            ConversionEventType.UPSELL_ACCEPTED: "upsell",
            ConversionEventType.UPSELL_REJECTED: "upsell",
            ConversionEventType.CROSS_SELL_OFFERED: "cross_sell",
            ConversionEventType.CROSS_SELL_ACCEPTED: "cross_sell",
            ConversionEventType.CROSS_SELL_REJECTED: "cross_sell",
            ConversionEventType.POST_SALE_ENGAGEMENT: "post_sale",
            ConversionEventType.RE_PURCHASE_INTENT: "post_sale",
            ConversionEventType.REFERRAL_GENERATED: "post_sale",
        }
        return categories[self]