from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery


async def delete_cancel_msgs(
    caller: CallbackQuery, msg_ids: list[int], chat_id: int | str
) -> None:
    try:
        await caller.bot.delete_messages(message_ids=msg_ids, chat_id=chat_id)
    except TelegramAPIError as e:
        print(f"Не удалось удалить сообщение: {e}")
