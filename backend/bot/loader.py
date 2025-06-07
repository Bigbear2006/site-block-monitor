import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.i18n import I18n

from bot.config import config

logger = logging.getLogger('bot')
loop = asyncio.get_event_loop()

bot = Bot(config.BOT_TOKEN)
storage = RedisStorage.from_url(config.REDIS_URL)
dp = Dispatcher(storage=storage)
i18n = I18n(path='locales')
