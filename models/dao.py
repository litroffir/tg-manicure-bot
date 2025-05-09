import datetime

from sqlalchemy import update, delete, select
from sqlalchemy.exc import SQLAlchemyError

from models import Appointment, User


class BaseDAO:
    model = None

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        from utils import async_session
        async with async_session() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()


class AppointmentDAO(BaseDAO):
    model = Appointment
    rel_model = User

    @classmethod
    async def update_appointment(cls, booking_id: int, user_id: int, **values):
        from utils import async_session
        async with async_session() as session:
            async with session.begin():
                query = (
                    update(cls.model)
                        .where((cls.model.booking_id == booking_id) & (cls.model.user_id == user_id))
                        .values(**values)
                        .execution_options(synchronize_session="fetch")
                )
                result = await session.execute(query)
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return result.rowcount > 0

    @classmethod
    async def delete_appointment(cls, booking_id: int, user_id: int):
        from utils import async_session
        async with async_session() as session:
            async with session.begin():
                query = delete(cls.model).where((Appointment.user_id == user_id) & (Appointment.booking_id == booking_id))
                result = await session.execute(query)
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return result.rowcount > 0

    @classmethod
    async def select_appointments_by_date(cls, start_date: datetime.date, end_date: datetime.date, csv: bool = False):
        text = []
        from utils import async_session
        async with async_session() as session:
            stmt = select(cls.model.master, cls.model.service, cls.model.wishes, cls.model.start_datetime,
                          cls.model.end_datetime, cls.rel_model.username, cls.rel_model.full_name
                          ).join(cls.rel_model, cls.rel_model.id == cls.model.user_id)
            result = await session.execute(stmt)

            bookings = result.all()
            for book in bookings:
                if start_date <= book.start_datetime.date() <= end_date:
                    if csv:
                        text.append([f"{book.start_datetime.strftime('%Y-%m-%d %H:%M')}-"
                                     f"{book.end_datetime.strftime('%H:%M')}", book.full_name, book.username,
                                     book.master, book.service, book.wishes])
                    else:
                        text.append(f"👩 Мастер: {book.master}\n"
                                    f"💅 Услуга: {book.service}\n"
                                    f"📅 Дата: {book.start_datetime.strftime('%Y-%m-%d %H:%M')}-"
                                    f"{book.end_datetime.strftime('%H:%M')}\n"
                                    f"📝 Пожелания: {book.wishes}\n"
                                    f"🙍‍♂ Контактная информация: @{book.username} {book.full_name}\n\n")
        return text
