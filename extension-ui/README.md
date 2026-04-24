# Language Assist Chrome Extension

React + TypeScript приложение для Chrome расширения Language Assist.

## 🚀 Быстрый старт

### Установка зависимостей

```bash
npm install
```

### Запуск в режиме разработки

```bash
npm run dev
```

### Сборка для продакшена

```bash
npm run build
```

## 📁 Структура проекта

```
extension-ui/
├── public/
│   ├── manifest.json          # Конфигурация Chrome расширения
│   └── icons/                 # Иконки расширения
├── src/
│   ├── components/
│   │   ├── auth/              # Компоненты аутентификации
│   │   │   ├── LoginForm.tsx
│   │   │   ├── RegisterForm.tsx
│   │   │   └── ForgotPasswordForm.tsx
│   │   ├── onboarding/        # Компоненты онбординга
│   │   │   ├── OnboardingWizard.tsx
│   │   │   ├── LanguageLevelSelector.tsx
│   │   │   └── InterestsSelector.tsx
│   │   └── ui/                # Базовые UI компоненты
│   │       ├── Button.tsx
│   │       ├── Input.tsx
│   │       ├── Card.tsx
│   │       └── Alert.tsx
│   ├── hooks/                 # Кастомные хуки
│   │   ├── useAuth.ts
│   │   └── useStorage.ts
│   ├── lib/                   # Утилиты и API
│   │   ├── utils.ts
│   │   └── api.ts
│   ├── types/                 # TypeScript типы
│   │   └── auth.ts
│   ├── App.tsx                # Главный компонент
│   ├── main.tsx               # Точка входа
│   └── index.css              # Глобальные стили
├── .env.example               # Пример переменных окружения
├── tailwind.config.js         # Конфигурация Tailwind CSS
├── vite.config.ts             # Конфигурация Vite
└── package.json
```

## 🔧 Технологии

- **React 19** - UI библиотека
- **TypeScript** - Типизация
- **Vite** - Сборщик
- **Tailwind CSS** - Стилизация
- **Framer Motion** - Анимации
- **React Hook Form** - Управление формами
- **Zod** - Валидация схем
- **Chrome Storage API** - Хранение данных

## 📦 Установка расширения в Chrome

1. Соберите проект:
   ```bash
   npm run build
   ```

2. Откройте Chrome и перейдите на страницу `chrome://extensions/`

3. Включите "Режим разработчика" (переключатель в правом верхнем углу)

4. Нажмите "Загрузить распакованное расширение" и выберите папку `dist`

5. Расширение появится в панели расширений

## 🔐 Настройка API

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Измените `VITE_API_URL` на адрес вашего API сервера.

## 🎨 Компоненты

### Аутентификация

- **LoginForm** - Форма входа с email/password и Google OAuth
- **RegisterForm** - Форма регистрации с валидацией паролей
- **ForgotPasswordForm** - Форма восстановления пароля

### Онбординг

- **OnboardingWizard** - Мастер настройки из 3 шагов
- **LanguageLevelSelector** - Выбор языка и уровня (A1-C2 / HSK 1-6)
- **InterestsSelector** - Выбор интересов пользователя

### UI компоненты

- **Button** - Кнопка с вариантами и состоянием загрузки
- **Input** - Поле ввода с лейблом и ошибкой
- **Card** - Карточка с заголовком и содержимым
- **Alert** - Сообщение об успехе/ошибке

## 📝 Функционал

1. **Экран входа** - появляется при первом открытии
2. **Email/Password аутентификация** - с валидацией через Zod
3. **Google OAuth** - вход через Google аккаунт
4. **Восстановление пароля** - отправка инструкции на email
5. **Онбординг из 3 шагов**:
   - Выбор языка (английский/китайский)
   - Выбор уровня (A1-C2 или HSK 1-6)
   - Выбор интересов (10 категорий)
6. **Сохранение токена** - в chrome.storage.local
7. **Плавные анимации** - с помощью Framer Motion

## 🎯 Типизация

Все компоненты строго типизированы. Типы определены в `src/types/auth.ts`:

```typescript
// Пример использования
import type { LoginFormData, UserSession } from './types/auth';
```

## 🧪 Тестирование

```bash
npm run lint
npm run build
```

## 📄 Лицензия

MIT
