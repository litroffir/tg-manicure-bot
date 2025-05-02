# import logging
# from typing import Any, Dict, Tuple
#
# from telegram import __version__ as TG_VER
#
# try:
#     from telegram import __version_info__
# except ImportError:
#     __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]
#
# if __version_info__ < (20, 0, 0, "alpha", 1):
#     raise RuntimeError(
#         f"This example is not compatible with your current PTB version {TG_VER}. To view the "
#         f"{TG_VER} version of this example, "
#         f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
#     )
# from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
# from telegram.ext import (
#     Application,
#     CallbackQueryHandler,
#     CommandHandler,
#     ContextTypes,
#     ConversationHandler,
#     MessageHandler,
#     filters,
# )
#
# # Enable logging
# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
# )
# logger = logging.getLogger(__name__)
#
# # State definitions for top level conversation
# SELECTING_ACTION, ADDING_MEMBER, ADDING_SELF, DESCRIBING_SELF = map(chr, range(4))
# # State definitions for second level conversation
# SELECTING_LEVEL, SELECTING_GENDER = map(chr, range(4, 6))
# # State definitions for descriptions conversation
# SELECTING_FEATURE, TYPING = map(chr, range(6, 8))
# # Meta states
# STOPPING, SHOWING = map(chr, range(8, 10))
# # Shortcut for ConversationHandler.END
# END = ConversationHandler.END
#
# # Different constants for this example
# (
#     PARENTS,
#     CHILDREN,
#     SELF,
#     GENDER,
#     MALE,
#     FEMALE,
#     AGE,
#     NAME,
#     START_OVER,
#     FEATURES,
#     CURRENT_FEATURE,
#     CURRENT_LEVEL,
# ) = map(chr, range(10, 22))
#
#
# # Helper
# def _name_switcher(level: str) -> Tuple[str, str]:
#     if level == PARENTS:
#         return "Father", "Mother"
#     return "Brother", "Sister"
#
#
# # Top level conversation callbacks
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
#     """Select an action: Adding parent/child or show data."""
#     text = (
#         "You may choose to add a family member, yourself, show the gathered data, or end the "
#         "conversation. To abort, simply type /stop."
#     )
#
#     buttons = [
#         [
#             InlineKeyboardButton(text="Add family member", callback_data=str(ADDING_MEMBER)),
#             InlineKeyboardButton(text="Add yourself", callback_data=str(ADDING_SELF)),
#         ],
#         [
#             InlineKeyboardButton(text="Show data", callback_data=str(SHOWING)),
#             InlineKeyboardButton(text="Done", callback_data=str(END)),
#         ],
#     ]
#     keyboard = InlineKeyboardMarkup(buttons)
#
#     # If we're starting over we don't need to send a new message
#     if context.user_data.get(START_OVER):
#         await update.callback_query.answer()
#         await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
#     else:
#         await update.message.reply_text(
#             "Hi, I'm Family Bot and I'm here to help you gather information about your family."
#         )
#         await update.message.reply_text(text=text, reply_markup=keyboard)
#
#     context.user_data[START_OVER] = False
#     return SELECTING_ACTION
#
#
# async def adding_self(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
#     """Add information about yourself."""
#     context.user_data[CURRENT_LEVEL] = SELF
#     text = "Okay, please tell me about yourself."
#     button = InlineKeyboardButton(text="Add info", callback_data=str(MALE))
#     keyboard = InlineKeyboardMarkup.from_button(button)
#
#     await update.callback_query.answer()
#     await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
#
#     return DESCRIBING_SELF
#
#
# async def show_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
#     """Pretty print gathered data."""
#
#     def pretty_print(data: Dict[str, Any], level: str) -> str:
#         people = data.get(level)
#         if not people:
#             return "\nNo information yet."
#
#         return_str = ""
#         if level == SELF:
#             for person in data[level]:
#                 return_str += f"\nName: {person.get(NAME, '-')}, Age: {person.get(AGE, '-')}"
#         else:
#             male, female = _name_switcher(level)
#
#             for person in data[level]:
#                 gender = female if person[GENDER] == FEMALE else male
#                 return_str += (
#                     f"\n{gender}: Name: {person.get(NAME, '-')}, Age: {person.get(AGE, '-')}"
#                 )
#         return return_str
#
#     user_data = context.user_data
#     text = f"Yourself:{pretty_print(user_data, SELF)}"
#     text += f"\n\nParents:{pretty_print(user_data, PARENTS)}"
#     text += f"\n\nChildren:{pretty_print(user_data, CHILDREN)}"
#
#     buttons = [[InlineKeyboardButton(text="Back", callback_data=str(END))]]
#     keyboard = InlineKeyboardMarkup(buttons)
#
#     await update.callback_query.answer()
#     await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
#     user_data[START_OVER] = True
#
#     return SHOWING
#
#
# async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """End Conversation by command."""
#     await update.message.reply_text("Okay, bye.")
#
#     return END
#
#
# async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """End conversation from InlineKeyboardButton."""
#     await update.callback_query.answer()
#
#     text = "See you around!"
#     await update.callback_query.edit_message_text(text=text)
#
#     return END
#
#
# # Second level conversation callbacks
# async def select_level(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
#     """Choose to add a parent or a child."""
#     text = "You may add a parent or a child. Also you can show the gathered data or go back."
#     buttons = [
#         [
#             InlineKeyboardButton(text="Add parent", callback_data=str(PARENTS)),
#             InlineKeyboardButton(text="Add child", callback_data=str(CHILDREN)),
#         ],
#         [
#             InlineKeyboardButton(text="Show data", callback_data=str(SHOWING)),
#             InlineKeyboardButton(text="Back", callback_data=str(END)),
#         ],
#     ]
#     keyboard = InlineKeyboardMarkup(buttons)
#
#     await update.callback_query.answer()
#     await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
#
#     return SELECTING_LEVEL
#
#
# async def select_gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
#     """Choose to add mother or father."""
#     level = update.callback_query.data
#     context.user_data[CURRENT_LEVEL] = level
#
#     text = "Please choose, whom to add."
#
#     male, female = _name_switcher(level)
#
#     buttons = [
#         [
#             InlineKeyboardButton(text=f"Add {male}", callback_data=str(MALE)),
#             InlineKeyboardButton(text=f"Add {female}", callback_data=str(FEMALE)),
#         ],
#         [
#             InlineKeyboardButton(text="Show data", callback_data=str(SHOWING)),
#             InlineKeyboardButton(text="Back", callback_data=str(END)),
#         ],
#     ]
#     keyboard = InlineKeyboardMarkup(buttons)
#
#     await update.callback_query.answer()
#     await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
#
#     return SELECTING_GENDER
#
#
# async def end_second_level(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Return to top level conversation."""
#     context.user_data[START_OVER] = True
#     await start(update, context)
#
#     return END
#
#
# # Third level callbacks
# async def select_feature(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
#     """Select a feature to update for the person."""
#     buttons = [
#         [
#             InlineKeyboardButton(text="Name", callback_data=str(NAME)),
#             InlineKeyboardButton(text="Age", callback_data=str(AGE)),
#             InlineKeyboardButton(text="Done", callback_data=str(END)),
#         ]
#     ]
#     keyboard = InlineKeyboardMarkup(buttons)
#
#     # If we collect features for a new person, clear the cache and save the gender
#     if not context.user_data.get(START_OVER):
#         context.user_data[FEATURES] = {GENDER: update.callback_query.data}
#         text = "Please select a feature to update."
#
#         await update.callback_query.answer()
#         await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
#     # But after we do that, we need to send a new message
#     else:
#         text = "Got it! Please select a feature to update."
#         await update.message.reply_text(text=text, reply_markup=keyboard)
#
#     context.user_data[START_OVER] = False
#     return SELECTING_FEATURE
#
#
# async def ask_for_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
#     """Prompt user to input data for selected feature."""
#     context.user_data[CURRENT_FEATURE] = update.callback_query.data
#     text = "Okay, tell me."
#
#     await update.callback_query.answer()
#     await update.callback_query.edit_message_text(text=text)
#
#     return TYPING
#
#
# async def save_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
#     """Save input for feature and return to feature selection."""
#     user_data = context.user_data
#     user_data[FEATURES][user_data[CURRENT_FEATURE]] = update.message.text
#
#     user_data[START_OVER] = True
#
#     return await select_feature(update, context)
#
#
# async def end_describing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """End gathering of features and return to parent conversation."""
#     user_data = context.user_data
#     level = user_data[CURRENT_LEVEL]
#     if not user_data.get(level):
#         user_data[level] = []
#     user_data[level].append(user_data[FEATURES])
#
#     # Print upper level menu
#     if level == SELF:
#         user_data[START_OVER] = True
#         await start(update, context)
#     else:
#         await select_level(update, context)
#
#     return END
#
#
# async def stop_nested(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
#     """Completely end conversation from within nested conversation."""
#     await update.message.reply_text("Okay, bye.")
#
#     return STOPPING
#
#
# def main() -> None:
#     """Run the bot."""
#     # Create the Application and pass it your bot's token.
#     application = Application.builder().token("7874319913:AAENKsWWF2xGSUd94dHIGiObAkAJE_CuAAs").build()
#
#     # Set up third level ConversationHandler (collecting features)
#     description_conv = ConversationHandler(
#         entry_points=[
#             CallbackQueryHandler(
#                 select_feature, pattern="^" + str(MALE) + "$|^" + str(FEMALE) + "$"
#             )
#         ],
#         states={
#             SELECTING_FEATURE: [
#                 CallbackQueryHandler(ask_for_input, pattern="^(?!" + str(END) + ").*$")
#             ],
#             TYPING: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_input)],
#         },
#         fallbacks=[
#             CallbackQueryHandler(end_describing, pattern="^" + str(END) + "$"),
#             CommandHandler("stop", stop_nested),
#         ],
#         map_to_parent={
#             # Return to second level menu
#             END: SELECTING_LEVEL,
#             # End conversation altogether
#             STOPPING: STOPPING,
#         },
#     )
#
#     # Set up second level ConversationHandler (adding a person)
#     add_member_conv = ConversationHandler(
#         entry_points=[CallbackQueryHandler(select_level, pattern="^" + str(ADDING_MEMBER) + "$")],
#         states={
#             SELECTING_LEVEL: [
#                 CallbackQueryHandler(select_gender, pattern=f"^{PARENTS}$|^{CHILDREN}$")
#             ],
#             SELECTING_GENDER: [description_conv],
#         },
#         fallbacks=[
#             CallbackQueryHandler(show_data, pattern="^" + str(SHOWING) + "$"),
#             CallbackQueryHandler(end_second_level, pattern="^" + str(END) + "$"),
#             CommandHandler("stop", stop_nested),
#         ],
#         map_to_parent={
#             # After showing data return to top level menu
#             SHOWING: SHOWING,
#             # Return to top level menu
#             END: SELECTING_ACTION,
#             # End conversation altogether
#             STOPPING: END,
#         },
#     )
#
#     # Set up top level ConversationHandler (selecting action)
#     # Because the states of the third level conversation map to the ones of the second level
#     # conversation, we need to make sure the top level conversation can also handle them
#     selection_handlers = [
#         add_member_conv,
#         CallbackQueryHandler(show_data, pattern="^" + str(SHOWING) + "$"),
#         CallbackQueryHandler(adding_self, pattern="^" + str(ADDING_SELF) + "$"),
#         CallbackQueryHandler(end, pattern="^" + str(END) + "$"),
#     ]
#     conv_handler = ConversationHandler(
#         entry_points=[CommandHandler("start", start)],
#         states={
#             # SHOWING: [CallbackQueryHandler(start, pattern="^" + str(END) + "$")],
#             SELECTING_ACTION: selection_handlers,
#             SELECTING_LEVEL: selection_handlers,
#             DESCRIBING_SELF: [description_conv],
#             STOPPING: [CommandHandler("start", start)],
#         },
#         fallbacks=[CommandHandler("stop", stop)],
#     )
#
#     application.add_handler(conv_handler)
#
#     # Run the bot until the user presses Ctrl-C
#     application.run_polling()
#
#
# if __name__ == "__main__":
#     main()
#
#
# # import logging
# #
# # from telegram import __version__ as TG_VER
# #
# # try:
# #     from telegram import __version_info__
# # except ImportError:
# #     __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]
# #
# # if __version_info__ < (20, 0, 0, "alpha", 1):
# #     raise RuntimeError(
# #         f"This example is not compatible with your current PTB version {TG_VER}. To view the "
# #         f"{TG_VER} version of this example, "
# #         f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
# #     )
# # from telegram import (
# #     KeyboardButton,
# #     KeyboardButtonPollType,
# #     Poll,
# #     ReplyKeyboardMarkup,
# #     ReplyKeyboardRemove,
# #     Update,
# # )
# # from telegram.constants import ParseMode
# # from telegram.ext import (
# #     Application,
# #     CommandHandler,
# #     ContextTypes,
# #     MessageHandler,
# #     PollAnswerHandler,
# #     PollHandler,
# #     filters,
# # )
# #
# # # Enable logging
# # logging.basicConfig(
# #     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
# # )
# # logger = logging.getLogger(__name__)
# #
# #
# # async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
# #     """Inform user about what this bot can do"""
# #     await update.message.reply_text(
# #         "Please select /poll to get a Poll, /quiz to get a Quiz or /preview"
# #         " to generate a preview for your poll"
# #     )
# #
# #
# # async def poll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
# #     """Sends a predefined poll"""
# #     questions = ["Good", "Really good", "Fantastic", "Great"]
# #     message = await context.bot.send_poll(
# #         update.effective_chat.id,
# #         "How are you?",
# #         questions,
# #         is_anonymous=False,
# #         allows_multiple_answers=True,
# #     )
# #     # Save some info about the poll the bot_data for later use in receive_poll_answer
# #     payload = {
# #         message.poll.id: {
# #             "questions": questions,
# #             "message_id": message.message_id,
# #             "chat_id": update.effective_chat.id,
# #             "answers": 0,
# #         }
# #     }
# #     context.bot_data.update(payload)
# #
# #
# # async def receive_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
# #     """Summarize a users poll vote"""
# #     answer = update.poll_answer
# #     answered_poll = context.bot_data[answer.poll_id]
# #     try:
# #         questions = answered_poll["questions"]
# #     # this means this poll answer update is from an old poll, we can't do our answering then
# #     except KeyError:
# #         return
# #     selected_options = answer.option_ids
# #     answer_string = ""
# #     for question_id in selected_options:
# #         if question_id != selected_options[-1]:
# #             answer_string += questions[question_id] + " and "
# #         else:
# #             answer_string += questions[question_id]
# #     await context.bot.send_message(
# #         answered_poll["chat_id"],
# #         f"{update.effective_user.mention_html()} feels {answer_string}!",
# #         parse_mode=ParseMode.HTML,
# #     )
# #     answered_poll["answers"] += 1
# #     # Close poll after three participants voted
# #     if answered_poll["answers"] == 3:
# #         await context.bot.stop_poll(answered_poll["chat_id"], answered_poll["message_id"])
# #
# #
# # async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
# #     """Send a predefined poll"""
# #     questions = ["1", "2", "4", "20"]
# #     message = await update.effective_message.reply_poll(
# #         "How many eggs do you need for a cake?", questions, type=Poll.QUIZ, correct_option_id=2
# #     )
# #     # Save some info about the poll the bot_data for later use in receive_quiz_answer
# #     payload = {
# #         message.poll.id: {"chat_id": update.effective_chat.id, "message_id": message.message_id}
# #     }
# #     context.bot_data.update(payload)
# #
# #
# # async def receive_quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
# #     """Close quiz after three participants took it"""
# #     # the bot can receive closed poll updates we don't care about
# #     if update.poll.is_closed:
# #         return
# #     if update.poll.total_voter_count == 3:
# #         try:
# #             quiz_data = context.bot_data[update.poll.id]
# #         # this means this poll answer update is from an old poll, we can't stop it then
# #         except KeyError:
# #             return
# #         await context.bot.stop_poll(quiz_data["chat_id"], quiz_data["message_id"])
# #
# #
# # async def preview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
# #     """Ask user to create a poll and display a preview of it"""
# #     # using this without a type lets the user chooses what he wants (quiz or poll)
# #     button = [[KeyboardButton("Press me!", request_poll=KeyboardButtonPollType())]]
# #     message = "Press the button to let the bot generate a preview for your poll"
# #     # using one_time_keyboard to hide the keyboard
# #     await update.effective_message.reply_text(
# #         message, reply_markup=ReplyKeyboardMarkup(button, one_time_keyboard=True)
# #     )
# #
# #
# # async def receive_poll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
# #     """On receiving polls, reply to it by a closed poll copying the received poll"""
# #     actual_poll = update.effective_message.poll
# #     # Only need to set the question and options, since all other parameters don't matter for
# #     # a closed poll
# #     await update.effective_message.reply_poll(
# #         question=actual_poll.question,
# #         options=[o.text for o in actual_poll.options],
# #         # with is_closed true, the poll/quiz is immediately closed
# #         is_closed=True,
# #         reply_markup=ReplyKeyboardRemove(),
# #     )
# #
# #
# # async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
# #     """Display a help message"""
# #     await update.message.reply_text("Use /quiz, /poll or /preview to test this bot.")
# #
# #
# # def main() -> None:
# #     """Run bot."""
# #     # Create the Application and pass it your bot's token.
# #     application = Application.builder().token("7874319913:AAENKsWWF2xGSUd94dHIGiObAkAJE_CuAAs").build()
# #     application.add_handler(CommandHandler("start", start))
# #     application.add_handler(CommandHandler("poll", poll))
# #     application.add_handler(CommandHandler("quiz", quiz))
# #     application.add_handler(CommandHandler("preview", preview))
# #     application.add_handler(CommandHandler("help", help_handler))
# #     application.add_handler(MessageHandler(filters.POLL, receive_poll))
# #     application.add_handler(PollAnswerHandler(receive_poll_answer))
# #     application.add_handler(PollHandler(receive_quiz_answer))
# #
# #     # Run the bot until the user presses Ctrl-C
# #     application.run_polling()
# #
# #
# # if __name__ == "__main__":
# #     print(list(map(chr, range(4))))

