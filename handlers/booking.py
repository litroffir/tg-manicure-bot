from __future__ import annotations

import numpy as np

import datetime

from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from aiogram_calendar import SimpleCalendarCallback

from sqlalchemy import select

from handlers import start
from models import Appointment
from states import BookingStates
from utils import (
    master_choice_kb,
    service_choice_kb,
    wishes_kb,
    time_keyboard, get_time_slots, myCalendar
)

from utils import async_session

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
    if master == "kseniya":
        await state.update_data(master="Ксения")
    elif master == "anastasia":
        await state.update_data(master="Анастасия")

    data = await state.get_data()
    await callback.message.edit_text(
        "Выберите услугу:",
        reply_markup=service_choice_kb("kseniya" if data["master"] == "Ксения" else "anastasia")
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
    elif service == "pedicure":
        await state.update_data(service="Педикюр")

    await callback.message.edit_text(
        "Выберите дату:",
        reply_markup=await myCalendar.start_calendar()
    )
    await state.set_state(BookingStates.choosing_date)


@book_router.callback_query(SimpleCalendarCallback.filter())
async def choose_time(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date_selected = await myCalendar.process_selection(callback, callback_data, state)
    if not selected:
        return
    convrt_date = datetime.date(year=date_selected.year, month=date_selected.month, day=date_selected.day)
    if convrt_date < datetime.date.today() or convrt_date.isoweekday() in (6, 7):
        await callback.answer("В этот день мы не работаем😥", show_alert=True)
        return
    await state.update_data(selected_date=convrt_date)

    await callback.message.edit_text(
        "Выберите время:",
        reply_markup=time_keyboard(await get_time_slots())
    )
    await state.set_state(BookingStates.choosing_time)


@book_router.callback_query(F.data.startswith("time_"))
async def enter_wishes(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_time = callback.data.split("_")[1]
    start_dttm = datetime.datetime(year=data["selected_date"].year, month=data["selected_date"].month,
                                   day=data["selected_date"].day,
                                   hour=int(selected_time.split('-')[0].split(":")[0]),
                                   minute=int(selected_time.split('-')[0].split(":")[1]), second=0)
    end_dttm = datetime.datetime(year=data["selected_date"].year, month=data["selected_date"].month,
                                 day=data["selected_date"].day,
                                 hour=int(selected_time.split('-')[1].split(":")[0]),
                                 minute=int(selected_time.split('-')[1].split(":")[1]), second=0)
    if start_dttm < datetime.datetime.now():
        await callback.answer("Слишком поздно😥", show_alert=True)
        return

    async with async_session() as session:
        existing = (await session.execute(
            select(Appointment).where((Appointment.start_datetime == start_dttm)
                                      & (Appointment.end_datetime == end_dttm)
                                      & (Appointment.master == data["master"]))
        )).scalar_one_or_none()

        if existing:
            await callback.answer("Это время уже занято! Выберите другое.", show_alert=True)
            return

    await state.update_data(selected_start_datetime=start_dttm, selected_end_datetime=end_dttm)
    await callback.message.edit_text(
        f"Выбрана дата: {data['selected_date']}\n"
        f"Время: {start_dttm.strftime('%H:%M')}-{end_dttm.strftime('%H:%M')}\nНапишите ваши пожелания:"
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
    booking_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    # Сохраняем запись
    async with async_session() as session:
        new_appointment = Appointment(
            user_id=message.from_user.id,
            booking_id=np.int64(booking_id),
            master=data['master'],
            service=data['service'],
            wishes=wishes,
            start_datetime=data['selected_start_datetime'],
            end_datetime=data["selected_end_datetime"]
        )
        session.add(new_appointment)
        await session.commit()

    text = (
        "✨ *Запись подтверждена!* ✨\n\n"
        f"👩 Мастер: {data['master']}\n\n"
        f"💅 Услуга: {data['service']}\n\n"
        f"📅 Дата: {data['selected_start_datetime'].strftime('%Y-%m-%d %H:%M')}-{data['selected_end_datetime'].strftime('%H:%M')}\n\n"
        f"📝 Пожелания: {wishes}"
    )

    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()
    await start(message, state)
