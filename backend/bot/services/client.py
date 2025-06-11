from core.models import MonitoredSite, Payment, Client


async def get_uncreated_sites_count(client_id: int):
    """
    If client paid for adding of a site,
    but somehow didn't create it (because of error, etc.)
    """
    paid_count = await Payment.objects.filter(
        client_id=client_id,
        payload='add_site',
    ).acount()
    created_count = await MonitoredSite.objects.get_count(client_id)
    return paid_count - created_count


async def get_available_sites_count(client: Client) -> int:
    uncreated = await get_uncreated_sites_count(client.pk)
    if client.has_trial():
        return uncreated + 2  # two free sites on trial
    return uncreated
