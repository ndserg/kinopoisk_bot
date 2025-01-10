from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from states.search import SearchState
from .utils.show_results import get_search_results


router = Router(name=__name__)


@router.message(SearchState.limit)
async def get_results_count(message: Message, state: FSMContext) -> None:
    """Хэндлер этапа запроса количества выводимых результатов"""

    limit_count = message.text

    if limit_count.isdigit() and int(limit_count) > 0:
        await state.update_data(limit=limit_count)

        await get_search_results(message, state)
    else:
        await message.answer("Количество результатов может быть только числом")
