# MISIS ID

Асинхронный Python клиент для работы с личным кабинетом МИСИС (Московский институт стали и сплавов).

## Возможности

- 🔐 Асинхронная аутентификация в личном кабинете МИСИС
- 📊 Получение информации о студенте
- 🏗️ Современная архитектура с использованием asyncio
- 🛡️ Обработка ошибок и валидация данных
- 📝 Подробное логирование
- 🧪 Полное покрытие тестами

## Установка

```bash
pip install git+https://github.com/s1rne/misis-id
```

## Быстрый старт

```python
import asyncio
from misis_id import MisisClient

async def main():
    client = MisisClient()
    
    # Аутентификация
    await client.authenticate("your_login", "your_password")
    
    # Получение информации о студенте
    student_info = await client.get_student_info()
    print(f"Студент: {student_info.full_name}")
    print(f"Группа: {student_info.group}")
    print(f"Факультет: {student_info.faculty}")
    
    await client.close()

asyncio.run(main())
```

## CLI использование

```bash
misis-id --login your_login --password your_password
```

## Требования

- Python 3.8+
- aiohttp
- pydantic

## Лицензия

MIT License
