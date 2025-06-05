# Импортируем обработчики из модулей
from .start import start, start_router
from .booking import (
    choose_master,
    choose_service,
    choose_date,
    enter_wishes,
    confirm_booking,
    book_router
)
from .bookings_management import (
    handle_booking_selection,
    show_bookings,
    edit_booking,
    delete_booking,
    book_management_router
)

from .masters import (
    master_router
)
from .admin import (
    admin_router,
    show_users_appointments
)
# Экспортируем всё, что должно быть доступно извне
__all__ = [
    'start',
    'start_router',
    'choose_master',
    'choose_service',
    'choose_date',
    'enter_wishes',
    'confirm_booking',
    'book_router',
    'handle_booking_selection',
    'show_bookings',
    'edit_booking',
    'delete_booking',
    'book_management_router',
    'master_router',
    'show_users_appointments',
    'admin_router'
]