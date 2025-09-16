"""
CLI интерфейс для MISIS ID.
"""

import argparse
import asyncio
import json
import logging
import sys
from typing import Optional

from .client import MisisClient
from .exceptions import MisisError


def setup_logging(verbose: bool = False) -> None:
    """Настройка логирования."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


async def get_student_info(
    login: str,
    password: str,
    output_format: str = "text",
    verbose: bool = False
) -> None:
    """
    Получение информации о студенте.
    
    Args:
        login: Логин пользователя
        password: Пароль пользователя
        output_format: Формат вывода (text, json)
        verbose: Подробный вывод
    """
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    try:
        async with MisisClient() as client:
            logger.info("Начинаем аутентификацию...")
            await client.authenticate(login, password)
            
            logger.info("Получаем информацию о студенте...")
            student_info = await client.get_student_info()
            
            if output_format == "json":
                print(json.dumps(student_info.dict(), ensure_ascii=False, indent=2))
            else:
                print_student_info_text(student_info)
                
    except MisisError as e:
        logger.error(f"Ошибка MISIS: {e.message}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        sys.exit(1)


def print_student_info_text(student_info) -> None:
    """Вывод информации о студенте в текстовом формате."""
    print("=" * 50)
    print("ИНФОРМАЦИЯ О СТУДЕНТЕ")
    print("=" * 50)
    print(f"ФИО: {student_info.full_name}")
    print(f"Номер зачетки: {student_info.record_book_number}")
    print(f"Форма обучения: {student_info.study_form}")
    print(f"Уровень подготовки: {student_info.preparation_level}")
    
    if student_info.specialization:
        print(f"Специализация: {student_info.specialization}")
    
    print(f"Специальность: {student_info.specialty}")
    print(f"Факультет: {student_info.faculty}")
    print(f"Курс: {student_info.course}")
    print(f"Группа: {student_info.group}")
    print(f"Форма финансирования: {student_info.financing_form}")
    print(f"Общежитие: {student_info.dormitory}")
    print(f"Дата окончания: {student_info.end_date}")
    
    if student_info.personal_email:
        print(f"Личная почта: {student_info.personal_email}")
    
    if student_info.personal_phone:
        print(f"Личный телефон: {student_info.personal_phone}")
    
    if student_info.corporate_email:
        print(f"Корпоративная почта: {student_info.corporate_email}")
    
    print("=" * 50)


def main() -> None:
    """Главная функция CLI."""
    parser = argparse.ArgumentParser(
        description="MISIS ID - Асинхронный клиент для работы с личным кабинетом МИСИС",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  # Получение информации о студенте
  misis-id --login your_login --password your_password

  # Вывод в JSON формате
  misis-id --login your_login --password your_password --format json

  # Подробный вывод
  misis-id --login your_login --password your_password --verbose
        """
    )
    
    parser.add_argument(
        "--login",
        required=True,
        help="Логин для входа в личный кабинет МИСИС"
    )
    
    parser.add_argument(
        "--password",
        required=True,
        help="Пароль для входа в личный кабинет МИСИС"
    )
    
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Формат вывода (по умолчанию: text)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Подробный вывод"
    )
    
    args = parser.parse_args()
    
    # Запуск асинхронной функции
    asyncio.run(get_student_info(
        login=args.login,
        password=args.password,
        output_format=args.format,
        verbose=args.verbose
    ))


if __name__ == "__main__":
    main()
