import json
from datetime import datetime, date
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, get_user_locale
from aiogram_calendar.schemas import SimpleCalAct

from handlers.utils.delete_cancel_msgs import delete_cancel_msgs
from handlers.utils.set_cancel_cb import set_cancel_cb
from keyboards.inline.cancel import get_cancel_kb_markup
from keyboards.inline.watch_list import get_watchlist_kb_markup
from states.history import HistoryState
from utils.misc.movie_card import get_movie_card_markup
from utils.misc.types import search_types
from database.CRUD import get_histories, get_films_by_history, update_user_watchlist
from handlers.utils.pagination import Pagination, DataStructure, CurrentData
from keyboards.inline.history_show import get_history_show_kb_markup


router = Router(name=__name__)
pagination = Pagination()

search_commands = {search_types[item]["text"] for item in search_types}
date_template_str = "%d.%m.%Y"


class CurrentCalendar:
    """
    Класс календаря текущей сессии поиска

    Attributes:
        __calendar: инстанс класса SimpleCalendar

    """

    __calendar: SimpleCalendar = None

    @classmethod
    async def set_calendar(cls, user) -> None:
        """
        Метод установки календаря с локалью пользователя

        Args:
            user: Данные о пользователе Telegram
        """
        user_lang = await get_user_locale(user)

        cls.__calendar = SimpleCalendar(locale=user_lang, show_alerts=True)
        cls.__calendar.set_dates_range(datetime(2022, 1, 1), datetime(2026, 12, 31))

    @classmethod
    async def get_calendar(cls) -> SimpleCalendar:
        """
        Метод получения текущего календаря с нужными настройками (инстанс класса SimpleCalendar)

        Returns:
            Возвращает инстанс класса SimpleCalendar
        """
        return cls.__calendar


current_calendar = CurrentCalendar()

today: datetime = datetime.now()

watched_marks = {
    "watched": "<b>Просмотрен -</b> ✅",
    "not_watched": "<b>Не просмотрен -</b> ❌",
}


def get_new_film_structured(movie_obj: dict, watched_list: set[str]) -> DataStructure:
    """
        Функция возвращает структурированный объект для пагинации с данными о фильме в виде строки и если необходимо - клавиатурами, которые могут быть вставлены перед или после клавиатуры с навигацией.
    Args:
        movie_obj: Объект с данными о фильме
        watched_list: Уникальный список ID просмотренных фильмов

    Returns:
        new_film: Сформированный объект для пагинации с данными для отрисовки и опционально с клавиатурами до и после основной пагинации
    """
    is_watched: bool = (
        str(movie_obj["id"]) in watched_list if not watched_list is None else False
    )

    movie_str: str = (
        f"{watched_marks["not_watched"]}\n\n{get_movie_card_markup(movie_obj)}"
    )

    if is_watched:
        movie_str = f"{watched_marks["watched"]}\n\n{get_movie_card_markup(movie_obj)}"

    new_film: DataStructure = {
        "data": movie_str,
        "kb_before": get_watchlist_kb_markup(
            txt=f"{'Удалить из просмотренных' if is_watched else 'Добавить в просмотренные'}",
            cb=f"watchlist_toggle#{movie_obj["id"]}#{True if is_watched else False}",
        ),
        "kb_after": None,
    }

    return new_film


async def date_picker(
    callback_query: CallbackQuery,
    callback_data: SimpleCalendarCallback,
    state: FSMContext,
) -> str | None:
    """Функция выбора даты. Проверяет выбрана дата или произошла отмена выбора.

    Returns:
        Возвращает строку с датой или None в случае отмены выбора.
    """
    data = await state.get_data()
    result: str | None = None

    calendar: SimpleCalendar = await current_calendar.get_calendar()

    selected, selected_date = await calendar.process_selection(
        callback_query, callback_data
    )

    if selected:
        result = selected_date.strftime(date_template_str)
    elif callback_data.act == SimpleCalAct.cancel:
        await callback_query.bot.delete_message(
            message_id=data["calendar_id"], chat_id=callback_query.message.chat.id
        )

        await state.clear()

        await callback_query.message.answer("Вы отменили вывод истории поиска!")

    return result


@router.message(StateFilter(None), F.text == search_types["history"]["text"])
@router.message(StateFilter(None), Command("history"))
async def get_history_dates(message: Message, state: FSMContext) -> None:
    """Хэндлер запуска вывода истории поисковых запросов"""

    await state.set_state(HistoryState.history_start)

    await current_calendar.set_calendar(message.from_user)
    calendar: SimpleCalendar = await current_calendar.get_calendar()

    msg = await message.answer(
        "Выберите за какой период показать историю запросов",
        reply_markup=await calendar.start_calendar(year=today.year, month=today.month),
    )

    await state.update_data(calendar_id=msg.message_id)


