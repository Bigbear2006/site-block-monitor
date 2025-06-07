from datetime import datetime

from bot.config import config


def date_to_str(__date: datetime):
    return datetime.strftime(__date, config.DATE_FMT)
