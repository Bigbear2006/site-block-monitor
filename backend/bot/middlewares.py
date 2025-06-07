from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, TelegramObject
from aiogram.utils.i18n import I18nMiddleware

from core.models import Client


class ClientMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: dict[str, Any],
    ) -> Any:
        with_client = get_flag(data, 'with_client')
        if with_client:
            data['client'] = await Client.objects.get_from_event(event)
        return await handler(event, data)


class CustomI18nMiddleware(I18nMiddleware):
    async def get_locale(
        self,
        event: TelegramObject,
        data: dict[str, Any],
    ) -> str:
        state: FSMContext = data.get('state')
        lang = await state.get_value('language')

        if lang:
            return lang

        client = data.get('client')
        if not client:
            client = await Client.objects.get_from_event(event)
            if not client:
                return 'en'

        await state.update_data(language=client.language)
        return client.language
