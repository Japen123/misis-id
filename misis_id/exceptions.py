"""
Исключения для пакета misis-id.
"""


class MisisError(Exception):
    """Базовое исключение для всех ошибок MISIS ID."""
    
    def __init__(self, message: str, status_code: int = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AuthenticationError(MisisError):
    """Ошибка аутентификации."""
    
    def __init__(self, message: str = "Ошибка аутентификации") -> None:
        super().__init__(message, status_code=401)


class NetworkError(MisisError):
    """Ошибка сети."""
    
    def __init__(self, message: str = "Ошибка сети") -> None:
        super().__init__(message, status_code=0)


class ParseError(MisisError):
    """Ошибка парсинга данных."""
    
    def __init__(self, message: str = "Ошибка парсинга данных") -> None:
        super().__init__(message, status_code=200)


class SessionExpiredError(MisisError):
    """Сессия истекла."""
    
    def __init__(self, message: str = "Сессия истекла") -> None:
        super().__init__(message, status_code=401)
