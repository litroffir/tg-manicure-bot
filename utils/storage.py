from datetime import datetime

user_bookings = {}


class BotHolder:
    _bot_instance = None

    @classmethod
    def set_bot(cls, bot):
        cls._bot_instance = bot

    @classmethod
    def get_bot(cls):
        return cls._bot_instance


# def get_user_bookings(user_id: int):
#     return user_bookings.get(user_id, {})
#
#
# def add_booking(user_id: int, booking_data: dict):
#     booking_id = datetime.now().strftime("%Y%m%d%H%M%S")
#     if user_id not in user_bookings:
#         user_bookings[user_id] = {}
#     user_bookings[user_id][booking_id] = booking_data
#     return booking_id
#
#
# def delete_booking(user_id: int, booking_id: str):
#     if user_id in user_bookings and booking_id in user_bookings[user_id]:
#         del user_bookings[user_id][booking_id]
#         return True
#     return False
#
#
# def update_booking(user_id: int, booking_id: str, data: dict):
#     if user_id not in user_bookings:
#         user_bookings[user_id] = {}
#     user_bookings[user_id][booking_id] = {
#         **data,
#         'last_updated': datetime.now().strftime("%d.%m.%Y %H:%M")
#     }