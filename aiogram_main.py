from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove, BotCommand

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

bot = Bot(token="7874319913:AAGJMeykamMTJ_GyP4P-f2S-ypS3XPCqVMU")
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# Состояния FSM
class BookingStates(StatesGroup):
    choosing_action = State()
    choosing_master = State()
    choosing_service = State()
    choosing_date = State()
    entering_wishes = State()
    viewing_bookings = State()
    editing_booking = State()
    deleting_booking = State()


user_bookings = {}


# Генерация дат
def generate_dates():
    return [
        (datetime.now() + timedelta(days=i)).strftime("%d.%m %H:%M")
        for i in range(1, 8)
    ]


async def check_inactivity(state: FSMContext):
    data = await state.get_data()
    last_activity = data.get('last_activity')
    if last_activity and (datetime.now() - last_activity).seconds > 5:
        await state.clear()
        return True
    return False


# Храним время последней активности
async def update_last_activity(state: FSMContext):
    await state.update_data(last_activity=datetime.now())


async def reset_inactivity_timer(state: FSMContext):
    await update_last_activity(state)
    asyncio.create_task(inactivity_checker(state))


async def inactivity_checker(state: FSMContext):
    await asyncio.sleep(5)  # 5 минут
    if await check_inactivity(state):
        pass
        # Можно добавить отправку уведомления пользователю
        # return


@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await show_main_menu(message)
    # await state.set_state(BookingStates.choosing_action)
    await reset_inactivity_timer(state)


async def show_main_menu(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="💅 Записаться", callback_data="book")],
        [types.InlineKeyboardButton(text="📝 Мои записи", callback_data="my_bookings")]
    ])
    await message.answer(
        "🌸 *Добро пожаловать в Beauty Bits!* 🌸\n\n"
        "🎀 *Акция:* Первый визит со скидкой 15%!\n\n"
        "Выберите действие:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


# Обработка кнопки "💅 Записаться"
@dp.callback_query(F.data == "book")
async def choose_master(callback: types.Message | types.CallbackQuery, state: FSMContext):
    if await check_inactivity(state):
        await callback.answer("Сессия истекла, начните заново, написав /start", show_alert=True)
        await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
        return

    await reset_inactivity_timer(state)
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Ксения 💅", callback_data="master_kseniya")],
        [types.InlineKeyboardButton(text="Анастасия 👑", callback_data="master_anastasia")],
        [types.InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
    ])
    if isinstance(callback, types.CallbackQuery):
        await callback.message.edit_text("Выберите мастера:", reply_markup=keyboard)
    else:
        await callback.answer("Выберите мастера:", reply_markup=keyboard)
    await state.set_state(BookingStates.choosing_master)


@dp.message(Command("book"))
async def start_booking_command(message: types.Message, state: FSMContext):
    # Проверяем истекла ли сессия
    if await check_inactivity(state):
        await message.answer("Сессия истекла, начните заново, написав /start", show_alert=True)
        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message.message_id)
        await state.clear()

    # Сбрасываем таймер и начинаем процесс
    await reset_inactivity_timer(state)
    await choose_master(message, state)


