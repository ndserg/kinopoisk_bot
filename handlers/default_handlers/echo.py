from aiogram.types import Message
from .default_router import default_router


@default_router.message()
async def bot_echo(message: Message) -> None:
    """Эхо хендлер, куда летят текстовые сообщения без указанного состояния"""
    await message.reply("Эхо без состояния или фильтра.\n" f"Сообщение: {message.text}")
