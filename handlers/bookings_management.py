from __future__ import annotations

import datetime

from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
from aiogram_calendar import SimpleCalendarCallback
from sqlalchemy import select

from models import Appointment, AppointmentDAO
from back_handlers import back_to_bookings
from states import BookingStates
from utils import (
    bookings_kb,
    booking_selection_kb,
    edit_booking_kb,
    master_choice_kb, service_choice_kb, async_session, myCalendar, time_keyboard, get_time_slots, admin_kb,
    generate_excel
)

book_management_router = Router()


@book_management_router.message(Command("my_bookings"))
@book_management_router.callback_query(F.data == "my_bookings")
async def show_bookings(callback: types.Message | types.CallbackQuery, state: FSMContext):
    await state.clear()
    async with async_session() as session:
        result = await session.execute(
            select(Appointment).where(Appointment.user_id == callback.from_user.id)
        )
        bookings = result.scalars().all()
        if not bookings:
            if isinstance(callback, types.CallbackQuery):
                await callback.message.edit_text("📭 У вас пока нет активных записей",
                                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                                     [types.InlineKeyboardButton(text="🔙 Назад",
                                                                                 callback_data="start")]
                                                 ]))
                return
            else:
                await callback.answer("📭 У вас пока нет активных записей",
                                      reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                          [types.InlineKeyboardButton(text="🔙 Назад", callback_data="start")]
                                      ]))
                return
        else:
            if isinstance(callback, types.CallbackQuery):
                await callback.message.edit_text("📖 Ваши активные записи:", reply_markup=bookings_kb(bookings))
            else:
                await callback.answer("📖 Ваши активные записи:", reply_markup=bookings_kb(bookings))
            await state.set_state(BookingStates.viewing_bookings)


# Обработчик выбора конкретной записи
@book_management_router.callback_query(F.data.startswith("view_booking_"))
async def handle_booking_selection(callback: types.CallbackQuery, state: FSMContext):
    booking_id = callback.data.split("_")[2]
    async with async_session() as session:
        result = await session.execute(
            select(Appointment).where(
                (Appointment.user_id == callback.from_user.id) & (Appointment.booking_id == int(booking_id)))
        )
        book = result.scalar_one_or_none()
        if not book:
            await callback.answer("Запись не найдена", show_alert=True)
            return

    text = (
        f"👩🎨 Мастер: {book.master}\n\n"
        f"💅 Услуга: {book.service}\n\n"
        f"📅 Дата: {book.start_datetime.strftime('%Y-%m-%d %H:%M')}-{book.end_datetime.strftime('%H:%M')}\n\n"
        f"📝 Пожелания: {book.wishes}"
    )

    await callback.message.edit_text(
        f"📄 Детали записи:\n\n{text}",
        reply_markup=booking_selection_kb(booking_id)
    )
    await state.update_data(original_message_id=callback.message.message_id, current_master=book.master)


# Обработчики действий с записями
@book_management_router.callback_query(F.data.startswith("edit_"))
async def edit_booking(callback: types.CallbackQuery, state: FSMContext):
    booking_id = callback.data.split("_")[1]

    await state.update_data(current_booking=booking_id)
    await state.set_state(BookingStates.editing_booking)
    await callback.message.edit_text("Выберите что хотите изменить:", reply_markup=edit_booking_kb(booking_id))


@book_management_router.callback_query(F.data.startswith("delete_"))
async def delete_booking(callback: types.CallbackQuery, state: FSMContext):
    booking_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    result = await AppointmentDAO.delete_appointment(booking_id, user_id)
    if result:
        await back_to_bookings(callback, state)
        await callback.answer("Запись удалена", show_alert=True)
    else:
        await callback.answer("Ошибка удаления", show_alert=True)


# Редактирование мастера
@book_management_router.callback_query(F.data.startswith("editingMaster_"))
async def edit_master_handler(callback: types.CallbackQuery, state: FSMContext):
    booking_id = callback.data.split("_")[1]

    await callback.message.edit_text(
        "Выберите нового мастера:",
        reply_markup=master_choice_kb(True, booking_id)
    )
    await state.set_state(BookingStates.editing_master)


