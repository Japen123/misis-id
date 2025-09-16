"""
Асинхронный клиент для работы с MISIS API.
"""

import asyncio
import logging
from typing import Optional
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup

from .exceptions import (
    AuthenticationError,
    NetworkError,
    ParseError,
    SessionExpiredError,
)
from .models import AuthenticationData, SessionInfo, StudentInfo

logger = logging.getLogger(__name__)


class MisisClient:
    """
    Асинхронный клиент для работы с личным кабинетом МИСИС.
    
    Предоставляет методы для аутентификации и получения информации о студенте.
    """
    
    BASE_URL = "https://lk.misis.ru"
    AUTH_URL = f"{BASE_URL}/ru/users/sign_in"
    
    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        session: Optional[aiohttp.ClientSession] = None,
    ) -> None:
        """
        Инициализация клиента.
        
        Args:
            timeout: Таймаут для HTTP запросов в секундах
            max_retries: Максимальное количество повторных попыток
            session: Существующая aiohttp сессия (опционально)
        """
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self._session = session
        self._session_info: Optional[SessionInfo] = None
        self._owned_session = session is None
        
    async def __aenter__(self) -> "MisisClient":
        """Асинхронный контекстный менеджер - вход."""
        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Асинхронный контекстный менеджер - выход."""
        await self.close()
    
    async def close(self) -> None:
        """Закрытие сессии."""
        if self._session and self._owned_session:
            await self._session.close()
            self._session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Получение HTTP сессии."""
        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session
    
    async def _make_request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> tuple[int, str, str, dict]:
        """
        Выполнение HTTP запроса с обработкой ошибок.
        
        Args:
            method: HTTP метод
            url: URL для запроса
            **kwargs: Дополнительные параметры для запроса
            
        Returns:
            Кортеж (status_code, response_text, response_url)
            
        Raises:
            NetworkError: Ошибка сети
        """
        session = await self._get_session()
        
        for attempt in range(self.max_retries):
            try:
                async with session.request(method, url, **kwargs) as response:
                    if response.status >= 400:
                        logger.warning(
                            f"HTTP {response.status} для {url}, попытка {attempt + 1}"
                        )
                        if attempt == self.max_retries - 1:
                            raise NetworkError(
                                f"HTTP {response.status}: {response.reason}"
                            )
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    
                    # Извлекаем данные до выхода из async with
                    text = await response.text()
                    return response.status, text, str(response.url), response.headers
                    
            except aiohttp.ClientError as e:
                logger.error(f"Ошибка сети для {url}: {e}")
                if attempt == self.max_retries - 1:
                    raise NetworkError(f"Ошибка сети: {e}")
                await asyncio.sleep(2 ** attempt)
        
        raise NetworkError("Превышено максимальное количество попыток")
    
    async def _get_csrf_token(self) -> str:
        """
        Получение CSRF токена.
        
        Returns:
            CSRF токен
            
        Raises:
            ParseError: Ошибка парсинга токена
        """
        try:
            status, text, url, headers = await self._make_request("GET", self.AUTH_URL)
            
            soup = BeautifulSoup(text, 'html.parser')
            csrf_meta = soup.find('meta', {'name': 'csrf-token'})
            
            if not csrf_meta:
                raise ParseError("CSRF токен не найден на странице")
            
            csrf_token = csrf_meta.get('content')
            if not csrf_token:
                raise ParseError("CSRF токен пустой")
            
            logger.debug("CSRF токен успешно получен")
            return csrf_token
            
        except Exception as e:
            if isinstance(e, (ParseError, NetworkError)):
                raise
            raise ParseError(f"Ошибка получения CSRF токена: {e}")
    
    async def authenticate(self, login: str, password: str) -> SessionInfo:
        """
        Аутентификация в системе.
        
        Args:
            login: Логин пользователя
            password: Пароль пользователя
            
        Returns:
            Информация о сессии
            
        Raises:
            AuthenticationError: Ошибка аутентификации
            NetworkError: Ошибка сети
            ParseError: Ошибка парсинга
        """
        auth_data = AuthenticationData(login=login, password=password)
        
        try:
            # Получаем CSRF токен
            csrf_token = await self._get_csrf_token()
            
            # Выполняем аутентификацию
            auth_payload = {
                "user[login]": auth_data.login,
                "user[password]": auth_data.password,
                "user[remember_me]": "1" if auth_data.remember_me else "0",
                "commit": "Войти",
                "utf8": "✓",
                "authenticity_token": csrf_token,
            }
            
            status, text, url, headers = await self._make_request(
                "POST",
                self.AUTH_URL,
                data=auth_payload,
                allow_redirects=False
            )
            if not headers.get("Location"):
                raise AuthenticationError("Неверный логин или пароль")
            if "/s" not in headers.get("Location"):
                raise AuthenticationError("Неверный логин или пароль")
            
            # Проверяем успешность аутентификации
            if status not in [302, 200]:
                raise AuthenticationError(
                    f"Неожиданный статус ответа: {status}"
                )
            
            # Проверяем, что аутентификация прошла успешно
            if "Неверный логин или пароль" in text:
                raise AuthenticationError("Неверный логин или пароль")
            
            # Извлекаем API ID
            # api_id = self._extract_api_id(text)
            api_id = headers.get("Location").split("/ru/")[1].split("/")[0]
            
            self._session_info = SessionInfo(
                api_id=api_id,
                csrf_token=csrf_token,
                is_authenticated=True
            )
            
            logger.info(f"Успешная аутентификация для пользователя: {login}")
            return self._session_info
            
        except Exception as e:
            if isinstance(e, (AuthenticationError, NetworkError, ParseError)):
                raise
            raise AuthenticationError(f"Ошибка аутентификации: {e}")
    
    def _extract_api_id(self, text: str) -> str:
        """
        Извлечение API ID из HTML.
        
        Args:
            text: HTML текст страницы
            
        Returns:
            API ID
            
        Raises:
            ParseError: Ошибка парсинга API ID
        """
        try:
            # Ищем API ID в JavaScript переменной
            if "var au_api_url = '/ru/" in text:
                api_id = text.split("var au_api_url = '/ru/")[1].split("/")[0]
                if api_id:
                    return api_id
            
            # Альтернативный способ поиска
            soup = BeautifulSoup(text, 'html.parser')
            scripts = soup.find_all('script')
            
            for script in scripts:
                if script.string and "au_api_url" in script.string:
                    content = script.string
                    if "var au_api_url = '/ru/" in content:
                        api_id = content.split("var au_api_url = '/ru/")[1].split("/")[0]
                        if api_id:
                            return api_id
            
            raise ParseError("API ID не найден в ответе сервера")
            
        except Exception as e:
            if isinstance(e, ParseError):
                raise
            raise ParseError(f"Ошибка извлечения API ID: {e}")
    
    async def get_student_info(self) -> StudentInfo:
        """
        Получение информации о студенте.
        
        Returns:
            Информация о студенте
            
        Raises:
            SessionExpiredError: Сессия истекла
            NetworkError: Ошибка сети
            ParseError: Ошибка парсинга
        """
        if not self._session_info or not self._session_info.is_authenticated:
            raise SessionExpiredError("Необходима аутентификация")
        
        try:
            profile_url = f"{self.BASE_URL}/ru/{self._session_info.api_id}/profile"
            status, text, url, headers = await self._make_request("GET", profile_url)
            
            # Проверяем, что мы все еще аутентифицированы
            if "sign_in" in url:
                self._session_info.is_authenticated = False
                raise SessionExpiredError("Сессия истекла")
            
            # Парсим информацию о студенте
            student_info = self._parse_student_info(text)
            
            logger.info(f"Информация о студенте получена: {student_info.full_name}")
            return student_info
            
        except Exception as e:
            if isinstance(e, (SessionExpiredError, NetworkError, ParseError)):
                raise
            raise ParseError(f"Ошибка получения информации о студенте: {e}")
    
    def _parse_student_info(self, html: str) -> StudentInfo:
        """
        Парсинг информации о студенте из HTML.
        
        Args:
            html: HTML код страницы профиля
            
        Returns:
            Информация о студенте
            
        Raises:
            ParseError: Ошибка парсинга
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Извлекаем данные
            data = {}
            
            # Полное имя
            name_element = soup.find('div', class_='person_name')
            if name_element:
                h3 = name_element.find('h3')
                data['full_name'] = h3.get_text(strip=True) if h3 else ""
            
            # Функция для извлечения значения по лейблу
            def extract_value(label_text: str) -> str:
                label = soup.find('span', class_='person__label', string=lambda text: text and label_text in text)
                if label:
                    value_span = label.find_next_sibling('span', class_='person__value')
                    if value_span:
                        return value_span.get_text(strip=True)
                return None
            
            # Извлекаем остальные поля
            data['record_book_number'] = extract_value('Номер зачетки:')
            data['study_form'] = extract_value('Форма обучения:')
            data['preparation_level'] = extract_value('Уровень подготовки:')
            data['specialization'] = extract_value('Специализация:')
            data['specialty'] = extract_value('Специальность:')
            data['faculty'] = extract_value('Факультет:')
            data['course'] = extract_value('Курс:')
            data['group'] = extract_value('Группа:')
            data['financing_form'] = extract_value('Форма финансирования:')
            data['dormitory'] = extract_value('Общежитие:')
            data['end_date'] = extract_value('Дата окончания:')
            data['personal_email'] = extract_value('Личная почта:')
            data['personal_phone'] = extract_value('Личный номер телефона:')
            data['corporate_email'] = extract_value('Корпоративная почта:')
            
            # Проверяем обязательные поля
            required_fields = ['full_name', 'record_book_number', 'study_form', 
                             'preparation_level', 'specialty', 'faculty', 
                             'course', 'group', 'financing_form', 'dormitory', 'end_date']
            
            for field in required_fields:
                if data.get(field) is None:
                    raise ParseError(f"Обязательное поле '{field}' не найдено")
            
            return StudentInfo(**data)
            
        except Exception as e:
            if isinstance(e, ParseError):
                raise
            raise ParseError(f"Ошибка парсинга информации о студенте: {e}")
    
    @property
    def is_authenticated(self) -> bool:
        """Проверка статуса аутентификации."""
        return self._session_info is not None and self._session_info.is_authenticated
    
    @property
    def session_info(self) -> Optional[SessionInfo]:
        """Получение информации о сессии."""
        return self._session_info
