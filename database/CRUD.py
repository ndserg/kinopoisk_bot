import json
from sqlalchemy.orm import contains_eager
from sqlalchemy.dialects.sqlite import insert
from database.engine import async_session
from database.models import User, History, Films, FilmsInHistories
from sqlalchemy import select, update


async def add_user(user_id: int) -> None:
    """
    Функция добавления пользователя в базу данных

    Args:
        user_id: Telegram ID пользователя
    """
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.id == user_id))

        if not user:
            new_user = User(id=user_id)
            session.add(new_user)
            await session.commit()


async def update_user_watchlist(user_id: int, watchlist: set[str]) -> None:
    """
    Функция обновления данных пользователя (для обновления списка просмотренных фильмов)

    Args:
        user_id: Telegram ID пользователя
        watchlist: Список просмотренных фильмов
    """
    watchlist_str = ",".join(list(watchlist))

    async with async_session() as session:
        stmt = update(User).where(User.id == user_id).values(watched_list=watchlist_str)

        await session.execute(stmt)
        await session.commit()


async def add_history(user_id: int, history_params: str, films: list[dict]) -> None:
    """
    Функция добавления истории поиска

    Args:
        user_id: Telegram ID пользователя
        history_params: Параметры поискового запроса в истории
        films: Список фильмов в результате поискового запроса (объект с id фильма и описанием в виде строки JSON)
    """
    async with async_session() as session:
        new_history = History(user_id=user_id, history_params=history_params)
        session.add(new_history)
        await session.flush()

        film_values = [
            {"id": movie["id"], "film_data": json.dumps(movie, ensure_ascii=False)}
            for movie in films
        ]

        stmt_films = insert(Films).values(film_values).on_conflict_do_nothing()

        association_values = [
            {"histrory_id": new_history.id, "film_id": movie["id"]} for movie in films
        ]

        stmt_associations = (
            insert(FilmsInHistories).values(association_values).on_conflict_do_nothing()
        )

        await session.execute(stmt_films)
        await session.execute(stmt_associations)

        await session.commit()


async def get_histories(user_id: int, date_start, date_end) -> User | None:
    """
    Функция получения истории поисковых запросов по ID пользователя и выборкой между указанными датами

    Args:
        user_id: Telegram ID пользователя
        date_start: Начальная дата поисковых запросов
        date_end: Конечная дата поисковых запросов

    Returns:
        Возвращает данные о поисковых запрсах в случае их наличия или None - если данных нет
    """
    async with async_session() as session:
        stmt = (
            select(User)
            .join(User.user_histories)
            .filter(User.id == user_id)
            .filter(History.created_at.between(date_start, date_end))
            .options(contains_eager(User.user_histories))
        )

        result = await session.execute(stmt)
        user_data: User | None = result.scalars().unique().first()

        return user_data


async def get_films_by_history(history_id: int) -> list | None:
    """
    Функция получения данных о фильмах в выбранном поисковом запросе

    Args:
        history_id: Id истории поискового запроса

    Returns:
        Возвращает список фильмоа или None - если данные отсутствуют
    """
    async with async_session() as session:
        stmt = select(Films).join(History.film_ids).filter(History.id == history_id)

        result = await session.execute(stmt)
        films: list = result.scalars().all()

        return films
