# Руководство по использованию MISIS ID

## Установка

```bash
# Клонируйте репозиторий
git clone <repository-url>
cd misis-id

# Создайте виртуальное окружение
python3 -m venv .venv
source .venv/bin/activate  # На Windows: .venv\Scripts\activate

# Установите пакет
pip install -e .
```

## Использование

### 1. Программный интерфейс

```python
import asyncio
from misis_id import MisisClient

async def main():
    async with MisisClient() as client:
        # Аутентификация
        await client.authenticate("your_login", "your_password")
        
        # Получение информации о студенте
        student_info = await client.get_student_info()
        
        print(f"Студент: {student_info.full_name}")
        print(f"Группа: {student_info.group}")
        print(f"Факультет: {student_info.faculty}")

asyncio.run(main())
```

### 2. CLI интерфейс

```bash
# Базовое использование
misis-id --login your_login --password your_password

# Вывод в JSON формате
misis-id --login your_login --password your_password --format json

# Подробный вывод с логированием
misis-id --login your_login --password your_password --verbose
```

### 3. Пример использования (main.py)

```bash
# Отредактируйте main.py, указав ваши данные
python main.py
```

## Структура проекта

```
misis-id/
├── misis_id/           # Основной пакет
│   ├── __init__.py     # Экспорты пакета
│   ├── client.py       # Асинхронный клиент
│   ├── models.py       # Модели данных (Pydantic)
│   ├── exceptions.py   # Исключения
│   ├── cli.py          # CLI интерфейс
│   └── version.py      # Версия пакета
├── main.py             # Пример использования
├── setup.py            # Конфигурация установки
├── pyproject.toml      # Современная конфигурация
├── requirements.txt    # Зависимости
├── README.md           # Документация
└── LICENSE             # Лицензия MIT
```

## Возможности

- ✅ Асинхронная работа с aiohttp
- ✅ Валидация данных с Pydantic V2
- ✅ Обработка ошибок и логирование
- ✅ CLI интерфейс
- ✅ Контекстный менеджер для автоматического закрытия сессии
- ✅ Поддержка Python 3.8+
- ✅ Готовность к публикации в PyPI

## Разработка

```bash
# Установка в режиме разработки
pip install -e ".[dev]"

# Форматирование кода
make format

# Проверка кода
make lint

# Сборка пакета
make build

# Загрузка в PyPI
make upload
```

## Лицензия

MIT License - свободно используйте в своих проектах.
