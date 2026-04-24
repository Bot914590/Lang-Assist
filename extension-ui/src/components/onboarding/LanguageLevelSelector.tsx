import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../lib/utils';
import type { LanguageOption } from '../../types/auth';

interface LanguageLevelSelectorProps {
  selectedLanguage: LanguageOption | null;
  selectedLevel: string | null;
  onLanguageChange: (language: LanguageOption) => void;
  onLevelChange: (level: string) => void;
  error?: string;
}

const languageData = {
  english: {
    name: 'Английский',
    flag: '🇬🇧',
    gradient: 'from-blue-500 to-cyan-500',
    levels: ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'],
    levelNames: {
      A1: 'Начальный',
      A2: 'Элементарный',
      B1: 'Средний',
      B2: 'Выше среднего',
      C1: 'Продвинутый',
      C2: 'Владение в совершенстве',
    },
  },
  chinese: {
    name: 'Китайский',
    flag: '🇨🇳',
    gradient: 'from-red-500 to-orange-500',
    levels: ['HSK 1', 'HSK 2', 'HSK 3', 'HSK 4', 'HSK 5', 'HSK 6'],
    levelNames: {
      'HSK 1': 'Начальный (150 слов)',
      'HSK 2': 'Элементарный (300 слов)',
      'HSK 3': 'Средний (600 слов)',
      'HSK 4': 'Выше среднего (1200 слов)',
      'HSK 5': 'Продвинутый (2500 слов)',
      'HSK 6': 'Владение в совершенстве (5000+ слов)',
    },
  },
};

export const LanguageLevelSelector: React.FC<LanguageLevelSelectorProps> = ({
  selectedLanguage,
  selectedLevel,
  onLanguageChange,
  onLevelChange,
  error,
}) => {
  return (
    <div className="space-y-6">
      {/* Выбор языка */}
      <div>
        <label className="block text-sm font-semibold text-dark-700 mb-4">
          Какой язык вы хотите изучать?
        </label>
        <div className="grid grid-cols-2 gap-4">
          {(Object.keys(languageData) as LanguageOption[]).map((lang) => {
            const data = languageData[lang];
            const isSelected = selectedLanguage === lang;

            return (
              <motion.button
                key={lang}
                type="button"
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => {
                  onLanguageChange(lang);
                  onLevelChange('');
                }}
                className={cn(
                  'p-6 rounded-2xl border-2 transition-all duration-300',
                  'flex flex-col items-center gap-3',
                  'hover:shadow-lg',
                  isSelected
                    ? `border-transparent bg-gradient-to-br ${data.gradient} text-white shadow-glow`
                    : 'border-dark-200 hover:border-dark-300 bg-white'
                )}
              >
                <span className="text-4xl filter drop-shadow-lg">{data.flag}</span>
                <span className={cn(
                  'font-semibold text-lg',
                  isSelected ? 'text-white' : 'text-dark-900'
                )}>
                  {data.name}
                </span>
              </motion.button>
            );
          })}
        </div>
      </div>

      {/* Выбор уровня */}
      {selectedLanguage && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <label className="block text-sm font-semibold text-dark-700 mb-4">
            Какой у вас текущий уровень?
          </label>
          <div className="space-y-2">
            {languageData[selectedLanguage].levels.map((level) => {
              const isSelected = selectedLevel === level;
              const levelName =
                languageData[selectedLanguage].levelNames[
                  level as keyof typeof languageData[typeof selectedLanguage]['levelNames']
                ];

              return (
                <motion.button
                  key={level}
                  type="button"
                  whileHover={{ scale: 1.01, x: 4 }}
                  whileTap={{ scale: 0.99 }}
                  onClick={() => onLevelChange(level)}
                  className={cn(
                    'w-full p-4 rounded-xl border-2 transition-all duration-300',
                    'flex items-center justify-between',
                    'hover:shadow-md',
                    isSelected
                      ? 'border-primary-500 bg-gradient-to-r from-primary-50 to-primary-100 shadow-md'
                      : 'border-dark-200 hover:border-dark-300 bg-white'
                  )}
                >
                  <div className="flex items-center gap-4">
                    <div
                      className={cn(
                        'w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold transition-all duration-300',
                        isSelected
                          ? 'bg-gradient-primary text-white shadow-lg'
                          : 'bg-dark-100 text-dark-600'
                      )}
                    >
                      {selectedLanguage === 'chinese'
                        ? level.replace('HSK ', '')
                        : level}
                    </div>
                    <div className="text-left">
                      <p className="font-semibold text-dark-900">{level}</p>
                      <p className="text-sm text-dark-500 font-medium">{levelName}</p>
                    </div>
                  </div>
                  {isSelected && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                    >
                      <svg
                        className="w-6 h-6 text-primary-500"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </motion.div>
                  )}
                </motion.button>
              );
            })}
          </div>
          {error && (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-3 text-sm text-accent-600 font-medium flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              {error}
            </motion.p>
          )}
        </motion.div>
      )}
    </div>
  );
};
