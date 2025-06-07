from dataclasses import asdict
from datetime import datetime
from typing import Literal

from aiohttp import ClientSession
from yarl import URL

from bot.config import config
from bot.loader import logger
from bot.ping_admin.schemas import (
    AddTaskParams,
    DeleteTaskParams,
    EditTaskParams,
    TaskStats,
    TaskStatsParams,
)


class APIClient:
    def __init__(self, base_url: str | URL | None = None, **session_kwargs):
        self.session = ClientSession(base_url, **session_kwargs)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()


class PingAdminClient(APIClient):
    date_fmt = '%Y-%m-%d %H:%M:%S'

    def __init__(self, **session_kwargs):
        super().__init__('https://ping-admin.com/', **session_kwargs)

    async def add_task(self, params: AddTaskParams) -> int:
        async with self.session.get('', params=asdict(params)) as rsp:
            data = await rsp.json(content_type=None)
            logger.info(data)
        return data[0]['tid']

    async def edit_task(self, params: EditTaskParams) -> bool:
        async with self.session.get('', params=asdict(params)) as rsp:
            data = await rsp.json(content_type=None)
            logger.info(data)
        return 'status' in data[0]

    async def delete_task(self, task_id: int) -> bool:
        async with self.session.get(
            '',
            params=asdict(DeleteTaskParams(task_id)),
        ) as rsp:
            data = await rsp.json(content_type=None)
            logger.info(data)
        return 'status' in data[0]

    async def get_task_stats(
        self,
        task_id: int,
        limit: int = 10,
    ) -> list[TaskStats]:
        async with self.session.get(
            '',
            params=asdict(TaskStatsParams(task_id, limit)),
        ) as rsp:
            data = await rsp.json(content_type=None)
            logger.info(data)

        return [
            TaskStats(
                status=i['status'] == 1,
                description=i['descr'],
                country=i['tm'],
                date=datetime.strptime(i['data'], self.date_fmt).replace(
                    tzinfo=config.TZ,
                ),
            )
            for i in data[0]['tasks_logs']
        ]


async def add_task(site_url: str, country_code: str, period: int = 5) -> int:
    async with PingAdminClient() as ping_admin:
        return await ping_admin.add_task(
            AddTaskParams(url=site_url, tm=country_code, period=period),
        )


async def edit_task(
    task_id: int,
    *,
    site_url: str = '',
    country_code: str = '',
    period: int = '',
    status: Literal[0, 1, ''] = '',
) -> bool:
    async with PingAdminClient() as ping_admin:
        return await ping_admin.edit_task(
            EditTaskParams(
                id=task_id,
                url=site_url,
                tm=country_code,
                period=period,
                status=status,
            ),
        )


async def delete_task(task_id: int) -> bool:
    async with PingAdminClient() as ping_admin:
        return await ping_admin.delete_task(task_id)
