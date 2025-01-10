from aiogram.fsm.state import State, StatesGroup


class HistoryState(StatesGroup):
    history_start = State()
    history_end = State()
