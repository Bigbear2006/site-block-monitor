from typing import Literal

from bot.integrations.ping_admin.client import PingAdminClient
from bot.integrations.ping_admin.schemas import (
    AddTaskParams,
    CheckType,
    EditTaskParams,
)


async def add_task(site_url: str, country_code: str, period: int = 5) -> int:
    async with PingAdminClient() as ping_admin:
        return await ping_admin.add_task(
            AddTaskParams(
                url=site_url,
                tm=country_code,
                tip=CheckType.from_url(site_url),
                period=period,
            ),
        )


async def edit_task(
    task_id: int,
    *,
    site_url: str = '',
    country_code: str = '',
    period: int | str = '',
    status: Literal[0, 1, ''] = '',
) -> bool:
    async with PingAdminClient() as ping_admin:
        check_type = CheckType.from_url(site_url) if site_url else ''
        return await ping_admin.edit_task(
            EditTaskParams(
                id=task_id,
                url=site_url,
                tm=country_code,
                tip=check_type,
                period=period,
                status=status,
            ),
        )


async def enable_task(task_id: int) -> bool:
    return await edit_task(task_id, status=1)


async def disable_task(task_id: int) -> bool:
    return await edit_task(task_id, status=0)


async def delete_task(task_id: int) -> bool:
    async with PingAdminClient() as ping_admin:
        return await ping_admin.delete_task(task_id)
