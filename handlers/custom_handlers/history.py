from datetime import datetime
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from aiogram_calendar.schemas import SimpleCalAct
from states.history import HistoryState
from utils.misc.types import search_types


router = Router(name=__name__)


calendar = SimpleCalendar(locale="ru-RU", show_alerts=True)
calendar.set_dates_range(datetime(2022, 1, 1), datetime(2026, 12, 31))

today: datetime = datetime.now()


async def date_picker(
    callback_query: CallbackQuery,
    callback_data: SimpleCalendarCallback,
    state: FSMContext,
) -> str | None:
    """Функция выбора даты. Проверяет выбрана дата или произошла отмена выбора.

    Returns:
        Возвращает строку с датой или None в случае отмены выбора.
    """
    result: str | None = None

    selected, date = await calendar.process_selection(callback_query, callback_data)

    if selected:
        await callback_query.bot.delete_message(
            callback_query.message.chat.id, callback_query.message.message_id
        )

        result = date.strftime("%d.%m.%Y")
    elif callback_data.act == SimpleCalAct.cancel:
        await callback_query.bot.delete_message(
            callback_query.message.chat.id, callback_query.message.message_id
        )

        await state.clear()

        await callback_query.message.answer("Вы отменили вывод истории поиска!")

    return result


@router.message(F.text == search_types["history"]["text"])
@router.message(Command("history"))
async def get_history(message: Message, state: FSMContext) -> None:
    """Хэндлер запуска вывода истории поисковых запросов"""

    await state.set_state(HistoryState.history_start)

    await message.answer(
        "Выберите за какой период показать историю запросов",
        reply_markup=await calendar.start_calendar(year=today.year, month=today.month),
    )


@router.message(HistoryState.history_start or HistoryState.history_end)
async def not_date_selected(message: Message) -> None:
    """Хэндлер вызывается если не выбраны даты начала и конца периода для показа истории запросов."""

    await message.answer("Необходимо выбрать даты или нажать кнопку отмены - 'Cancel'.")


@router.callback_query(HistoryState.history_start, SimpleCalendarCallback.filter())
async def get_start_date(
    callback_query: CallbackQuery,
    callback_data: SimpleCalendarCallback,
    state: FSMContext,
) -> None:
    """Хэндлер получения начальной даты поиска"""

    start_date = await date_picker(callback_query, callback_data, state)

    if not start_date is None:
        await state.update_data(history_start=start_date)

        await callback_query.message.answer(
            f"Начальная дата {start_date}\nТеперь выберите конечную дату",
            reply_markup=await calendar.start_calendar(
                year=today.year, month=today.month
            ),
        )

        await state.set_state(HistoryState.history_end)


@router.callback_query(HistoryState.history_end, SimpleCalendarCallback.filter())
async def get_end_date(
    callback_query: CallbackQuery,
    callback_data: SimpleCalendarCallback,
    state: FSMContext,
) -> None:
    """Хэндлер получения конечной даты поиска"""

    end_date = await date_picker(callback_query, callback_data, state)

    if not end_date is None:
        await state.update_data(history_end=end_date)

        data = await state.get_data()

        await callback_query.message.answer(
            f"Период показа истории поиска с {data["history_start"]} по {data["history_end"]}"
        )

        await state.clear()
