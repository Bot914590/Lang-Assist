import { useState, useEffect } from 'react';

/**
 * Хук для работы с chrome.storage.local
 */
export function useStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(initialValue);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadValue = async () => {
      try {
        const result = await new Promise<any>((resolve) => {
          chrome.storage.local.get([key], (res: Record<string, any>) => {
            resolve(res);
          });
        });
        setStoredValue(result[key] ?? initialValue);
      } catch (error) {
        console.error('Error loading from storage:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadValue();
  }, [key]);

  const setValue = async (value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      await new Promise<void>((resolve) => {
        chrome.storage.local.set({ [key]: valueToStore }, () => {
          resolve();
        });
      });
    } catch (error) {
      console.error('Error saving to storage:', error);
    }
  };

  return [storedValue, setValue, isLoading] as const;
}
