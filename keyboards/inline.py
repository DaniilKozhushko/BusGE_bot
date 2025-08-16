from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def set_city() -> InlineKeyboardMarkup:
    """
    Inline-keyboard for selecting a city.

    :return: InlineKeyboardMarkup
    """

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Тбилиси", callback_data="Tbilisi"),
        InlineKeyboardButton(text="Батуми", callback_data="Batumi"),
    )
    return builder.as_markup()


def refresh_schedule(city_name: str, stop_id: int, chat_id: int, message_id: int) -> InlineKeyboardMarkup:
    """
    Inline-keyboard for refreshing the schedule.

    :param city_name: name of the city selected by the user
    :param stop_id: bus stop number to refresh
    :param chat_id: chat id where the update is happening
    :param message_id: id of the message that needs to be updated
    :return: InlineKeyboardMarkup
    """

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data=f"menu:{chat_id}:{message_id}"),
        InlineKeyboardButton(text="🔄 Обновить", callback_data=f"refresh:{city_name}:{stop_id}:{chat_id}:{message_id}")
    )
    return builder.as_markup()


def main_menu(chat_id: int, message_id: int) -> InlineKeyboardMarkup:
    """
    Inline-keyboard with the menu.

    :param chat_id: chat id with the message
    :param message_id: id of the message
    :return: InlineKeyboardMarkup
    """

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🚏 Сохранённые остановки", callback_data=f"saved_stops:{chat_id}:{message_id}")
    )
    builder.row(
        InlineKeyboardButton(text="🗺 Сохранённые маршруты", callback_data=f"saved_routes:{chat_id}:{message_id}")
    )
    return builder.as_markup()


def saved_stops(user_stops: list[tuple[str, int, int]], chat_id: int, message_id: int) -> InlineKeyboardMarkup:
    """
    Inline-keyboard to display saved stops.

    :param user_stops: list of tuples of user's saved stops
    :param chat_id: chat id with the message
    :param message_id: id of the message
    :return: InlineKeyboardMarkup
    """

    builder = InlineKeyboardBuilder()
    for stop in user_stops:
        name, city_id, stop_id = stop
        builder.row(
            InlineKeyboardButton(text=f"{name}", callback_data=f"user_stop:{chat_id}:{message_id}:{city_id}:{stop_id}")
        )
    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data=f"menu:{chat_id}:{message_id}")
    )
    return builder.as_markup()


def delete_stop(city_id: int, stop_id: int, chat_id: int, message_id: int) -> InlineKeyboardMarkup:
    """
    Inline-keyboard to display the stop manipulation buttons.

    :param city_id: id of the city with the stop
    :param stop_id: id of the bus stop
    :param chat_id: chat id with the message
    :param message_id: id of the message
    :return: InlineKeyboardMarkup
    """

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔄 Обновить", callback_data=f"refresh_del:{city_id}:{stop_id}:{chat_id}:{message_id}")
    )
    builder.row(
        InlineKeyboardButton(text="🚏 Сохранённые остановки", callback_data=f"if_saved_stops:{chat_id}:{message_id}"),
        InlineKeyboardButton(text="🗑 Удалить остановку", callback_data=f"del:{city_id}:{stop_id}")
    )
    return builder.as_markup()