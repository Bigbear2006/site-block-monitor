from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from bot.keyboards.menu import to_menu_kb
from bot.services.monitored_site import get_sites_last_checks
from bot.utils.formatters import date_to_str

router = Router()


@router.callback_query(F.data == 'checks_history')
async def checks_history_handler(query: CallbackQuery):
    status_working = _('Working')
    status_not_working = _('Not Working')
    check_info = _(
        'URL: {url}\nCountry: {country}\nDate: {date}\nStatus: {status}',
    )

    sites = get_sites_last_checks(query.message.chat.id)
    checks_info = '\n\n'.join(
        [
            check_info.format(
                url=i.site.url,
                country=i.country.name,
                date=date_to_str(i.last_checks[0].date),
                status=status_working
                if i.last_checks[0].status
                else status_not_working,
            )
            async for i in sites
        ],
    )

    await query.message.edit_text(
        _('Last checks\n\n{checks_info}').format(checks_info=checks_info),
        reply_markup=to_menu_kb(),
    )
