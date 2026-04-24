"""
Клиент для подключения к Go микросервису анализа текста.
С обработкой ошибок, retry механизмом и fallback на jieba.
"""
import httpx
import os
import time
import logging
from typing import List, Dict, Any, Optional
from functools import wraps

# Настройка логирования
logger = logging.getLogger(__name__)

GO_ANALYZER_URL = os.getenv("GO_ANALYZER_URL", "http://localhost:8080")
GO_ANALYZER_TIMEOUT = float(os.getenv("GO_ANALYZER_TIMEOUT", "30.0"))
GO_ANALYZER_MAX_RETRIES = int(os.getenv("GO_ANALYZER_MAX_RETRIES", "3"))
GO_ANALYZER_RETRY_DELAY = float(os.getenv("GO_ANALYZER_RETRY_DELAY", "1.0"))


def retry_on_failure(max_retries: int = GO_ANALYZER_MAX_RETRIES, delay: float = GO_ANALYZER_RETRY_DELAY):
    """Декоратор для retry при ошибках сети."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    result = func(*args, **kwargs)
                    if result is not None:
                        return result
                except httpx.ConnectError as e:
                    last_exception = e
                    logger.warning(f"Go service connection error (attempt {attempt + 1}/{max_retries}): {e}")
                except httpx.TimeoutException as e:
                    last_exception = e
                    logger.warning(f"Go service timeout (attempt {attempt + 1}/{max_retries}): {e}")
                except httpx.HTTPStatusError as e:
                    logger.error(f"Go service HTTP error {e.response.status_code}: {e}")
                    return None
                except Exception as e:
                    logger.error(f"Unexpected error calling Go service: {e}")
                    return None
                
                if attempt < max_retries - 1:
                    time.sleep(delay * (attempt + 1))  # Exponential backoff
            
            if last_exception:
                logger.error(f"Go service unavailable after {max_retries} attempts: {last_exception}")
            return None
        return wrapper
    return decorator


class GoAnalyzerClient:
    """Клиент для взаимодействия с Go analyzer сервисом."""

    def __init__(self, base_url: str = GO_ANALYZER_URL):
        self.base_url = base_url
        self.timeout = GO_ANALYZER_TIMEOUT
        self._health_cache = None
        self._health_cache_time = 0

    def is_available(self) -> bool:
        """Проверить доступность Go сервиса (с кэшированием)."""
        current_time = time.time()
        # Кэшируем результат на 10 секунд
        if self._health_cache is not None and (current_time - self._health_cache_time) < 10:
            return self._health_cache
        
        self._health_cache = self.health_check()
        self._health_cache_time = current_time
        return self._health_cache

    @retry_on_failure()
    def analyze_text(
        self,
        text: str,
        language: str = "zh",
        user_level: int = 1,
    ) -> Optional[Dict[str, Any]]:
        """
        Отправить текст на анализ в Go микросервис.

        Args:
            text: Текст для анализа
            language: Код языка (zh, en, etc.)
            user_level: Уровень пользователя (для HSK)

        Returns:
            Словарь с результатами анализа или None при ошибке
        """
        payload = {
            "text": text,
            "lang": language,
            "user_level": user_level,
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/analyze",
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()
                logger.info(f"Go analyze response: status={result.get('status')}, tokens_count={result.get('tokens_count')}")
                if result.get('tokens'):
                    logger.info(f"First token: {result['tokens'][0]}")
                return result
        except Exception as e:
            logger.error(f"Error calling Go analyze: {e}")
            raise  # Re-raise для обработки в декораторе

    @retry_on_failure()
    def simplify_text(
        self,
        text: str,
        target_level: int,
        language: str = "zh",
    ) -> Optional[Dict[str, Any]]:
        """
        Упростить текст до целевого уровня HSK.

        Args:
            text: Текст для упрощения
            target_level: Целевой уровень HSK (1-6)
            language: Код языка

        Returns:
            Словарь с результатами упрощения или None при ошибке
        """
        payload = {
            "text": text,
            "lang": language,
            "target_level": target_level,
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/simplify",
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()
                logger.debug(f"Go simplify response: {result.get('status')} - {result.get('replaced_count')} replacements")
                return result
        except Exception as e:
            logger.error(f"Error calling Go simplify: {e}")
            raise  # Re-raise для обработки в декораторе

    @retry_on_failure()
    def get_word_info(self, word: str) -> Optional[Dict[str, Any]]:
        """
        Получить информацию о слове (HSK уровень, pinyin, перевод).

        Args:
            word: Слово для поиска

        Returns:
            Словарь с информацией о слове или None при ошибке
        """
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.base_url}/word/info",
                    params={"word": word},
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error calling Go word info: {e}")
            raise

    def health_check(self) -> bool:
        """Проверить доступность Go сервиса."""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/health")
                is_ok = response.status_code == 200
                if is_ok:
                    logger.debug("Go service health check: OK")
                else:
                    logger.warning(f"Go service health check: {response.status_code}")
                return is_ok
        except Exception as e:
            logger.error(f"Go service health check failed: {e}")
            return False

    def analyze_text_with_fallback(
        self,
        text: str,
        language: str = "zh",
        user_level: int = 1,
    ) -> Optional[Dict[str, Any]]:
        """
        Анализ текста с fallback на jieba если Go сервис недоступен.

        Args:
            text: Текст для анализа
            language: Код языка
            user_level: Уровень пользователя

        Returns:
            Результаты анализа или None при полной неудаче
        """
        # Пытаемся через Go сервис
        if self.is_available():
            result = self.analyze_text(text, language, user_level)
            if result is not None:
                logger.info(f"Go analyze result: {len(result.get('tokens', []))} tokens")
                # Проверяем positions
                for token in result.get('tokens', [])[:3]:
                    logger.info(f"Token '{token.get('value')}': positions={token.get('positions')}")
                return result

        # Fallback на jieba
        logger.info("Falling back to jieba for tokenization")
        return self._analyze_with_jieba(text, language, user_level)

    def _analyze_with_jieba(self, text: str, language: str, user_level: int) -> Dict[str, Any]:
        """Локальная токенизация через jieba (fallback)."""
        try:
            import jieba
            
            if language.startswith("zh"):
                tokens_list = list(jieba.cut(text, cut_all=False))
                tokens_list = [t for t in tokens_list if t.strip()]
            else:
                tokens_list = text.split()
            
            # Подсчёт частотности
            freq_map = {}
            for token in tokens_list:
                freq_map[token] = freq_map.get(token, 0) + 1
            
            tokens = []
            for value, frequency in freq_map.items():
                tokens.append({
                    "value": value,
                    "frequency": frequency,
                    "hsk": 0,  # Неизвестно
                    "is_known": False,
                })
            
            return {
                "status": "ok (fallback)",
                "tokens_count": len(tokens_list),
                "tokens": tokens,
                "fallback": True,
            }
        except ImportError:
            logger.error("jieba not installed, cannot fallback")
            return None
        except Exception as e:
            logger.error(f"Fallback tokenization error: {e}")
            return None


# Глобальный экземпляр клиента для analyzer
go_analyzer = GoAnalyzerClient()

# Глобальный экземпляр клиента для simplifier (на другом порту)
GO_SIMPLIFIER_URL = os.getenv("GO_SIMPLIFIER_URL", "http://localhost:8081")
go_simplifier = GoAnalyzerClient(base_url=GO_SIMPLIFIER_URL)
