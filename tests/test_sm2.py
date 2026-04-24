"""
Unit тесты для алгоритма SM-2 (Spaced Repetition).
"""
import pytest
from datetime import datetime, timedelta
from services.sm2 import calculate_sm2, calculate_next_review


class TestCalculateSM2:
    """Тесты для функции calculate_sm2."""

    def test_perfect_quality_5(self):
        """Оценка 5 (отлично) - интервал увеличивается."""
        ef, interval, repetitions = calculate_sm2(
            quality=5,
            easiness_factor=2.5,
            interval=1,
            repetitions=1,
        )
        assert ef > 2.5  # EF увеличивается
        assert interval > 1  # Интервал увеличивается
        assert repetitions == 2  # Повторения увеличиваются

    def test_good_quality_4(self):
        """Оценка 4 (хорошо) - интервал увеличивается."""
        ef, interval, repetitions = calculate_sm2(
            quality=4,
            easiness_factor=2.5,
            interval=1,
            repetitions=1,
        )
        assert repetitions == 2
        assert interval > 1

    def test_passable_quality_3(self):
        """Оценка 3 (удовлетворительно) - минимальный проходной балл."""
        ef, interval, repetitions = calculate_sm2(
            quality=3,
            easiness_factor=2.5,
            interval=1,
            repetitions=1,
        )
        assert repetitions == 2
        # Интервал должен увеличиться, но не сильно

    def test_poor_quality_2_reset(self):
        """Оценка 2 (плохо) - сброс повторений."""
        ef, interval, repetitions = calculate_sm2(
            quality=2,
            easiness_factor=2.5,
            interval=10,
            repetitions=5,
        )
        assert repetitions == 0  # Сброс
        assert interval == 1  # Начальный интервал

    def test_poor_quality_0_reset(self):
        """Оценка 0 (очень плохо) - полный сброс."""
        ef, interval, repetitions = calculate_sm2(
            quality=0,
            easiness_factor=2.5,
            interval=20,
            repetitions=10,
        )
        assert repetitions == 0
        assert interval == 1

    def test_ef_decreases_on_poor_quality(self):
        """EF уменьшается при плохой оценке."""
        initial_ef = 2.5
        ef, _, _ = calculate_sm2(
            quality=2,
            easiness_factor=initial_ef,
            interval=1,
            repetitions=1,
        )
        assert ef < initial_ef

    def test_ef_minimum_limit(self):
        """EF не может быть меньше 1.3."""
        ef, _, _ = calculate_sm2(
            quality=0,
            easiness_factor=1.5,  # Низкий начальный EF
            interval=1,
            repetitions=1,
        )
        assert ef >= 1.3

    def test_first_repetition_interval(self):
        """Первое повторение - интервал 1 день."""
        _, interval, repetitions = calculate_sm2(
            quality=5,
            easiness_factor=2.5,
            interval=0,
            repetitions=0,
        )
        assert repetitions == 1
        assert interval == 1

    def test_second_repetition_interval(self):
        """Второе повторение - интервал 6 дней."""
        _, interval, repetitions = calculate_sm2(
            quality=5,
            easiness_factor=2.5,
            interval=1,
            repetitions=1,
        )
        assert repetitions == 2
        assert interval == 6

    def test_third_repetition_interval(self):
        """Третье повторение - интервал умножается на EF."""
        _, interval, repetitions = calculate_sm2(
            quality=5,
            easiness_factor=2.5,
            interval=6,
            repetitions=2,
        )
        assert repetitions == 3
        # Интервал = round(6 * 2.5) = 15, но может быть 16 из-за округления EF
        assert interval in [15, 16]  # 15-16 дней

    def test_quality_bounds(self):
        """Проверка ограничения quality от 0 до 5."""
        # Quality > 5 должен обрабатываться как 5
        ef1, _, _ = calculate_sm2(quality=10, easiness_factor=2.5, interval=1, repetitions=1)
        ef2, _, _ = calculate_sm2(quality=5, easiness_factor=2.5, interval=1, repetitions=1)
        assert ef1 == ef2

        # Quality < 0 должен обрабатываться как 0
        ef3, _, _ = calculate_sm2(quality=-5, easiness_factor=2.5, interval=1, repetitions=1)
        ef4, _, _ = calculate_sm2(quality=0, easiness_factor=2.5, interval=1, repetitions=1)
        assert ef3 == ef4


class TestCalculateNextReview:
    """Тесты для функции calculate_next_review."""

    def test_returns_correct_structure(self):
        """Функция возвращает правильную структуру."""
        result = calculate_next_review(
            quality=4,
            easiness_factor=2.5,
            interval=1,
            repetitions=1,
        )
        assert "easiness_factor" in result
        assert "interval" in result
        assert "repetitions" in result
        assert "next_review" in result

    def test_next_review_is_future(self):
        """Дата следующего повторения в будущем."""
        result = calculate_next_review(
            quality=4,
            easiness_factor=2.5,
            interval=1,
            repetitions=1,
        )
        assert result["next_review"] > datetime.now()

    def test_next_review_date_accuracy(self):
        """Точность даты следующего повторения."""
        result = calculate_next_review(
            quality=5,
            easiness_factor=2.5,
            interval=1,
            repetitions=1,
        )
        expected_date = datetime.now() + timedelta(days=6)  # Второе повторение
        # Сравниваем с точностью до 1 дня (чтобы избежать проблем с временем выполнения теста)
        assert abs((result["next_review"].date() - expected_date.date()).days) <= 1

    def test_poor_quality_resets_schedule(self):
        """Плохая оценка сбрасывает расписание."""
        result = calculate_next_review(
            quality=2,
            easiness_factor=2.5,
            interval=10,
            repetitions=5,
        )
        assert result["repetitions"] == 0
        assert result["interval"] == 1
        # Дата следующего повторения - завтра
        expected_date = datetime.now() + timedelta(days=1)
        assert abs((result["next_review"].date() - expected_date.date()).days) <= 1


class TestSM2Integration:
    """Интеграционные тесты для SM-2."""

    def test_full_learning_cycle(self):
        """Полный цикл обучения: от первого повторения до запоминания."""
        ef = 2.5
        interval = 0
        repetitions = 0

        # Симуляция 5 успешных повторений
        for i in range(5):
            ef, interval, repetitions = calculate_sm2(
                quality=5,  # Всегда отлично
                easiness_factor=ef,
                interval=interval,
                repetitions=repetitions,
            )

        assert repetitions == 5
        assert interval > 1  # Интервал должен вырасти
        assert ef > 2.5  # EF должен вырасти

    def test_alternating_quality(self):
        """Чередование хороших и плохих оценок."""
        ef = 2.5
        interval = 0
        repetitions = 0

        # Хорошее повторение
        ef, interval, repetitions = calculate_sm2(
            quality=5, easiness_factor=ef, interval=interval, repetitions=repetitions
        )
        assert repetitions == 1

        # Плохое повторение - сброс
        ef, interval, repetitions = calculate_sm2(
            quality=2, easiness_factor=ef, interval=interval, repetitions=repetitions
        )
        assert repetitions == 0
        assert interval == 1

    def test_long_term_retention(self):
        """Долгосрочное запоминание (30+ дней)."""
        ef = 2.5
        interval = 0
        repetitions = 0

        # 10 успешных повторений
        for _ in range(10):
            ef, interval, repetitions = calculate_sm2(
                quality=4,
                easiness_factor=ef,
                interval=interval,
                repetitions=repetitions,
            )

        # После 10 повторений интервал должен быть большим
        assert interval > 30  # Больше месяца
        assert repetitions == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
