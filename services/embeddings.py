"""
Сервис для работы с эмбеддингами и семантического поиска.
"""
import os
from typing import List, Dict, Optional, Tuple
import struct
from pathlib import Path


class EmbeddingService:
    """Сервис для загрузки и поиска эмбеддингов."""

    def __init__(self, embeddings_path: Optional[str] = None):
        """
        Инициализировать сервис эмбеддингов.

        Args:
            embeddings_path: Путь к файлу с эмбеддингами (бинарный формат)
        """
        self.embeddings_path = embeddings_path or os.getenv(
            "EMBEDDINGS_PATH",
            "data/light_Tencent_AILab_ChineseEmbedding.bin"
        )
        self.embeddings: Dict[str, List[float]] = {}
        self.vector_size: int = 0
        self.is_loaded: bool = False

    def load_embeddings(self, max_words: Optional[int] = None) -> int:
        """
        Загрузить эмбеддинги из бинарного файла.

        Args:
            max_words: Ограничить количество загружаемых слов (для тестов)

        Returns:
            Количество загруженных слов
        """
        if not os.path.exists(self.embeddings_path):
            print(f"Embeddings file not found: {self.embeddings_path}")
            return 0

        self.embeddings = {}
        count = 0

        try:
            with open(self.embeddings_path, "rb") as f:
                # Чтение заголовка: "<кол-во слов> <размер вектора>"
                header = f.readline().decode("utf-8").strip()
                parts = header.split()
                if len(parts) >= 2:
                    self.vector_size = int(parts[1])
                else:
                    print("Invalid header format")
                    return 0

                while True:
                    # Чтение слова (до пробела)
                    word_bytes = bytearray()
                    while True:
                        b = f.read(1)
                        if not b or b == b" " or b == b"\n":
                            break
                        word_bytes.extend(b)

                    if not word_bytes:
                        break

                    word = word_bytes.decode("utf-8", errors="ignore")

                    # Чтение вектора
                    vector = []
                    for _ in range(self.vector_size):
                        vec_bytes = f.read(4)
                        if len(vec_bytes) < 4:
                            break
                        value = struct.unpack("<f", vec_bytes)[0]
                        vector.append(value)

                    if len(vector) == self.vector_size:
                        self.embeddings[word] = vector
                        count += 1

                    if max_words and count >= max_words:
                        break

            self.is_loaded = True
            print(f"Loaded {count} embeddings")
            return count

        except Exception as e:
            print(f"Error loading embeddings: {e}")
            return 0

    def get_embedding(self, word: str) -> Optional[List[float]]:
        """Получить эмбеддинг для слова."""
        return self.embeddings.get(word)

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Вычислить косинусное сходство между двумя векторами.

        Args:
            vec1: Первый вектор
            vec2: Второй вектор

        Returns:
            Косинусное сходство (от -1 до 1)
        """
        if len(vec1) != len(vec2) or not vec1:
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def find_similar_words(
        self,
        word: str,
        top_k: int = 10,
        min_similarity: float = 0.7,
    ) -> List[Tuple[str, float]]:
        """
        Найти семантически похожие слова.

        Args:
            word: Исходное слово
            top_k: Количество результатов
            min_similarity: Минимальный порог сходства

        Returns:
            Список кортежей (слово, сходство)
        """
        target_embedding = self.get_embedding(word)
        if not target_embedding:
            return []

        similarities = []
        for candidate, embedding in self.embeddings.items():
            if candidate == word:
                continue
            sim = self.cosine_similarity(target_embedding, embedding)
            if sim >= min_similarity:
                similarities.append((candidate, sim))

        # Сортировка по убыванию сходства
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def get_word_mean_embedding(self, words: List[str]) -> Optional[List[float]]:
        """
        Получить усреднённый эмбеддинг для списка слов.

        Args:
            words: Список слов

        Returns:
            Усреднённый вектор или None
        """
        embeddings = [self.get_embedding(w) for w in words if self.get_embedding(w)]
        if not embeddings:
            return None

        vector_size = len(embeddings[0])
        mean_vector = [0.0] * vector_size

        for emb in embeddings:
            for i, val in enumerate(emb):
                mean_vector[i] += val

        for i in range(vector_size):
            mean_vector[i] /= len(embeddings)

        return mean_vector


# Глобальный экземпляр сервиса
embedding_service = EmbeddingService()
