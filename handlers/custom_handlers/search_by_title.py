from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from states.search import SearchState
from .utils.genres_select import genres_select_step
from utils.misc.types import search_types


router = Router(name=__name__)

min_title_length = 4


@router.message(StateFilter(None), F.text == search_types["title"]["text"])
@router.message(StateFilter(None), Command("search"))
async def search(message: Message, state: FSMContext) -> None:
    """Хэндлер запуска поиска по названию фильма"""

    await state.set_state(SearchState.title)
    await state.update_data(search_by=search_types["title"]["name"])
    await message.answer(f"Введите название фильма для поиска")


@router.message(SearchState.title)
async def get_title(message: Message, state: FSMContext) -> None:
    """Хэндлер получения названия фильма. Поиск продолжиться при вводе минимум 4-х символов"""

    if len(message.text) >= min_title_length:
        await state.update_data(title=message.text)

        await genres_select_step(message, state)
    else:
        await message.answer("Введите не менее 4-х символов")
