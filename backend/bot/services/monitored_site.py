from datetime import datetime, timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import (
    Prefetch,
    QuerySet,
    RestrictedError,
)
from django.utils.timezone import now

from bot.integrations.ping_admin import add_task, delete_task, edit_task
from bot.loader import logger
from core.models import (
    ClientMonitoredSite,
    Country,
    MonitoredSite,
    Site,
    SiteCheck,
)


async def get_monitored_site(site: Site, country: Country, period: int):
    monitored_site = await MonitoredSite.objects.aget(
        site=site,
        country=country,
    )
    if monitored_site.period > period:
        await edit_task(monitored_site.task_id, period=period)
        await MonitoredSite.objects.update_by_id(
            monitored_site.pk,
            period=period,
        )
    return monitored_site


async def get_or_create_monitored_site(
    site_url: str,
    country_code: str,
    period: int = 5,
) -> MonitoredSite:
    site, created = await Site.objects.aget_or_create(url=site_url)
    country = await Country.objects.aget(code=country_code)
    try:
        monitored_site = await get_monitored_site(site, country, period)
    except ObjectDoesNotExist:
        task_id = await add_task(site_url, country_code, period)
        try:
            monitored_site = await MonitoredSite.objects.acreate(
                task_id=task_id,
                site=site,
                country=country,
                period=period,
            )
        except IntegrityError:
            monitored_site = await get_monitored_site(site, country, period)
    return monitored_site


async def add_monitored_site_to_client(
    client_id: int | str,
    *,
    site_url: str,
    country_code: str,
    period: int = 5,
    subscription_end: datetime | None = None,
) -> ClientMonitoredSite:
    monitored_site = await get_or_create_monitored_site(
        site_url,
        country_code,
        period,
    )
    return await ClientMonitoredSite.objects.acreate(
        client_id=client_id,
        monitored_site=monitored_site,
        subscription_end=subscription_end or now() + timedelta(days=30),
    )


async def edit_client_monitored_site(
    pk: int | str,
    *,
    site_url: str | None = None,
    country_code: str | None = None,
):
    cms = await ClientMonitoredSite.objects.get_by_id(pk)
    clients_count = await ClientMonitoredSite.objects.filter(
        monitored_site=cms.monitored_site,
    ).acount()

    if clients_count == 1:
        if site_url:
            site, created = await Site.objects.aget_or_create(url=site_url)
            cms.monitored_site.site = site
        if country_code:
            cms.monitored_site.country_id = country_code

        await cms.monitored_site.asave()
        await edit_task(
            cms.monitored_site.task_id,
            site_url=site_url or '',
            country_code=country_code or '',
        )
        return

    monitored_site = await get_or_create_monitored_site(
        site_url=site_url or cms.monitored_site.site.url,
        country_code=country_code or cms.monitored_site.country.code,
    )
    await ClientMonitoredSite.objects.filter(pk=cms.pk).aupdate(
        monitored_site=monitored_site,
    )


async def delete_client_monitored_site(pk: int | str):
    cms = await ClientMonitoredSite.objects.aget(pk=pk)
    await ClientMonitoredSite.objects.filter(pk=pk).adelete()
    try:
        await MonitoredSite.objects.filter(pk=cms.monitored_site_id).adelete()
        await delete_task(cms.monitored_site_id)
    except RestrictedError:
        logger.info(f'Cannot delete MonitoredSite pk={cms.monitored_site_id}')


def get_sites_last_checks(client_id: int | str) -> QuerySet[MonitoredSite]:
    return (
        MonitoredSite.objects.filter(
            clients__client_id=client_id,
            checks__isnull=False,
        )
        .prefetch_related(
            Prefetch(
                'checks',
                SiteCheck.objects.order_by('-date')[:1],
                'last_checks',
            ),
        )
        .select_related('site', 'country')
        .distinct()
    )
