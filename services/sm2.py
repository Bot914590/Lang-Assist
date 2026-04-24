"""
Алгоритм SM-2 (SuperMemo-2) для расчёта интервалов повторения карточек.
"""
from datetime import datetime, timedelta
from typing import Tuple


def calculate_sm2(
    quality: int,
    easiness_factor: float = 2.5,
    interval: int = 0,
    repetitions: int = 0,
) -> Tuple[float, int, int]:
    """
    Рассчитать новые параметры карточки по алгоритму SM-2.

    Args:
        quality: Оценка качества ответа (0-5)
        easiness_factor: Текущий коэффициент лёгкости (EF)
        interval: Текущий интервал в днях
        repetitions: Количество успешных повторений подряд

    Returns:
        Кортеж (new_ef, new_interval, new_repetitions)
    """
    # Ограничиваем quality от 0 до 5
    quality = max(0, min(5, quality))

    # Расчёт нового EF (E-Factor)
    # EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    new_ef = easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    new_ef = max(1.3, new_ef)  # EF не может быть меньше 1.3

    # Если качество ответа меньше 3, карточка начинается заново
    if quality < 3:
        new_repetitions = 0
        new_interval = 1
    else:
        new_repetitions = repetitions + 1
        if new_repetitions == 1:
            new_interval = 1
        elif new_repetitions == 2:
            new_interval = 6
        else:
            new_interval = round(interval * new_ef)

    return new_ef, new_interval, new_repetitions


def calculate_next_review(
    quality: int,
    easiness_factor: float = 2.5,
    interval: int = 0,
    repetitions: int = 0,
) -> dict:
    """
    Рассчитать дату следующего повторения и новые параметры.

    Args:
        quality: Оценка качества ответа (0-5)
        easiness_factor: Текущий коэффициент лёгкости
        interval: Текущий интервал в днях
        repetitions: Количество успешных повторений

    Returns:
        Словарь с новыми параметрами и датой следующего повторения
    """
    new_ef, new_interval, new_repetitions = calculate_sm2(
        quality=quality,
        easiness_factor=easiness_factor,
        interval=interval,
        repetitions=repetitions,
    )

    next_review = datetime.now() + timedelta(days=new_interval)

    return {
        "easiness_factor": new_ef,
        "interval": new_interval,
        "repetitions": new_repetitions,
        "next_review": next_review,
    }
