from typing import Literal


_query_defaults = {
    "selectFields": [
        "id",
        "name",
        "description",
        "rating",
        "year",
        "genres",
        "ageRating",
        "poster",
        "budget",
    ],
    "notNullFields": [
        "name",
        "genres.name",
        "rating.kp",
        "description",
        "budget.value",
    ],
}

type SortType = Literal["1", "-1"]


def build_quiry(
    limit: int = 20,
    title: str = None,
    genres: list[str] = None,
    rating: str = None,
    budget: str = None,
    sort_field: list[str] = "rating.kp",
    sort_type: SortType = "1",
) -> dict[str, int | str | list[str]]:
    """Функция build_quiry - получает параметры для поиска,
        формирует и возвразает объект с существуюшими полями для поиска

    Args:
        limit: Количество результатов
        title: Название фильма
        genres: Жанры фильмов
        rating: Рейтинг фильмов в формате ["2", "5", "7.2-9"] по рейтингу Кинопоиска
        budget: Бюджет фильмов в формате ["1000-7777777"]
        sort_field: Поле для по которому будет осуществлена сортировка
        sort_type: Направление сортировки в формате ["1", "-1"]

    Returns:
        query: Обект с существующими (not Null) полями для поиска фильмов.

    """

    search_params = {
        "limit": limit,
        "title": title,
        "sortField": [sort_field],
        "sortType": [sort_type],
        "genres.name": genres,
        "rating.kp": rating.split(",") if rating else None,
        "budget.value": budget.split("-") if budget else None,
    }

    query_params = {
        key: value for key, value in search_params.items() if not value is None
    }

    query = {**_query_defaults, **query_params}

    return query
