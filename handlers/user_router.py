import database as db
import utils.utils as u
from aiogram import Router, F
import utils.async_utils as au
import keyboards.inline as ikb
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery


# router for processing messages from users
user_router = Router()


# command /start handler
@user_router.message(Command("start"))
async def start_command(message: Message):
    user_id = message.from_user.id
    # checking if a user are in the database
    if await db.user_exists(user_id):

        # checking if a city is selected by the user
        if await db.city_selected(user_id):
            await message.answer(
                text=f"""👋🏻 Приветствую тебя снова, {message.from_user.first_name}!

Чтобы получить расписание автобусов - введи номер остановки (4 цифры можно узнать, посмотрев на табло, или на Яндекс.Картах)"""
            )
        else:
            await message.answer(
                text=f"""👋🏻 Приветствую тебя снова, {message.from_user.first_name}!

Чтобы получить расписание автобусов - выбери свой город и введи номер остановки (4 цифры можно узнать, посмотрев на табло, или на Яндекс.Картах)"""
            )

            # offering the user to select a city
            await set_city_command(message)
    else:
        # adding a new user to the database
        await db.add_user(user_id)
        await message.answer(
            text=f"""Приветствую, {message.from_user.first_name}!

Чтобы получить расписание автобусов - выбери свой город и введи номер остановки (4 цифры можно узнать, посмотрев на табло, или на Яндекс.Картах)"""
        )

        # offering user to select city
        await set_city_command(message)


# command /set_city
@user_router.message(Command("set_city"))
async def set_city_command(message: Message):
    # offering user to select city
    await message.answer(text="Выбери свой город:", reply_markup=ikb.set_city())


# selecting a city
@user_router.callback_query(F.data.in_({"Tbilisi", "Batumi"}))
async def select_tbilisi(callback: CallbackQuery):
    await callback.answer(text=f"Выбран город {callback.data}")
    user_id = callback.from_user.id
    city_name = callback.data

    # changing the user's selected city in the database
    await db.set_city(user_id, city_name)


# command /about
@user_router.message(Command("about"))
async def about_command(message: Message):
    await message.answer(
        text="""Чтобы получить расписание автобусов - выбери свой город и введи номер остановки.
    
Номер можно узнать, посмотрев на табло у остановки - в левом нижнем углу написано <b>ID:XXXX</b>, где XXXX - номер твоей остановки.

Введи номер и получишь расписание автобусов, например:
<code>17:55</code> 🔴 <code>408</code> через <b>3</b> мин. Rustaveli M/S
<code>17:58</code> 🟡 <code>331</code> через <b>6</b> мин. Krtsanisi Street - Station Square
<code>18:04</code> 🟢 <code>333</code> через <b>12</b> мин. Vazisubani M/D-2 - Tbilisi Mall

Красный маркер - до прибытия автобуса осталось 3 минуты или меньше
Жёлтый - 4-6 минут
Зелёный - 7 и больше"""
    )


# any user's message
@user_router.message(F.text)
async def user_text(message: Message):
    user_id = message.from_user.id

    # check if the city is selected by the user
    if await db.city_selected(user_id):

        # user's message validation
        text = message.text.strip()
        try:
            bus_stop_number = int(text)
        except ValueError:
            await message.answer(text=f"<i>{text}</i> - это точно корректный номер остановки?")
            return

        # getting user's city
        city = await db.get_city_name(user_id)

        # functions by cities
        schedule_funcs = {
            "Tbilisi": au.get_tbilisi_schedule,
            "Batumi": au.get_batumi_schedule,
        }

        # sending action as if the bot is typing
        await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

        # getting schedule depending on user's city
        schedule = await schedule_funcs[city](bus_stop_number)
        if schedule:
            parse_funcs = {
                "Tbilisi": u.parse_tbilisi_schedule,
                "Batumi": u.parse_batumi_schedule
            }

            # schedule formatting
            answer = parse_funcs[city](schedule)
            await message.answer(text=f"{answer}")
        else:
            await message.answer(
                text="😢 В ближайшее время автобусов не ожидается или указан неверный номер остановки."
            )
    else:
        # offering user to select city
        await message.answer(
            text="Выбери, пожалуйста, свой город чтобы получить расписание автобусов.",
            reply_markup=ikb.set_city(),
        )