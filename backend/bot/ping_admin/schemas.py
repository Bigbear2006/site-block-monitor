from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

from bot.config import config


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
    period: int = 5
    algoritm: int = 1
    oshib: int = 0
    sa: str = field(init=False, default='new_task')


@dataclass(frozen=True)
class EditTaskParams(BasePingAdminParams):
    """https://ping-admin.com/texts/110.html"""

    id: int
    url: str = ''
    tm: str = ''
    period: int = ''
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