import logging
import uuid
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove, BotCommand
from aiogram.fsm.storage.memory import MemoryStorage

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

bot = Bot(token="7874319913:AAENKsWWF2xGSUd94dHIGiObAkAJE_CuAAs")
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# Состояния FSM
class BookingStates(StatesGroup):
    choosing_action = State()
    choosing_master = State()
    choosing_service = State()
    choosing_date = State()
    entering_wishes = State()


# Генерация дат
def generate_dates():
    return [
        (datetime.now() + timedelta(days=i)).strftime("%d.%m %H:%M")
        for i in range(1, 8)
    ]


def generate_session_id():
    return str(uuid.uuid4())


@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()

    # Генерируем новую сессию
    session_id = generate_session_id()
    await state.update_data(session_id=session_id)

    # Удаляем предыдущие сообщения с кнопками (опционально)
    # ... здесь можно добавить логику удаления старых сообщений

    # Показываем новое меню
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(
            text="💅 Записаться",
            callback_data=f"book_{session_id}")  # Уникальный ID сессии
        ]
    ])

    await message.answer(
        "🌸 Начнем новую запись! 🌸",
        reply_markup=keyboard
    )


# Обработка кнопки "💅 Записаться"
@dp.callback_query(F.data == "book_")
async def choose_master(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    session_id = callback.data.split("_")[1]

    # Проверяем актуальность сессии
    if data.get("session_id") != session_id:
        await callback.answer("Сессия устарела, начните заново ⚠️")
        return

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Ксения 💅", callback_data="master_kseniya")],
        [types.InlineKeyboardButton(text="Анастасия 👑", callback_data="master_anastasia")],
        [types.InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
    ])

    await callback.message.edit_text(
        "Выберите мастера:",
        reply_markup=keyboard
    )
    await state.set_state(BookingStates.choosing_master)


# Выбор услуги
@dp.callback_query(F.data.startswith("master_"))
async def choose_service(callback: types.CallbackQuery, state: FSMContext):
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


# Обработка кнопок "Назад"
@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    await start(callback.message, state)


@dp.callback_query(F.data == "back_to_masters")
async def back_to_masters(callback: types.CallbackQuery, state: FSMContext):
    await choose_master(callback, state)


@dp.callback_query(F.data == "back_to_services")
async def back_to_services(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await choose_service(callback, state)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="new_booking", description="Запись на маникюр"),
        BotCommand(command="my_bookings", description="Мои записи"),
        BotCommand(command="masters", description="Список мастеров")
    ]
    await bot.set_my_commands(commands)

# Добавьте в главную функцию запуска:
if __name__ == '__main__':
    # Установка команд при старте бота
    dp.startup.register(set_commands)
    dp.run_polling(bot)