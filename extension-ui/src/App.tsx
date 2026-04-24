import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { useAuth } from './hooks/useAuth';
import { LoginForm } from './components/auth/LoginForm';
import { RegisterForm } from './components/auth/RegisterForm';
import { ForgotPasswordForm } from './components/auth/ForgotPasswordForm';
import { OnboardingWizard } from './components/onboarding/OnboardingWizard';

type AuthView = 'login' | 'register' | 'forgot-password';

function App() {
  const { isAuthenticated, isOnboardingCompleted, isLoading, completeOnboarding, logout } = useAuth();
  const [authView, setAuthView] = useState<AuthView>('login');

  // Показываем загрузку во время проверки сессии
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="relative">
            <div className="w-16 h-16 border-4 border-white/30 border-t-white rounded-full animate-spin" />
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-2xl">🌍</span>
            </div>
          </div>
          <p className="mt-6 text-white/90 font-medium text-lg">Загрузка...</p>
        </div>
      </div>
    );
  }

  // Если пользователь не аутентифицирован - показываем формы входа/регистрации
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        {/* Фоновые декоративные элементы */}
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-white/10 rounded-full blur-3xl" />
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-white/10 rounded-full blur-3xl" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-white/5 rounded-full blur-3xl" />
        </div>

        <div className="w-full max-w-md relative z-10">
          {/* Логотип */}
          <div className="text-center mb-8">
            <motion.div 
              className="inline-flex items-center justify-center w-20 h-20 bg-white/20 backdrop-blur-sm rounded-2xl mb-4 shadow-glow"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.5 }}
            >
              <span className="text-4xl">🌍</span>
            </motion.div>
            <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">Language Assist</h1>
            <p className="text-white/80 font-medium">
              Изучайте языки эффективно с помощью ИИ
            </p>
          </div>

          <AnimatePresence mode="wait">
            {authView === 'login' && (
              <LoginForm
                key="login"
                onSwitchToRegister={() => setAuthView('register')}
                onSwitchToForgotPassword={() => setAuthView('forgot-password')}
                onSuccess={() => {}}
              />
            )}

            {authView === 'register' && (
              <RegisterForm
                key="register"
                onSwitchToLogin={() => setAuthView('login')}
                onSuccess={() => {}}
              />
            )}

            {authView === 'forgot-password' && (
              <ForgotPasswordForm
                key="forgot-password"
                onSwitchToLogin={() => setAuthView('login')}
              />
            )}
          </AnimatePresence>

          {/* Footer */}
          <p className="text-center text-white/60 text-sm mt-8 font-medium">
            © 2024 Language Assist. All rights reserved.
          </p>
        </div>
      </div>
    );
  }

  // Если пользователь аутентифицирован, но не прошел онбординг
  if (!isOnboardingCompleted) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-white/10 rounded-full blur-3xl" />
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-white/10 rounded-full blur-3xl" />
        </div>
        <div className="relative z-10 w-full max-w-lg">
          <OnboardingWizard onComplete={completeOnboarding} />
        </div>
      </div>
    );
  }

  // Если пользователь аутентифицирован и прошел онбординг - показываем главный экран
  return (
    <div className="min-h-screen bg-gradient-primary">
      <header className="bg-white/10 backdrop-blur-md border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🌍</span>
            <h1 className="text-xl font-bold text-white">Language Assist</h1>
          </div>
          <button
            onClick={logout}
            className="text-sm text-white/80 hover:text-white font-medium transition-colors px-4 py-2 rounded-lg hover:bg-white/10"
          >
            Выйти
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-12">
        <div className="text-center py-16">
          <motion.div 
            className="w-24 h-24 bg-white/20 backdrop-blur-sm rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-glow-lg float"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
            <span className="text-5xl">✨</span>
          </motion.div>
          <h2 className="text-3xl font-bold text-white mb-3">
            Добро пожаловать!
          </h2>
          <p className="text-white/80 text-lg max-w-md mx-auto font-medium">
            Приложение готово к работе. Выберите текст для анализа или создайте новые карточки.
          </p>
        </div>
      </main>
    </div>
  );
}

export default App;
