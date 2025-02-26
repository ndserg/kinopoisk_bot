import asyncio
import logging
from loader import start_bot

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        print("Бот выключен")
