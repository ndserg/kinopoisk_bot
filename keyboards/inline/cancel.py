from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_cancel_kb_markup() -> InlineKeyboardMarkup:
    """Функция отмены поиска

    Returns:
        Возвращает клавиатуру для отмены поиска
    """
    cancel_kb_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отменить", callback_data="cancel")]
        ]
    )

    return cancel_kb_markup
