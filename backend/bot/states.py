from aiogram.fsm.state import State, StatesGroup


class AddSiteState(StatesGroup):
    url = State()
    country = State()
    invalid_url = State()
