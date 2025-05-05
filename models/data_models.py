from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    full_name = Column(String)


class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    booking_id = Column(BigInteger)
    master = Column(String)
    service = Column(String)
    wishes = Column(String)
    date_time = Column(String)