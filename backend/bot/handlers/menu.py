from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from bot.keyboards.menu import menu_kb

router = Router()


@router.callback_query(F.data == 'to_menu')
async def to_menu_handler(query: CallbackQuery, state: FSMContext):
    await state.set_state()
    await query.message.edit_text(
        _("Hello! I'm SiteOn - sites block monitor!"),
        reply_markup=menu_kb(),
    )
