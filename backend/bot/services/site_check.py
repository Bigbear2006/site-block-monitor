import asyncio

from django.db.models import Max

from bot.loader import logger
from bot.ping_admin.client import PingAdminClient
from core.models import MonitoredSite, SiteCheck


async def asyncio_wait(
    fs,
    *,
    timeout=None,
    return_when=asyncio.ALL_COMPLETED,
) -> tuple[set, set]:
    if not fs:
        return set(), set()
    return await asyncio.wait(fs, timeout=timeout, return_when=return_when)


async def fetch_task_stats(ping_admin: PingAdminClient, site: MonitoredSite):
    last_check_date = (
        await SiteCheck.objects.filter(monitored_site=site).aaggregate(
            last_check_date=Max('date'),
        )
    )['last_check_date']

    stats = await ping_admin.get_task_stats(site.task_id)
    logger.info(stats)
    if last_check_date:
        stats = [i for i in stats if i.date > last_check_date]

    await SiteCheck.objects.abulk_create(
        [
            SiteCheck(
                monitored_site=site,
                status=stat.status,
                description=stat.description,
                country_id=stat.country or site.country_id,
                date=stat.date,
            )
            for stat in stats
        ],
    )


async def fetch_tasks_stats():
    async with PingAdminClient() as ping_admin:
        sem = asyncio.Semaphore(2)
        async with sem:
            await asyncio_wait(
                [
                    asyncio.create_task(fetch_task_stats(ping_admin, site))
                    async for site in MonitoredSite.objects.all()
                ],
            )
