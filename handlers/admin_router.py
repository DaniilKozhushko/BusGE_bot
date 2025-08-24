from config import ADMIN
from logger import logger
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from database import add_answer, get_user_request
from middlewares.only_admin import AdminMiddleware


# router for processing messages from users
admin_router = Router()

# check if user is admin
admin_router.message.middleware(AdminMiddleware(ADMIN))


# command /answer handler
@admin_router.message(Command("answer"))
async def answer_command(message: Message):
    logger.info("command answer",
                extra={"user_id": message.from_user.id}
    )

    # splitting a message into parameters
    _, user_id, request_id, *answer_parts = message.text.split()
    answer = " ".join(answer_parts)
    user_id, request_id = map(int, (user_id, request_id))

    try:
        # saving the answer to the database
        await add_answer(answer, request_id)

        # getting user's request text
        request = await get_user_request(user_id, request_id)

        # sending a message to a user
        await message.bot.send_message(
            chat_id=user_id,
            text=f"От тебя поступил запрос:\n<pre>{request}</pre>\nОтвет админа:\n<pre>{answer}</pre>"
        )
        await message.reply(text="✅ Сообщение отправлено.")
    except Exception as e:
        await message.reply(f"❎ Ошибка при отправке: {e}")