from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from utils.misc.types import search_types


def get_main_menu_markup() -> ReplyKeyboardMarkup:
    """Фнкция построения клавиатуры основного меню с основными командами (запросами) для поиска

    Returns:
        Возвращает клавиатуру с основными командами (запросами) для поиска
    """
    search_by_title_btn = KeyboardButton(text=search_types["title"]["text"])
    search_by_rating_btn = KeyboardButton(text=search_types["rating"]["text"])
    search_by_low_budget_btn = KeyboardButton(text=search_types["low_budget"]["text"])
    search_by_high_budget_btn = KeyboardButton(text=search_types["high_budget"]["text"])
    history_btn = KeyboardButton(text=search_types["history"]["text"])

    first_row = [search_by_title_btn, search_by_rating_btn]
    second_row = [search_by_low_budget_btn, search_by_high_budget_btn]
    third_row = [history_btn]

    menu_keyboard = ReplyKeyboardMarkup(
        keyboard=[first_row, second_row, third_row],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    return menu_keyboard
