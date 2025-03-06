from aiogram.types import Message
from aiogram.fsm.context import FSMContext


async def set_cancel_cb(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    cb_ids = data["cancel_cbs_ids"] if data.get("cancel_cbs_ids") else []

    cb_ids.append(message.message_id)
    await state.update_data(cancel_cbs_ids=cb_ids)
