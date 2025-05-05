from .data_models import Base, User, Appointment
from .dao import AppointmentDAO

# Экспортируем всё, что должно быть доступно извне
__all__ = [
    'Base',
    'User',
    'Appointment',
    'AppointmentDAO'
]