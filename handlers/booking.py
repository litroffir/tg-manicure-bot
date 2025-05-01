from __future__ import annotations

from datetime import datetime

from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from handlers import start
from states import BookingStates
from utils import (
    master_choice_kb,
    service_choice_kb,
    dates_kb,
    wishes_kb
)
from utils.storage import user_bookings

book_router = Router()


# Обработка кнопки "💅 Записаться"
@book_router.message(Command("book"))
@book_router.callback_query(F.data == "book")
async def choose_master(callback: types.Message | types.CallbackQuery, state: FSMContext):
    if isinstance(callback, types.CallbackQuery):
        await callback.message.edit_text("Выберите мастера:", reply_markup=master_choice_kb())
    else:
        await callback.answer("Выберите мастера:", reply_markup=master_choice_kb())
    await state.set_state(BookingStates.choosing_master)


# Выбор услуги
@book_router.callback_query(F.data.startswith("master_"))
async def choose_service(callback: types.CallbackQuery, state: FSMContext):
    master = callback.data.split("_")[1]
    await state.update_data(master="Ксения" if master == "kseniya" else "Анастасия")

    await callback.message.edit_text(
        "Выберите услугу:",
        reply_markup=service_choice_kb(master)
    )
    await state.set_state(BookingStates.choosing_service)


# Выбор даты
@book_router.callback_query(F.data.startswith("service_"))
async def choose_date(callback: types.CallbackQuery, state: FSMContext):
    service = callback.data.split("_")[1]
    if service == "classic":
        await state.update_data(service="Классический маникюр")
    elif service == "apparatus":
        await state.update_data(service="Аппаратный маникюр")
    elif service == "manicure":
        await state.update_data(service="Маникюр")
    else:
        await state.update_data(service="Педикюр")

    await callback.message.edit_text(
        f"Выберите дату:",
        reply_markup=dates_kb()
    )
    await state.set_state(BookingStates.choosing_date)


# Ввод пожеланий
@book_router.callback_query(F.data.startswith("date_"))
async def enter_wishes(callback: types.CallbackQuery, state: FSMContext):
    date = callback.data.split("_", 1)[1]
    await state.update_data(date=date)

    await callback.message.edit_text(
        f"Выбрана дата: {date}\nНапишите ваши пожелания:"
    )
    await callback.message.answer(
        "Или нажмите 'Пропустить'",
        reply_markup=wishes_kb()
    )
    await state.set_state(BookingStates.entering_wishes)


# Подтверждение записи
@book_router.message(BookingStates.entering_wishes)
async def confirm_booking(message: types.Message, state: FSMContext):
    data = await state.get_data()
    wishes = "не указаны" if message.text == "Пропустить" else message.text

    # Сохраняем запись
    booking_id = datetime.now().strftime("%Y%m%d%H%M%S")
    user_id = message.from_user.id
    if user_id not in user_bookings:
        user_bookings[user_id] = {}

    user_bookings[user_id][booking_id] = {
        "master": data['master'],
        "service": data['service'],
        "date": data['date'],
        "wishes": wishes
    }

    text = (
        "✨ *Запись подтверждена!* ✨\n\n"
        f"👩🎨 Мастер: {data['master']}\n\n"
        f"💅 Услуга: {data['service']}\n\n"
        f"📅 Дата: {data['date']}\n\n"
        f"📝 Пожелания: {wishes}"
    )

    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()
    await start(message, state)