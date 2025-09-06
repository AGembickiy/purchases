# Система дизайна - Система закупок

## 📋 Обзор

Данный документ описывает систему дизайна для проекта "Система закупок". Система построена на основе CSS переменных и Tailwind CSS, обеспечивает единообразный внешний вид и простоту поддержки.

## 🎨 Цветовая палитра

### Основные цвета

```css
/* Основные цвета - синяя палитра */
--color-primary-50: #eff6ff;
--color-primary-100: #dbeafe;
--color-primary-500: #3b82f6;  /* Основной цвет */
--color-primary-600: #2563eb;
--color-primary-700: #1d4ed8;

/* Вторичные цвета - серая палитра */
--color-secondary-500: #64748b;
--color-secondary-600: #475569;
--color-secondary-700: #334155;

/* Нейтральные цвета */
--color-neutral-50: #fafafa;   /* Фон */
--color-neutral-100: #f5f5f5;
--color-neutral-200: #e5e5e5;  /* Границы */
--color-neutral-500: #737373;  /* Текст второстепенный */
--color-neutral-900: #171717;  /* Текст основной */
```

### Специальные цвета

```css
/* Статусы операций */
--color-status-draft: var(--color-neutral-500);      /* Черновик */
--color-status-pending: var(--color-warning-500);    /* Ожидание */
--color-status-processing: var(--color-primary-500); /* В процессе */
--color-status-completed: var(--color-success-500);  /* Завершено */
--color-status-cancelled: var(--color-error-500);    /* Отменено */

/* Приоритеты */
--color-priority-low: var(--color-success-400);      /* Низкий */
--color-priority-medium: var(--color-warning-400);   /* Средний */
--color-priority-high: var(--color-error-400);       /* Высокий */
--color-priority-urgent: var(--color-error-600);     /* Срочный */

/* Категории товаров */
--color-category-electronics: #6366f1;  /* Электроника */
--color-category-office: #8b5cf6;       /* Офис */
--color-category-furniture: #06b6d4;    /* Мебель */
--color-category-supplies: #10b981;     /* Расходники */
--color-category-equipment: #f59e0b;    /* Оборудование */
--color-category-services: #ef4444;     /* Услуги */
```

## 📏 Размеры и отступы

```css
/* Системные размеры */
--header-height: 4rem;
--sidebar-width: 16rem;
--content-max-width: 80rem;
--dashboard-card-min-height: 8rem;
--table-row-height: 3rem;
--form-field-height: 2.75rem;

/* Отступы */
--spacing-xs: 0.25rem;   /* 4px */
--spacing-sm: 0.5rem;    /* 8px */
--spacing-md: 1rem;      /* 16px */
--spacing-lg: 1.5rem;    /* 24px */
--spacing-xl: 2rem;      /* 32px */
--spacing-2xl: 3rem;     /* 48px */

/* Радиусы скругления */
--border-radius-sm: 0.375rem;  /* 6px */
--border-radius-md: 0.5rem;    /* 8px */
--border-radius-lg: 0.75rem;   /* 12px */
--border-radius-xl: 1rem;      /* 16px */
```

## 🧩 Компоненты

### Кнопки

```html
<!-- Основные кнопки -->
<button class="btn btn-primary">Основная кнопка</button>
<button class="btn btn-secondary">Вторичная кнопка</button>
<button class="btn btn-success">Успех</button>
<button class="btn btn-warning">Предупреждение</button>
<button class="btn btn-error">Ошибка</button>
<button class="btn btn-outline">Контурная кнопка</button>

<!-- Кнопки действий -->
<button class="btn-action btn-action-edit">
    <i class="bi bi-pencil mr-2"></i>
    Редактировать
</button>
<button class="btn-action btn-action-delete">
    <i class="bi bi-trash mr-2"></i>
    Удалить
</button>
<button class="btn-action btn-action-view">
    <i class="bi bi-eye mr-2"></i>
    Просмотр
</button>
```

### Карточки дашборда

```html
<!-- Обычная карточка -->
<div class="dashboard-card">
    <div class="flex items-center mb-4">
        <i class="bi bi-building-gear text-primary-600 text-xl mr-3"></i>
        <h3 class="text-lg font-semibold text-neutral-900">Заголовок</h3>
    </div>
    <div class="space-y-3">
        <p>Содержимое карточки</p>
    </div>
</div>

<!-- Метрика дашборда -->
<div class="dashboard-card dashboard-metric">
    <div class="flex items-center justify-center mb-3">
        <i class="bi bi-cart-check text-primary-600 text-2xl"></i>
    </div>
    <div class="dashboard-metric-value text-primary-600">156</div>
    <div class="dashboard-metric-label">Активных заказов</div>
</div>
```

