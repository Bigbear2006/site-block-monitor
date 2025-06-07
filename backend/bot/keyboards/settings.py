from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _


def settings_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_('Language'),
                    callback_data='language',
                ),
            ],
            [InlineKeyboardButton(text=_('Back'), callback_data='to_menu')],
        ],
    )
