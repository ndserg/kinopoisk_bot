import asyncio
import sys
from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from config_data.config import (
    DEFAULT_COMMANDS,
    ExpectedEnvs,
    OptionalEnvs,
    MAIN_ENV,
    OPT_ENV,
    IS_WEBHOOK,
)
from handlers.default_handlers.default_router import router as default_router
from handlers.custom_handlers.search import router as search_router
from database.engine import create_db, drop_db

bot = Bot(token=MAIN_ENV.get(ExpectedEnvs.bot_token.value))
dp = Dispatcher()

if IS_WEBHOOK:
    WEB_SERVER_HOST = OPT_ENV.get(OptionalEnvs.web_server_host.value)
    WEB_SERVER_PORT = OPT_ENV.get(OptionalEnvs.web_server_port.value)
    WEBHOOK_PATH = OPT_ENV.get(OptionalEnvs.webhook_path.value)
    WEBHOOK_SECRET = OPT_ENV.get(OptionalEnvs.webhook_secret.value)
    BASE_WEBHOOK_URL = OPT_ENV.get(OptionalEnvs.base_webhook_url.value)


async def on_startup() -> None:
    """
    Фнкция установки webhook при старте бота
    Returns:

    """
    async with bot:
        await bot.set_webhook(
            f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET
        )


async def on_shutdown() -> None:
    """
    Функция удаления webhook при остановке бота
    """
    await bot.delete_webhook()


async def set_default_commands() -> None:
    """Функция для установки команд бота по умолчанию"""
    commands = [BotCommand(command=i[0], description=i[1]) for i in DEFAULT_COMMANDS]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def start_bot() -> None:
    """Функция запуска бота.
    Подключает роутеры, команды по умолчанию и запускает бота.

    Запуск в редиме WEBHOOK если переданы необходимые параметры в .env,
    в противном случае - запуск в режиме polling.
    """
    if "--drop-db" in sys.argv:
        await drop_db()

    dp.include_routers(search_router, default_router)
    await create_db()
    await set_default_commands()
    await bot.delete_webhook(drop_pending_updates=True)

    if not IS_WEBHOOK:
        await dp.start_polling(bot)
    else:
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)

        app = web.Application()

        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
            secret_token=WEBHOOK_SECRET,
        )

        webhook_requests_handler.register(app, path=WEBHOOK_PATH)

        setup_application(app, dp, bot=bot)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, WEB_SERVER_HOST, WEB_SERVER_PORT)
        await site.start()
        await asyncio.Event().wait()
