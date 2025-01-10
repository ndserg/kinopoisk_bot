from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeDefault
from config_data import config
from handlers.default_handlers.default_router import router as default_router
from handlers.custom_handlers.search import router as search_router


bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()


async def set_default_commands() -> None:
    """Функция для установки команд бота по умолчанию"""
    commands = [
        BotCommand(command=i[0], description=i[1]) for i in config.DEFAULT_COMMANDS
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def start_bot() -> None:
    """Функция запуска бота.
    Подключает роутеры, команды по умолчанию и запускает бота.
    """
    dp.include_routers(search_router, default_router)
    await set_default_commands()
    await dp.start_polling(bot)
