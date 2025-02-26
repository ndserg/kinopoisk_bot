import sys
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeDefault
from config_data import config
from handlers.default_handlers.default_router import router as default_router
from handlers.custom_handlers.search import router as search_router
from database.engine import create_db, drop_db

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
    if "--drop-db" in sys.argv:
        await drop_db()

    dp.include_routers(search_router, default_router)
    await create_db()
    await set_default_commands()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
