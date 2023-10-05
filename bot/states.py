from aiogram.dispatcher.filters.state import StatesGroup, State


class States(StatesGroup):
    types = State()
    rest = State()
    stops = State()
    pizza = State()
    settings = State()
    out_call = State()
    command = State()
    audit = State()
