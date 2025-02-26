from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_history_show_kb_markup(txt: str, cb: str) -> InlineKeyboardMarkup:
    """Функция вывода фильмов выбранной истории поиска

    Args:
        txt: Текст кнопки
        cb: Коллбэк дата

    Returns:
        Возвращает клавиатуру для показа фильмов в выбранной истории поиска
    """
    history_kb_markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=txt, callback_data=cb)]]
    )

    return history_kb_markup
