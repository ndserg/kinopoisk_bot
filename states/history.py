from aiogram.fsm.state import State, StatesGroup


class HistoryState(StatesGroup):
    calendar_id = State()
    history_start = State()
    history_end = State()
    history_show = State()
    films_show = State()
    watched_list = State()
