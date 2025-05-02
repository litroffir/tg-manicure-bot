from __future__ import annotations

from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from utils.keyboards import main_menu_kb

start_router = Router()


@start_router.message(Command("start"))
async def start(callback: types.Message | types.CallbackQuery, state: FSMContext):
    await state.clear()
    if isinstance(callback, types.CallbackQuery):
        await callback.message.edit_text(
            text="🌸 *Добро пожаловать в Beauty Bits!* 🌸\n\n"
                 "🎀 *Акция:* Первый визит со скидкой 15%!\n\n"
                 "Выберите действие:",
            reply_markup=main_menu_kb(),
            parse_mode="Markdown"
        )
    else:
        await callback.answer(
            text="🌸 *Добро пожаловать в Beauty Bits!* 🌸\n\n"
                 "🎀 *Акция:* Первый визит со скидкой 15%!\n\n"
                 "Выберите действие:",
            reply_markup=main_menu_kb(),
            parse_mode="Markdown"
        )