@router.callback_query(HistoryState.history_start, SimpleCalendarCallback.filter())
async def get_start_date(
    callback_query: CallbackQuery,
    callback_data: SimpleCalendarCallback,
    state: FSMContext,
) -> None:
    """Хэндлер получения начальной даты поиска"""
    data = await state.get_data()
    start_date: str = await date_picker(callback_query, callback_data, state)

    calendar: SimpleCalendar = await current_calendar.get_calendar()

    if not start_date is None:
        await state.update_data(history_start=start_date)
        await callback_query.bot.delete_message(
            message_id=data["calendar_id"], chat_id=callback_query.message.chat.id
        )

        msg = await callback_query.message.answer(
            f"Начальная дата {start_date}\nТеперь выберите конечную дату",
            reply_markup=await calendar.start_calendar(
                year=today.year, month=today.month
            ),
        )

        await state.update_data(calendar_id=msg.message_id)
        await state.set_state(HistoryState.history_end)


@router.callback_query(HistoryState.history_end, SimpleCalendarCallback.filter())
async def get_end_date(
    callback_query: CallbackQuery,
    callback_data: SimpleCalendarCallback,
    state: FSMContext,
) -> None:
    """Хэндлер получения конечной даты поиска"""

    end_date: str = await date_picker(callback_query, callback_data, state)

    if not end_date is None:
        await state.set_state(HistoryState.history_show)
        await state.update_data(history_end=end_date)

        data = await state.get_data()

        start_date: date = datetime.strptime(data["history_start"], "%d.%m.%Y").date()
        end_date: date = datetime.strptime(data["history_end"], "%d.%m.%Y").date()

        if start_date > end_date:
            [start_date, end_date] = [end_date, start_date]

        user_data = await get_histories(
            user_id=callback_query.from_user.id,
            date_start=start_date,
            date_end=end_date,
        )

        if not user_data is None:
            if not user_data.watched_list is None:
                await state.update_data(
                    watched_list=set(user_data.watched_list.split(","))
                )
            else:
                await state.update_data(watched_list=set())

            await callback_query.bot.delete_message(
                message_id=data["calendar_id"], chat_id=callback_query.message.chat.id
            )

            await state.update_data(calendar_id=None)

            await callback_query.message.answer(
                text=f"Период показа истории поиска с {start_date.strftime(date_template_str)} по {end_date.strftime(date_template_str)}"
            )

            histories_list: list[DataStructure] = []

            for histrory in user_data.user_histories:
                new_history: DataStructure = {
                    "data": f"<b>🗓 Дата поиска: {histrory.created_at.strftime(date_template_str)}</b>\n\n{histrory.history_params}",
                    "kb_before": get_history_show_kb_markup(
                        txt="Показать фильмы", cb=f"history_id#{histrory.id}"
                    ),
                    "kb_after": None,
                }

                histories_list.append(new_history)

            await pagination.clear_data()
            await pagination.set_data(histories_list)
            await pagination.send_character_page(callback_query.message)
        else:
            await callback_query.bot.delete_message(
                message_id=data["calendar_id"], chat_id=callback_query.message.chat.id
            )

            await callback_query.message.answer(
                text=f"Истории поисков за перид с {start_date.strftime(date_template_str)} по {end_date.strftime(date_template_str)} не найдено"
            )

            await state.clear()


@router.message(
    HistoryState.history_start, ~F.text.startswith("/") & ~F.text.in_(search_commands)
)
@router.message(
    HistoryState.history_end, ~F.text.startswith("/") & ~F.text.in_(search_commands)
)
async def not_date_selected(message: Message) -> None:
    """Хэндлер вызывается если не выбраны даты начала и конца периода для показа истории запросов."""
    await message.answer("Необходимо выбрать даты или нажать кнопку отмены - 'Cancel'.")


@router.message(
    HistoryState.history_show, ~F.text.startswith("/") & ~F.text.in_(search_commands)
)
@router.message(
    HistoryState.films_show, ~F.text.startswith("/") & ~F.text.in_(search_commands)
)
async def unknown_text(message: Message, state: FSMContext) -> None:
    """Хэндлер не известных запросов/текста."""
    msg = await message.answer(
        "Не известная команда.\nЕсли хотите прервать вывод истории - нажмите 'Отмена'",
        reply_markup=get_cancel_kb_markup(),
    )

    await set_cancel_cb(msg, state)


