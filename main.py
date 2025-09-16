#!/usr/bin/env python3
"""
Пример использования асинхронного клиента MISIS ID.

Этот файл демонстрирует, как использовать новый асинхронный клиент
вместо старого синхронного кода.
"""

import asyncio
import logging
from misis_id import MisisClient

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def main():
    """Основная функция для демонстрации использования клиента."""
    # Замените на ваши реальные данные
    login = "your_login_here"
    password = "your_password_here"
    
    if not login or not password or login == "your_login_here":
        print("Пожалуйста, укажите ваши реальные данные для входа в main.py")
        print("Или используйте CLI: misis-id --login your_login --password your_password")
        return
    
    try:
        # Создаем клиент и используем контекстный менеджер
        async with MisisClient() as client:
            print("🔐 Аутентификация...")
            await client.authenticate(login, password)
            print("✅ Аутентификация успешна!")
            
            print("📊 Получение информации о студенте...")
            student_info = await client.get_student_info()
            
            # Выводим информацию
            print("\n" + "="*50)
            print("ИНФОРМАЦИЯ О СТУДЕНТЕ")
            print("="*50)
            print(f"👤 ФИО: {student_info.full_name}")
            print(f"📚 Номер зачетки: {student_info.record_book_number}")
            print(f"🎓 Форма обучения: {student_info.study_form}")
            print(f"📖 Уровень подготовки: {student_info.preparation_level}")
            
            if student_info.specialization:
                print(f"🔬 Специализация: {student_info.specialization}")
            
            print(f"📋 Специальность: {student_info.specialty}")
            print(f"🏛️ Факультет: {student_info.faculty}")
            print(f"📅 Курс: {student_info.course}")
            print(f"👥 Группа: {student_info.group}")
            print(f"💰 Форма финансирования: {student_info.financing_form}")
            print(f"🏠 Общежитие: {student_info.dormitory}")
            print(f"📆 Дата окончания: {student_info.end_date}")
            
            if student_info.personal_email:
                print(f"📧 Личная почта: {student_info.personal_email}")
            
            if student_info.personal_phone:
                print(f"📱 Личный телефон: {student_info.personal_phone}")
            
            if student_info.corporate_email:
                print(f"🏢 Корпоративная почта: {student_info.corporate_email}")
            
            print("="*50)
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())