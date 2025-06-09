import asyncio

from django.db.models import Max

from bot.integrations.ping_admin import PingAdminClient
from bot.utils.aio import asyncio_wait
from core.models import MonitoredSite, SiteCheck


async def fetch_task_stats(ping_admin: PingAdminClient, site: MonitoredSite):
    last_check_date = (
        await SiteCheck.objects.filter(monitored_site=site).aaggregate(
            last_check_date=Max('date'),
        )
    )['last_check_date']

    stats = await ping_admin.get_task_stats(site.task_id)
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
