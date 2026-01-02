# TRACKING: FASE 6 - CONVERSIÓN Y UPSELL
## Proyecto: El Mayordomo del Diván

---

## ESTADO GENERAL

**Fase:** 6 - Conversión y Upsell
**Estado:** 🟡 EN PROGRESO
**Inicio:** 2025-12-31
**Última actualización:** 2025-12-31

---

## PROGRESO POR SECCIÓN

| ID | Sección | Estado | Tests | Notas |
|----|---------|--------|-------|-------|
| F6.1 | Flujo FREE → VIP | 🔄 | - | La Llave del Diván |
| F6.2 | Ofertas Contextuales VIP | ⬜ | - | Para usuarios Free |
| F6.3 | Flujo VIP → Premium | ⬜ | - | Contenido individual |
| F6.4 | Flujo VIP → Mapa del Deseo | ✅ | - | 3 tiers de paquetes |
| F6.5 | Sistema de Descuentos | ✅ | - | Por mérito y urgencia |
| F6.6 | Manejo de Objeciones | ⬜ | - | Respuestas de Lucien |
| F6.7 | Tracking y Analytics | ⬜ | - | Eventos de conversión |
| F6.8 | Sistema de Pagos Manual | 🔄 | - | **ADAPTADO - Pago manual** |
| F6.9 | Mensajes de Lucien | 🔄 | - | Biblioteca de mensajes |
| F6.10 | Comandos y Handlers | ⬜ | - | /vip, /premium, /mapa |

**Leyenda:**
- ⬜ No iniciado
- 🔄 En progreso
- ✅ Completado

---

## NOTAS IMPORTANTES

### Adaptación de Sistema de Pagos

**SITUACIÓN ACTUAL:**
- No hay sistema de pagos automatizado
- Proceso manual: Usuario contacta → Diana envía datos bancarios → Usuario transfiere → Envía confirmación → Diana aprueba

**ADAPTACIÓN REQUERIDA:**
- F6.8 se implementará con flujo manual de confirmación
- Botones "Obtener mi Llave" mostrarán datos bancarios
- Usuario sube captura de pago
- Admin recibe notificación para aprobar/rechazar
- Activación automática tras aprobación

**FLUJO MANUAL:**
```
Usuario → Click "Obtener Llave"
       → Ve datos bancarios
       → Hace transferencia (fuera del bot)
       → Click "Confirmar Pago"
       → Sube captura
       → Admin notificado
       → Admin aprueba
       → Acceso activado automáticamente
```

---

## SPRINTS PLANIFICADOS

### SPRINT 1: Base de Conversión (F6.1, F6.8, F6.9)
- Flujo FREE → VIP completo
- Sistema de pagos manual
- Mensajes de Lucien

### SPRINT 2: Ofertas y Premium (F6.2, F6.3)
- Ofertas contextuales
- Catálogo Premium

### SPRINT 3: Mapa del Deseo (F6.4, F6.5) ✅
- 3 tiers del Mapa ✅
- Sistema de descuentos ✅

### SPRINT 4: Finalización (F6.6, F6.7, F6.10)
- Objeciones
- Analytics
- Comandos finales

---

## MÉTRICAS DE ÉXITO

- [ ] Flujo FREE → VIP funcional con pago manual
- [ ] Notificaciones admin funcionando
- [ ] Activación automática post-aprobación
- [ ] Tests E2E de conversión completa
- [ ] Tracking de eventos implementado
- [ ] Mensajes de Lucien integrados

---

## DECISIONES TÉCNICAS

### Pago Manual (F6.8)
- **Modelo:** `PendingPayment` (user_id, product, screenshot, status)
- **Estados:** pending, approved, rejected
- **Notificación:** Mensaje a admin con captura
- **Handlers:** callback_confirm_payment, callback_approve_payment

### Activación Automática
- Reutilizar lógica existente de `activate_vip_subscription`
- Otorgar Favores de bienvenida
- Agregar a canal VIP
- Mensaje de confirmación

---

## PRÓXIMOS PASOS

1. Implementar lógica de descuentos y precios dinámicos.
2. Completar la lógica de `activate_product` (otorgar favores, etc.).
3. Implementar el handler para "Tengo preguntas".
4. Crear tests E2E para el flujo de conversión completo.
5. Refinar los mensajes y la interacción.

---

*Documento creado: 2025-12-31*
*Última modificación: 2025-12-31*
