from dataclasses import dataclass, field
from zoneinfo import ZoneInfo

from environs import env

env.read_env()


@dataclass
class Config:
    BOT_TOKEN: str = field(default_factory=lambda: env('BOT_TOKEN'))
    PROVIDER_TOKEN: str = field(default_factory=lambda: env('PROVIDER_TOKEN'))
    REDIS_URL: str = field(default_factory=lambda: env('REDIS_URL'))
    PING_ADMIN_API_KEY: str = field(
        default_factory=lambda: env('PING_ADMIN_API_KEY'),
    )
    PING_ADMIN_WEBHOOK_URL: str = field(
        default_factory=lambda: env('PING_ADMIN_WEBHOOK_URL'),
    )

    PAGE_SIZE: int = field(default=5)
    DATE_FMT: str = field(default='%d.%m.%Y %H:%M:%S')
    TZ: ZoneInfo = field(default=ZoneInfo('Europe/Moscow'))
    CURRENCY: str = field(default='EUR')


config = Config()
