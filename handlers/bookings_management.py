from __future__ import annotations

from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from states import BookingStates
from utils.storage import user_bookings, BotHolder
from utils import (
    bookings_kb,
    booking_selection_kb,
    edit_booking_kb,
    master_choice_kb, service_choice_kb, dates_kb
)

book_management_router = Router()


async def get_current_booking_data(user_id, state: FSMContext) -> tuple[str, dict]:
    data = await state.get_data()
    return data['current_booking'], user_bookings[user_id][data['current_booking']]


@book_management_router.message(Command("my_bookings"))
@book_management_router.callback_query(F.data == "my_bookings")
async def show_bookings(callback: types.Message | types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    bookings = user_bookings.get(user_id, {})
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

    if isinstance(callback, types.CallbackQuery):
        await callback.message.edit_text("📖 Ваши активные записи:", reply_markup=bookings_kb(bookings))
    else:
        await callback.answer("📖 Ваши активные записи:", reply_markup=bookings_kb(bookings))
    await state.set_state(BookingStates.viewing_bookings)


# Обработчик выбора конкретной записи
@book_management_router.callback_query(F.data.startswith("view_booking_"))
async def handle_booking_selection(callback: types.CallbackQuery, state: FSMContext):

    booking_id = callback.data.split("_")[2]
    user_id = callback.from_user.id

    if user_id not in user_bookings or booking_id not in user_bookings[user_id]:
        await callback.answer("Запись не найдена", show_alert=True)
        return

    booking = user_bookings[user_id][booking_id]
    text = (
        f"👩🎨 Мастер: {booking['master']}\n\n"
        f"💅 Услуга: {booking['service']}\n\n"
        f"📅 Дата: {booking['date']}\n\n"
        f"📝 Пожелания: {booking['wishes']}"
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
    booking_id = callback.data.split("_")[1]
    user_id = callback.from_user.id

    if user_id in user_bookings and booking_id in user_bookings[user_id]:
        del user_bookings[user_id][booking_id]
        await callback.answer("Запись удалена", show_alert=True)
        from handlers.common import back_to_bookings
        await back_to_bookings(callback, state)
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
    master = "Ксения" if "kseniya" in callback.data else "Анастасия"
    user_bookings[user_id][booking_id]['master'] = master

    await callback.answer("Мастер успешно изменён! Теперь выберите услугу", show_alert=True)
    await callback.message.edit_text(
        "Выберите новую услугу:",
        reply_markup=service_choice_kb(callback.data.split("_")[1], True, booking_id)
    )


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
        user_bookings[user_id][booking_id]['service'] = "Классический маникюр"
    elif service == "apparatus":
        user_bookings[user_id][booking_id]['service'] = "Аппаратный маникюр"
    elif service == "manicure":
        user_bookings[user_id][booking_id]['service'] = "Маникюр"
    else:
        user_bookings[user_id][booking_id]['service'] = "Педикюр"

    await callback.answer("Услуга выбрана!", show_alert=True)
    from handlers.common import back_to_bookings
    await back_to_bookings(callback, state)


# Редактирование услуги
@book_management_router.callback_query(F.data.startswith("editingService_"))
async def edit_service_handler(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    booking_id = callback.data.split("_")[1]

    master = "kseniya" if user_bookings[user_id][booking_id]['master'] == "Ксения" else "anastasia"
    await callback.message.edit_text(
        "Выберите новую услугу:",
        reply_markup=service_choice_kb(master, True, booking_id)
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
        user_bookings[user_id][booking_id]['service'] = "Классический маникюр"
    elif service == "apparatus":
        user_bookings[user_id][booking_id]['service'] = "Аппаратный маникюр"
    elif service == "manicure":
        user_bookings[user_id][booking_id]['service'] = "Маникюр"
    else:
        user_bookings[user_id][booking_id]['service'] = "Педикюр"

    await callback.answer("Услуга выбрана!", show_alert=True)
    from handlers.common import back_to_bookings
    await back_to_bookings(callback, state)


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
    user_bookings[user_id][booking_id]['date'] = date

    await callback.answer("Дата выбрана!", show_alert=True)
    from handlers.common import back_to_bookings
    await back_to_bookings(callback, state)


# Редактирование пожеланий
@book_management_router.callback_query(F.data.startswith("editingWishes_"))
async def edit_wishes_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Напишите ваши пожелания:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text="🔙 Назад", callback_data=f"back_to_bookings")]])
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
    user_bookings[user_id][booking_id]["wishes"] = wishes

    await message.answer("Хорошо!", show_alert=True)
    from handlers.common import back_to_bookings
    await back_to_bookings(message, state)