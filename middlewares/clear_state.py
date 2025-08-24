from aiogram.types import Message
from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from typing import Callable, Awaitable, Dict, Any


class AutoClearStateMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, any]
    ) -> Any:
        state: FSMContext | None = data.get("state")

        # if the message is a command and there is an active state, then it is reset
        if event.text and event.text.startswith("/") and state:
            await state.clear()

        return await handler(event, data)