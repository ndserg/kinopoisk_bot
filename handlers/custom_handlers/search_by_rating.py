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


@router.message(StateFilter(None), F.text == search_types["rating"]["text"])
@router.message(StateFilter(None), Command("rating"))
async def search(message: Message, state: FSMContext) -> None:
    """Хэндлер запуска поиска по рейтингу"""

    await state.set_state(SearchState.rating)
    await state.update_data(search_by=search_types["rating"]["name"])
    await state.update_data(sort={"sort_field": "rating.kp", "sort_type": "-1"})

    await message.answer(
        f"Введите рейтинг фильмов для поиска"
        f"(число, числа через запятую или диапазон через дефис)\n"
        f"<b>Пример: 4, 5, 7-9</b>",
        parse_mode=ParseMode.HTML,
    )


@router.message(SearchState.rating)
async def get_rating(message: Message, state: FSMContext) -> None:
    """Хэндлер получения рейтинга.
    Проверяет введенный результат на соответсвие
    допустимому паттерну (число, числа через запятую, диапазон через дефис).
    """

    range_pattern = r"^[0-9]+(-[0-9]+)*(,\s[0-9]+|,\s[0-9]+-[0-9]+)*$"

    is_match = re.match(range_pattern, message.text)

    if not is_match is None:
        await state.update_data(rating=message.text)

        await genres_select_step(message, state)
    else:
        await message.answer("Нужно указать рейтинг числом")
