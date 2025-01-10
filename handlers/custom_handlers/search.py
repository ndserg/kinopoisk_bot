from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import Message, CallbackQuery, ErrorEvent
from aiogram.fsm.context import FSMContext
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
    ~StateFilter(None), F.text.startswith("/") | F.text.in_(search_commands)
)
async def unknowns_interceptor(message: Message) -> None:
    """Хэндлер для перехвата вызова комманд или коллбэк данных (комманд для поиска) во время поиска.
    Дает возможность отменить текущий поиск и сбросить текущее состояние.
    """

    await message.answer(
        'Ответы не должны начинаться со знака "/" команды бота или содержать текст из комманд меню поиска. \n'
        'Если хотите выйти из текущего поиска - нажмите "Отмена" или просто продолжите текущий поиск.',
        reply_markup=get_cancel_kb_markup(),
    )


@router.callback_query(~StateFilter(None), F.data == "cancel")
async def cancel_callback_query(call: CallbackQuery, state: FSMContext) -> None:
    """Хэндлер отменяет текущий поиск и сбросывает текущее состояние"""

    await state.clear()
    await call.bot.delete_message(
        chat_id=call.message.chat.id, message_id=call.message.message_id
    )
    await call.message.answer(
        "Текущий поиск прерван. \n"
        "Для начала нового поиска - команда /start. \n"
        "Для вызова справки по командам - /help.",
    )


@router.error(ExceptionTypeFilter(RequestError), F.update.message.as_("message"))
async def error_handler(event: ErrorEvent, message: Message) -> None:
    """Хэндлер перехвата ошибок запроса данных на сервер. Выводит информацию об ошибке."""

    await message.answer(f"❗️Ошибка:\n{event.exception}")
