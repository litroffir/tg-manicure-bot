from __future__ import annotations

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

master_router = Router()

MASTERS_INFO = """
🌟 *Наши мастера* 🌟

\U0001F487 *Ксения* 
- Опыт работы: 5 лет
- Специализация: 
  • Классический маникюр
  • Аппаратный маникюр
  • Наращивание ногтей

\U0001F487 *Анастасия* 
- Опыт работы: 3 года
- Специализация:
  • Дизайн ногтей
  • SPA-уходы
  • Покрытие гель-лаком
"""


@master_router.message(Command("masters"))
@master_router.callback_query(F.data == "masters")
async def masters_command(callback: types.Message | types.CallbackQuery):
    if isinstance(callback, types.CallbackQuery):
        await callback.message.edit_text(
            MASTERS_INFO,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data=f"start")]
            ])
        )
    else:
        await callback.answer(
            MASTERS_INFO,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data=f"start")]
            ])
        )

