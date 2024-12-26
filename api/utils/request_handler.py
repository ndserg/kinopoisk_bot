import requests
import asyncio
from requests import Response
from .error_handlers import RequestError


async def fetch(
    end_point: str, url: str, headers: dict[str, str], query_str: dict[str, str | int]
) -> Response:
    """Функция fetch - отправляет запрос на заданный URL.
    Возвращает соответствкющие запросу данные.
    При возникновении ошибок - вызывает исключение RequestError.

    Args:
        end_point: Базовый URL для запросов
        url: URL для определенного маршрута запроса
        headers: Объект заголовков запроса
        query_str: Строка параметров запроса (параметры для поиска)

    Returns:
        response: Ответ от сервера

    Raises:
        RequestError: Перехватывает ошибки соединения и неудачных ответов сервера
    """

    error = None

    try:
        response = await asyncio.to_thread(
            requests.get, url=f"{end_point}{url}", headers=headers, params=query_str
        )

        if response.status_code != 200:
            error = response.json()
            response.raise_for_status()
        else:
            return response

    except requests.exceptions.ConnectionError:
        raise RequestError(
            "11001",
            "Ошибка соединения!",
            "Сервер не отвечает, либо неверно указан адрес!",
        )

    except requests.exceptions.RequestException:
        raise RequestError(error["statusCode"], error["message"], error["error"])