@book_management_router.callback_query(
    F.data.startswith("master_"),
    BookingStates.editing_master
)
async def process_edit_master(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    booking_id = data['current_booking']
    user_id = callback.from_user.id

    # Обновляем данные
    new_master = "Ксения" if "kseniya" in callback.data else "Анастасия"
    result = await AppointmentDAO.update_appointment(booking_id=int(booking_id), user_id=user_id, master=new_master)

    if result:
        await callback.answer("Мастер успешно изменён! Теперь выберите услугу", show_alert=True)
        await callback.message.edit_text(
            "Выберите новую услугу:",
            reply_markup=service_choice_kb(callback.data.split("_")[1], True, booking_id)
        )
    else:
        await callback.answer("Ошибка редактирования", show_alert=True)


@book_management_router.callback_query(
    F.data.startswith("service_"),
    BookingStates.editing_master
)
async def process_edit_master_service(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    booking_id = data['current_booking']
    user_id = callback.from_user.id

    # Обновляем данные
    service = callback.data.split("_")[1]
    if service == "classic":
        new_service = "Классический маникюр"
    elif service == "apparatus":
        new_service = "Аппаратный маникюр"
    elif service == "manicure":
        new_service = "Маникюр"
    else:
        new_service = "Педикюр"

    result = await AppointmentDAO.update_appointment(booking_id=int(booking_id), user_id=user_id, service=new_service)
    if result:
        await callback.answer("Услуга выбрана!", show_alert=True)
        await back_to_bookings(callback, state)
    else:
        await callback.answer("Ошибка редактирования", show_alert=True)


# Редактирование услуги
@book_management_router.callback_query(F.data.startswith("editingService_"))
async def edit_service_handler(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    booking_id = callback.data.split("_")[1]

    appointment = await AppointmentDAO.find_one_or_none(user_id=user_id, booking_id=int(booking_id))
    await callback.message.edit_text(
        "Выберите новую услугу:",
        reply_markup=service_choice_kb("kseniya" if appointment.master == "Ксения" else "anastasia", True, booking_id)
    )
    await state.set_state(BookingStates.editing_service)


@book_management_router.callback_query(
    F.data.startswith("service_"),
    BookingStates.editing_service
)
async def process_edit_service(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    booking_id = data['current_booking']
    user_id = callback.from_user.id

    # Обновляем данные
    service = callback.data.split("_")[1]
    if service == "classic":
        new_service = "Классический маникюр"
    elif service == "apparatus":
        new_service = "Аппаратный маникюр"
    elif service == "manicure":
        new_service = "Маникюр"
    else:
        new_service = "Педикюр"

    result = await AppointmentDAO.update_appointment(booking_id=int(booking_id), user_id=user_id, service=new_service)

    if result:
        await callback.answer("Услуга выбрана!", show_alert=True)
        await back_to_bookings(callback, state)
    else:
        await callback.answer("Ошибка редактирования", show_alert=True)


# Редактирование даты
@book_management_router.callback_query(F.data.startswith("editingDate_"))
async def edit_date_handler(callback: types.CallbackQuery, state: FSMContext):
    booking_id = callback.data.split("_")[1]

    await callback.message.edit_text(
        "Выберите новую дату:",
        reply_markup=await myCalendar.start_calendar(edit_mode=True)
    )
    await state.set_state(BookingStates.editing_date)


@book_management_router.callback_query(
    SimpleCalendarCallback.filter(),
    BookingStates.editing_date
)
async def process_edit_date(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    data = await state.get_data()
    booking_id = data['current_booking']
    selected, date_selected = await myCalendar.process_selection(callback, callback_data, state)

    if not selected:
        return
    convrt_date = datetime.date(year=date_selected.year, month=date_selected.month, day=date_selected.day)
    if convrt_date < datetime.date.today() or convrt_date.isoweekday() in (6, 7):
        await callback.answer("В этот день мы не работаем😥", show_alert=True)
        return

    await state.update_data(selected_date=convrt_date)

    await callback.answer("Дата выбрана!", show_alert=True)
    await callback.message.edit_text(
        "Выберите время:",
        reply_markup=time_keyboard(await get_time_slots(), True, booking_id=booking_id)
    )


@book_management_router.callback_query(
    F.data.startswith("time_"),
    BookingStates.editing_date
)
async def process_edit_date_time(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    booking_id = data['current_booking']
    user_id = callback.from_user.id
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
                                      & (Appointment.end_datetime == end_dttm))
        )).scalar_one_or_none()

        if existing:
            await callback.answer("Это время уже занято! Выберите другое.", show_alert=True)
            return

    result = await AppointmentDAO.update_appointment(booking_id=int(booking_id), user_id=user_id,
                                                     start_datetime=start_dttm, end_datetime=end_dttm)
    if result:
        await callback.answer("Время измененно!", show_alert=True)
        await back_to_bookings(callback, state)
    else:
        await callback.answer("Ошибка редактирования", show_alert=True)


# Редактирование пожеланий
@book_management_router.callback_query(F.data.startswith("editingWishes_"))
async def edit_wishes_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Напишите ваши пожелания:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text="🔙 Назад", callback_data=f"back_to_bookings")]])
    )
    await state.set_state(BookingStates.editing_wishes)


