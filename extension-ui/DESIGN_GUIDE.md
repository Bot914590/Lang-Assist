# 🎨 Дизайн-система Language Assist

## Обзор

Современный, минималистичный дизайн с акцентом на типографику, плавные анимации и градиенты.

## Цветовая палитра

### Основные цвета
```
Primary (Фиолетовый):
- 50: #f5f3ff  │ 100: #ede9fe  │ 200: #ddd6fe
- 300: #c4b5fd │ 400: #a78bfa  │ 500: #8b5cf6
- 600: #7c3aed │ 700: #6d28d9  │ 800: #5b21b6
- 900: #4c1d95 │ 950: #2e1065

Accent (Красный):
- 50: #fef2f2  │ 100: #fee2e2  │ 200: #fecaca
- 300: #fca5a5 │ 400: #f87171  │ 500: #ef4444
- 600: #dc2626 │ 700: #b91c1c  │ 800: #991b1b
- 900: #7f1d1d

Dark (Серый):
- 50: #f8fafc  │ 100: #f1f5f9  │ 200: #e2e8f0
- 300: #cbd5e1 │ 400: #94a3b8  │ 500: #64748b
- 600: #475569 │ 700: #334155  │ 800: #1e293b
- 900: #0f172a │ 950: #020617
```

### Градиенты
- **Primary**: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- **Accent**: `linear-gradient(135deg, #f093fb 0%, #f5576c 100%)`
- **Success**: `linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)`
- **Dark**: `linear-gradient(135deg, #1e293b 0%, #0f172a 100%)`

## Типографика

### Шрифт
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
```

### Размеры
- **Заголовки**: 20-24px, font-weight: 700
- **Подзаголовки**: 16-18px, font-weight: 600
- **Основной текст**: 14-16px, font-weight: 400-500
- **Подписи**: 12-14px, font-weight: 500

## Компоненты

### Кнопки

#### Варианты
1. **Primary** - фиолетовая кнопка с тенью
2. **Gradient** - градиентная кнопка с эффектом свечения
3. **Outline** - контурная кнопка
4. **Ghost** - прозрачная кнопка

#### Размеры
- **Sm**: 36px height, padding: 4px 16px
- **Md**: 42px height, padding: 10px 20px
- **Lg**: 52px height, padding: 14px 28px

#### Состояния
- **Hover**: scale(1.02), усиление тени
- **Active**: scale(0.98)
- **Disabled**: opacity(0.6), cursor: not-allowed
- **Loading**: спиннер вместо иконки

### Поля ввода (Input)

#### Стили
- Border: 2px solid #e2e8f0
- Border-radius: 12px
- Padding: 12px 16px
- Focus: border-primary-500 + ring

#### Состояния
- **Default**: серый бордер
- **Focus**: фиолетовый бордер + ring
- **Error**: красный бордер + сообщение
- **Disabled**: серый фон

### Карточки (Card)

#### Стили
- Background: белый с glassmorphism эффектом
- Border-radius: 20px
- Shadow: мягкая тень с размытием
- Border: 1px solid rgba(255, 255, 255, 0.2)

### Уведомления (Alert)

#### Варианты
- **Info**: синий (#eff6ff фон, #1d4ed8 текст)
- **Success**: зеленый (#ecfdf5 фон, #047857 текст)
- **Warning**: желтый (#fef3c7 фон, #b45309 текст)
- **Error**: красный (#fef2f2 фон, #b91c1c текст)

## Анимации

### Длительности
- **Fast**: 0.2s
- **Normal**: 0.3-0.4s
- **Slow**: 0.5s+

### Типы анимаций

#### Появление
```css
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
```

#### Пульсация
```css
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
```

#### Парение
```css
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}
```

#### Shimmer (скелетон)
```css
@keyframes shimmer {
  0% { background-position: -1000px 0; }
  100% { background-position: 1000px 0; }
}
```

## Эффекты

### Glassmorphism
```css
.glass {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}
```

### Glow (Свечение)
```css
.shadow-glow {
  box-shadow: 0 0 40px rgba(124, 58, 237, 0.3);
}

.shadow-glow-lg {
  box-shadow: 0 0 60px rgba(124, 58, 237, 0.4);
}
```

### Градиентный текст
```css
.gradient-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
```

## Онбординг

### Индикатор прогресса
- 3 шага с визуальными маркерами
- Прогресс-бар с плавной анимацией
- Завершенные шаги отмечаются галочкой

### Шаги
1. **Язык и уровень** - выбор с карточками
2. **Интересы** - grid с иконками
3. **Подтверждение** - сводка с иконками

## Формы аутентификации

### Вход
- Email + пароль
- Кнопка Google OAuth
- Ссылка "Забыли пароль?"

### Регистрация
- Email + пароль + подтверждение
- Валидация в реальном времени

### Восстановление
- Только email
- Сообщение об успехе

## Адаптивность

### Breakpoints
- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

### Popup
- Минимальная ширина: 360px
- Рекомендуемая: 400-450px
- Высота: авто с мин. 100vh

## Иконки

### Размеры
- **Small**: 16x16 (20px)
- **Medium**: 20x20 (24px)
- **Large**: 24x24 (28px)

### Стиль
- Outline для неактивных состояний
- Fill для активных состояний
- Градиентные для акцентов

## Тени

```css
shadow-soft: 0 2px 15px -3px rgba(0, 0, 0, 0.07), 0 10px 20px -2px rgba(0, 0, 0, 0.04)
shadow-soft-lg: 0 10px 40px -10px rgba(0, 0, 0, 0.1), 0 20px 25px -5px rgba(0, 0, 0, 0.05)
shadow-glow: 0 0 40px rgba(124, 58, 237, 0.3)
shadow-glow-lg: 0 0 60px rgba(124, 58, 237, 0.4)
```

## Best Practices

1. **Контрастность**: Минимум 4.5:1 для текста
2. **Отступы**: Кратны 4px (4, 8, 12, 16, 24, 32...)
3. **Радиусы**: Кратны 4px (8, 12, 16, 20, 24px)
4. **Анимации**: Ease-out для появления, ease-in-out для микро-взаимодействий
5. **Цвета**: Использовать палитру Tailwind для консистентности