@router.message(
    StateFilter(HistoryState), F.text.startswith("/") | F.text.in_(search_commands)
)
async def unknowns_commands(message: Message, state: FSMContext) -> None:
    """Хэндлер для перехвата вызова комманд или коллбэк данных (комманд для поиска) во время поиска.
    Дает возможность отменить текущий поиск и сбросить текущее состояние.
    """
    msg = await message.answer(
        'Ответы не должны начинаться со знака "/" команды бота или содержать текст из комманд меню поиска. \n'
        'Если хотите прервать вывод истории - нажмите "Отмена" или просто продолжите текущий поиск.',
        reply_markup=get_cancel_kb_markup(),
    )

    await set_cancel_cb(msg, state)


@router.callback_query(StateFilter(HistoryState), F.data == "cancel")
async def cancel_callback(call: CallbackQuery, state: FSMContext) -> None:
    """Хэндлер отменяет текущий поиск, сбросывает текущее состояние и удаляет не нужные сообщения (календарь, истрию, фильмы)"""
    data = await state.get_data()

    if not data["calendar_id"] is None:
        await call.bot.delete_message(
            message_id=data["calendar_id"], chat_id=call.message.chat.id
        )

    await pagination.destroy_pagination(call, call.message.chat.id)

    if not data.get("cancel_cbs_ids") is None:
        await delete_cancel_msgs(
            call, msg_ids=data["cancel_cbs_ids"], chat_id=call.message.chat.id
        )

    await state.clear()

    await call.message.answer(
        "Вывод истории поисков прерван. \n"
        "Для начала нового поиска - команда /start. \n"
        "Для вызова справки по командам - /help.",
    )


@router.callback_query(HistoryState.history_show, F.data.split("#")[0] == "character")
@router.callback_query(HistoryState.films_show, F.data.split("#")[0] == "character")
async def characters_page_callback(call: CallbackQuery) -> None:
    """Коллбэк функция - реагирует на клик по кнопкам пагинации и вызывает отрисовку соответствующей страницы"""
    page = int(call.data.split("#")[1])

    await pagination.send_character_page(call.message, page, is_next_page=True)


@router.callback_query(HistoryState.history_show, F.data.split("#")[0] == "history_id")
async def show_films_in_history(call: CallbackQuery, state: FSMContext) -> None:
    """Коллбэк функция - реагирует на клик по кнопке показа истории в пагинации и вызывает вывод фильмов выбранной истории поиска"""
    await state.set_state(HistoryState.films_show)

    state_data = await state.get_data()

    watched_list = state_data["watched_list"]

    await call.bot.delete_message(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
    )

    history_id: str = call.data.split("#")[1]

    films_list: list | None = await get_films_by_history(int(history_id))

    if not films_list is None:
        movies_list: list[DataStructure] = []

        for movie in films_list:
            movie_obj: dict = json.loads(movie.film_data)

            new_film: DataStructure = get_new_film_structured(movie_obj, watched_list)

            movies_list.append(new_film)

        await pagination.clear_data()
        await pagination.set_data(data_list=movies_list, additional_data=watched_list)
        await pagination.send_character_page(call.message)
    else:
        await call.message.answer(
            f"Что-то пошло не так. Не удалось полчуить список фильмов. Попробуйте запросить историю еще раз!"
        )

        await state.clear()


@router.callback_query(
    HistoryState.films_show, F.data.split("#")[0] == "watchlist_toggle"
)
async def watchlist_toggle_callback(call: CallbackQuery) -> None:
    """Коллбэк функция - реагирует на клик по кнопкам пагинации
    и вызывает добавление/удаление фильма в списке просмотренных
    """
    film_id = call.data.split("#")[1]
    is_watched = True if call.data.split("#")[2] == "True" else False

    current_data: CurrentData = await pagination.get_current_data()

    page_data = current_data.get("page_data")["data"]
    watched_list: set = current_data.get("additional_data")

    if is_watched:
        new_movie_str = page_data.replace(
            watched_marks["watched"], watched_marks["not_watched"]
        )
        watched_list.remove(film_id)
        is_watched = False
    else:
        watched_list.add(film_id)
        new_movie_str = page_data.replace(
            watched_marks["not_watched"], watched_marks["watched"]
        )
        is_watched = True

    await update_user_watchlist(call.from_user.id, watched_list)

    new_data: DataStructure = {
        "data": new_movie_str,
        "kb_before": get_watchlist_kb_markup(
            txt=f"{'Удалить из просмотренных' if is_watched else 'Добавить в просмотренные'}",
            cb=f"watchlist_toggle#{film_id}#{is_watched}",
        ),
        "kb_after": None,
    }

    await pagination.update_data(new_data, watched_list)
    await pagination.send_character_page(call.message, is_next_page=True)
