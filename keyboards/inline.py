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


def refresh_schedule(city: str, bus_stop_number: int, chat_id: int, message_id: int) -> InlineKeyboardMarkup:
    """
    Inline-keyboard for refreshing the schedule.

    :param city: name of the city selected by the user
    :param bus_stop_number: bus stop number to refresh
    :param chat_id: chat id where the update is happening
    :param message_id: id of the message that needs to be updated
    :return: InlineKeyboardMarkup
    """

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔄 Обновить", callback_data=f"refr:{city}:{bus_stop_number}:{chat_id}:{message_id}")
    )
    return builder.as_markup()