# Выбор услуги
@dp.callback_query(F.data.startswith("master_"))
async def choose_service(callback: types.CallbackQuery, state: FSMContext):
    if await check_inactivity(state):
        await callback.answer("Сессия истекла, начните заново, написав /start", show_alert=True)
        await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
        return

    await reset_inactivity_timer(state)

    master = callback.data.split("_")[1]
    await state.update_data(master="Ксения" if master == "master_kseniya" else "Анастасия")

    if master == "kseniya":
        services = [
            ["Классический маникюр 💅", "service_classic"],
            ["Аппаратный маникюр 🔧", "service_apparatus"]
        ]
    else:
        services = [
            ["Маникюр 💅", "service_manicure"],
            ["Педикюр 👣", "service_pedicure"]
        ]

    buttons = [
        [types.InlineKeyboardButton(text=text, callback_data=data)]
        for text, data in services
    ]
    buttons.append([types.InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_masters")])

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.edit_text(
        "Выберите услугу:",
        reply_markup=keyboard
    )
    await state.set_state(BookingStates.choosing_service)


# Выбор даты
@dp.callback_query(F.data.startswith("service_"))
async def choose_date(callback: types.CallbackQuery, state: FSMContext):
    if await check_inactivity(state):
        await callback.answer("Сессия истекла, начните заново, написав /start", show_alert=True)
        await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
        return

    await reset_inactivity_timer(state)

    service = callback.data.split("_")[1]
    if service == "classic":
        await state.update_data(service="Классический маникюр")
    elif service == "apparatus":
        await state.update_data(service="Аппаратный маникюр")
    elif service == "manicure":
        await state.update_data(service="Маникюр")
    else:
        await state.update_data(service="Педикюр")

    dates = generate_dates()
    buttons = [
        [types.InlineKeyboardButton(text=date, callback_data=f"date_{date}")]
        for date in dates
    ]
    buttons.append([types.InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_services")])

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.edit_text(
        f"Выберите дату:",
        reply_markup=keyboard
    )
    await state.set_state(BookingStates.choosing_date)


# Ввод пожеланий
@dp.callback_query(F.data.startswith("date_"))
async def enter_wishes(callback: types.CallbackQuery, state: FSMContext):
    if await check_inactivity(state):
        await callback.answer("Сессия истекла, начните заново, написав /start", show_alert=True)
        await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
        return

    await reset_inactivity_timer(state)

    date = callback.data.split("_", 1)[1]
    await state.update_data(date=date)

    await callback.message.edit_text(
        f"Выбрана дата: {date}\nНапишите ваши пожелания:"
    )
    await callback.message.answer(
        "Или нажмите 'Пропустить'",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text="Пропустить")]],
            resize_keyboard=True
        )
    )
    await state.set_state(BookingStates.entering_wishes)


# Подтверждение записи
@dp.message(BookingStates.entering_wishes)
async def confirm_booking(message: types.Message, state: FSMContext):
    data = await state.get_data()
    wishes = "не указаны" if message.text == "Пропустить" else message.text

    # Сохраняем запись
    booking_id = datetime.now().strftime("%Y%m%d%H%M%S")
    user_id = message.from_user.id
    if user_id not in user_bookings:
        user_bookings[user_id] = {}

    user_bookings[user_id][booking_id] = {
        "master": data['master'],
        "service": data['service'],
        "date": data['date'],
        "wishes": wishes
    }

    text = (
        "✨ *Запись подтверждена!* ✨\n\n"
        f"👩🎨 Мастер: {data['master']}\n\n"
        f"💅 Услуга: {data['service']}\n\n"
        f"📅 Дата: {data['date']}\n\n"
        f"📝 Пожелания: {wishes}"
    )

    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()
    await start(message, state)


@dp.message(Command("my_bookings"))
@dp.callback_query(F.data == "my_bookings")
async def show_bookings(message_or_query: types.Message | types.CallbackQuery, state: FSMContext):
    user_id = message_or_query.from_user.id
    if isinstance(message_or_query, types.CallbackQuery):
        message = message_or_query.message
        await message_or_query.answer()
    else:
        message = message_or_query

    if user_id not in user_bookings or not user_bookings[user_id]:
        await message.answer("📭 У вас пока нет активных записей")
        return

    await state.set_state(BookingStates.viewing_bookings)
    await show_bookings_list(message, user_id)


