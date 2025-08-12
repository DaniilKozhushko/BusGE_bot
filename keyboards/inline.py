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