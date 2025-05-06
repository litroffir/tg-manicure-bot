from aiogram import types
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)

from utils.dates import generate_dates


def main_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💅 Записаться", callback_data="book"),
         InlineKeyboardButton(text="📝 Мои записи", callback_data="my_bookings")],
        [InlineKeyboardButton(text="🌟 Наши мастера", callback_data="masters")]
    ])


def master_choice_kb(edit_mode: bool = False, booking_id: str = None):
    text_suffix = f"_edit_{booking_id}" if edit_mode else ""
    back_suffix = "_bookings" if edit_mode else "_menu"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Ксения 💅", callback_data=f"master_kseniya{text_suffix}")],
        [InlineKeyboardButton(text="Анастасия 👑", callback_data=f"master_anastasia{text_suffix}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"back_to{back_suffix}")]
    ])


def service_choice_kb(master: str, edit_mode: bool = False, booking_id: str = None):
    text_suffix = f"_edit_{booking_id}" if edit_mode else ""
    if master == "kseniya":
        services = [
            ["Классический маникюр 💅", f"service_classic{text_suffix}"],
            ["Аппаратный маникюр 🔧", f"service_apparatus{text_suffix}"]
        ]
    else:
        services = [
            ["Маникюр 💅", f"service_manicure{text_suffix}"],
            ["Педикюр 👣", f"service_pedicure{text_suffix}"]
        ]
    buttons = [
        [types.InlineKeyboardButton(text=text, callback_data=data)]
        for text, data in services
    ]
    if not edit_mode:
        buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_masters")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def dates_kb(edit_mode: bool = False, booking_id: str = None):
    dates = generate_dates()
    buttons = [
        [types.InlineKeyboardButton(text=date, callback_data=f"date_{date}")]
        for date in dates
    ]
    if edit_mode:
        buttons.append([types.InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_bookings")])
    else:
        buttons.append([types.InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_services")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def wishes_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Пропустить")]],
        resize_keyboard=True
    )


def bookings_kb(bookings):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for data in bookings:
        # print(data.booking_id)
        text = f"{data.date_time} - {data.service} ({data.master})"
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=text,
                callback_data=f"view_booking_{data.booking_id}"
            )
        ])

    keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")])
    return keyboard


def booking_selection_kb(booking_id: str):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_{booking_id}"),
            types.InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_{booking_id}")
        ],
        [types.InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_bookings")]
    ])
    return keyboard


def edit_booking_kb(booking_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Мастера", callback_data=f"editingMaster_{booking_id}")],
        [types.InlineKeyboardButton(text="Услугу", callback_data=f"editingService_{booking_id}")],
        [types.InlineKeyboardButton(text="Дату", callback_data=f"editingDate_{booking_id}")],
        [types.InlineKeyboardButton(text="Пожелания", callback_data=f"editingWishes_{booking_id}")],
        [types.InlineKeyboardButton(text="🔙 Назад", callback_data=f"back_to_bookings")]
    ])
