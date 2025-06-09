from urllib.parse import urlparse

from aiogram.dispatcher.event.bases import SkipHandler
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _
from aiohttp import ClientConnectorDNSError, ClientSession, ClientTimeout

from bot.loader import logger


async def validate_url(msg: Message) -> str:
    url = urlparse(msg.text)
    error_msg = _(
        'Invalid URL or it does not exist. '
        'It must start with http:// or https://',
    )

    if url.scheme not in ('http', 'https') or '.' not in url.netloc:
        await msg.answer(error_msg)
        raise SkipHandler

    try:
        async with ClientSession(timeout=ClientTimeout(5)) as session:
            async with session.get(url.geturl()):
                pass
    except ClientConnectorDNSError as e:
        await msg.answer(error_msg)
        raise SkipHandler from e
    except Exception as e:
        logger.exception(str(e), exc_info=e)

    return url.geturl()
