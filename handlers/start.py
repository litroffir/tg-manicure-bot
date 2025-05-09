from __future__ import annotations

from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from config_reader import config
from models import User
from utils import async_session
from utils.keyboards import main_menu_kb

start_router = Router()


@start_router.message(Command("start"))
@start_router.callback_query(F.data == "start")
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
            reply_markup=main_menu_kb(is_admin=callback.from_user.id == config.telegram.admin_id),
            parse_mode="Markdown"
        )
    else:
        await callback.answer(
            text="🌸 *Добро пожаловать в Beauty Bits!* 🌸\n\n"
                 "🎀 *Акция:* Первый визит со скидкой 15%!\n\n"
                 "Выберите действие:",
            reply_markup=main_menu_kb(is_admin=callback.from_user.id == config.telegram.admin_id),
            parse_mode="Markdown"
        )
