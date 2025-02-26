import re
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from states.search import SearchState
from .utils.genres_select import genres_select_step
from utils.misc.types import search_types


router = Router(name=__name__)


@router.message(StateFilter(None), F.text == search_types["high_budget"]["text"])
@router.message(StateFilter(None), Command("high"))
async def search(message: Message, state: FSMContext) -> None:
    """Хэндлер запуска поиска фильмов с высоким бюджетом"""

    await state.set_state(SearchState.high_budget)
    await state.update_data(search_by=search_types["high_budget"]["name"])
    await state.update_data(sort={"sort_field": "budget.value", "sort_type": "-1"})

    await message.answer(
        f"Введите бюджет фильма min-max числа через дефис.\n"
        f"<b>Пример: 7000-600000</b>",
        parse_mode=ParseMode.HTML,
    )


@router.message(SearchState.high_budget)
async def get_budget(message: Message, state: FSMContext) -> None:
    """Хэндлер получения бюджета фильма.
    Проверяет введенный результат на соответсвие
    допустимому паттерну (числовой диапазон через дефис).
    """

    range_pattern = r"^[0-9]+-[0-9]+$"

    is_match = re.match(range_pattern, message.text)

    if not is_match is None:
        await state.update_data(high_budget=message.text)

        await genres_select_step(message, state)
    else:
        await message.answer("Нужно указать диапазон числами через дефис")
