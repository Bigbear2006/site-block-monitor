from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Literal

from bot.config import config


class CheckType(StrEnum):
    HTTP_HEAD = 'http'
    HTTP_GET = 'http_get'
    HTTP_POST = 'http_post'
    HTTPS_HEAD = 'https'
    HTTPS_GET = 'https_get'
    HTTPS_POST = 'https_post'
    PING = 'ping'

    @classmethod
    def from_url(cls, site_url: str):
        return (
            cls.HTTP_GET if site_url.startswith('http://') else cls.HTTPS_GET
        )


@dataclass(frozen=True)
class BasePingAdminParams:
    """https://ping-admin.com/texts/60.html"""

    a: str = field(init=False, default='api')
    api_key: str = field(init=False, default=config.PING_ADMIN_API_KEY)
    enc: str = field(init=False, default='utf8')


@dataclass(frozen=True)
class AddTaskParams(BasePingAdminParams):
    """https://ping-admin.com/texts/93.html"""

    url: str
    tm: str
    tip: CheckType = CheckType.HTTP_HEAD
    period: int = 5
    algoritm: int = 1
    oshib: int = 0
    sa: str = field(init=False, default='new_task')
    https: str = field(init=False, default=config.PING_ADMIN_WEBHOOK_URL)


@dataclass(frozen=True)
class EditTaskParams(BasePingAdminParams):
    """https://ping-admin.com/texts/110.html"""

    id: int
    url: str = ''
    tm: str = ''
    tip: CheckType | str = ''
    period: int | str = ''
    status: Literal[0, 1, ''] = ''
    sa: str = field(init=False, default='edit_task')


@dataclass(frozen=True)
class DeleteTaskParams(BasePingAdminParams):
    """https://ping-admin.com/texts/92.html"""

    id: int
    sa: str = field(init=False, default='del_task')


@dataclass(frozen=True)
class TaskStatsParams(BasePingAdminParams):
    """https://ping-admin.com/texts/64.html"""

    id: int
    limit: int = 10
    sa: str = field(init=False, default='task_stat')


@dataclass(frozen=True)
class TaskStats:
    status: bool
    description: str
    country: str
    date: datetime
