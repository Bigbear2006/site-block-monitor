from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from bot.keyboards.menu import to_menu_kb
from bot.keyboards.monitored_site import (
    back_to_monitored_site_kb,
    get_countries_kb,
    get_monitored_sites_kb,
    monitored_site_kb,
)
from bot.services.monitored_site import (
    add_monitored_site_to_client,
    delete_client_monitored_site,
    edit_client_monitored_site,
)
from bot.states import AddSiteState
from core.models import ClientMonitoredSite

router = Router()


@router.callback_query(F.data == 'add_site')
async def add_site_handler(query: CallbackQuery, state: FSMContext):
    await state.set_state(AddSiteState.url)
    await query.message.edit_text(
        _('Enter site URL'),
        reply_markup=to_menu_kb(),
    )


@router.callback_query(F.data.startswith('edit_monitored_site_url'))
async def edit_monitored_site_url_handler(
    query: CallbackQuery,
    state: FSMContext,
):
    await state.update_data(cms_id=query.data.split(':')[1])
    await add_site_handler(query, state)


@router.message(F.text, StateFilter(AddSiteState.url))
async def set_site_url_handler(msg: Message, state: FSMContext):
    if cms_id := await state.get_value('cms_id'):
        await edit_client_monitored_site(cms_id, site_url=msg.text)
        await msg.answer(
            _('URL has been changed!'),
            reply_markup=back_to_monitored_site_kb(cms_id),
        )
        await state.clear()
        return

    await state.update_data(url=msg.text)
    await state.set_state(AddSiteState.country)
    await msg.answer(
        _('Choose country'),
        reply_markup=await get_countries_kb(),
    )


@router.callback_query(F.data.startswith('edit_monitored_site_country'))
async def choose_country_handler(query: CallbackQuery, state: FSMContext):
    await state.update_data(cms_id=query.data.split(':')[1])
    await state.set_state(AddSiteState.country)
    await query.message.edit_text(
        _('Choose country'),
        reply_markup=await get_countries_kb(),
    )


@router.callback_query(
    F.data.startswith('country'),
    StateFilter(AddSiteState.country),
)
async def set_country_handler(query: CallbackQuery, state: FSMContext):
    country_code = query.data.split(':')[1]
    if cms_id := await state.get_value('cms_id'):
        await edit_client_monitored_site(cms_id, country_code=country_code)
        await query.message.edit_text(
            _('Country has been changed!'),
            reply_markup=back_to_monitored_site_kb(cms_id),
        )
        await state.clear()
        return

    await add_monitored_site_to_client(
        query.message.chat.id,
        site_url=await state.get_value('url'),
        country_code=country_code,
    )
    await query.message.edit_text(_('Site added!'), reply_markup=to_menu_kb())
    await state.clear()


@router.callback_query(F.data == 'monitored_sites')
async def monitored_sites_handler(query: CallbackQuery):
    await query.message.edit_text(
        _("You're monitoring these sites"),
        reply_markup=await get_monitored_sites_kb(query.message.chat.id),
    )


@router.callback_query(F.data.startswith('monitored_site'))
async def monitored_site_handler(query: CallbackQuery):
    cms = await ClientMonitoredSite.objects.select_related(
        'monitored_site__site',
        'monitored_site__country',
    ).aget(
        client_id=query.message.chat.id,
        monitored_site_id=query.data.split(':')[1],
    )

    await query.message.edit_text(
        _('URL: {url}\nCountry: {country}').format(
            url=cms.monitored_site.site.url,
            country=cms.monitored_site.country.name,
        ),
        reply_markup=monitored_site_kb(cms.pk),
    )


@router.callback_query(F.data.startswith('delete_monitored_site'))
async def delete_monitored_site_handler(query: CallbackQuery):
    await delete_client_monitored_site(query.data.split(':')[1])
    await monitored_sites_handler(query)
