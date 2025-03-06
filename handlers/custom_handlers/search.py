from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import Message, CallbackQuery, ErrorEvent
from aiogram.fsm.context import FSMContext

from states.search import SearchState
from .search_by_title import router as title_router
from .search_by_rating import router as raiting_router
from .search_by_low_budget import router as low_budget_router
from .search_by_high_budget import router as high_budget_router
from .history import router as history_router
from .genres_handlers import router as genres_router
from .limit_handlers import router as limit_router
from handlers.utils.pagination import router as pagination_router
from api.utils.error_handlers import RequestError
from keyboards.inline.cancel import get_cancel_kb_markup
from utils.misc.types import search_types
from .utils.show_results import pagination
from ..utils.delete_cancel_msgs import delete_cancel_msgs
from ..utils.set_cancel_cb import set_cancel_cb

router = Router(name="search")
router.include_routers(
    title_router,
    raiting_router,
    low_budget_router,
    high_budget_router,
    history_router,
    genres_router,
    limit_router,
    pagination_router,
)


search_commands = {search_types[item]["text"] for item in search_types}


@router.message(
    StateFilter(SearchState), F.text.startswith("/") | F.text.in_(search_commands)
)
async def unknowns_commands(message: Message, state: FSMContext) -> None:
    """Хэндлер для перехвата вызова комманд или коллбэк данных (комманд для поиска) во время поиска.
    Дает возможность отменить текущий поиск и сбросить текущее состояние.
    """
    msg = await message.answer(
        'Ответы не должны начинаться со знака "/" команды бота или содержать текст из комманд меню поиска. \n'
        'Если хотите выйти из текущего поиска - нажмите "Отмена" или просто продолжите текущий поиск.',
        reply_markup=get_cancel_kb_markup(),
    )

    await set_cancel_cb(msg, state)


@router.callback_query(StateFilter(SearchState), F.data == "cancel")
async def cancel_callback(call: CallbackQuery, state: FSMContext) -> None:
    """Хэндлер отменяет текущий поиск и сбросывает текущее состояние"""
    data = await state.get_data()

    if not data.get("genres_select_msg_id") is None:
        await call.bot.delete_message(
            message_id=data["genres_select_msg_id"], chat_id=call.message.chat.id
        )

    await pagination.destroy_pagination(call, call.message.chat.id)

    if not data.get("cancel_cbs_ids") is None:
        await delete_cancel_msgs(
            call, msg_ids=data["cancel_cbs_ids"], chat_id=call.message.chat.id
        )

    await state.clear()

    await call.message.answer(
        "Текущий поиск прерван. \n"
        "Для начала нового поиска - команда /start. \n"
        "Для вызова справки по командам - /help.",
    )


@router.error(ExceptionTypeFilter(RequestError), F.update.message.as_("message"))
async def error_handler(event: ErrorEvent, message: Message) -> None:
    """Хэндлер перехвата ошибок запроса данных на сервер. Выводит информацию об ошибке."""

    await message.answer(f"❗️Ошибка:\n{event.exception}")
