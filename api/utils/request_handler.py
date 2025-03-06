import asyncio
import json
import aiohttp
from .error_handlers import RequestError


async def fetch(
    end_point: str, url: str, headers: dict[str, str], query_str: dict[str, str | int]
) -> json:
    """Функция fetch - отправляет запрос на заданный URL.
    Возвращает соответствкющие запросу данные.
    При возникновении ошибок - вызывает исключение RequestError.

    Args:
        end_point: Базовый URL для запросов
        url: URL для определенного маршрута запроса
        headers: Объект заголовков запроса
        query_str: Строка параметров запроса (параметры для поиска)

    Returns:
        response: Ответ от сервера в формате JSON

    Raises:
        RequestError: Перехватывает ошибки соединения и неудачных ответов сервера
    """
    timeout = aiohttp.ClientTimeout(total=5)

    try:
        async with aiohttp.ClientSession(
            headers=headers, timeout=timeout, raise_for_status=True
        ) as session:
            async with session.get(url=f"{end_point}{url}", params=query_str) as resp:
                response = await resp.json()
                return response

    except aiohttp.ClientResponseError as e:
        raise RequestError(
            e.status, e.message, "Сервер не отвечает, либо неверно указан адрес!"
        )
    except aiohttp.ClientError as e:
        raise RequestError("", "Ошибка клиента!", f"{e}")
    except asyncio.TimeoutError:
        raise RequestError("", "Ошибка: превышено время ожидания", "")
    except Exception as e:
        raise RequestError("", "Неизвестная ошибка", f"{e}")
