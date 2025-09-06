# Настройка Tailwind CSS в проекте

## Что было сделано

1. **Установлен Tailwind CSS** через npm с плагином форм
2. **Настроена конфигурация** с CSS переменными для цветовой схемы
3. **Создана система CSS переменных** для единообразного оформления
4. **Обновлены базовые шаблоны** с использованием Tailwind классов
5. **Настроена сборка** статических файлов

## Структура файлов

```
static/
├── src/
│   └── input.css          # Исходный CSS с переменными и компонентами
├── css/
│   └── output.css         # Скомпилированный CSS (генерируется автоматически)
└── js/                    # JavaScript файлы (если понадобятся)

tailwind.config.js         # Конфигурация Tailwind CSS
package.json               # Зависимости и скрипты
```

## CSS переменные

Проект использует систему CSS переменных для цветов:

- **Primary** - основная синяя палитра
- **Secondary** - серая палитра
- **Accent** - зеленая палитра для акцентов
- **Neutral** - нейтральные цвета
- **Success** - цвета успеха (зеленые)
- **Warning** - цвета предупреждения (желтые)
- **Error** - цвета ошибки (красные)

Каждая палитра имеет 9 оттенков (50-900).

## Компоненты

В `input.css` определены готовые компоненты:

- `.btn` - кнопки с вариантами (primary, secondary, success, warning, error, outline)
- `.card` - карточки с header, body, footer
- `.form-input`, `.form-label`, `.form-error` - элементы форм
- `.table` - стилизованные таблицы
- `.badge` - значки с вариантами
- `.alert` - уведомления с вариантами

## Команды

```bash
# Разработка (с отслеживанием изменений)
npm run dev

# Сборка для продакшена (минифицированная)
npm run build

# Только CSS (с отслеживанием)
npm run build-css

# Только CSS (продакшен)
npm run build-css-prod
```

## Использование

### В шаблонах Django

```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/output.css' %}">
```

### Примеры классов

```html
<!-- Кнопки -->
<button class="btn btn-primary">Основная кнопка</button>
<button class="btn btn-secondary">Вторичная кнопка</button>
<button class="btn btn-outline">Контурная кнопка</button>

<!-- Карточки -->
<div class="card">
    <div class="card-header">
        <h3>Заголовок</h3>
    </div>
    <div class="card-body">
        Содержимое карточки
    </div>
</div>

<!-- Формы -->
<div>
    <label class="form-label">Название поля</label>
    <input type="text" class="form-input" placeholder="Введите значение">
    <div class="form-error">Ошибка валидации</div>
</div>

<!-- Таблицы -->
<table class="table">
    <thead>
        <tr>
            <th>Колонка 1</th>
            <th>Колонка 2</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Данные 1</td>
            <td>Данные 2</td>
        </tr>
    </tbody>
</table>

<!-- Значки -->
<span class="badge badge-primary">Активный</span>
<span class="badge badge-success">Успех</span>
<span class="badge badge-error">Ошибка</span>

<!-- Уведомления -->
<div class="alert alert-success">
    Операция выполнена успешно!
</div>
```

## Темная тема

Система автоматически поддерживает темную тему через `@media (prefers-color-scheme: dark)`. Цвета автоматически инвертируются для темной темы.

## Кастомизация

Для изменения цветовой схемы отредактируйте CSS переменные в `static/src/input.css`:

```css
:root {
  --color-primary-500: #3b82f6; /* Основной цвет */
  --color-primary-600: #2563eb; /* Темнее */
  /* ... */
}
```

После изменения запустите сборку:
```bash
npm run build-css-prod
```

## Интеграция с Django

1. Убедитесь, что `STATIC_URL` и `STATICFILES_DIRS` настроены в `settings.py`
2. Используйте `{% load static %}` в шаблонах
3. Подключайте CSS через `{% static 'css/output.css' %}`
4. Запускайте `python manage.py collectstatic` для продакшена

## Рекомендации

1. **Используйте готовые компоненты** из `input.css` для консистентности
2. **Следуйте принципу mobile-first** при создании адаптивных дизайнов
3. **Используйте CSS переменные** для кастомизации цветов
4. **Запускайте сборку** после изменений в `input.css`
5. **Тестируйте на разных устройствах** для проверки адаптивности
