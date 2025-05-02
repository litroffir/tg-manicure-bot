import logging
from datetime import datetime, timedelta

from telegram import (
    BotCommand,
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove
)

from telegram.ext import (
    Application,
    ContextTypes,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
    ConversationHandler,
)

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния разговора
SELECTING_ACTION, CHOOSING_MASTER, CHOOSING_SERVICE, CHOOSING_DATE, ENTERING_WISHES = map(chr, range(5))
END = ConversationHandler.END

# Данные пользователей (временное хранилище)
users_data = {}


# Доступные даты
def generate_dates():
    return [
        (datetime.now() + timedelta(days=i)).strftime("%d.%m %H:%M")
        for i in range(1, 8)
    ]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    keyboard = [
        [
            InlineKeyboardButton("💅 Записаться", callback_data=str(CHOOSING_MASTER)),
            # InlineKeyboardButton("📝 Мои записи", callback_data="my_bookings")
        ],
    ]

    if update.message:
        await update.message.reply_text(
            "🌸 *Добро пожаловать в Beauty Bits!* 🌸\n\n"
            "🎀 *Акция:* Первый визит со скидкой 15%!\n\n"
            "Выберите действие:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    else:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "🌸 *Добро пожаловать в Beauty Bits!* 🌸\n\n"
            "🎀 *Акция:* Первый визит со скидкой 15%!\n\n"
            "Выберите действие:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    return SELECTING_ACTION


async def choose_master(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = context._user_id
    if user not in users_data:
        users_data[user] = {}

    keyboard = [
        [InlineKeyboardButton("Ксения 💅", callback_data="Ксения")],
        [InlineKeyboardButton("Анастасия 👑", callback_data="Анастасия")],
        [InlineKeyboardButton("🔙 Назад в меню", callback_data=str(END))]
    ]

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text="Выберите мастера:", reply_markup=InlineKeyboardMarkup(keyboard))

    return CHOOSING_MASTER


async def choose_service(update: Update, context: CallbackContext) -> int:
    # master = update.callback_query.data
    # master = update.message.text
    # context.user_data['master'] = master
    query = update.callback_query
    await query.answer()
    master = query.data  # Получаем callback_data из нажатой кнопки
    context.user_data['master'] = master
    if master == "Ксения":
        services = [
            [InlineKeyboardButton("Классический маникюр 💅", callback_data="service_1")],
            [InlineKeyboardButton("Аппаратный маникюр 🔧", callback_data="service_2")],
            [InlineKeyboardButton("🔙 Назад к мастерам", callback_data=str(CHOOSING_MASTER))]
        ]
    else:
        services = [
            [InlineKeyboardButton("Маникюр 💅", callback_data="service_3")],
            [InlineKeyboardButton("Педикюр 👣", callback_data="service_4")],
            [InlineKeyboardButton("🔙 Назад к мастерам", callback_data=str(CHOOSING_MASTER))]
        ]

    await query.edit_message_text(
        text="Выберите услугу:",
        reply_markup=InlineKeyboardMarkup(services)
    )
    return CHOOSING_SERVICE
    # if "Ксения" in master:
    #     services = [
    #         [InlineKeyboardButton("Классический маникюр 💅")],
    #         [InlineKeyboardButton("Аппаратный маникюр 🔧")],
    #         [InlineKeyboardButton("🔙 Назад к мастерам")]
    #     ]
    # else:
    #     services = [
    #         [InlineKeyboardButton("Маникюр 💅")],
    #         [InlineKeyboardButton("Педикюр 👣")],
    #         [InlineKeyboardButton("🔙 Назад к мастерам")]
    #     ]
    #
    # await update.message.reply_text(
    #     "Выберите услугу:",
    #     reply_markup=InlineKeyboardMarkup(services),
    # )
    #
    # return CHOOSING_SERVICE


async def choose_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    service = update.message.text
    users_data[context._user_id]["service"] = service

    dates = generate_dates()
    keyboard = [[InlineKeyboardButton(date, callback_data=f"date_{date}")] for date in dates] \
               + [[InlineKeyboardButton("🔙 Назад к услугам", callback_data="back_to_services")]]

    await update.message.reply_text(
        f"Выбрана услуга: {service}\nВыберите дату:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return CHOOSING_DATE


async def enter_wishes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора даты"""
    query = update.callback_query
    await query.answer()

    date = query.data.split('_')[1]
    users_data[context._user_id]['date'] = date

    # Убираем инлайн-кнопки
    await query.edit_message_reply_markup(reply_markup=None)

    await query.message.reply_text(
        f"Выбрана дата: {date}\nНапишите ваши пожелания (или нажмите 'Пропустить'):",
        reply_markup=ReplyKeyboardMarkup([
            ["Пропустить"],
            ["🔙 Назад к датам"]
        ], resize_keyboard=True)
    )
    return ENTERING_WISHES


async def confirm_booking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    wishes = "не указаны" if update.message.text == "Пропустить" else update.message.text
    users_data[context._user_id]['wishes'] = wishes

    booking = users_data[context._user_id]
    text = (
        "✨ *Запись подтверждена!* ✨\n\n"
        f"👩‍🎨 Мастер: {booking['master']}\n"
        f"💅 Услуга: {booking['service']}\n"
        f"📅 Дата: {booking['date']}\n"
        f"📝 Пожелания: {wishes}"
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown"
    )
    await start(update, context)
    return ConversationHandler.END


async def set_commands(app: Application):
    commands = [
        BotCommand("start", "Главное меню"),
        BotCommand("new_booking", "Запись на маникюр"),
        BotCommand("my_bookings", "Мои записи"),
        BotCommand("masters", "Список мастеров")
    ]
    await app.bot.set_my_commands(commands)


async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат в главное меню"""
    await update.message.reply_text(
        "Возвращение в главное меню",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    await start(update, context)
    return ConversationHandler.END


def main():
    app = Application.builder().token("7874319913:AAENKsWWF2xGSUd94dHIGiObAkAJE_CuAAs").post_init(set_commands).build()

    # Главное меню
    app.add_handler(CommandHandler('start', start))

    booking_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                choose_master, pattern=f"^{str(CHOOSING_MASTER)}$"
            )
        ],
        states={
            CHOOSING_MASTER: [
                CallbackQueryHandler(choose_service, pattern="^(Ксения|Анастасия)$")
            ],
            CHOOSING_SERVICE: [CallbackQueryHandler(choose_date, pattern="^service_")],
            CHOOSING_DATE: [
                CallbackQueryHandler(enter_wishes, pattern="^" + str(ENTERING_WISHES) + "$")
            ],
            # ENTERING_WISHES: [
            #     CallbackQueryHandler(enter_wishes, pattern="^" + str(ENTERING_WISHES) + "$")
            # ]
        },
        fallbacks=[
            CallbackQueryHandler(back_to_menu, pattern="^" + str(END) + "$"),
        ],
        map_to_parent={
            # Return to second level menu
            END: SELECTING_ACTION,
        },
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            # SHOWING: [CallbackQueryHandler(start, pattern="^" + str(END) + "$")],
            SELECTING_ACTION: [booking_conv],
            # SELECTING_LEVEL: selection_handlers,
            # DESCRIBING_SELF: [description_conv],
            # STOPPING: [CommandHandler("start", start)],
        },
        fallbacks=[CommandHandler("stop", back_to_menu)],
    )

    app.add_handler(conv_handler)

    app.run_polling()


if __name__ == '__main__':
    main()