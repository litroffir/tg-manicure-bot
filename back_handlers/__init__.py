# Импортируем обработчики из модулей
from .back import (
    back_to_menu,
    back_to_masters,
    back_to_services,
    back_router,
    back_to_bookings
)

# Экспортируем всё, что должно быть доступно извне
__all__ = [
    'back_to_menu',
    'back_to_masters',
    'back_to_services',
    'back_router',
    'back_to_bookings',
]