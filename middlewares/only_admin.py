from aiogram.types import Message
from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Dict, Any


class AdminMiddleware(BaseMiddleware):
    def __init__(self, admin_id: int):
        self.admin_id = admin_id

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:

        # let in only admin
        if event.from_user.id != int(self.admin_id):
            try:
                await event.bot.delete_message(
                    chat_id=event.chat.id,
                    message_id=event.message_id
                )
            except Exception as e:
                print(e)
                pass
            return

        return await handler(event, data)
