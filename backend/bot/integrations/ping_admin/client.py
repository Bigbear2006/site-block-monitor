from dataclasses import asdict
from datetime import datetime

from aiohttp import ClientResponse

from bot.config import config
from bot.integrations.common.client import APIClient
from bot.integrations.ping_admin.exceptions import (
    PingAdminException,
    URLDoesNotExist,
)
from bot.integrations.ping_admin.schemas import (
    AddTaskParams,
    DeleteTaskParams,
    EditTaskParams,
    TaskStats,
    TaskStatsParams,
)
from bot.loader import logger


async def get_data(rsp: ClientResponse) -> dict:
    data = await rsp.json(content_type=None)
    logger.info(data)
    if err := data[0].get('error'):
        if 'Невозможно определить IP проверяемого адреса' in err:
            raise URLDoesNotExist(err)
        raise PingAdminException(err)
    return data[0]


class PingAdminClient(APIClient):
    date_fmt = '%Y-%m-%d %H:%M:%S'

    def __init__(self, **session_kwargs):
        super().__init__('https://ping-admin.com/', **session_kwargs)

    async def add_task(self, params: AddTaskParams) -> int:
        async with self.session.get('', params=asdict(params)) as rsp:
            data = await get_data(rsp)
        return data['tid']

    async def edit_task(self, params: EditTaskParams) -> bool:
        async with self.session.get('', params=asdict(params)) as rsp:
            data = await get_data(rsp)
        return 'status' in data

    async def delete_task(self, task_id: int) -> bool:
        async with self.session.get(
            '',
            params=asdict(DeleteTaskParams(task_id)),
        ) as rsp:
            data = await get_data(rsp)
        return 'status' in data

    async def get_task_stats(
        self,
        task_id: int,
        limit: int = 10,
    ) -> list[TaskStats]:
        async with self.session.get(
            '',
            params=asdict(TaskStatsParams(task_id, limit)),
        ) as rsp:
            data = await get_data(rsp)
        return [
            TaskStats(
                status=i['status'] == 1,
                description=i['descr'],
                country=i['tm'],
                date=datetime.strptime(i['data'], self.date_fmt).replace(
                    tzinfo=config.TZ,
                ),
            )
            for i in data['tasks_logs']
        ]
