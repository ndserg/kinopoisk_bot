from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from keyboards.reply.main_menu import get_main_menu_markup
from database.CRUD import add_user


router = Router(name=__name__)


@router.message(CommandStart())
async def bot_start(message: Message) -> None:
    """Хэндлер команды '/start'
    Выводит приветственное сообщение с подсказкой о команде '/help'.
    А так же вызывает клавиатуру с основным меню.
    Добавляет пользователя в базу данных (если ранее еще не был добавлен)
    """
    text = (
        f"Привет, {message.from_user.first_name}! \n"
        f"Этот бот поможет найти фильмы по различным параметрам. \n"
        f"Для этого можно воспользоваться удобным меню внизу. \n"
        f"А также, для просмотра всех доступных команд - достаточно написать команду /help."
    )

    await add_user(user_id=message.from_user.id)

    await message.answer(text, reply_markup=get_main_menu_markup())
