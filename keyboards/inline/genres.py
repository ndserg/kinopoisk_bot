from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_genres_kb_markup(
    genres: dict[str, str], selected: list[str] = list, row_width: int = 3
) -> InlineKeyboardMarkup:
    """Функция построения клавиатуры для выбора жанров из списка.
        С возможностью пропуска и сохранения результатов.

    Args:
        genres: Словарь списка жанров
        selected: Список выбранных жанров
        row_width: Количество жанров для выбора в строке

    Returns:
        Возвращает клавиатуру со списком жанров
    """
    genres_kb_builder = InlineKeyboardBuilder()

    for slug, name in genres.items():
        is_selected = f"✅ {name}" if slug in selected else name

        genres_kb_builder.button(text=is_selected, callback_data=slug)

    genres_kb_builder.adjust(row_width)

    genres_kb_skip_btn = InlineKeyboardButton(text="Пропуск ⏭️", callback_data="skip")
    genres_kb_save_btn = InlineKeyboardButton(text="Сохранить 💾", callback_data="save")

    genres_kb_actions_btn_row = [[genres_kb_skip_btn, genres_kb_save_btn]]

    genres_kb_actions_markup = InlineKeyboardMarkup(
        inline_keyboard=genres_kb_actions_btn_row
    )

    genres_kb_builder.attach(
        InlineKeyboardBuilder.from_markup(genres_kb_actions_markup)
    )

    return genres_kb_builder.as_markup()
