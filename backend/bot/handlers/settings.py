import contextlib

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from bot.keyboards.settings import settings_kb
from bot.keyboards.utils import keyboard_from_choices
from bot.loader import i18n
from core.choices import Language
from core.models import Client

router = Router()


@router.callback_query(F.data == 'settings')
async def settings_handler(query: CallbackQuery):
    await query.message.edit_text(_('Settings'), reply_markup=settings_kb())


@router.callback_query(F.data.startswith('language'))
async def change_language_handler(query: CallbackQuery, state: FSMContext):
    if ':' in query.data:
        lang = query.data.split(':')[1]
        await state.update_data(language=lang)
        await Client.objects.update_by_id(
            pk=query.message.chat.id,
            language=lang,
        )
    else:
        client = await Client.objects.get_from_event(query)
        lang = client.language

    with (
        contextlib.suppress(TelegramBadRequest),
        i18n.context(),
        i18n.use_locale(lang),
    ):
        await query.message.edit_text(
            _('Current language: {lang}').format(lang=Language(lang).label),
            reply_markup=keyboard_from_choices(
                Language,
                prefix='language',
                back_button_data='settings',
            ),
        )