### Статусы и бейджи

```html
<!-- Статусы операций -->
<span class="status-badge status-draft">Черновик</span>
<span class="status-badge status-pending">Ожидание</span>
<span class="status-badge status-processing">В процессе</span>
<span class="status-badge status-completed">Завершено</span>
<span class="status-badge status-cancelled">Отменено</span>

<!-- Приоритеты -->
<span class="priority-badge priority-low">Низкий</span>
<span class="priority-badge priority-medium">Средний</span>
<span class="priority-badge priority-high">Высокий</span>
<span class="priority-badge priority-urgent">Срочный</span>

<!-- Категории товаров -->
<span class="category-badge category-electronics">Электроника</span>
<span class="category-badge category-office">Офис</span>
<span class="category-badge category-furniture">Мебель</span>
```

### Формы

```html
<div class="form-group">
    <label class="form-label">Название поля</label>
    <input type="text" class="form-input-enhanced" placeholder="Введите текст">
</div>

<div class="form-group">
    <label class="form-label">Выпадающий список</label>
    <select class="form-select">
        <option>Выберите опцию</option>
    </select>
</div>

<div class="form-group">
    <label class="form-label">Текстовая область</label>
    <textarea class="form-textarea" placeholder="Многострочный текст"></textarea>
</div>
```

### Таблицы

```html
<table class="data-table">
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
```

### Уведомления

```html
<div class="alert alert-success">Сообщение об успехе</div>
<div class="alert alert-warning">Предупреждение</div>
<div class="alert alert-error">Сообщение об ошибке</div>
<div class="alert alert-info">Информационное сообщение</div>
```

## 📐 Макеты страниц

### Структура страницы

```html
<div class="page-container">
    <div class="page-header">
        <h1 class="page-title">Заголовок страницы</h1>
        <p class="page-subtitle">Подзаголовок</p>
    </div>

    <div class="content-section">
        <h2>Секция контента</h2>
        <!-- Содержимое секции -->
    </div>
</div>
```

### Сетки

```html
<!-- 2 колонки -->
<div class="content-grid content-grid-2">
    <div>Колонка 1</div>
    <div>Колонка 2</div>
</div>

<!-- 3 колонки -->
<div class="content-grid content-grid-3">
    <div>Колонка 1</div>
    <div>Колонка 2</div>
    <div>Колонка 3</div>
</div>

<!-- 4 колонки -->
<div class="content-grid content-grid-4">
    <div>Колонка 1</div>
    <div>Колонка 2</div>
    <div>Колонка 3</div>
    <div>Колонка 4</div>
</div>
```

## 🌙 Темная тема

Система поддерживает автоматическое переключение на темную тему в зависимости от настроек системы пользователя через CSS `@media (prefers-color-scheme: dark)`.

## 🚀 Использование

### 1. Компиляция стилей

```bash
# Компиляция CSS с watch режимом
npx tailwindcss -i ./static/src/input.css -o ./static/css/output.css --watch

# Однократная компиляция
npx tailwindcss -i ./static/src/input.css -o ./static/css/output.css
```

### 2. Подключение в шаблонах

```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/output.css' %}">
<link rel="stylesheet" href="{% static 'css/test.css' %}">
```

### 3. Добавление новых компонентов

Все новые компоненты добавляются в `static/src/input.css` в секцию `@layer components`:

```css
@layer components {
  .my-component {
    @apply bg-white rounded-lg shadow-soft;
    /* Дополнительные стили */
  }
}
```

## 📖 Примеры

Для просмотра всех компонентов в действии посетите:
**URL:** `/companies/style-guide/`

## 🛠 Поддержка

- Все стили используют CSS переменные для простоты изменения
- Поддержка темной темы через CSS переменные
- Responsive дизайн через Tailwind CSS утилиты
- Консистентная анимация и переходы

## ✅ Правила использования

1. **Всегда используйте CSS переменные** вместо фиксированных значений
2. **Следуйте неймингу** компонентов (dashboard-card, btn-action, etc.)
3. **Не используйте !important** без крайней необходимости
4. **Используйте семантические классы** для статусов и приоритетов
5. **Соблюдайте единообразие** в отступах и размерах
