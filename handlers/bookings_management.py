from __future__ import annotations

from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models import Appointment, AppointmentDAO
from back_handlers import back_to_bookings
from states import BookingStates
from utils import (
    bookings_kb,
    booking_selection_kb,
    edit_booking_kb,
    master_choice_kb, service_choice_kb, dates_kb, async_session
)

book_management_router = Router()


@book_management_router.message(Command("my_bookings"))
@book_management_router.callback_query(F.data == "my_bookings")
async def show_bookings(callback: types.Message | types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
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
                                                                                 callback_data="back_to_menu")]
                                                 ]))
                return
            else:
                await callback.answer("📭 У вас пока нет активных записей",
                                      reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                          [types.InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
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
        f"📅 Дата: {book.date_time}\n\n"
        f"📝 Пожелания: {book.wishes}"
    )

    await callback.message.edit_text(
        f"📄 Детали записи:\n\n{text}",
        reply_markup=booking_selection_kb(booking_id)
    )
    await state.update_data(original_message_id=callback.message.message_id)


# Обработчики действий с записями
@book_management_router.callback_query(F.data.startswith("edit_"))
async def edit_booking(callback: types.CallbackQuery, state: FSMContext):
    booking_id = callback.data.split("_")[1]
    user_id = callback.from_user.id

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
        reply_markup=dates_kb(True, booking_id)
    )
    await state.set_state(BookingStates.editing_date)


@book_management_router.callback_query(
    F.data.startswith("date_"),
    BookingStates.editing_date
)
async def process_edit_date(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    booking_id = data['current_booking']
    user_id = callback.from_user.id

    # Обновляем данные
    date = callback.data.split("_", 1)[1]
    result = await AppointmentDAO.update_appointment(booking_id=int(booking_id), user_id=user_id, date_time=date)
    if result:
        await callback.answer("Дата выбрана!", show_alert=True)
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


