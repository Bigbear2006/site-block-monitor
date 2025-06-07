import os

import django
from aiogram import F
from aiogram.enums import ChatType
from aiogram.types import BotCommand

from bot.loader import bot, dp, i18n, logger, loop
from bot.utils.loop_tasks import run_loop_task


async def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()

    from bot.handlers import (
        checks_history,
        menu,
        monitored_site,
        settings,
        start,
    )
    from bot.middlewares import ClientMiddleware, CustomI18nMiddleware
    from bot.services.site_check import fetch_tasks_stats

    dp.include_routers(
        start.router,
        menu.router,
        monitored_site.router,
        checks_history.router,
        settings.router,
    )

    dp.message.filter(F.chat.type == ChatType.PRIVATE)

    dp.message.middleware(ClientMiddleware())
    dp.callback_query.middleware(ClientMiddleware())

    i18n_middleware = CustomI18nMiddleware(i18n)
    i18n_middleware.setup(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(
        [
            BotCommand(command='/start', description='Start bot'),
        ],
    )

    loop.create_task(run_loop_task(fetch_tasks_stats))

    logger.info('Starting bot...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    loop.run_until_complete(main())
