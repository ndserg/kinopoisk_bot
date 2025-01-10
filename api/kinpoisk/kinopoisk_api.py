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
    async def get_genres(cls) -> dict[str, str]:
        """Метод get_genres - для получения списка всех жанров

        Returns:
            genres: Возвращает объектов жанров
                                    в формате {"slug": "string"}
        """

        url = "/v1/movie/possible-values-by-field"
        query = {"field": "genres.name"}

        res = await fetch(end_point, url, headers, query)
        genres: list[dict[str, str]] = res.json()
        genres_dict: dict[str, str] = {item["slug"]: item["name"] for item in genres}

        return genres_dict

    @classmethod
    async def get_films_by_title(cls, query: dict[str, int | str | list[str]]) -> list:
        """Метод get_films_by_title - для получения списка фильмов по названию.
        Так как API предоставляет только два параметра для поиска (название и количество результатов на странице),
        фильтрация по жанрам и сортировка по рейтингу производится внутри данного метода.

        Args:
            query: Параметры для поиска (название фильма, жанры, кол-во показываемых результатов)

        Returns:
            films: Возвращает список объектов с данными о фильмах.
                    За исключением фильмов с отстутствующем описанием или названием.
        """

        url = "/v1.4/movie/search"
        query_str = {
            "limit": query["limit"],
            "query": query["title"],
        }

        res = await fetch(end_point, url, headers, query_str)
        data: dict = res.json()

        def check_genres(film: dict) -> bool:
            if film.get("genres") and len(film.get("genres")) > 0:
                film_genres = [genre["name"] for genre in film.get("genres")]

                for genre in query["genres.name"]:
                    if genre in film_genres:
                        return True

                return False
            else:
                return False

        def filter_films(film: dict) -> bool | dict:
            if not film.get("description"):
                return False

            if not query.get("genres.name") is None:
                return check_genres(film)

            if film.get("name"):
                return film
            elif film.get("alternativeName"):
                film["name"] = film.get("alternativeName")
                return film
            else:
                return False

        filtered_films = list(filter(filter_films, data["docs"]))

        films = sorted(
            filtered_films, key=lambda film: film["rating"]["kp"], reverse=True
        )

        return films

    @classmethod
    async def get_films_by_params(cls, query: dict[str, int | str | list[str]]) -> list:
        """Метод get_films_by_params - для получения списка фильмов по заданным параметрам.

        Args:
            query: Параметры для поиска (жанр, рейтинг, бюджет,
                    кол-во показываемых результатов, сортировка)

        Returns:
            films: Возвращает список объектов с данными о фильмах
        """

        url = "/v1.4/movie"

        res = await fetch(end_point, url, headers, query)
        data: dict = res.json()

        films = data["docs"]

        return films


if __name__ == "__main__":
    KinopoiskApi()
