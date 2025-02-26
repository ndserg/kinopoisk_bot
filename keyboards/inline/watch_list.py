from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_watchlist_kb_markup(txt: str, cb: str) -> InlineKeyboardMarkup:
    """Функция добавления/удаления фильмов в список просмотренных

    Args:
        txt: Текст кнопки
        cb: Коллбэк дата

    Returns:
        Возвращает клавиатуру для добавления/удаления фильмов в список просмотренных
    """
    watchlist_kb_markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=txt, callback_data=cb)]]
    )

    return watchlist_kb_markup
