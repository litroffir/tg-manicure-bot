from __future__ import annotations

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from handlers import choose_master, start, choose_service, show_bookings

back_router = Router()


# Обработка кнопок "Назад"
@back_router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    await start(callback, state)


@back_router.callback_query(F.data == "back_to_masters")
async def back_to_masters(callback: types.CallbackQuery, state: FSMContext):
    await choose_master(callback, state)


@back_router.callback_query(F.data == "back_to_services")
async def back_to_services(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await choose_service(callback, state)


@back_router.callback_query(F.data == "back_to_bookings")
async def back_to_bookings(callback: types.Message | types.CallbackQuery, state: FSMContext):
    await show_bookings(callback, state)