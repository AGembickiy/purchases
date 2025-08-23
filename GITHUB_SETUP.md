# Настройка GitHub репозитория

## Шаг 1: Создание репозитория на GitHub

1. Перейдите на [GitHub.com](https://github.com)
2. Нажмите кнопку "New" или "+" → "New repository"
3. Заполните форму:
   - **Repository name**: `django-user-management` (или другое название)
   - **Description**: `Django система управления пользователями с веб-интерфейсом`
   - **Visibility**: Public или Private (по вашему выбору)
   - **Initialize this repository with**: НЕ ставьте галочки (у нас уже есть файлы)
4. Нажмите "Create repository"

## Шаг 2: Подключение локального репозитория

После создания репозитория GitHub покажет команды. Выполните их в терминале:

```bash
# Добавить удаленный репозиторий (замените YOUR_USERNAME на ваше имя пользователя)
git remote add origin https://github.com/YOUR_USERNAME/django-user-management.git

# Отправить код в репозиторий
git push -u origin main
```

## Шаг 3: Проверка

Перейдите в созданный репозиторий на GitHub и убедитесь, что все файлы загружены.

## Структура проекта

```
django-user-management/
├── .cursorrules          # Правила для Cursor IDE
├── .gitignore           # Исключения для Git
├── README.md            # Документация проекта
├── requirements.txt     # Зависимости Python
├── manage.py           # Управление Django
├── purchases_project/  # Основной проект Django
│   ├── settings.py     # Настройки
│   ├── urls.py         # Главные URL
│   └── wsgi.py         # WSGI конфигурация
└── users/              # Приложение пользователей
    ├── models.py       # Модели данных
    ├── views.py        # Представления
    ├── forms.py        # Формы
    ├── templates/      # HTML шаблоны
    └── admin.py        # Админка Django
```

## Возможности системы

- 👤 Управление пользователями и профилями
- 🔐 Система аутентификации
- 🎨 Современный веб-интерфейс
- 📱 Адаптивный дизайн
- 🔒 Разграничение прав доступа
- 📊 Админ-панель Django
