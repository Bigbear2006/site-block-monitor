from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from bot.keyboards.menu import menu_kb
from bot.loader import logger
from core.models import Client

router = Router()


@router.message(Command('start'))
async def start_handler(msg: Message, state: FSMContext):
    await state.set_state()
    client, created = await Client.objects.create_or_update(msg.from_user)
    if created:
        logger.info(f'New client {client} id={client.pk} was created')
    else:
        logger.info(f'Client {client} id={client.pk} was updated')

    await msg.answer(
        _("Hello! I'm SiteOn - sites block monitor!"),
        reply_markup=menu_kb(),
    )
