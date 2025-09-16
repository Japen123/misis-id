"""
Модели данных для MISIS ID.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


class StudentInfo(BaseModel):
    """Информация о студенте."""
    
    full_name: str = Field(..., description="Полное имя студента")
    record_book_number: str = Field(..., description="Номер зачетной книжки")
    study_form: str = Field(..., description="Форма обучения")
    preparation_level: str = Field(..., description="Уровень подготовки")
    specialization: Optional[str] = Field(None, description="Специализация")
    specialty: str = Field(..., description="Специальность")
    faculty: str = Field(..., description="Факультет")
    course: str = Field(..., description="Курс")
    group: str = Field(..., description="Группа")
    financing_form: str = Field(..., description="Форма финансирования")
    dormitory: str = Field(..., description="Общежитие")
    end_date: str = Field(..., description="Дата окончания")
    personal_email: Optional[str] = Field(None, description="Личная почта")
    personal_phone: Optional[str] = Field(None, description="Личный номер телефона")
    corporate_email: Optional[str] = Field(None, description="Корпоративная почта")
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        """Валидация полного имени."""
        if not v or not v.strip():
            raise ValueError("Полное имя не может быть пустым")
        return v.strip()
    
    @field_validator('record_book_number')
    @classmethod
    def validate_record_book_number(cls, v: str) -> str:
        """Валидация номера зачетной книжки."""
        if not v or not v.strip():
            raise ValueError("Номер зачетной книжки не может быть пустым")
        return v.strip()
    
    @field_validator('personal_email')
    @classmethod
    def validate_personal_email(cls, v: Optional[str]) -> Optional[str]:
        """Валидация личной почты."""
        if v and '@' not in v:
            raise ValueError("Некорректный формат email")
        return v
    
    @field_validator('corporate_email')
    @classmethod
    def validate_corporate_email(cls, v: Optional[str]) -> Optional[str]:
        """Валидация корпоративной почты."""
        if v and '@' not in v:
            raise ValueError("Некорректный формат email")
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "Иванов Иван Иванович",
                "record_book_number": "12345678",
                "study_form": "Очная",
                "preparation_level": "Бакалавриат",
                "specialization": "Информационные технологии",
                "specialty": "09.03.01 Информатика и вычислительная техника",
                "faculty": "ИТ",
                "course": "3",
                "group": "ИТ-21-1",
                "financing_form": "Бюджет",
                "dormitory": "Да",
                "end_date": "2025-06-30",
                "personal_email": "ivanov@example.com",
                "personal_phone": "+7 (999) 123-45-67",
                "corporate_email": "ivanov@student.misis.ru"
            }
        }
    )


class AuthenticationData(BaseModel):
    """Данные для аутентификации."""
    
    login: str = Field(..., description="Логин")
    password: str = Field(..., description="Пароль")
    remember_me: bool = Field(False, description="Запомнить меня")
    
    @field_validator('login')
    @classmethod
    def validate_login(cls, v: str) -> str:
        """Валидация логина."""
        if not v or not v.strip():
            raise ValueError("Логин не может быть пустым")
        return v.strip()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Валидация пароля."""
        if not v:
            raise ValueError("Пароль не может быть пустым")
        return v


class SessionInfo(BaseModel):
    """Информация о сессии."""
    
    api_id: str = Field(..., description="ID API")
    csrf_token: str = Field(..., description="CSRF токен")
    is_authenticated: bool = Field(False, description="Статус аутентификации")
    
    @field_validator('api_id')
    @classmethod
    def validate_api_id(cls, v: str) -> str:
        """Валидация API ID."""
        if not v or not v.strip():
            raise ValueError("API ID не может быть пустым")
        return v.strip()
    
    @field_validator('csrf_token')
    @classmethod
    def validate_csrf_token(cls, v: str) -> str:
        """Валидация CSRF токена."""
        if not v or not v.strip():
            raise ValueError("CSRF токен не может быть пустым")
        return v.strip()
