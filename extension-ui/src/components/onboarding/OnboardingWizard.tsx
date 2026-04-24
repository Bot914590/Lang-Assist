import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  onboardingStep1Schema,
  onboardingStep3Schema,
  type LanguageOption,
  type InterestOption,
  type OnboardingCompleteData,
} from '../../types/auth';
import { authApi, storageApi } from '../../lib/api';
import { Button } from '../ui/Button';
import { Card, CardContent, CardHeader } from '../ui/Card';
import { Alert } from '../ui/Alert';
import { LanguageLevelSelector } from './LanguageLevelSelector';
import { InterestsSelector } from './InterestsSelector';

interface OnboardingWizardProps {
  onComplete: () => void;
}

type Step = 1 | 2 | 3;

export const OnboardingWizard: React.FC<OnboardingWizardProps> = ({
  onComplete,
}) => {
  const [currentStep, setCurrentStep] = useState<Step>(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [selectedLanguage, setSelectedLanguage] = useState<LanguageOption | null>(null);
  const [selectedLevel, setSelectedLevel] = useState<string | null>(null);
  const [selectedInterests, setSelectedInterests] = useState<InterestOption[]>([]);

  const step1Form = useForm({
    resolver: zodResolver(onboardingStep1Schema),
  });

  const step3Form = useForm({
    resolver: zodResolver(onboardingStep3Schema),
  });

  const handleNext = () => {
    if (currentStep < 3) {
      setCurrentStep((currentStep + 1) as Step);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep((currentStep - 1) as Step);
    }
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const session = await storageApi.getSession();
      if (!session) {
        throw new Error('Сессия не найдена');
      }

      const data: OnboardingCompleteData = {
        language: selectedLanguage!,
        level: selectedLevel!,
        interests: selectedInterests,
      };

      await authApi.completeOnboarding(session.token, data);
      await storageApi.setOnboardingCompleted(true);

      onComplete();
    } catch (err: any) {
      setError(err.message || 'Ошибка сохранения данных');
    } finally {
      setIsLoading(false);
    }
  };

  const canProceed = () => {
    switch (currentStep) {
      case 1:
        return selectedLanguage !== null && selectedLevel !== null;
      case 2:
        return selectedInterests.length > 0;
      case 3:
        return true;
      default:
        return false;
    }
  };

  const steps = [
    { title: 'Язык', subtitle: 'Выберите язык и уровень' },
    { title: 'Интересы', subtitle: 'Укажите интересы' },
    { title: 'Готово', subtitle: 'Проверьте данные' },
  ];

  const progress = ((currentStep - 1) / 2) * 100;

  return (
    <Card className="shadow-glow-lg overflow-hidden">
      <CardHeader className="bg-gradient-to-br from-white to-primary-50/50 border-b border-white/50">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-dark-900">Настройка профиля</h2>
            <p className="text-sm text-dark-500 font-medium mt-0.5">
              Шаг {currentStep} из 3
            </p>
          </div>
          <div className="w-12 h-12 bg-gradient-primary rounded-2xl flex items-center justify-center shadow-lg">
            <span className="text-xl">🎯</span>
          </div>
        </div>

        {/* Индикатор прогресса */}
        <div className="relative">
          <div className="h-2 bg-dark-200 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-primary"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
            />
          </div>
          <div className="flex justify-between mt-2">
            {steps.map((step, index) => (
              <motion.div
                key={step.title}
                initial={{ scale: 1 }}
                animate={{ scale: index + 1 <= currentStep ? 1.1 : 1 }}
                className={cn(
                  'flex items-center gap-2',
                  index + 1 <= currentStep ? 'text-primary-600' : 'text-dark-400'
                )}
              >
                <div
                  className={cn(
                    'w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-300',
                    index + 1 <= currentStep
                      ? 'bg-gradient-primary text-white shadow-md'
                      : 'bg-dark-200 text-dark-500'
                  )}
                >
                  {index + 1 < currentStep ? (
                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  ) : (
                    index + 1
                  )}
                </div>
                <span className="text-xs font-semibold hidden sm:inline">{step.title}</span>
              </motion.div>
            ))}
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-6">
        {error && (
          <Alert variant="error" className="mb-5" onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <AnimatePresence mode="wait">
          {/* Шаг 1: Выбор языка и уровня */}
          {currentStep === 1 && (
            <motion.div
              key="step1"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              <LanguageLevelSelector
                selectedLanguage={selectedLanguage}
                selectedLevel={selectedLevel}
                onLanguageChange={setSelectedLanguage}
                onLevelChange={setSelectedLevel}
                error={step1Form.formState.errors.language?.message as string}
              />
            </motion.div>
          )}

          {/* Шаг 2: Выбор интересов */}
          {currentStep === 2 && (
            <motion.div
              key="step2"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              <InterestsSelector
                selectedInterests={selectedInterests}
                onInterestsChange={setSelectedInterests}
                error={step3Form.formState.errors.interests?.message as string}
              />
            </motion.div>
          )}

          {/* Шаг 3: Подтверждение */}
          {currentStep === 3 && (
            <motion.div
              key="step3"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-5"
            >
              <div className="text-center py-6">
                <motion.div
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ delay: 0.1, type: 'spring', stiffness: 500 }}
                  className="w-20 h-20 bg-gradient-success rounded-3xl flex items-center justify-center mx-auto mb-4 shadow-glow-lg"
                >
                  <span className="text-4xl">✨</span>
                </motion.div>
                <h3 className="text-xl font-bold text-dark-900 mb-2">
                  Всё готово!
                </h3>
                <p className="text-dark-500 font-medium">
                  Проверьте выбранные настройки
                </p>
              </div>

              <div className="bg-gradient-to-br from-dark-50 to-white rounded-2xl p-5 space-y-4 border border-dark-200">
                <div className="flex justify-between items-center p-3 bg-white rounded-xl shadow-sm">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">🌍</span>
                    <span className="text-sm font-medium text-dark-500">Язык изучения:</span>
                  </div>
                  <span className="font-bold text-dark-900">
                    {selectedLanguage === 'english' ? (
                      <span className="flex items-center gap-2">
                        🇬🇧 Английский
                      </span>
                    ) : (
                      <span className="flex items-center gap-2">
                        🇨🇳 Китайский
                      </span>
                    )}
                  </span>
                </div>
                <div className="flex justify-between items-center p-3 bg-white rounded-xl shadow-sm">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">📊</span>
                    <span className="text-sm font-medium text-dark-500">Уровень:</span>
                  </div>
                  <span className="font-bold text-dark-900">{selectedLevel}</span>
                </div>
                <div className="p-3 bg-white rounded-xl shadow-sm">
                  <div className="flex items-center gap-3 mb-3">
                    <span className="text-2xl">❤️</span>
                    <span className="text-sm font-medium text-dark-500">Интересы:</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {selectedInterests.map((interest) => (
                      <span
                        key={interest}
                        className="px-3 py-1.5 bg-gradient-primary text-white rounded-full text-xs font-semibold shadow-md"
                      >
                        {interest}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Кнопки навигации */}
        <div className="flex gap-3 mt-6 pt-4 border-t border-dark-100">
          {currentStep > 1 ? (
            <Button
              type="button"
              variant="outline"
              onClick={handleBack}
              className="flex-1"
              size="lg"
              leftIcon={
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
              }
            >
              Назад
            </Button>
          ) : (
            <div className="flex-1" />
          )}

          {currentStep < 3 ? (
            <Button
              type="button"
              onClick={handleNext}
              disabled={!canProceed()}
              className="flex-1"
              size="lg"
              variant="gradient"
              rightIcon={
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              }
            >
              Далее
            </Button>
          ) : (
            <Button
              type="button"
              onClick={handleSubmit}
              isLoading={isLoading}
              className="flex-1"
              size="lg"
              variant="gradient"
            >
              Завершить
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

function cn(...classes: (string | boolean | undefined)[]) {
  return classes.filter(Boolean).join(' ');
}
