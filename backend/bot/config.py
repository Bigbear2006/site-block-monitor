from dataclasses import dataclass, field
from zoneinfo import ZoneInfo

from environs import env

env.read_env()


@dataclass
class Config:
    BOT_TOKEN: str = field(default_factory=lambda: env('BOT_TOKEN'))
    REDIS_URL: str = field(default_factory=lambda: env('REDIS_URL'))
    PING_ADMIN_API_KEY: str = field(
        default_factory=lambda: env('PING_ADMIN_API_KEY'),
    )
    PAGE_SIZE: int = field(default=5)
    DATE_FMT: str = field(default='%d.%m.%Y %H:%M:%S')
    TZ: ZoneInfo = field(default=ZoneInfo('Europe/Moscow'))


config = Config()