@book_management_router.message(
    BookingStates.editing_wishes
)
async def process_edit_wishes(message: types.Message, state: FSMContext):
    data = await state.get_data()
    booking_id = data['current_booking']
    user_id = message.from_user.id
    wishes = message.text

    # Сохраняем запись
    result = await AppointmentDAO.update_appointment(booking_id=int(booking_id), user_id=user_id, wishes=wishes)
    if result:
        await message.answer("Хорошо!", show_alert=True)
        await back_to_bookings(message, state)
    else:
        await message.answer("Ошибка редактирования", show_alert=True)


@book_management_router.callback_query(F.data == "clients")
async def admin_kb_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="Выберите временной диапозон:",
        reply_markup=admin_kb()
    )


@book_management_router.callback_query(F.data.startswith("show_users_books"))
async def show_users_appointments(callback: types.CallbackQuery, state: FSMContext):
    callback_date = callback.data.split("_")[-1]
    if callback_date == "today":
        result = await AppointmentDAO.select_appointments_by_date(datetime.date.today(), datetime.date.today())
        if result:
            await callback.message.edit_text(text="✨ *Текущие записи* ✨\n\n{}".format('\n'.join(result)), reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="clients")]]))
        else:
            await callback.answer("Записей нет!", show_alert=True)
    elif callback_date == "tomorrow":
        result = await AppointmentDAO.select_appointments_by_date(datetime.date.today() + datetime.timedelta(days=1),
                                                                  datetime.date.today() + datetime.timedelta(days=1))
        if result:
            await callback.message.edit_text(text="✨ *Текущие записи* ✨\n\n{}".format('\n'.join(result)), reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="clients")]]))
        else:
            await callback.answer("Записей нет!", show_alert=True)
    elif callback_date == "week":
        start_date = datetime.datetime.now().date()
        end_date = start_date + datetime.timedelta(days=7)
        result = await AppointmentDAO.select_appointments_by_date(start_date=start_date, end_date=end_date, csv=True)

        if result:
            excel_data = await generate_excel(result)
            excel_file = BufferedInputFile(
                file=excel_data,
                filename="weekly_appointments.xlsx"
            )
            await callback.message.reply_document(
                document=excel_file,
                caption="📊 Записи на ближайшую неделю"
            )
        else:
            await callback.answer("Записей нет!", show_alert=True)
    elif callback_date == "month":
        start_date = datetime.datetime.now().date()
        end_date = start_date + datetime.timedelta(days=30)
        result = await AppointmentDAO.select_appointments_by_date(start_date=start_date, end_date=end_date, csv=True)
        if result:
            excel_data = await generate_excel(result)
            excel_file = BufferedInputFile(
                file=excel_data,
                filename="monthly_appointments.xlsx"
            )
            await callback.message.reply_document(
                document=excel_file,
                caption="📊 Записи на ближайший месяц"
            )
        else:
            await callback.answer("Записей нет!", show_alert=True)