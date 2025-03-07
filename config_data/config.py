import os
from enum import Enum
from dotenv import load_dotenv, find_dotenv


class ExpectedEnvs(Enum):
    bot_token = "BOT_TOKEN"
    api_key = "API_KEY"
    end_point = "END_POINT"
    database = "DATABASE"


class OptionalEnvs(Enum):
    web_server_host = "WEB_SERVER_HOST"
    web_server_port = "WEB_SERVER_PORT"
    webhook_path = "WEBHOOK_PATH"
    webhook_secret = "WEBHOOK_SECRET"
    base_webhook_url = "BASE_WEBHOOK_URL"


error_messages = {
    ExpectedEnvs.bot_token: "BOT_TOKEN отсутствует в переменных окружения",
    ExpectedEnvs.api_key: "API_KEY отсутствует в переменных окружения",
    ExpectedEnvs.end_point: "END_POINT API отсутствует в переменных окружения",
    ExpectedEnvs.database: "DATABASE отсутствует в переменных окружения",
}

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

MAIN_ENV: dict[str, any] = {}
OPT_ENV: dict[str, any] | None = {}

IS_WEBHOOK: bool = False

for env in ExpectedEnvs:
    if not os.getenv(env.value) is None:
        MAIN_ENV[env.value] = os.getenv(env.value)
    else:
        exit(error_messages[env])

for env in OptionalEnvs:
    if not os.getenv(env.value) is None:
        IS_WEBHOOK = True
        OPT_ENV[env.value] = os.getenv(env.value)
    else:
        IS_WEBHOOK = False
        break

DEFAULT_COMMANDS = (
    ("start", "Запустить бота"),
    ("help", "Вывести справку"),
    ("search", "Поиск по названию"),
    ("low", "Поиск с низким бюджетом"),
    ("high", "Поиск с высоким бюджетом"),
    ("rating", "Поиск по рейтингу"),
    ("history", "История запросов и поиска"),
)
