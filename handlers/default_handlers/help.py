from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from config_data.config import DEFAULT_COMMANDS


router = Router(name=__name__)


@router.message(F.text.lower().in_(["help", "помощь"]))
@router.message(Command("help"))
async def bot_help(message: Message) -> None:
    """Хэндлер команды '/help'
    Выводит сообщение со списком возможных команд бота
    """
    text = [f"/{command} - {desk}" for command, desk in DEFAULT_COMMANDS]

    await message.reply("\n".join(text))
