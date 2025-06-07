from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _

from bot.keyboards.utils import keyboard_from_queryset, one_button_keyboard
from core.models import Country, MonitoredSite


def monitored_site_kb(cms_id: int | str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_('Edit URL'),
                    callback_data=f'edit_monitored_site_url:{cms_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    text=_('Edit Country'),
                    callback_data=f'edit_monitored_site_country:{cms_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    text=_('Delete'),
                    callback_data=f'delete_monitored_site:{cms_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    text=_('Back'),
                    callback_data='monitored_sites',
                ),
            ],
        ],
    )


def back_to_monitored_site_kb(cms_id: int | str):
    return one_button_keyboard(
        text=_('Back'),
        callback_data=f'monitored_site:{cms_id}',
    )


async def get_countries_kb():
    return await keyboard_from_queryset(
        Country.objects.all(),
        prefix='country',
    )


async def get_monitored_sites_kb(client_id: int | str):
    return await keyboard_from_queryset(
        MonitoredSite.objects.get_client_sites(client_id),
        prefix='monitored_site',
        back_button_data='to_menu',
    )
