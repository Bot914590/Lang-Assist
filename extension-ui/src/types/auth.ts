// Схемы валидации и типы для аутентификации

import { z } from 'zod';

// Схема для входа
export const loginSchema = z.object({
  email: z.string().email('Некорректный email'),
  password: z.string().min(6, 'Пароль должен содержать минимум 6 символов'),
});

export type LoginFormData = z.infer<typeof loginSchema>;

// Схема для регистрации
export const registerSchema = z.object({
  email: z.string().email('Некорректный email'),
  password: z.string().min(6, 'Пароль должен содержать минимум 6 символов'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Пароли не совпадают',
  path: ['confirmPassword'],
});

export type RegisterFormData = z.infer<typeof registerSchema>;

// Схема для восстановления пароля
export const forgotPasswordSchema = z.object({
  email: z.string().email('Некорректный email'),
});

export type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>;

// Типы для онбординга
export const languageOptions = ['english', 'chinese'] as const;
export type LanguageOption = typeof languageOptions[number];

export const levelOptionsEnglish = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'] as const;
export type LevelOptionEnglish = typeof levelOptionsEnglish[number];

export const levelOptionsChinese = ['HSK 1', 'HSK 2', 'HSK 3', 'HSK 4', 'HSK 5', 'HSK 6'] as const;
export type LevelOptionChinese = typeof levelOptionsChinese[number];

export const interestOptions = [
  'technology',
  'travel',
  'business',
  'culture',
  'science',
  'art',
  'sports',
  'music',
  'movies',
  'literature',
] as const;

export type InterestOption = typeof interestOptions[number];

// Схема для шага 1 онбординга (язык)
export const onboardingStep1Schema = z.object({
  language: z.enum([...languageOptions] as [string, ...string[]]).refine(
    (val) => val !== undefined,
    { message: 'Выберите язык для изучения' }
  ),
});

export type OnboardingStep1Data = z.infer<typeof onboardingStep1Schema>;

// Схема для шага 2 онбординга (уровень)
export const onboardingStep2Schema = z.object({
  level: z.string().min(1, 'Выберите ваш текущий уровень'),
});

export type OnboardingStep2Data = z.infer<typeof onboardingStep2Schema>;

// Схема для шага 3 онбординга (интересы)
export const onboardingStep3Schema = z.object({
  interests: z.array(z.enum(interestOptions)).min(1, 'Выберите хотя бы один интерес'),
});

export type OnboardingStep3Data = z.infer<typeof onboardingStep3Schema>;

// Полная схема онбординга
export const onboardingCompleteSchema = z.object({
  language: z.enum(languageOptions),
  level: z.string(),
  interests: z.array(z.enum(interestOptions)).min(1),
});

export type OnboardingCompleteData = z.infer<typeof onboardingCompleteSchema>;

// Типы для пользовательской сессии
export interface UserSession {
  token: string;
  user: {
    id: string;
    email: string;
    name?: string;
  };
  onboardingCompleted: boolean;
}

// Типы для состояний формы
export type FormStatus = 'idle' | 'loading' | 'success' | 'error';

// Типы для ошибок API
export interface ApiError {
  message: string;
  code?: string;
}
