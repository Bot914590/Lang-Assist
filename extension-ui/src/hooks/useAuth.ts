import { useState, useEffect, useCallback } from 'react';
import { storageApi } from '../lib/api';
import type { UserSession } from '../types/auth';

/**
 * Хук для управления состоянием аутентификации
 */
export function useAuth() {
  const [session, setSession] = useState<UserSession | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Загрузка сессии при монтировании
  useEffect(() => {
    const loadSession = async () => {
      try {
        const savedSession = await storageApi.getSession();
        setSession(savedSession);
      } catch (error) {
        console.error('Failed to load session:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadSession();
  }, []);

  // Вход
  const login = useCallback(async (newSession: UserSession) => {
    await storageApi.setSession(newSession);
    setSession(newSession);
  }, []);

  // Выход
  const logout = useCallback(async () => {
    await storageApi.clearSession();
    setSession(null);
  }, []);

  // Завершение онбординга
  const completeOnboarding = useCallback(async () => {
    if (session) {
      const updatedSession = { ...session, onboardingCompleted: true };
      await storageApi.setSession(updatedSession);
      setSession(updatedSession);
    }
  }, [session]);

  return {
    session,
    isLoading,
    isAuthenticated: !!session,
    isOnboardingCompleted: session?.onboardingCompleted ?? false,
    login,
    logout,
    completeOnboarding,
  };
}