async def show_bookings_list(message: types.Message, user_id: int):
    bookings = user_bookings.get(user_id, {})
    if not bookings:
        await message.answer("📭 У вас пока нет активных записей")
        return

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[])
    for booking_id, booking in bookings.items():
        text = f"{booking['date']} - {booking['service']} ({booking['master']})"
        keyboard.inline_keyboard.append([
            types.InlineKeyboardButton(
                text=text,
                callback_data=f"view_booking_{booking_id}"
            )
        ])

    keyboard.inline_keyboard.append([types.InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")])

    await message.answer(
        "📖 Ваши активные записи:",
        reply_markup=keyboard
    )


# Обработчик выбора конкретной записи
@dp.callback_query(F.data.startswith("view_booking_"))
async def handle_booking_selection(callback: types.CallbackQuery, state: FSMContext):
    booking_id = callback.data.split("_")[2]
    user_id = callback.from_user.id

    if user_id not in user_bookings or booking_id not in user_bookings[user_id]:
        await callback.answer("Запись не найдена", show_alert=True)
        return

    booking = user_bookings[user_id][booking_id]
    text = (
        f"👩🎨 Мастер: {booking['master']}\n"
        f"💅 Услуга: {booking['service']}\n"
        f"📅 Дата: {booking['date']}\n"
        f"📝 Пожелания: {booking['wishes']}"
    )

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_{booking_id}"),
            types.InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_{booking_id}")
        ],
        [types.InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_bookings")]
    ])

    await callback.message.edit_text(
        f"📄 Детали записи:\n\n{text}",
        reply_markup=keyboard
    )


# Обработчики действий с записями
@dp.callback_query(F.data.startswith("edit_"))
async def edit_booking(callback: types.CallbackQuery, state: FSMContext):
    booking_id = callback.data.split("_")[1]
    user_id = callback.from_user.id

    await state.update_data(current_booking=booking_id)
    await state.set_state(BookingStates.editing_booking)
    await callback.message.answer("Выберите что хотите изменить:",
                                  reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                      [types.InlineKeyboardButton(text="Мастера", callback_data="edit_master")],
                                      [types.InlineKeyboardButton(text="Услугу", callback_data="edit_service")],
                                      [types.InlineKeyboardButton(text="Дату", callback_data="edit_date")],
                                      [types.InlineKeyboardButton(text="Пожелания", callback_data="edit_wishes")],
                                      [types.InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_booking")]
                                  ]))


@dp.callback_query(F.data.startswith("delete_"))
async def delete_booking(callback: types.CallbackQuery):
    booking_id = callback.data.split("_")[1]
    user_id = callback.from_user.id

    if user_id in user_bookings and booking_id in user_bookings[user_id]:
        del user_bookings[user_id][booking_id]
        await callback.answer("Запись удалена", show_alert=True)
        await show_bookings_list(callback.message, user_id)
    else:
        await callback.answer("Ошибка удаления", show_alert=True)


# Обработка кнопок "Назад"
@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    if await check_inactivity(state):
        await callback.answer("Сессия истекла, начните заново, написав /start", show_alert=True)
        await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
        return
    else:
        await reset_inactivity_timer(state)
        await start(callback.message, state)


@dp.callback_query(F.data == "back_to_masters")
async def back_to_masters(callback: types.CallbackQuery, state: FSMContext):
    if await check_inactivity(state):
        await callback.answer("Сессия истекла, начните заново, написав /start", show_alert=True)
        await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
        return
    else:
        await reset_inactivity_timer(state)
        await choose_master(callback, state)


@dp.callback_query(F.data == "back_to_services")
async def back_to_services(callback: types.CallbackQuery, state: FSMContext):
    if await check_inactivity(state):
        await callback.answer("Сессия истекла, начните заново, написав /start", show_alert=True)
        await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
        return
    else:
        await reset_inactivity_timer(state)
        data = await state.get_data()
        await choose_service(callback, state)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="book", description="Запись на маникюр"),
        BotCommand(command="my_bookings", description="Мои записи"),
        BotCommand(command="masters", description="Список мастеров")
    ]
    await bot.set_my_commands(commands)


async def on_shutdown(dp):
    await storage.close()

if __name__ == '__main__':
    # Установка команд при старте бота
    dp.startup.register(set_commands)
    dp.run_polling(bot)