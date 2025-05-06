from __future__ import annotations

from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from models import User
from utils import async_session
from utils.keyboards import main_menu_kb

start_router = Router()


@start_router.message(Command("start"))
async def start(callback: types.Message | types.CallbackQuery, state: FSMContext):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.id == callback.from_user.id)
        )
        user = result.scalar_one_or_none()

        if not user:
            new_user = User(
                id=callback.from_user.id,
                username=callback.from_user.username,
                full_name=callback.from_user.full_name
            )
            session.add(new_user)
            await session.commit()
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