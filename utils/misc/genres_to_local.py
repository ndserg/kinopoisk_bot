def get_local_genres_list(
    genres_dict: dict[str, str], genres_list: list[str]
) -> list[str]:
    """Функция для конвертации списка выбранных жанров на английском в список жанров на русском языке.

    Args:
        genres_dict: Словарь жанров (по которому происходит сопоставление EN/RU языка)
        genres_list: Список выбранных жанров на английском языке

    Returns:
        Возвращает локализованный список жанров.
    """

    local_genres_list: list[str] = [genres_dict[item] for item in genres_list]

    return local_genres_list
