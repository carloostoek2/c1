"""
Handler de panel de estadísticas de economía de besitos.

Muestra:
- Estadísticas globales de economía (circulación, promedios, distribución)
- Configuración de fuentes que otorgan besitos (Reacciones, Misiones, Regalo Diario, Niveles)
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery
from html import escape

from bot.filters.admin import IsAdmin
from bot.middlewares import DatabaseMiddleware
from bot.gamification.services.container import GamificationContainer
from bot.utils.keyboards import create_inline_keyboard

router = Router(name="gamification_economy")
router.callback_query.filter(IsAdmin())
router.callback_query.middleware(DatabaseMiddleware())


@router.callback_query(F.data == "gamif:admin:economy")
async def show_economy_stats(
    callback: CallbackQuery,
    gamification: GamificationContainer
):
    """
    Muestra panel completo de economía de besitos.

    Incluye:
    - Resumen global (circulación, promedios, históricos)
    - Top holders (Top 5 usuarios con más besitos)
    - Distribución por nivel
    - Configuración de fuentes (Reacciones, Misiones, Regalo Diario, Niveles)
    """
    # Obtener datos
    overview = await gamification.stats.get_economy_overview()
    sources = await gamification.stats.get_besitos_sources_config()

    # Formatear mensaje
    text = _format_economy_message(overview, sources)

    # Keyboard simple con botón volver
    keyboard = create_inline_keyboard([
        [{"text": "🔙 Volver", "callback_data": "gamif:menu"}]
    ])

    # Enviar mensaje
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await callback.answer()


def _format_economy_message(overview: dict, sources: dict) -> str:
    """
    Formatea el mensaje completo del panel de economía.

    Args:
        overview: Datos de get_economy_overview()
        sources: Datos de get_besitos_sources_config()

    Returns:
        String formateado en HTML para Telegram
    """
    lines = [
        "💰 <b>Estadísticas de Economía</b>",
        "",
        "<b>📊 Resumen Global</b>"
    ]

    # Economía global
    lines.extend([
        f"• Besitos en circulación: <b>{overview['total_in_circulation']:,}</b>",
        f"• Promedio por usuario: <b>{overview['average_per_user']:.1f}</b>",
        f"• Total ganado (histórico): <b>{overview['total_earned_historical']:,}</b>",
        f"• Total gastado (histórico): <b>{overview['total_spent_historical']:,}</b>",
        f"• Usuarios con besitos: <b>{overview['total_users_with_besitos']:,}</b>",
        ""
    ])

    # Top holders (limitar a 5)
    lines.append("<b>🏆 Top Holders</b>")
    if overview['top_holders']:
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        top_5 = overview['top_holders'][:5]  # Limitar a 5
        for i, holder in enumerate(top_5):
            medal = medals[i] if i < len(medals) else "•"
            lines.append(f"  {medal} Usuario #{holder['user_id']}: {holder['total_besitos']:,} besitos")
    else:
        lines.append("  <i>No hay usuarios con besitos</i>")
    lines.append("")

    # Distribución por nivel
    if overview['by_level']:
        lines.append("<b>📈 Distribución por Nivel</b>")
        # Ordenar por total de besitos descendente
        sorted_levels = sorted(
            overview['by_level'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        for level_name, total in sorted_levels[:10]:  # Mostrar top 10 niveles
            lines.append(f"  • {escape(level_name)}: {total:,} besitos")

        if len(overview['by_level']) > 10:
            remaining = len(overview['by_level']) - 10
            lines.append(f"  <i>... y {remaining} niveles más</i>")
        lines.append("")

    # === CONFIGURACIÓN DE FUENTES ===
    lines.extend([
        "━━━━━━━━━━━━━━━━━━━━",
        "<b>⚙️ Configuración de Fuentes</b>",
        ""
    ])

    # Reacciones
    reactions = sources['reactions']
    lines.append(f"<b>❤️ Reacciones</b> ({len(reactions)} activas)")
    if reactions:
        for r in reactions[:5]:  # Mostrar top 5
            lines.append(f"  • {r['emoji']} {escape(r['name'])}: {r['besitos_value']} besitos")
        if len(reactions) > 5:
            lines.append(f"  <i>... y {len(reactions) - 5} más</i>")
    else:
        lines.append("  <i>No hay reacciones configuradas</i>")
    lines.append("")

    # Misiones
    missions = sources['missions']
    lines.append(f"<b>📋 Misiones</b> ({len(missions)} activas con recompensa)")
    if missions:
        for m in missions[:5]:  # Mostrar top 5
            lines.append(f"  • {escape(m['name'])}: {m['besitos_reward']} besitos")
        if len(missions) > 5:
            lines.append(f"  <i>... y {len(missions) - 5} más</i>")
    else:
        lines.append("  <i>No hay misiones con recompensas</i>")
    lines.append("")

    # Regalo diario
    daily = sources['daily_gift']
    status_emoji = "✅" if daily['enabled'] else "❌"
    lines.extend([
        f"<b>🎁 Regalo Diario</b> {status_emoji}",
        f"  • Estado: {'Habilitado' if daily['enabled'] else 'Deshabilitado'}",
    ])
    if daily['enabled']:
        lines.append(f"  • Cantidad: {daily['amount']} besitos")
    else:
        lines.append("  • Cantidad: N/A")
    lines.append("")

    # Niveles
    levels = sources['levels']
    lines.append(f"<b>⭐ Bonificaciones por Nivel</b> ({len(levels)} niveles)")
    if levels:
        for lvl in levels[:5]:  # Mostrar top 5
            lines.append(
                f"  • Nivel {lvl['level_number']} ({escape(lvl['name'])}): "
                f"+{lvl['besitos_bonus']} besitos"
            )
        if len(levels) > 5:
            lines.append(f"  <i>... y {len(levels) - 5} más</i>")
    else:
        lines.append("  <i>No hay bonificaciones por nivel</i>")

    return "\n".join(lines)
