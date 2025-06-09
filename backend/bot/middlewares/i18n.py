from typing import Any

from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject
from aiogram.utils.i18n import I18nMiddleware

from core.models import Client


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
