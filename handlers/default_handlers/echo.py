from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message


router = Router(name=__name__)


@router.message(StateFilter(None))
async def bot_echo(message: Message) -> None:
    """Эхо хендлер, куда летят текстовые сообщения без указанного состояния и с неизвестными командами"""
    await message.reply(
        "Извините, не известная команда.\n"
        "Для помощи по доступным командам наберите - /help\n"
        "Для вызова меню - /start"
    )
