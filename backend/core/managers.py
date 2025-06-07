from typing import TYPE_CHECKING, Optional

from aiogram import types
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

if TYPE_CHECKING:
    from core.models import Client, ClientMonitoredSite


class ClientManager(models.Manager):
    async def get_from_event(
        self,
        event: types.Message | types.CallbackQuery,
    ) -> Optional['Client']:
        pk = (
            event.chat.id
            if isinstance(event, types.Message)
            else event.message.chat.id
        )
        try:
            return await self.aget(pk=pk)
        except ObjectDoesNotExist:
            return

    async def from_tg_user(self, user: types.User) -> 'Client':
        return await self.acreate(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            is_premium=user.is_premium or False,
        )

    async def update_from_tg_user(self, user: types.User) -> None:
        await self.filter(pk=user.id).aupdate(
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            is_premium=user.is_premium or False,
        )

    async def create_or_update(
        self,
        user: types.User,
    ) -> tuple['Client', bool]:
        try:
            client = await self.aget(pk=user.id)
            await self.update_from_tg_user(user)
            await client.arefresh_from_db()
            return client, False
        except ObjectDoesNotExist:
            return await self.from_tg_user(user), True

    async def update_by_id(self, pk: int | str, **kwargs):
        return await self.filter(pk=pk).aupdate(**kwargs)


class MonitoredSiteManager(models.Manager):
    def get_client_sites(self, client_id: int | str):
        return self.filter(clients__client_id=client_id).select_related(
            'site',
            'country',
        )

    async def update_by_id(self, pk: int | str, **kwargs):
        return await self.filter(pk=pk).aupdate(**kwargs)


class ClientMonitoredSiteManager(models.Manager):
    async def get_by_id(self, pk: int | str) -> 'ClientMonitoredSite':
        return await self.select_related(
            'monitored_site__site',
            'monitored_site__country',
        ).aget(pk=pk)
