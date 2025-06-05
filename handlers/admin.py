from __future__ import annotations

import datetime

from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile

from models import AppointmentDAO, BaseDAO
from utils import admin_dates_kb, generate_excel, admin_choice_kb, admin_stats_kb

admin_router = Router()


@admin_router.callback_query(F.data == "clients")
async def admin_choice_kb_hadndler(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Выберите, что хотите  посмотреть",
                                     reply_markup=admin_choice_kb())


@admin_router.callback_query(F.data == "clients_books")
async def admin_kb_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="Выберите временной диапозон:",
        reply_markup=admin_dates_kb()
    )


@admin_router.callback_query(F.data.startswith("show_users_books"))
async def show_users_appointments(callback: types.CallbackQuery, state: FSMContext):
    callback_date = callback.data.split("_")[-1]
    if callback_date == "today":
        result = await AppointmentDAO.select_appointments_by_date(datetime.date.today(), datetime.date.today())
        if result:
            await callback.message.edit_text(text="✨ *Текущие записи* ✨\n\n{}".format('\n'.join(result)),
                                             reply_markup=InlineKeyboardMarkup(
                                                 inline_keyboard=[
                                                     [InlineKeyboardButton(text="🔙 Назад", callback_data="clients_books")]]))
        else:
            await callback.answer("Записей нет!", show_alert=True)
    elif callback_date == "tomorrow":
        result = await AppointmentDAO.select_appointments_by_date(datetime.date.today() + datetime.timedelta(days=1),
                                                                  datetime.date.today() + datetime.timedelta(days=1))
        if result:
            await callback.message.edit_text(text="✨ *Текущие записи* ✨\n\n{}".format('\n'.join(result)),
                                             reply_markup=InlineKeyboardMarkup(
                                                 inline_keyboard=[
                                                     [InlineKeyboardButton(text="🔙 Назад", callback_data="clients_books")]]))
        else:
            await callback.answer("Записей нет!", show_alert=True)
    elif callback_date == "week":
        start_date = datetime.datetime.now().date()
        end_date = start_date + datetime.timedelta(days=7)
        result = await AppointmentDAO.select_appointments_by_date(start_date=start_date, end_date=end_date, csv=True)

        if result:
            excel_data = await generate_excel(result)
            excel_file = BufferedInputFile(
                file=excel_data,
                filename="weekly_appointments.xlsx"
            )
            await callback.message.reply_document(
                document=excel_file,
                caption="📊 Записи на ближайшую неделю"
            )
        else:
            await callback.answer("Записей нет!", show_alert=True)
    elif callback_date == "month":
        start_date = datetime.datetime.now().date()
        end_date = start_date + datetime.timedelta(days=30)
        result = await AppointmentDAO.select_appointments_by_date(start_date=start_date, end_date=end_date, csv=True)
        if result:
            excel_data = await generate_excel(result)
            excel_file = BufferedInputFile(
                file=excel_data,
                filename="monthly_appointments.xlsx"
            )
            await callback.message.reply_document(
                document=excel_file,
                caption="📊 Записи на ближайший месяц"
            )
        else:
            await callback.answer("Записей нет!", show_alert=True)


@admin_router.callback_query(F.data == "clients_stats")
async def admin_stats_kb_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="За какое время:",
        reply_markup=admin_stats_kb()
    )


@admin_router.callback_query(F.data.startswith("show_users_stats"))
async def show_users_stats(callback: types.CallbackQuery, state: FSMContext):
    callback_date = callback.data.split("_")[-1]
    if callback_date == "today":
        result = await BaseDAO.find_all_by_date(datetime.date.today(), datetime.date.today())
        if result:
            excel_data = await generate_excel(result, stats=True)
            excel_file = BufferedInputFile(
                file=excel_data,
                filename="day_stat.xlsx"
            )
            await callback.message.reply_document(
                document=excel_file,
                caption="📊 Статистика по количеству новых пользователей за день:"
            )
        else:
            await callback.answer("В этот период никто не зарегистрировался!", show_alert=True)
    elif callback_date == "yesterday":
        result = await BaseDAO.find_all_by_date(datetime.date.today() - datetime.timedelta(days=1),
                                                datetime.date.today() - datetime.timedelta(days=1))
        if result:
            excel_data = await generate_excel(result, stats=True)
            excel_file = BufferedInputFile(
                file=excel_data,
                filename="yesterday_stat.xlsx"
            )
            await callback.message.reply_document(
                document=excel_file,
                caption="📊 Статистика по количеству новых пользователей за вчера:"
            )
        else:
            await callback.answer("В этот период никто не зарегистрировался!", show_alert=True)
    elif callback_date == "week":
        start_date = datetime.datetime.now().date()
        end_date = start_date - datetime.timedelta(days=7)
        result = await BaseDAO.find_all_by_date(start_date=end_date, end_date=start_date)

        if result:
            excel_data = await generate_excel(result, stats=True)
            excel_file = BufferedInputFile(
                file=excel_data,
                filename="week_stat.xlsx"
            )
            await callback.message.reply_document(
                document=excel_file,
                caption="📊 Статистика по количеству новых пользователей за прошлую неделю:"
            )
        else:
            await callback.answer("В этот период никто не зарегистрировался!", show_alert=True)
    elif callback_date == "month":
        start_date = datetime.datetime.now().date()
        end_date = start_date - datetime.timedelta(days=30)
        result = await BaseDAO.find_all_by_date(start_date=end_date, end_date=start_date)
        if result:
            excel_data = await generate_excel(result, stats=True)
            excel_file = BufferedInputFile(
                file=excel_data,
                filename="month_stat.xlsx"
            )
            await callback.message.reply_document(
                document=excel_file,
                caption="📊 Статистика по количеству новых пользователей за прошлый месяц"
            )
        else:
            await callback.answer("В этот период никто не зарегистрировался!", show_alert=True)
    else:
        result = await BaseDAO.find_all_by_date(all_time=True)
        if result:
            excel_data = await generate_excel(result, stats=True)
            excel_file = BufferedInputFile(
                file=excel_data,
                filename="all_stat.xlsx"
            )
            await callback.message.reply_document(
                document=excel_file,
                caption="📊 Статистика по количеству новых пользователей за все время"
            )
        else:
            await callback.answer("В этот период никто не зарегистрировался!", show_alert=True)
