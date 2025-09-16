"""
MISIS ID - Асинхронный клиент для работы с личным кабинетом МИСИС.

Этот пакет предоставляет удобный интерфейс для аутентификации
и получения информации о студентах МИСИС.
"""

from .client import MisisClient
from .models import StudentInfo
from .exceptions import AuthenticationError, MisisError
from .version import __version__

__all__ = [
    "MisisClient",
    "StudentInfo", 
    "AuthenticationError",
    "MisisError",
    "__version__",
]

__version__ = "1.0.0"
