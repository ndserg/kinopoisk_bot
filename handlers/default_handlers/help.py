from aiogram.filters import Command
from aiogram.types import Message

from config_data.config import DEFAULT_COMMANDS
from .default_router import default_router


@default_router.message(Command("help"))
async def bot_help(message: Message) -> None:
    """Хэндлер команды '/help'
    Выводит сообщение со списком возможных команд бота
    """
    text = [f"/{command} - {desk}" for command, desk in DEFAULT_COMMANDS]

    await message.reply("\n".join(text))
