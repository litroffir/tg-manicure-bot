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
    show_bookings,
    handle_booking_selection,
    edit_booking,
    delete_booking,
    book_management_router
)
from .common import (
    back_to_menu,
    back_to_masters,
    back_to_services,
    back_router
)

from .masters import (
    master_router
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
    'show_bookings',
    'handle_booking_selection',
    'edit_booking',
    'delete_booking',
    'back_to_menu',
    'back_to_masters',
    'back_to_services',
    'back_router',
    'book_management_router',
    'master_router'
]