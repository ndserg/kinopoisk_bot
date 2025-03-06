import os
from enum import Enum
from dotenv import load_dotenv, find_dotenv


class ExpectedEnvs(Enum):
    bot_token = "BOT_TOKEN"
    api_key = "API_KEY"
    end_point = "END_POINT"
    database = "DATABASE"


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

for env in ExpectedEnvs:
    if os.getenv(env.value) is None:
        exit(error_messages[env])

BOT_TOKEN = os.getenv(ExpectedEnvs.bot_token.value)
API_KEY = os.getenv(ExpectedEnvs.api_key.value)
END_POINT = os.getenv(ExpectedEnvs.end_point.value)
DATABASE = os.getenv(ExpectedEnvs.database.value)

DEFAULT_COMMANDS = (
    ("start", "Запустить бота"),
    ("help", "Вывести справку"),
    ("search", "Поиск по названию"),
    ("low", "Поиск с низким бюджетом"),
    ("high", "Поиск с высоким бюджетом"),
    ("rating", "Поиск по рейтингу"),
    ("history", "История запросов и поиска"),
)
