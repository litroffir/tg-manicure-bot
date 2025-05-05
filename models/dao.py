from sqlalchemy import update, delete, select
from sqlalchemy.exc import SQLAlchemyError

from models import Appointment
from utils import async_session


class BaseDAO:
    model = None

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()


class AppointmentDAO(BaseDAO):
    model = Appointment

    @classmethod
    async def update_appointment(cls, booking_id: int, user_id: int, **values):
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
