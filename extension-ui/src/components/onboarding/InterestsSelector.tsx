import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../lib/utils';
import type { InterestOption } from '../../types/auth';

interface InterestsSelectorProps {
  selectedInterests: InterestOption[];
  onInterestsChange: (interests: InterestOption[]) => void;
  error?: string;
}

const interestsData: Record<
  InterestOption,
  { label: string; icon: string; gradient: string; color: string }
> = {
  technology: { label: 'Технологии', icon: '💻', gradient: 'from-blue-500 to-cyan-500', color: 'blue' },
  travel: { label: 'Путешествия', icon: '✈️', gradient: 'from-green-500 to-emerald-500', color: 'green' },
  business: { label: 'Бизнес', icon: '💼', gradient: 'from-purple-500 to-pink-500', color: 'purple' },
  culture: { label: 'Культура', icon: '🎭', gradient: 'from-pink-500 to-rose-500', color: 'pink' },
  science: { label: 'Наука', icon: '🔬', gradient: 'from-indigo-500 to-violet-500', color: 'indigo' },
  art: { label: 'Искусство', icon: '🎨', gradient: 'from-yellow-500 to-orange-500', color: 'yellow' },
  sports: { label: 'Спорт', icon: '⚽', gradient: 'from-orange-500 to-red-500', color: 'orange' },
  music: { label: 'Музыка', icon: '🎵', gradient: 'from-red-500 to-rose-500', color: 'red' },
  movies: { label: 'Кино', icon: '🎬', gradient: 'from-teal-500 to-cyan-500', color: 'teal' },
  literature: { label: 'Литература', icon: '📚', gradient: 'from-amber-500 to-yellow-500', color: 'amber' },
};

export const InterestsSelector: React.FC<InterestsSelectorProps> = ({
  selectedInterests,
  onInterestsChange,
  error,
}) => {
  const toggleInterest = (interest: InterestOption) => {
    if (selectedInterests.includes(interest)) {
      onInterestsChange(selectedInterests.filter((i) => i !== interest));
    } else {
      onInterestsChange([...selectedInterests, interest]);
    }
  };

  return (
    <div>
      <label className="block text-sm font-semibold text-dark-700 mb-2">
        Какие темы вас интересуют?
      </label>
      <p className="text-sm text-dark-500 mb-5 font-medium">
        Выберите хотя бы один вариант. Мы подберем тексты по вашим интересам.
      </p>

      <div className="grid grid-cols-2 gap-3">
        {(Object.keys(interestsData) as InterestOption[]).map((interest) => {
          const data = interestsData[interest];
          const isSelected = selectedInterests.includes(interest);

          return (
            <motion.button
              key={interest}
              type="button"
              whileHover={{ scale: 1.03, y: -2 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => toggleInterest(interest)}
              className={cn(
                'p-4 rounded-xl border-2 transition-all duration-300',
                'flex items-center gap-3',
                'hover:shadow-lg',
                isSelected
                  ? `border-transparent bg-gradient-to-br ${data.gradient} text-white shadow-glow`
                  : 'border-dark-200 hover:border-dark-300 bg-white'
              )}
            >
              <span className="text-2xl filter drop-shadow">{data.icon}</span>
              <span className={cn(
                'text-sm font-semibold',
                isSelected ? 'text-white' : 'text-dark-900'
              )}>
                {data.label}
              </span>
              {isSelected && (
                <motion.svg
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="w-5 h-5 ml-auto"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </motion.svg>
              )}
            </motion.button>
          );
        })}
      </div>

      {error && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-4 text-sm text-accent-600 font-medium flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          {error}
        </motion.p>
      )}

      {selectedInterests.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-5 flex flex-wrap gap-2"
        >
          {selectedInterests.map((interest) => {
            const data = interestsData[interest];
            return (
              <motion.span
                key={interest}
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className={cn(
                  'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold shadow-md',
                  `bg-gradient-to-br ${data.gradient} text-white`
                )}
              >
                <span>{data.icon}</span>
                <span>{data.label}</span>
              </motion.span>
            );
          })}
        </motion.div>
      )}
    </div>
  );
};
