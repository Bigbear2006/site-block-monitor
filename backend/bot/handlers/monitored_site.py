from aiogram import F, Router, flags
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)
from aiogram.utils.i18n import gettext as _

from bot.config import config
from bot.keyboards.menu import to_menu_kb
from bot.keyboards.monitored_site import (
    back_to_monitored_site_kb,
    get_countries_kb,
    get_monitored_sites_kb,
    monitored_site_kb,
    pay_kb,
)
from bot.services.client import get_available_sites_count
from bot.services.monitored_site import (
    add_monitored_site_to_client,
    delete_client_monitored_site,
    edit_client_monitored_site,
)
from bot.states import AddSiteState
from bot.utils.validators import validate_url
from core.models import Client, ClientMonitoredSite, MonitoredSite, Payment

router = Router()


@router.callback_query(F.data == 'add_site')
@flags.with_client
async def add_site_handler(
    query: CallbackQuery,
    state: FSMContext,
    client: Client,
):
    if await get_available_sites_count(client) > 0:
        await state.set_state(AddSiteState.url)
        await query.message.edit_text(
            _('Enter site URL'),
            reply_markup=to_menu_kb(),
        )
        return

    await query.message.edit_text(
        _('Monitoring a single site in one country costs €10 per month'),
        reply_markup=pay_kb(),
    )


@router.callback_query(F.data == 'pay_one_site')
async def pay_one_site(query: CallbackQuery):
    title = _('One site monitoring')
    await query.message.answer_invoice(
        title,
        title,
        'add_site',
        config.CURRENCY,
        [LabeledPrice(label=config.CURRENCY, amount=10 * 100)],
        config.PROVIDER_TOKEN,
    )


@router.pre_checkout_query()
async def accept_pre_checkout_query(query: PreCheckoutQuery):
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def after_one_site_buying(msg: Message, state: FSMContext):
    await Payment.objects.from_message(msg)
    await state.set_state(AddSiteState.url)
    await msg.answer(_('Enter site URL'), reply_markup=to_menu_kb())


@router.callback_query(F.data.startswith('edit_monitored_site_url'))
async def edit_monitored_site_url_handler(
    query: CallbackQuery,
    state: FSMContext,
):
    await state.update_data(cms_id=query.data.split(':')[1])
    await state.set_state(AddSiteState.url)
    await query.message.edit_text(
        _('Enter site URL'),
        reply_markup=to_menu_kb(),
    )


@router.message(F.text, StateFilter(AddSiteState.url))
async def set_site_url_handler(msg: Message, state: FSMContext):
    url = await validate_url(msg)
    if cms_id := await state.get_value('cms_id'):
        await edit_client_monitored_site(cms_id, site_url=url)
        await msg.answer(
            _('URL has been changed!'),
            reply_markup=back_to_monitored_site_kb(cms_id),
        )
        await state.clear()
        return

    await state.update_data(url=url)
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
    cms = await ClientMonitoredSite.objects.with_site_and_country().aget(
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
