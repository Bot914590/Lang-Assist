import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { motion } from 'framer-motion';
import { forgotPasswordSchema, type ForgotPasswordFormData } from '../../types/auth';
import { authApi } from '../../lib/api';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Alert } from '../ui/Alert';
import { Card, CardContent, CardHeader, CardTitle, CardSubtitle } from '../ui/Card';

interface ForgotPasswordFormProps {
  onSwitchToLogin: () => void;
}

export const ForgotPasswordForm: React.FC<ForgotPasswordFormProps> = ({
  onSwitchToLogin,
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
  });

  const onSubmit = async (data: ForgotPasswordFormData) => {
    setIsLoading(true);
    setError(null);

    try {
      await authApi.forgotPassword(data);
      setSuccess(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка отправки запроса.');
    } finally {
      setIsLoading(false);
    }
  };

  if (success) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
      >
        <Card className="shadow-glow-lg">
          <CardHeader className="bg-gradient-to-br from-emerald-50 to-white">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-gradient-success rounded-xl flex items-center justify-center shadow-lg">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <CardTitle>Проверьте почту</CardTitle>
                <CardSubtitle>Письмо отправлено</CardSubtitle>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-5">
            <Alert variant="success">
              Мы отправили инструкцию по восстановлению пароля на ваш email.
            </Alert>

            <Button onClick={onSwitchToLogin} className="w-full" size="lg" variant="primary">
              Вернуться ко входу
            </Button>
          </CardContent>
        </Card>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
    >
      <Card className="shadow-glow-lg">
        <CardHeader className="bg-gradient-to-br from-amber-50 to-white">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 bg-gradient-accent rounded-xl flex items-center justify-center shadow-lg">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
              </svg>
            </div>
            <div>
              <CardTitle>Восстановление</CardTitle>
              <CardSubtitle>Восстановим ваш пароль</CardSubtitle>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-5">
          {error && (
            <Alert variant="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          <p className="text-sm text-dark-600 font-medium bg-dark-50 p-4 rounded-xl border border-dark-200">
            Введите ваш email, и мы отправим инструкцию по восстановлению пароля.
          </p>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Input
              label="Email"
              type="email"
              placeholder="example@mail.com"
              error={errors.email?.message}
              icon={
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                </svg>
              }
              {...register('email')}
            />

            <Button type="submit" className="w-full" size="lg" isLoading={isLoading} variant="gradient">
              Отправить инструкцию
            </Button>
          </form>

          <button
            onClick={onSwitchToLogin}
            className="w-full text-sm font-medium text-dark-600 hover:text-dark-800 transition-colors flex items-center justify-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Вернуться ко входу
          </button>
        </CardContent>
      </Card>
    </motion.div>
  );
};
