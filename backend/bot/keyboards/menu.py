from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _

from bot.keyboards.utils import one_button_keyboard


def menu_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_('Add site'),
                    callback_data='add_site',
                ),
                InlineKeyboardButton(
                    text=_('My sites'),
                    callback_data='monitored_sites',
                ),
            ],
            [
                InlineKeyboardButton(
                    text=_('Checks history'),
                    callback_data='checks_history',
                ),
                InlineKeyboardButton(
                    text=_('Settings'),
                    callback_data='settings',
                ),
            ],
        ],
    )


def to_menu_kb():
    return one_button_keyboard(text=_('Back'), callback_data='to_menu')
