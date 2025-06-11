import asyncio
import functools

from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.utils.i18n import gettext as _
from celery import shared_task
from celery.utils.log import get_task_logger
from django.db.models import Count, F, Q
from django.utils.timezone import now

from bot.integrations.ping_admin.service import disable_task
from bot.loader import bot, i18n
from bot.utils.aio import asyncio_wait
from core.models import Client, MonitoredSite

task_logger = get_task_logger(__name__)


def handle_send_message_errors(send_message_func):
    async def decorator(chat_id: int | str, text: str, **kwargs):
        try:
            await send_message_func(chat_id, text, **kwargs)
        except TelegramRetryAfter as e:
            task_logger.info(
                f'Cannot send a message to user (id={chat_id}) '
                f'because of rate limit',
            )
            await asyncio.sleep(e.retry_after)
            await send_message_func(chat_id, text, **kwargs)
        except TelegramBadRequest as e:
            task_logger.info(
                f'Cannot send a message to user (id={chat_id}) '
                f'because of an {e.__class__.__name__} error: {str(e)}',
            )

    return decorator


@handle_send_message_errors
async def safe_send_message(chat_id: int | str, text: str, **kwargs):
    return await bot.send_message(chat_id, text, **kwargs)


def async_shared_task(func):
    @shared_task
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
        loop.run_until_complete(func(*args, **kwargs))

    return decorator


async def send_site_status_message(
    client: Client,
    site: MonitoredSite,
    status: str,
):
    with i18n.context(), i18n.use_locale(client.language):
        await safe_send_message(
            client.pk,
            _('Site {site} status in {country}: {status}').format(
                site=site.site.url,
                country=site.country.name,
                status=status,
            ),
        )


@async_shared_task
async def notify_site_status(task_id: int, status: str):
    site = await MonitoredSite.objects.select_related('site', 'country').aget(
        pk=task_id,
    )
    await asyncio_wait(
        [
            asyncio.create_task(
                send_site_status_message(client, site, status),
            )
            async for client in Client.objects.filter(
                monitored_sites__monitored_site=site,
            )
        ],
    )


@async_shared_task
async def disable_monitored_sites():
    sites_ids = (
        MonitoredSite.objects.annotate(
            total_count=Count('clients'),
            unpaid_count=Count(
                'clients',
                filter=Q(
                    clients__client__subscription_end__lt=now(),
                    clients__client__is_active=True,
                ),
            ),
        )
        .filter(total_count=F('unpaid_count'))
        .values_list('pk', flat=True)
        .order_by()
        .distinct()
    )
    await asyncio_wait(
        [
            asyncio.create_task(disable_task(site_id))
            async for site_id in sites_ids
        ],
    )
