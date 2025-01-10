from aiogram.fsm.state import State, StatesGroup


class SearchState(StatesGroup):
    search_by = State()
    title = State()
    rating = State()
    low_budget = State()
    high_budget = State()
    genres_all = State()
    genres_select = State()
    limit = State()
    sort = State()
