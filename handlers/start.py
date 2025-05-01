from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from utils.keyboards import main_menu_kb
from utils.inactivity import reset_inactivity_timer

start_router = Router()


@start_router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await show_main_menu(message)


async def show_main_menu(message: types.Message):
    await message.answer(
        "🌸 *Добро пожаловать в Beauty Bits!* 🌸\n\n"
        "🎀 *Акция:* Первый визит со скидкой 15%!\n\n"
        "Выберите действие:",
        reply_markup=main_menu_kb(),
        parse_mode="Markdown"
    )