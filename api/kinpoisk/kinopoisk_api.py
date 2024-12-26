from api.utils.request_handler import fetch
from config_data import config


end_point = config.END_POINT
api_key = config.API_KEY

headers = {"accept": "application/json", "X-API-KEY": api_key}


class KinopoiskApi:
    """Класс KinopoiskApi для работы с API kinoposk.
    Предоставляет методы для запроса информации на API.
    """

    @classmethod
    async def get_genres(cls) -> list[dict[str, str]]:
        """Метод get_genres - для получения списка всех жанров

        Returns:
            genres: Возвращает список объектов жанров
                                    в формате [{"name": "string","slug": "string"}, ...]
        """

        url = "/v1/movie/possible-values-by-field"
        query = {"field": "genres.name"}

        res = await fetch(end_point, url, headers, query)
        genres: list[dict[str, str]] = res.json()

        return genres

    @classmethod
    async def get_films_by_title(cls, query: dict[str, int | str | list[str]]) -> dict:
        """Метод get_films_by_title - для получения списка фильмов по названию.

        Args:
            query: Параметры для поиска (название фильма, текущая страница, кол-во результатов на странице)

        Returns:
            films: Возвращает объект со следующей информацией
                                - Объект со списком объектов фильмов.
                                - Количество результатов поиска.
                                - Количество выводимых результатов на странице.
                                - Текущая страница поиска.
                                - Количество страниц.
        """

        url = "/v1.4/movie/search"
        query_str = {
            "page": query["page"],
            "limit": query["limit"],
            "query": query["title"],
        }

        res = await fetch(end_point, url, headers, query_str)
        films: dict = res.json()

        films["docs"].sort(key=lambda film: film["rating"]["kp"], reverse=True)

        return films

    @classmethod
    async def get_films_by_params(cls, query: dict[str, int | str | list[str]]) -> dict:
        """Метод get_films_by_params - для получения списка фильмов по заданным параметрам.

        Args:
            query: Параметры для поиска (жанр, рейтинг, бюджет,
                    текущая страница, кол-во результатов на странице, сортировка)

        Returns:
            films: Возвращает объект со следующей информацией
                                - Объект со списком объектов фильмов
                                - Количество результатов поиска.
                                - Количество выводимых результатов на странице.
                                - Текущая страница поиска.
                                - Количество страниц.
        """

        url = "/v1.4/movie"

        res = await fetch(end_point, url, headers, query)
        films: dict = res.json()

        return films


if __name__ == "__main__":
    KinopoiskApi()
