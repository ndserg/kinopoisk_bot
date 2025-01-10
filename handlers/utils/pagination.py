from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup
from telegram_bot_pagination import InlineKeyboardPaginator


router = Router(name=__name__)


class Pagination:
    """Класс для реализации вывода информации через пагинацию

    Attributes:
        __data: любые данные в виде списка, которые будут выводиться через пагинацию
    """

    __data: list[any] = []

    @classmethod
    async def set_data(cls, data: list[any]) -> bool:
        """Метод для установки данных для вывода в пагинации.

        Args:
            data: любые данные в виде списка

        Returns:
            Возвращает True после успешной записи переданных данных.
        """
        cls.__data = data

        return True

    @classmethod
    async def clear_data(cls) -> bool:
        """Метод для очистки данных для пагинции.

        Returns:
            Возвращает True после успешной очистки данных.
        """
        cls.__data = []

        return True

    @classmethod
    async def send_character_page(cls, message: Message, page: int = 1) -> None:
        """Метод отрисовки данных с указанным номером страницы"""
        paginator = InlineKeyboardPaginator(
            len(cls.__data), current_page=page, data_pattern="character#{page}"
        )

        await message.answer(
            cls.__data[page - 1],
            reply_markup=InlineKeyboardMarkup.model_validate_json(paginator.markup),
            parse_mode="html",
        )


pagination = Pagination()


@router.callback_query(F.data.split("#")[0] == "character")
async def characters_page_callback(call) -> None:
    """Коллбэк функция - реагирует на клик по кнопкам пагинации и вызывает отрисовку соответствующей страницы"""
    page = int(call.data.split("#")[1])
    await call.bot.delete_message(
        chat_id=call.message.chat.id, message_id=call.message.message_id
    )
    await pagination.send_character_page(call.message, page)
