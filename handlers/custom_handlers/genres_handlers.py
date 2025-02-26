from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.enums.parse_mode import ParseMode
from states.search import SearchState
from keyboards.inline.genres import get_genres_kb_markup
from utils.misc.genres_to_local import get_local_genres_list


router = Router(name=__name__)


async def save_genres_choice(call: CallbackQuery, state: FSMContext) -> None:
    """Функция сохраняет выбранные фильмы в state"""

    await state.set_state(SearchState.limit)
    await call.message.answer(
        "Какое количество найденных фильмов показать в результате?"
    )


@router.message(SearchState.genres_select)
async def is_genre_selected(message: Message) -> None:
    """Хэндлер проверяет выбран ли жанр.
    Необходимо выбрать минимум один вариант или нажать кнопку 'Пропустить'.
    """

    await message.answer('Необходимо выбрать жанр из списка или нажать "Пропустить"')


@router.callback_query(SearchState.genres_select, F.data == "skip")
async def genres_skip_callback(call: CallbackQuery, state: FSMContext) -> None:
    """Хэндлер для пропуска шага выбора жанра."""
    await state.update_data(genres_select=[])

    data = await state.get_data()
    await call.bot.delete_message(
        message_id=data["genres_select_msg_id"], chat_id=call.message.chat.id
    )

    await state.update_data(genres_select_msg_id=None)

    await call.message.answer(
        "<b>Вы решили не указывать жанр</b>", parse_mode=ParseMode.HTML
    )

    await save_genres_choice(call, state)


@router.callback_query(SearchState.genres_select, F.data == "save")
async def genres_save_callback(call: CallbackQuery, state: FSMContext) -> None:
    """Хэндлер для сохранения выбранных жанров в state"""

    data = await state.get_data()

    selected_genres: list = data["genres_select"][:]

    await call.bot.delete_message(
        message_id=data["genres_select_msg_id"], chat_id=call.message.chat.id
    )

    await state.update_data(genres_select_msg_id=None)

    if len(selected_genres) > 0:
        local_genres: list[str] = get_local_genres_list(
            data["genres_all"], data["genres_select"]
        )

        message_text = f"<b>Вы выбрали жанры</b> - {', '.join(local_genres)}"
    else:
        message_text = "<b>Вы не выбрали ни одного жанра.</b>"

    await call.message.answer(
        message_text,
        parse_mode=ParseMode.HTML,
    )

    await save_genres_choice(call, state)


@router.callback_query(SearchState.genres_select)
async def genres_select_callback(call: CallbackQuery, state: FSMContext) -> None:
    """Хэндлер вывода этапа выбора жанров"""

    data = await state.get_data()

    selected_genres: list[str] = data["genres_select"][:]

    if call.data in selected_genres:
        selected_genres.remove(call.data)
    else:
        selected_genres.append(call.data)

    await state.update_data(genres_select=selected_genres)

    await call.bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=get_genres_kb_markup(data["genres_all"], selected=selected_genres),
    )
