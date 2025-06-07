from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.db.models import Choices, QuerySet

from bot.config import config


async def get_pagination_buttons(
    previous_button_data: str = None,
    next_button_data: str = None,
) -> list[InlineKeyboardButton]:
    pagination_buttons = []

    if previous_button_data:
        pagination_buttons.append(
            InlineKeyboardButton(
                text='<<',
                callback_data=previous_button_data,
            ),
        )

    if next_button_data:
        pagination_buttons.append(
            InlineKeyboardButton(text='>>', callback_data=next_button_data),
        )

    return pagination_buttons


async def keyboard_from_queryset(
    queryset: QuerySet,
    *,
    prefix: str,
    back_button_data: str = None,
    previous_button_data: str = None,
    next_button_data: str = None,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    async for obj in queryset:
        kb.button(text=str(obj), callback_data=f'{prefix}:{obj.pk}')

    if back_button_data:
        kb.button(text=_('Back'), callback_data=back_button_data)

    kb.adjust(1)
    kb.row(
        *await get_pagination_buttons(
            previous_button_data,
            next_button_data,
        ),
    )
    return kb.as_markup()


async def get_paginated_keyboard(
    queryset: QuerySet,
    *,
    prefix: str = '',
    page: int = 1,
    page_size: int = config.PAGE_SIZE,
    back_button_data: str = '',
    previous_button_data: str = '',
    next_button_data: str = '',
) -> InlineKeyboardMarkup:
    total_count = await queryset.acount()
    total_pages = (total_count + page_size - 1) // page_size
    start, end = (page - 1) * page_size, page * page_size

    return await keyboard_from_queryset(
        queryset[start:end],
        prefix=prefix,
        back_button_data=back_button_data,
        previous_button_data=previous_button_data if page > 1 else None,
        next_button_data=next_button_data if page < total_pages else None,
    )


def one_button_keyboard(
    *,
    back_button_data: str = None,
    **kwargs,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(**kwargs)
    if back_button_data:
        kb.button(text=_('Back'), callback_data=back_button_data)
    return kb.adjust(1).as_markup()


def keyboard_from_choices(
    choices: type[Choices],
    *,
    prefix: str = '',
    back_button_data: str | None = None,
    adjust: int = 1,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for value, label in choices.choices:
        kb.button(
            text=label,
            callback_data=f'{prefix}:{value}' if prefix else str(value),
        )
    if back_button_data:
        kb.button(text=_('Back'), callback_data=back_button_data)
    return kb.adjust(adjust).as_markup()
