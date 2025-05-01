from aiogram.fsm.state import StatesGroup, State


class BookingStates(StatesGroup):
    choosing_action = State()
    choosing_master = State()
    choosing_service = State()
    choosing_date = State()
    entering_wishes = State()
    viewing_bookings = State()
    editing_booking = State()
    deleting_booking = State()
    editing_master = State()
    editing_service = State()
    editing_date = State()
    editing_wishes = State()