from aiogram import types
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)


def main_menu_kb(is_admin: bool = False):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💅 Записаться", callback_data="book"),
         InlineKeyboardButton(text="📝 Мои записи", callback_data="my_bookings")],
        [InlineKeyboardButton(text="🌟 Наши мастера", callback_data="masters")]
    ])
    if is_admin:
        keyboard.inline_keyboard.append(
            [InlineKeyboardButton(text="Посмотреть данные по клиентам", callback_data="clients")])
    return keyboard


def admin_choice_kb():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Записи", callback_data="clients_books"),
         InlineKeyboardButton(text="📊 Статистика", callback_data="clients_stats")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"start")]
    ])
    return keyboard


def admin_dates_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Записи на сегодня", callback_data="show_users_books_today")],
        [InlineKeyboardButton(text="Записи на завтра", callback_data="show_users_books_tomorrow")],
        [InlineKeyboardButton(text="Записи на неделю", callback_data="show_users_books_week")],
        [InlineKeyboardButton(text="Записи на месяц", callback_data="show_users_books_month")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"clients")]
    ])


def admin_stats_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="За сегодня", callback_data="show_users_stats_today")],
        [InlineKeyboardButton(text="За вчера", callback_data="show_users_stats_yesterday")],
        [InlineKeyboardButton(text="За прошлую неделю", callback_data="show_users_stats_week")],
        [InlineKeyboardButton(text="За прошлый месяц", callback_data="show_users_stats_month")],
        [InlineKeyboardButton(text="За всё время", callback_data="show_users_stats_all")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"clients")]
    ])


def master_choice_kb(edit_mode: bool = False, booking_id: str = None):
    text_suffix = f"_edit_{booking_id}" if edit_mode else ""
    callback_suffix = "back_to_bookings" if edit_mode else "start"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Ксения 💅", callback_data=f"master_kseniya{text_suffix}")],
        [InlineKeyboardButton(text="Анастасия 👑", callback_data=f"master_anastasia{text_suffix}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=callback_suffix)]
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
        buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="book")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def wishes_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Пропустить")]],
        resize_keyboard=True
    )


def bookings_kb(bookings):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for data in bookings:
        text = f"{data.start_datetime.date()} - {data.service} ({data.master})"
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=text,
                callback_data=f"view_booking_{data.booking_id}"
            )
        ])

    keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="start")])
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


def time_keyboard(available_slots: list, edit_mode: bool = False, booking_id: str = None):
    text_suff = f"_{booking_id}" if edit_mode else ''
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for slot in available_slots:
        slot = slot.replace('"', '')
        keyboard.inline_keyboard.append([InlineKeyboardButton(
            text=slot,
            callback_data=f"time_{slot}{text_suff}"
        )])
    if not edit_mode:
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_calendar")])
    return keyboard


def edit_booking_kb(booking_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Мастера", callback_data=f"editingMaster_{booking_id}")],
        [types.InlineKeyboardButton(text="Услугу", callback_data=f"editingService_{booking_id}")],
        [types.InlineKeyboardButton(text="Дату", callback_data=f"editingDate_{booking_id}")],
        [types.InlineKeyboardButton(text="Пожелания", callback_data=f"editingWishes_{booking_id}")],
        [types.InlineKeyboardButton(text="🔙 Назад", callback_data=f"back_to_bookings")]
    ])
