import asyncio
from aiogram import Bot
from database import init_db
from aiogram import Dispatcher
from aiogram.enums import ParseMode
from config import TELEGRAM_BOT_TOKEN
from handlers.user_router import user_router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

# initialization of the Bot object with a token and indicating the formation of messages
bot = Bot(
    token=TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

# initializing the Dispatcher object with the memory storage
dp = Dispatcher(storage=MemoryStorage())


# main async function to start the bot
async def main():

    # initializing the database
    await init_db()

    # connecting a router
    dp.include_router(user_router)

    try:
        # clean updates so the bot doesn't process old commands after startup
        await bot.delete_webhook(drop_pending_updates=True)

        # start long polling
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        # correct closing of the session after the bot finishes working
        await bot.session.close()

# run
if __name__ == "__main__":
    asyncio.run(main())