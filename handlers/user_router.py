import database as db
import utils.async_utils as au
import keyboards.inline as ikb
from asyncio import sleep
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery


# router for processing messages from users
user_router = Router()


# command /start handler
@user_router.message(Command("start"))
async def start_command(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    # checking if a user are in the database
    if await db.user_exists(user_id):

        # checking if a city is selected by the user
        if await db.city_selected(user_id):
            await message.answer(
                text=f"""👋🏻 Приветствую тебя снова, {user_name}!

Полезная информация о боте доступна по команде /about"""
            )
        else:
            await message.answer(
                text=f"""👋🏻 Приветствую тебя снова, {user_name}!

Полезная информация о боте доступна по команде /about"""
            )

            # offering the user to select a city
            await set_city_command(message)
    else:
        # adding a new user to the database
        await db.add_user(user_id)

        await message.answer(
            text=f"""👋🏻 Приветствую, {user_name}!

Чтобы получить расписание автобусов - выбери свой город и введи номер остановки (4 цифры можно узнать, посмотрев на табло, или на Яндекс.Картах)

Больше полезной информации доступно по команде /about"""
        )

        # offering user to select city
        await set_city_command(message)


# command /menu handler
@user_router.message(Command("menu"))
async def start_command(message: Message):
    sent_msg = await message.answer(text="Автобусы Грузии 🇬🇪", reply_markup=None)
    await sent_msg.edit_reply_markup(
        reply_markup=ikb.main_menu(sent_msg.chat.id, sent_msg.message_id)
    )


# command /set_city
@user_router.message(Command("set_city"))
async def set_city_command(message: Message):
    # offering user to select a city
    await message.answer(text="🏘 Выбери свой город:", reply_markup=ikb.set_city())


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
    
Номер можно узнать в Яндекс.Картах или, посмотрев на табло у остановки - в левом нижнем углу написано <b>ID:XXXX</b>, где XXXX - номер твоей остановки.

Введи номер и получишь расписание автобусов, например:
<code>17:55</code> 🔴 <code>408</code> через <b>3</b> мин. Rustaveli M/S
<code>17:58</code> 🟡 <code>331</code> через <b>6</b> мин. Krtsanisi Street - Station Square
<code>18:04</code> 🟢 <code>333</code> через <b>12</b> мин. Vazisubani M/D-2 - Tbilisi Mall

Красный маркер - до прибытия автобуса осталось 3 минуты или меньше
Жёлтый - 4-6 минут
Зелёный - 7 и больше

Чтобы добавить остановку - введи её номер и название, например:
<b>2171 К метро</b>

Чтобы обновить название остановки - введи её номер и новое название.

Сохранённые маршруты и остановки можно посмотреть по команде /menu"""
    )


# any user's message
@user_router.message(F.text)
async def user_text(message: Message):
    user_id = message.from_user.id

    # check if the city is selected by the user
    if await db.city_selected(user_id):
        text = message.text.strip()
        stop_name = None

        if " " in text:
            text, stop_name = text.split(" ", 1)

        # user's message validation
        try:
            stop_id = int(text)
        except ValueError:
            await message.answer(text=f"<i>{text}</i> - это точно корректный номер остановки?")
            return

        # getting user's city
        city_name = await db.get_user_city_name(user_id)

        if not await db.stop_exists(city_name, stop_id):
            await message.answer(text=f"😢 В {city_name} такой остановки нет")
            return

        # if the user wants to save the stop
        if stop_name:

            # limit of saved stops: 10
            if await db.get_user_stops_count(user_id) >= 10:
                sent_message = await message.reply(text="""❎ У тебя уже довольно много сохранённых остановок.
Может удалить какую-нибудь старую?""")
            else:
                await db.add_user_stop(user_id, city_name, stop_id, stop_name)
                sent_message = await message.reply(text=f"✅ Остановка успешно добавлена")
            await sleep(6)

            # attempt to delete user and bot messages
            try:
                await message.bot.delete_message(
                    chat_id=sent_message.chat.id,
                    message_id=sent_message.message_id
                )
            except Exception as e:
                print(e)
            try:
                await message.bot.delete_message(
                    chat_id=message.chat.id,
                    message_id=message.message_id
                )
            except Exception as e:
                print(e)

            return

        # sending action as if the bot is typing
        await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

        # getting schedule
        answer = await au.return_schedule(stop_id, city_name)

        # sending a message to a user
        sent_msg  = await message.answer(text=answer, reply_markup=None)
        await sent_msg.edit_reply_markup(
            reply_markup=ikb.refresh_schedule(
                city_name=city_name,
                stop_id=stop_id,
                chat_id=sent_msg.chat.id,
                message_id=sent_msg.message_id
            )
        )
    else:
        # offering user to select city
        await message.answer(
            text="Выбери, пожалуйста, свой город чтобы получить расписание автобусов.",
            reply_markup=ikb.set_city(),
        )


# "refresh" button
@user_router.callback_query(F.data.startswith("refresh:"))
async def refresh_button(callback: CallbackQuery):
    # getting callback data
    callback_data = callback.data.split(":")
    city_name = callback_data[1]

    # writing callback data to variables
    stop_id, chat_id, message_id = map(int, callback_data[2:])

    # getting schedule
    answer = await au.return_schedule(stop_id, city_name)

    # if possible to change
    try:
        await callback.bot.edit_message_text(
            text=answer,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=ikb.refresh_schedule(city_name, stop_id, chat_id, message_id)
        )
        await callback.answer(text=f"Обновлено: {city_name} {stop_id}")
    except Exception as e:
        if "message is not modified" in str(e).lower():
            await callback.answer(text=f"Пока изменений в расписании нет: {city_name} {stop_id}")
            return

        print(e)

        # sending a message to a user
        sent_msg = await callback.message.answer(text=answer, reply_markup=None)
        await sent_msg.edit_reply_markup(
            reply_markup=ikb.refresh_schedule(
                city_name=city_name,
                stop_id=stop_id,
                chat_id=sent_msg.chat.id,
                message_id=sent_msg.message_id
            )
        )


# 'menu' button
@user_router.callback_query(F.data.startswith("menu:"))
async def menu_button(callback: CallbackQuery):
    # getting callback data
    callback_data = callback.data.split(":")

    # writing callback data to variables
    chat_id, message_id = map(int, callback_data[1:])

    # if possible to change bot message
    try:
        await callback.bot.edit_message_text(
            text="Автобусы Грузии 🇬🇪",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=ikb.main_menu(chat_id, message_id)
        )
    except Exception as e:
        print(e)

        # sending a new message to a user
        sent_msg = await callback.message.answer(text="Автобусы Грузии 🇬🇪", reply_markup=None)
        await sent_msg.edit_reply_markup(
            reply_markup=ikb.main_menu(
                chat_id=sent_msg.chat.id,
                message_id=sent_msg.message_id)
        )


# inline-keyboard with saved user routes
@user_router.callback_query(F.data.startswith("saved_routes:"))
async def saved_routes_button(callback: CallbackQuery):
    await callback.answer(text="*в разработке*")


# inline-keyboard with saved user stops
@user_router.callback_query(F.data.startswith("saved_stops:"))
async def saved_stops_button(callback: CallbackQuery):
    # getting callback data
    callback_data = callback.data.split(":")

    # writing callback data to variables
    chat_id, message_id = map(int, callback_data[1:])

    # getting user's saved stops
    saved_stops = await db.get_users_stops(callback.from_user.id)

    if saved_stops:
        await callback.answer()

        # if possible to change bot message
        try:
            await callback.bot.edit_message_text(
                text="🚏 Сохранённые остановки",
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=ikb.saved_stops(saved_stops, chat_id, message_id)
            )
        except Exception as e:
            print(e)

            # sending a new message
            sent_msg = await callback.message.answer(text="🚏 Сохранённые остановки", reply_markup=None)
            await sent_msg.edit_reply_markup(
                reply_markup=ikb.saved_stops(
                    user_stops=saved_stops,
                    chat_id=sent_msg.chat.id,
                    message_id=sent_msg.message_id)
            )
    else:
        await callback.answer(text="У тебя нет сохранённых остановок")


# saved user stop
@user_router.callback_query(F.data.startswith("user_stop:"))
async def saved_stops_button(callback: CallbackQuery):
    # getting callback data
    callback_data = callback.data.split(":")

    # writing callback data to variables
    chat_id, message_id, city_id, stop_id = map(int, callback_data[1:])

    # getting city_name
    city_name = await db.get_city_name(city_id)

    # getting schedule
    answer = await au.return_schedule(stop_id, city_name)

    # if possible to change bot message
    try:
        await callback.bot.edit_message_text(
            text=answer,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=ikb.delete_stop(city_id, stop_id, chat_id, message_id)
        )
    except Exception as e:
        print(e)

        # sending a new message
        sent_msg = await callback.message.answer(text=answer, reply_markup=None)
        await sent_msg.edit_reply_markup(
            reply_markup=ikb.delete_stop(city_id, stop_id, chat_id, message_id)
        )


# schedule with buttons for manipulation
@user_router.callback_query(F.data.startswith("refresh_del:"))
async def saved_stops_button(callback: CallbackQuery):
    # getting callback data
    callback_data = callback.data.split(":")
    city_id = int(callback_data[1])
    city_name = await db.get_city_name(city_id)

    # writing callback data to variables
    stop_id, chat_id, message_id = map(int, callback_data[2:])

    # getting schedule
    answer = await au.return_schedule(stop_id, city_name)

    city_id = await db.get_city_id(city_name)

    # if possible to change bot message
    try:
        await callback.bot.edit_message_text(
            text=answer,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=ikb.delete_stop(city_id, stop_id, chat_id, message_id)
        )
        await callback.answer(text=f"Обновлено: {city_name} {stop_id}")
    except Exception as e:
        if "message is not modified" in str(e).lower():
            await callback.answer(text=f"Пока изменений в расписании нет: {city_name} {stop_id}")
            return

        print(e)

        # sending a new message to a user
        sent_msg = await callback.message.answer(text=answer, reply_markup=None)
        await sent_msg.edit_reply_markup(
            reply_markup=ikb.delete_stop(city_id, stop_id, chat_id, message_id)
        )


# delete saved user stop
@user_router.callback_query(F.data.startswith("del:"))
async def saved_stops_button(callback: CallbackQuery):
    # getting callback data
    callback_data = callback.data.split(":")
    city_id, stop_id = map(int, callback_data[1:])

    await db.delete_user_stop(callback.from_user.id, city_id, stop_id)

    await callback.answer(text=f"Остановка {stop_id} удалена")


# if there are no saved stops - return to the menu
@user_router.callback_query(F.data.startswith("if_saved_stops:"))
async def saved_stops_button(callback: CallbackQuery):
    # getting callback data
    callback_data = callback.data.split(":")

    # writing callback data to variables
    chat_id, message_id = map(int, callback_data[1:])

    saved_stops = await db.get_users_stops(callback.from_user.id)

    if saved_stops:
        await callback.answer()

        # if possible to change bot message
        try:
            await callback.bot.edit_message_text(
                text="🚏 Сохранённые остановки",
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=ikb.saved_stops(saved_stops, chat_id, message_id)
            )
        except Exception as e:
            print(e)

            # sending a new message
            sent_msg = await callback.message.answer(text="🚏 Сохранённые остановки", reply_markup=None)
            await sent_msg.edit_reply_markup(
                reply_markup=ikb.saved_stops(saved_stops, sent_msg.chat.id, sent_msg.message_id)
            )
    else:
        await callback.answer(text="У тебя нет сохранённых остановок")
        await menu_button(callback)