import datetime

from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError

from models import Appointment
from utils import async_session


async def delete_expired_appointments():
    async with async_session() as session:
        async with session.begin():
            query = delete(Appointment).where(
                    Appointment.end_datetime < datetime.datetime.now()
            )
            result = await session.execute(query)
            try:
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                raise e
            return result.rowcount > 0



