from aiogram.dispatcher.filters.state import StatesGroup, State


class BotState(StatesGroup):
    AddMetric = State()
    ShowMetric = State()
    DeleteMetric = State()
