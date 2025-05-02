import logging
from datetime import datetime, timedelta

from telegram import (
    BotCommand,
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove
)

from telegram.ext import (
    Application,
    filters,
    ContextTypes,
    CommandHandler,
    MessageHandler,
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


# Доступные даты (пример)


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


# async def book_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Обработка кнопки 'Записаться' - отправка команды /new_booking"""
#     query = update.callback_query
#     await query.answer()
#
#     # Создаем новый контекст для обработки команды
#     new_context = context.__class__(context.application)
#     new_context._chat_id = query.message.chat_id
#     new_context._user_id = query.from_user.id
#     new_context.user_data = context.user_data
#
#     # Вызываем обработчик команды напрямую
#     return await start_booking(update, new_context)
#     # query = update.callback_query
#     # await query.answer()
#     #
#     # await context.bot.send_message(
#     #     chat_id=query.message.chat_id,
#     #     text="/new\\_booking",
#     #     parse_mode="Markdown"
#     # )


async def choose_master(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = context._user_id
    if user not in users_data:
        users_data[user] = {}

    keyboard = [
        [InlineKeyboardButton("Ксения 💅")],
        [InlineKeyboardButton("Анастасия 👑")],
        [InlineKeyboardButton("🔙 Назад в меню", callback_data=str(END))]
    ]

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text="Выберите мастера:", reply_markup=InlineKeyboardMarkup(keyboard))

    return CHOOSING_MASTER


async def choose_service(update: Update, context: CallbackContext) -> int:
    master = update.callback_query.data
    print(master)
    # master = update.message.text
    # context.user_data['master'] = master

    if "Ксения" in master:
        services = [
            [InlineKeyboardButton("Классический маникюр 💅")],
            [InlineKeyboardButton("Аппаратный маникюр 🔧")],
            [InlineKeyboardButton("🔙 Назад к мастерам")]
        ]
    else:
        services = [
            [InlineKeyboardButton("Маникюр 💅")],
            [InlineKeyboardButton("Педикюр 👣")],
            [InlineKeyboardButton("🔙 Назад к мастерам")]
        ]

    await update.message.reply_text(
        "Выберите услугу:",
        reply_markup=InlineKeyboardMarkup(services),
    )

    return CHOOSING_SERVICE


async def choose_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # await update.callback_query.message.edit_reply_markup(None)

    # if update.callback_query:
    #     query = update.callback_query
    #     await query.answer()
    #     service = query.data.split('_')[1]
    #     chat_id = query.message.chat_id
    # else:
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


# async def confirm_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     await query.answer()
#
#     user = query.from_user
#     wishes = "не указаны" if update.message.text == "Пропустить" else update.message.text
#     users_data[user.id]['wishes'] = wishes
#
#     booking = users_data[user.id]
#     text = (
#         "✨ *Запись подтверждена!* ✨\n\n"
#         f"👩‍🎨 *Мастер:* {booking['master']}\n"
#         f"💅 *Услуга:* {booking['service']}\n"
#         f"📅 *Дата:* {booking['date']}\n"
#         f"📝 *Пожелания:* {wishes}\n\n"
#         "Ждем вас в нашем салоне!"
#     )
#
#     await update.message.reply_text(
#         text,
#         reply_markup=ReplyKeyboardRemove(),
#         parse_mode="Markdown"
#     )
#     await start(update, context)
#     return ConversationHandler.END


async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    return await choose_service(update, context)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    del users_data[user.id]

    await update.message.reply_text(
        'До скорой встречи! 💌',
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


async def set_commands(app: Application):
    commands = [
        BotCommand("start", "Главное меню"),
        BotCommand("new_booking", "Запись на маникюр"),
        BotCommand("my_bookings", "Мои записи"),
        BotCommand("masters", "Список мастеров")
    ]
    await app.bot.set_my_commands(commands)


async def back_to_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат к выбору услуги"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)

    master = context.user_data.get('master', '')

    if "Ксения" in master:
        services = [
            ["Классический маникюр 💅"],
            ["Аппаратный маникюр 🔧"]
        ]
    else:
        services = [
            ["Маникюр 💅"],
            ["Педикюр 👣"],
            ["Комбо 💎"]
        ]

    services.append(["🔙 Назад к мастерам"])

    await query.message.reply_text(
        "Выберите услугу:",
        reply_markup=ReplyKeyboardMarkup(services, resize_keyboard=True)
    )
    return CHOOSING_SERVICE


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
    app = Application.builder().token("7874319913:AAGJMeykamMTJ_GyP4P-f2S-ypS3XPCqVMU").post_init(set_commands).build()

    # Главное меню
    app.add_handler(CommandHandler('start', start))

    booking_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                choose_master, pattern="^" + str(CHOOSING_MASTER) + "$"
            )
        ],
        states={
            CHOOSING_MASTER: [
                CallbackQueryHandler(choose_service, pattern="^" + str(CHOOSING_SERVICE) + "$")
            ],
            CHOOSING_SERVICE: [CallbackQueryHandler(choose_date, pattern="^" + str(CHOOSING_DATE) + "$")],
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

    # Set up second level ConversationHandler (adding a person)

    # Set up top level ConversationHandler (selecting action)
    # Because the states of the third level conversation map to the ones of the second level
    # conversation, we need to make sure the top level conversation can also handle them
    # selection_handlers = [
    #     add_member_conv,
    #     CallbackQueryHandler(show_data, pattern="^" + str(SHOWING) + "$"),
    #     CallbackQueryHandler(adding_self, pattern="^" + str(ADDING_SELF) + "$"),
    #     CallbackQueryHandler(end, pattern="^" + str(END) + "$"),
    # ]
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
    # app.add_handler(CallbackQueryHandler(book_now, pattern="^book_now$"))
    # app.add_handler(CallbackQueryHandler(start, pattern="^back_to_menu$"))

    # Просмотр записей
    # app.add_handler(CallbackQueryHandler(show_bookings, pattern="^my_bookings$"))

    # Процесс записи
    # conv_handler = ConversationHandler(
    #     entry_points=[
    #         CommandHandler("new_booking", start_booking)
    #     ],
    #     states={
    #         CHOOSING_MASTER: [
    #             MessageHandler(filters.Regex(r'^(Ксения|Анастасия)'), choose_master),
    #             MessageHandler(filters.Regex(r'^🔙 Назад в меню$'), back_to_menu)
    #         ],
    #         CHOOSING_SERVICE: [
    #             MessageHandler(filters.Regex(r'^(Классический|Аппаратный|Маникюр|Педикюр|Комбо)'), choose_service),
    #             MessageHandler(filters.Regex(r'^🔙 Назад к мастерам$'), back_to_masters)
    #         ],
    #         CHOOSING_DATE: [
    #             CallbackQueryHandler(handle_date_selection, pattern="^date_"),
    #             CallbackQueryHandler(back_to_services, pattern="^back_to_services$")
    #         ],
    #         ENTERING_WISHES: [
    #             MessageHandler(filters.TEXT & ~filters.COMMAND, enter_wishes),
    #             MessageHandler(filters.Regex(r'^🔙 Назад к датам$'), back_to_dates)
    #         ]
    #     },
    #     fallbacks=[
    #         CommandHandler("start", back_to_menu),
    #         CallbackQueryHandler(back_to_menu, pattern="^back_to_menu$")
    #     ],
    #     allow_reentry=True
    # )
    # conv_handler = ConversationHandler(
    #     entry_points=[CommandHandler("book", start_booking),
    #                   CallbackQueryHandler(start_booking, pattern="^book$")
    #                   ],
    #     states={
    #         CHOOSING_MASTER: [
    #             MessageHandler(
    #                 filters.Regex(r'^(Ксения|Анастасия)'),
    #                 choose_master
    #             ),
    #             MessageHandler(
    #                 filters.Regex(r'^🔙 Назад в меню$'),
    #                 back_to_menu
    #             )
    #         ],
    #         CHOOSING_SERVICE: [
    #             # CallbackQueryHandler(choose_date, pattern="^choose_date$"),
    #             CallbackQueryHandler(choose_service, pattern="^book$"),
    #             MessageHandler(
    #                 filters.Regex(r'^(Классический|Аппаратный|Маникюр|Педикюр|Комбо)'),
    #                 choose_service
    #             ),
    #             # CallbackQueryHandler(choose_date, pattern="^choose_date$"),
    #             CallbackQueryHandler(back_to_masters, pattern="^back_to_masters$"),
    #             MessageHandler(
    #                 filters.Regex(r'^🔙 Назад к мастерам$'),
    #                 back_to_masters
    #             )
    #         ],
    #         CHOOSING_DATE: [
    #             MessageHandler(
    #                 filters.Regex(r'^Пожелания'),
    #                 handle_date_selection
    #             ),
    #             MessageHandler(
    #                 filters.Regex(r'^🔙 Назад к датам$'),
    #                 back_to_dates
    #             )
    #         ],
    #         ENTERING_WISHES: [
    #             MessageHandler(filters.TEXT & ~filters.COMMAND, enter_wishes),
    #         ]
    #     },
    #     conversation_timeout=300,
    #     fallbacks=[CommandHandler('start', start),
    #                CallbackQueryHandler(back_to_menu, pattern="^back_to_menu$")]
    # )
    # app.add_handler(conv_handler)
    # app.add_handler(CallbackQueryHandler(start, pattern="^back_to_menu$"))

    # Другие кнопки меню
    # app.add_handler(CallbackQueryHandler(handle_back, pattern="^back_to_"))

    app.run_polling()


if __name__ == '__main__':
    main()


async def back_to_masters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат к выбору мастера"""
    query = update.callback_query
    if query:
        await query.answer()

    # Очищаем выбранную услугу
    if 'service' in context.user_data:
        del context.user_data['service']

    keyboard = [
        [InlineKeyboardButton("Ксения 💅"), InlineKeyboardButton("Анастасия 👑")],
        [InlineKeyboardButton("🔙 Назад в меню")]
    ]

    if query:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Выберите мастера:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            "Выберите мастера:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    return CHOOSING_MASTER


# async def back_to_dates(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Возврат к выбору услуги"""
#     return await handle_date_selection(update, context)