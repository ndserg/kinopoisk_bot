from typing import TypedDict, Optional
from aiogram import Router
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery
from telegram_bot_pagination import InlineKeyboardPaginator


router = Router(name=__name__)


class DataStructure(TypedDict):
    data: str
    kb_before: InlineKeyboardMarkup | None
    kb_after: InlineKeyboardMarkup | None


class CurrentData(TypedDict):
    pagination_msg_id: int | None
    page_data: DataStructure | None
    additional_data: list | dict | set | None


class Pagination:
    """Класс для реализации вывода информации через пагинацию

    Attributes:
        __msg_id: Id сообщения с пагинацией (для последующего замещения при переключении страниц и редактировании данных)
        __data_list: Данные в виде списка, которые будут выводиться через пагинацию
        __additional_data: Вспомогательная дополнительная информация
        __page: Текущая страница пагинации
    """

    __msg_id: int | None = None
    __data_list: list[DataStructure] = []
    __additional_data: list | dict | set | None = None
    __page: int = 1

    @classmethod
    async def get_current_data(cls) -> CurrentData:
        """
            Метод для получения текущих данных пагинации

        Returns:
            current_data: Возвращает объект типа CurrentData, с текущими данными пагинации
                            (id сообщения с пагинацией, данные текущей страницы, вспомошательные данные)
        """
        page_data = None

        if len(cls.__data_list) > 0:
            page_data = cls.__data_list[cls.__page - 1]

        current_data = {
            "pagination_msg_id": cls.__msg_id,
            "page_data": page_data,
            "additional_data": cls.__additional_data,
        }

        return current_data

    @classmethod
    async def update_data(
        cls,
        new_data: DataStructure,
        additional_data: Optional[list | dict | set] = None,
    ) -> bool:
        """
            Метод для обновления данных пагинации

        Args:
            new_data: Новые данные для пагинации - объект типа DataStructure
            additional_data: опциональные вспомогательные данные

        Returns:
            Возвращает True после обновления данных
        """
        cls.__data_list[cls.__page - 1] = new_data
        cls.__additional_data = additional_data

        return True

    @classmethod
    async def set_data(
        cls,
        data_list: list[DataStructure],
        additional_data: list | dict | set | None = None,
    ) -> bool:
        """Метод для установки данных для вывода в пагинации.

        Args:
            data_list: Данные в виде списка объектов с данными и опциаонально клавиатуры
                        для добавления до/после клавиатуры пагинации
            additional_data: Вспомогательная дополнительная информация

        Returns:
            Возвращает True после успешной записи переданных данных.
        """
        cls.__data_list = data_list
        cls.__additional_data = additional_data

        return True

    @classmethod
    async def clear_data(cls) -> bool:
        """Метод для очистки данных для пагинции.

        Returns:
            Возвращает True после успешной очистки данных.
        """
        cls.__msg_id = None
        cls.__data_list = []
        cls.__additional_data = None
        cls.__page = 1

        return True

    @classmethod
    async def send_character_page(
        cls, message: Message, page: int | None = None, is_next_page: bool = False
    ) -> None:
        """Метод отрисовки данных с указанным номером страницы

        Args:
            message: Telegram message
            page: переданный номер страницы из колбэка
            is_next_page: признак отрисовки следующих страниц (при первом рендере происходит
                            отрисовка первой страницы по умолчанию,
                            при отрисовке следующих страниц - сообщение редактируется по id первого сообщения

        """
        if page == cls.__page:
            return

        if not page is None:
            cls.__page = page

        paginator = InlineKeyboardPaginator(
            len(cls.__data_list),
            current_page=cls.__page,
            data_pattern="character#{page}",
        )

        paginator_kb_builder = InlineKeyboardBuilder()
        btns_markup_list = []

        if not cls.__data_list[cls.__page - 1]["kb_before"] is None:
            btns_markup_list.append(cls.__data_list[cls.__page - 1]["kb_before"])

        if not paginator.markup is None:
            btns_markup_list.append(
                InlineKeyboardMarkup.model_validate_json(paginator.markup)
            )

        if not cls.__data_list[cls.__page - 1]["kb_after"] is None:
            btns_markup_list.append(cls.__data_list[cls.__page - 1]["kb_after"])

        if len(btns_markup_list) > 0:
            for btn_markup in btns_markup_list:
                paginator_kb_builder.attach(
                    InlineKeyboardBuilder.from_markup(btn_markup)
                )

        if is_next_page:
            msg = await message.bot.edit_message_text(
                cls.__data_list[cls.__page - 1]["data"],
                message_id=cls.__msg_id,
                chat_id=message.chat.id,
                reply_markup=paginator_kb_builder.as_markup(),
                parse_mode="html",
            )
        else:
            msg = await message.answer(
                cls.__data_list[cls.__page - 1]["data"],
                reply_markup=paginator_kb_builder.as_markup(),
                parse_mode="html",
            )

        cls.__msg_id = msg.message_id

    @classmethod
    async def destroy_pagination(
        cls, caller: CallbackQuery, chat_id: int | str
    ) -> None:
        """Метод удаления пагинации

        Args:
            caller: Telegram CallbackQuery
            chat_id: Telegram Bot chat id
        """
        if not cls.__msg_id is None:
            await caller.bot.delete_message(message_id=cls.__msg_id, chat_id=chat_id)
            await cls.clear_data()
