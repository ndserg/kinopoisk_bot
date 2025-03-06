from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from keyboards.inline.cancel import get_cancel_kb_markup
from states.search import SearchState
from utils.misc.types import search_types
from .utils.show_results import get_search_results, pagination
from ..utils.set_cancel_cb import set_cancel_cb

router = Router(name=__name__)

search_commands = {search_types[item]["text"] for item in search_types}


@router.message(SearchState.limit)
async def get_results_count(message: Message, state: FSMContext) -> None:
    """Хэндлер этапа запроса количества выводимых результатов"""

    limit_count = message.text

    if limit_count.isdigit() and int(limit_count) > 0:
        await state.update_data(limit=limit_count)
        await state.set_state(SearchState.search_result)

        await get_search_results(message, state)
    else:
        await message.answer("Количество результатов может быть только числом")


@router.callback_query(SearchState.search_result, F.data.split("#")[0] == "character")
@router.callback_query(SearchState.search_result, F.data.split("#")[0] == "character")
async def characters_page_callback(call: CallbackQuery) -> None:
    """Коллбэк функция - реагирует на клик по кнопкам пагинации и вызывает отрисовку соответствующей страницы"""
    page = int(call.data.split("#")[1])

    await pagination.send_character_page(call.message, page, is_next_page=True)


@router.message(
    SearchState.search_result, ~F.text.startswith("/") & ~F.text.in_(search_commands)
)
@router.message(
    SearchState.search_result, ~F.text.startswith("/") & ~F.text.in_(search_commands)
)
async def unknown_text(message: Message, state: FSMContext) -> None:
    """Хэндлер не известных запросов/текста."""
    msg = await message.answer(
        "Не известная команда.\nЕсли хотите прервать вывод информации - нажмите 'Отмена'",
        reply_markup=get_cancel_kb_markup(),
    )

    await set_cancel_cb(msg, state)
