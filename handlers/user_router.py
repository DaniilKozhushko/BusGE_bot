import database as db
import utils.async_utils as au
import keyboards.inline as ikb
from config import ADMIN
from logger import logger
from asyncio import sleep
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup

# router for processing messages from users
user_router = Router()


# command /start handler
@user_router.message(Command("start"))
async def start_command(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    logger.info("command start",
                extra={"user_id": user_id}
                )

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
async def menu_command(message: Message):
    logger.info("command menu",
                extra={"user_id": message.from_user.id}
                )

    sent_msg = await message.answer(text="Автобусы Грузии 🇬🇪", reply_markup=None)
    await sent_msg.edit_reply_markup(
        reply_markup=ikb.main_menu(sent_msg.chat.id, sent_msg.message_id)
    )


# command /set_city
@user_router.message(Command("set_city"))
async def set_city_command(message: Message):
    logger.info("button set_city",
                extra={"user_id": message.from_user.id}
                )

    # offering user to select a city
    await message.answer(text="🏘 Выбери свой город:", reply_markup=ikb.set_city())


# selecting a city
@user_router.callback_query(F.data.in_({"Tbilisi", "Batumi"}))
async def select_city_button(callback: CallbackQuery):
    logger.info("button select_city",
                extra={"user_id": callback.from_user.id, "city_name": callback.data}
                )

    await callback.answer(text=f"Выбран город {callback.data}")

    user_id = callback.from_user.id
    city_name = callback.data

    # changing the user's selected city in the database
    await db.set_city(user_id, city_name)


# command /about
@user_router.message(Command("about"))
async def about_command(message: Message):
    logger.info("command about",
                extra={"user_id": message.from_user.id}
                )

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

Сохранённые маршруты и остановки можно посмотреть по команде /menu

Если есть вопрос/замечание/предложение, то запрос можно оставить по команде /admin"""
    )


class ContactWithAdmin(StatesGroup):
    making_request = State()


# command /admin handler
@user_router.message(Command("admin"))
async def admin_command(message: Message, state: FSMContext):
    logger.info("command admin",
                extra={"user_id": message.from_user.id}
                )

    # check the number of requests for the last 24 hours (limit - 5 requests)
    amount_requests = await db.count_requests(message.from_user.id)

    if amount_requests >= 5:
        await message.answer(
            text="""У тебя было довольно много запросов за последние 24 часа, на которые админ ещё не ответил.

Давай подождём немного ❤️"""
        )
        await menu_command(message)
    else:
        await message.answer(
            text="""Если у тебя есть вопрос/замечание/предложение, введи его и в ближайшее время админ пришлёт ответ.

Для отмены обращения нажми, пожалуйста, соответствующую кнопку ниже ⬇️""",
            reply_markup=ikb.cancel_request(),
        )
        await state.set_state(ContactWithAdmin.making_request)


# cancel request from user
@user_router.callback_query(F.data == "cancel_request")
async def cancel_request_button(callback: CallbackQuery, state: FSMContext):
    logger.info("button cancel_request",
                extra={"user_id": callback.from_user.id}
                )

    if await state.get_state() != ContactWithAdmin.making_request:
        await callback.answer(text="У тебя нет активного запроса.")
        return
    else:
        await state.clear()
        await callback.answer(text="Запрос отменён.")
        await menu_command(callback.message)


# receiving a request from a user
@user_router.message(ContactWithAdmin.making_request)
async def making_request_state(message: Message, state: FSMContext):
    user_id = message.from_user.id
    logger.info("text",
                extra={"user_id": message.from_user.id, "text": message.text}
                )
    # saving user text
    request = message.text.strip()

    # adding a request to the database
    request_id = await db.add_request(user_id, request)

    # sending request to admin
    await message.bot.send_message(
        chat_id=ADMIN,
        text=f"🆕 НОВЫЙ ЗАПРОС 🆕\n\nUSER_ID: <code>{user_id}</code>\nREQUEST_ID: <code>{request_id}</code>\n\n{request}\n\n/answer [user_id] [request_id] [answer]"
    )

    # reply to user and end State
    await message.reply(text="Твой запрос получен. ❤️ Пожалуйста, ожидай.")
    await state.clear()
    await menu_command(message)


# any user's message
@user_router.message(F.text)
async def user_text(message: Message):
    user_id = message.from_user.id

    logger.info("text",
                extra={"user_id": message.from_user.id, "text": message.text}
                )

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
            await message.reply(text=f"😢 В {city_name} такой остановки нет.")
            return

        # if the user wants to save the stop
        if stop_name:

            # limit of saved stops: 10
            if await db.get_user_stops_count(user_id) >= 10:
                sent_message = await message.reply(text="""❎ У тебя уже довольно много сохранённых остановок.
Может удалить какую-нибудь старую?""")
            else:
                # check if there is a stop with the alias in the database
                city_id = await db.get_city_id(city_name)
                row = await db.get_stop_alias(user_id, city_id, stop_id)

                if row:
                    await message.reply(text="❎ Такая остановка уже сохранена.")
                    return

                await db.add_user_stop(user_id, city_name, stop_id, stop_name)
                sent_message = await message.reply(text=f"✅ Остановка успешно добавлена.")
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
        answer = await au.return_schedule(stop_id, city_name, user_id)

        # sending a message to a user
        sent_msg = await message.answer(text=answer, reply_markup=None)
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
    user_id = callback.from_user.id
    logger.info("button refresh",
                extra={"user_id": user_id}
                )

    # getting callback data
    callback_data = callback.data.split(":")
    city_name = callback_data[1]

    # writing callback data to variables
    stop_id, chat_id, message_id = map(int, callback_data[2:])

    # sending action as if the bot is typing
    await callback.message.bot.send_chat_action(chat_id=chat_id, action="typing")

    # getting schedule
    answer = await au.return_schedule(stop_id, city_name, user_id)

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
    logger.info("button menu",
                extra={"user_id": callback.from_user.id}
                )

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
    logger.info("button saved_routes",
                extra={"user_id": callback.from_user.id}
                )

    await callback.answer(text="*в разработке*")


# inline-keyboard with saved user stops
@user_router.callback_query(F.data.startswith("saved_stops:"))
async def saved_stops_button(callback: CallbackQuery):
    logger.info("button saved_stops",
                extra={"user_id": callback.from_user.id}
                )

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
async def user_stop_button(callback: CallbackQuery):
    # getting callback data
    callback_data = callback.data.split(":")

    # writing callback data to variables
    chat_id, message_id, city_id, stop_id = map(int, callback_data[1:])
    user_id = callback.from_user.id

    logger.info("button user_stop",
                extra={"user_id": user_id}
                )

    # getting bus stop alias
    stop_alias = await db.get_stop_alias(user_id, city_id, stop_id)

    if not stop_alias:
        await callback.answer("Остановки с таким названием нет.")
        return

    # getting city_name
    city_name = await db.get_city_name(city_id)

    # sending action as if the bot is typing
    await callback.message.bot.send_chat_action(chat_id=chat_id, action="typing")

    # getting schedule
    answer = f"<b>{stop_alias}:</b>\n"
    answer += await au.return_schedule(stop_id, city_name, user_id)
    await callback.answer(text=f"{city_name} {stop_id}")

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
async def refresh_delete_stop_button(callback: CallbackQuery):
    # getting callback data
    callback_data = callback.data.split(":")
    city_id = int(callback_data[1])
    city_name = await db.get_city_name(city_id)

    # writing callback data to variables
    stop_id, chat_id, message_id = map(int, callback_data[2:])
    user_id = callback.from_user.id
    logger.info("button refresh_delete_stop",
                extra={"user_id": user_id}
                )

    # getting bus stop alias
    stop_alias = await db.get_stop_alias(user_id, city_id, stop_id)

    # sending action as if the bot is typing
    await callback.message.bot.send_chat_action(chat_id=chat_id, action="typing")

    # getting schedule
    answer = f"<b>{stop_alias}:</b>\n"
    answer += await au.return_schedule(stop_id, city_name, user_id)

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
async def delete_stop_button(callback: CallbackQuery):
    logger.info("button delete_stop",
                extra={"user_id": callback.from_user.id}
                )

    # getting callback data
    callback_data = callback.data.split(":")
    city_id, stop_id = map(int, callback_data[1:])

    await db.delete_user_stop(callback.from_user.id, city_id, stop_id)

    await callback.answer(text=f"Остановка {stop_id} удалена")


# if there are no saved stops - return to the menu
@user_router.callback_query(F.data.startswith("if_saved_stops:"))
async def if_saved_stops_button(callback: CallbackQuery):
    logger.info("button if_saved_stops",
                extra={"user_id": callback.from_user.id}
                )

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