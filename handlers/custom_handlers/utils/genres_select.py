from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from api.core import api
from states.search import SearchState
from keyboards.inline.genres import get_genres_kb_markup


async def genres_select_step(message: Message, state: FSMContext) -> None:
    """Функция выбора жанров.
    Предлагает выбрать жанры с помощью клавиатуры со списком возможных жанров или пропустить этот шаг.
    """

    await state.update_data(genres_select=[])

    genres = await api.get_genres()

    await state.update_data(genres_all=genres)

    msg = await message.answer(
        "Можете дополнительно выбрать жанр фильма",
        reply_markup=get_genres_kb_markup(genres, selected=[]),
    )

    await state.update_data(genres_select_msg_id=msg.message_id)

    await state.set_state(SearchState.genres_select)
