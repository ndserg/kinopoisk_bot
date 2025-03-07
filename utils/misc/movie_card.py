import aiogram.utils.markdown as fmt


def get_movie_card_markup(data: dict) -> str:
    """Функция для разметки карточки фильма

    Args:
        data: Словарь с данными о фильме

    Returns:
        Строку разметки с данными о фильме
    """
    movie = {key: value if value else "отсутствует" for key, value in data.items()}

    movie_genres = (
        ", ".join([genre.get("name") for genre in movie["genres"]])
        if isinstance(movie.get("genres"), list) and len(movie.get("genres")) > 0
        else "отсутствует"
    )

    if movie.get("poster") is None or movie["poster"].get("url") is None:
        movie["poster"] = {"url": "https://dendev.ru/img/no-image-for-tg.png"}

    if movie.get("budget") is None or movie["budget"].get("value") is None:
        movie_budget = "Не указан"
        movie_currency = "-"
    else:
        movie_budget = movie["budget"].get("value")
        movie_currency = movie["budget"].get("currency", "-")

    movie_card = (
        f"{fmt.hide_link(movie['poster'].get('url'))}"
        f"📺 <b>{movie.get('name', 'Название отсутствует').upper()}</b>\n\n"
        f"<b>ℹ️ Описание:</b>\n"
        f"{movie.get('description', "Описание отсутствует")}\n\n"
        f"⭐️ Рейтинг - <b>{movie['rating'].get('kp', "Данные отстутствют")}</b>\n\n"
        f"📆 Год производства - <b>{movie.get('year', "Не указан")}</b>\n\n"
        f"🎥 Жанр - <b>{movie_genres}</b>\n\n"
        f"🚹 Возрастной рейтинг - <b>{movie.get('ageRating', 'Отсутствует')}</b>\n\n"
        f"💰 Бюджет фильма - <b>{movie_budget}</b>; "
        f"(Валюта - <b>{movie_currency}</b>)"
    )

    return movie_card
