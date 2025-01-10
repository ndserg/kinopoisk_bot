from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from api.core import api
from api.utils.query_builder import build_quiry
from utils.misc.genres_to_local import get_local_genres_list
from handlers.utils.pagination import pagination
from utils.misc.movie_card import get_movie_card_markup
from utils.misc.types import search_types


async def get_search_results(message: Message, state: FSMContext) -> None:
    """Фунция вывода результатов запроса в виде пагинации."""

    data = await state.get_data()

    current_search_by: str = data.get("search_by")

    selected_genres: list[str] | None = None

    if len(data["genres_select"]) > 0:
        selected_genres = get_local_genres_list(
            data["genres_all"], data["genres_select"]
        )

    genres_str: str = (
        ", ".join(selected_genres)
        if not selected_genres is None
        else "Без указания жанра"
    )

    search_by_text: dict[str, str] = {
        "title": f"Название фильма - {data.get('title')}",
        "rating": f"Рейтинг фильма - {data.get('rating')}",
        "low_budget": f"Низкобюджетные фильмы в диапазоне - {data.get('low_budget')}",
        "high_budget": f"Высокобюджетные фильмы в диапазоне - {data.get('high_budget')}",
    }

    text: str = (
        f"Ищем фильмы по следующим параметрам: \n"
        f"{search_by_text.get(current_search_by)}\n"
        f"Жанр фильма - {genres_str}.\n"
        f"Покажем результатов - {data.get('limit')}\n"
    )

    await message.answer(text)

    await state.clear()

    is_budget_search: bool = (
        current_search_by == search_types["low_budget"]["name"]
    ) or (current_search_by == search_types["high_budget"]["name"])

    if current_search_by == search_types["title"]["name"]:
        query = build_quiry(
            title=data.get("title"),
            genres=selected_genres,
            limit=data.get("limit"),
        )
        movies: list[dict] = await api.get_films_by_title(query)
    else:
        query = build_quiry(
            rating=data.get("rating"),
            budget=data.get(current_search_by) if is_budget_search else None,
            genres=selected_genres,
            limit=data.get("limit"),
            sort_field=data["sort"].get("sort_field"),
            sort_type=data["sort"].get("sort_type"),
        )
        movies: list[dict] = await api.get_films_by_params(query)

    await pagination.clear_data()

    if not isinstance(movies, list) or len(movies) == 0:
        await message.answer(
            "Фильмы по заданным параметрам не найдены! Попробуйте заново."
        )
    elif isinstance(movies, list) and len(movies) > 1:
        movies_list: list[str] = [get_movie_card_markup(movie) for movie in movies]

        await pagination.set_data(movies_list)

        await pagination.send_character_page(message)
    else:
        movie = get_movie_card_markup(movies[0])
        await message.answer(movie, parse_mode="html")
