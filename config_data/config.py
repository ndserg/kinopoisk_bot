import os
from dotenv import load_dotenv, find_dotenv


if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if BOT_TOKEN is None:
    exit("BOT_TOKEN отсутствует в переменных окружения")

API_KEY = os.getenv("API_KEY")
if API_KEY is None:
    exit("API_KEY отсутствует в переменных окружения")

END_POINT = os.getenv("END_POINT")
if END_POINT is None:
    exit("END_POINT API отсутствует в переменных окружения")

DEFAULT_COMMANDS = (
    ("start", "Запустить бота"),
    ("help", "Вывести справку"),
    ("search", "Поиск по названию"),
    ("low", "Поиск с низким бюджетом"),
    ("high", "Поиск с высоким бюджетом"),
    ("rating", "Поиск по рейтингу"),
    ("history", "История запросов и поиска"),
)
