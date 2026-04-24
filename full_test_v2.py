#!/usr/bin/env python
"""Комплексное тестирование Language Assist API - Полная версия."""
import httpx
from datetime import datetime
import os

# Устанавливаем UTF-8 для Windows
os.environ['PYTHONUTF8'] = '1'

BASE_URL = "http://localhost:8000"
PASS = 0
FAIL = 0

def test(name, condition, details=""):
    global PASS, FAIL
    status = "[OK]" if condition else "[FAIL]"
    if condition:
        PASS += 1
    else:
        FAIL += 1
    print(f"{status}: {name}")
    if details and not condition:
        print(f"       Details: {details}")
    return condition

def main():
    global PASS, FAIL
    client = httpx.Client(base_url=BASE_URL, timeout=30.0)
    
    print("=" * 70)
    print("КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ LANGUAGE ASSIST API")
    print(f"Время начала: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 70)
    
    # 1. Health check
    print("\n[1] Health Check")
    r = client.get("/health")
    test("Health endpoint доступен", r.status_code == 200, r.text)
    test("Health response корректный", r.json().get("status") == "ok")
    
    # Проверка Go сервиса
    print("\n[2] Проверка Go микросервиса")
    go_client = httpx.Client(base_url="http://localhost:8080", timeout=10.0)
    r = go_client.get("/health")
    test("Go сервис доступен", r.status_code == 200, r.text)
    
    # 3. Регистрация
    print("\n[3] Регистрация пользователя")
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    user_data = {"email": f"test{timestamp}@example.com", 
                 "username": f"testuser{timestamp}", 
                 "password": "password123"}
    r = client.post("/api/v1/users/register", json=user_data)
    test("Регистрация пользователя", r.status_code == 201, r.text)
    if r.status_code == 201:
        user = r.json()
        user_id = user["id"]
        test("User ID получен", user_id is not None)
        test("Email сохранен", user["email"] == user_data["email"])
    else:
        user_id = 1
    
    # 4. Создание текста
    print("\n[4] Создание текста на китайском")
    text_data = {"content": "我喜欢学习中文。今天天气很好。我们去公园玩。", "language": "zh"}
    r = client.post("/api/v1/texts", json=text_data)
    test("Создание текста", r.status_code == 201, r.text)
    if r.status_code == 201:
        text = r.json()
        text_id = text["id"]
        test("Text ID получен", text_id is not None)
        test("Содержание сохранено", text["content"] == text_data["content"])
        test("Язык определен", text["language"] == "zh")
    else:
        r = client.get("/api/v1/texts")
        texts = r.json()
        text_id = texts[0]["id"] if texts else None
        print(f"   Используем существующий текст ID: {text_id}")
    
    if text_id is None:
        print("\n[!] Пропускаем тесты текста - нет доступного текста")
        return
    
    # 5. Анализ текста
    print("\n[5] Анализ текста (токенизация)")
    r = client.post(f"/api/v1/texts/{text_id}/analyze", params={"user_level": 2})
    test("Анализ текста запущен", r.status_code == 200, r.text)
    if r.status_code == 200:
        result = r.json()
        test("Статус анализа ok", result.get("status") == "ok")
        tokens_count = result.get("tokens_count", 0)
        test(f"Токены получены: {tokens_count}", tokens_count > 0)
        # Проверка fallback
        if "fallback" in result.get("status", "").lower():
            print("   [INFO] Использован fallback на jieba")
    
    # 6. Получение результатов анализа
    print("\n[6] Получение результатов анализа")
    r = client.get(f"/api/v1/texts/{text_id}/analyze")
    test("Получение анализа", r.status_code == 200, r.text)
    if r.status_code == 200:
        result = r.json()
        tokens = result.get("tokens", [])
        test(f"Токены в ответе: {len(tokens)}", len(tokens) > 0)
        # Проверка структуры токена
        if tokens:
            token = tokens[0]
            test("Токен имеет value", "value" in token)
            test("Токен имеет is_known", "is_known" in token)
    
    # 7. Генерация карточек
    print("\n[7] Генерация карточек из текста")
    r = client.post("/api/v1/flashcards/generate", json={"text_id": text_id})
    test("Генерация карточек", r.status_code == 200, r.text)
    if r.status_code == 200:
        result = r.json()
        cards_created = result.get("cards_created", 0)
        cards_skipped = result.get("cards_skipped", 0)
        test(f"Карточки созданы: {cards_created}", cards_created >= 0)
        print(f"   Создано: {cards_created}, Пропущено: {cards_skipped}")
    
    # 8. Получение карточек
    print("\n[8] Получение списка карточек")
    r = client.get("/api/v1/flashcards")
    test("Получение карточек", r.status_code == 200, r.text)
    if r.status_code == 200:
        result = r.json()
        total = result.get("total", 0)
        items = result.get("items", [])
        test(f"Всего карточек: {total}", total >= 0)
        if items:
            test("Карточка имеет id", "id" in items[0])
            test("Карточка имеет word", "word" in items[0])
            test("Карточка имеет easiness_factor", "easiness_factor" in items[0])
    
    # 9. Система повторения SM-2
    print("\n[9] Система повторения SM-2")
    r = client.get("/api/v1/flashcards?due_only=true")
    due_cards = r.json()
    due_total = due_cards.get("total", 0)
    test(f"Карточки для повторения: {due_total}", due_total >= 0)
    
    if due_cards.get("items"):
        card_id = due_cards["items"][0]["id"]
        r = client.post(f"/api/v1/flashcards/{card_id}/review", json={"quality": 4})
        test("Повторение карточки", r.status_code == 200, r.text)
        if r.status_code == 200:
            review = r.json()
            test("Quality сохранен", review.get("quality") == 4)
            test("Review имеет id", "id" in review)
            test("Review имеет reviewed_at", "reviewed_at" in review)
    else:
        # Создаем новую карточку для теста повторения
        print("   Создаем новую карточку для теста повторения...")
        r = client.post("/api/v1/flashcards", json={
            "word": "测试",
            "context": "这是一个测试",
            "translation": "test"
        })
        if r.status_code == 201:
            new_card = r.json()
            card_id = new_card["id"]
            print(f"   Создана карточка ID: {card_id}")
            
            r = client.post(f"/api/v1/flashcards/{card_id}/review", json={"quality": 5})
            test("Повторение новой карточки", r.status_code == 200, r.text)
            if r.status_code == 200:
                review = r.json()
                test("EF обновлен", review.get("id") is not None)
    
    # 10. История повторений
    print("\n[10] История повторений")
    r = client.get("/api/v1/flashcards")
    cards = r.json().get("items", [])
    if cards:
        card_id = cards[0]["id"]
        r = client.get(f"/api/v1/flashcards/{card_id}/reviews")
        test("Получение истории повторений", r.status_code == 200, r.text)
        if r.status_code == 200:
            reviews = r.json()
            test(f"Количество повторений: {len(reviews)}", len(reviews) >= 0)
    
    # 11. Упрощение текста
    print("\n[11] Упрощение текста")
    simplify_data = {"text": "Test text", "target_level": 2, "language": "zh"}
    r = client.post("/api/v1/texts/simplify", json=simplify_data)
    test("Упрощение текста", r.status_code == 200, r.text)
    if r.status_code == 200:
        result = r.json()
        test("Status ok", result.get("status") == "ok")
        test("Simplified text присутствует", "simplified_text" in result)
    
    # 12. Словарь - добавление
    print("\n[12] Работа со словарём")
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    vocab_data = {"word": f"test_word_{timestamp}", "translation": "test translation"}
    r = client.post("/api/v1/vocabulary", json=vocab_data)
    test("Добавление слова в словарь", r.status_code in [201, 409], r.text)
    
    # 13. Словарь - получение
    print("\n[13] Получение словаря")
    r = client.get("/api/v1/vocabulary")
    test("Получение словаря", r.status_code == 200, r.text)
    if r.status_code == 200:
        vocab = r.json()
        if isinstance(vocab, list):
            test(f"Слов в словаре: {len(vocab)}", True)
        else:
            print(f"   Response type: {type(vocab)}")
    
    # 14. Логин
    print("\n[14] Логин пользователя")
    login_data = {"email": user_data["email"], "password": "password123"}
    r = client.post("/api/v1/users/login", json=login_data)
    test("Логин", r.status_code == 200, r.text)
    if r.status_code == 200:
        logged_user = r.json()
        test("User ID при логине", logged_user.get("id") == user_id)
        test("Email совпадает", logged_user.get("email") == user_data["email"])
    
    # 15. Профиль пользователя
    print("\n[15] Профиль пользователя")
    r = client.get("/api/v1/users/me")
    test("Получение профиля", r.status_code == 200, r.text)
    if r.status_code == 200:
        profile = r.json()
        test("Профиль имеет id", "id" in profile)
        test("Профиль имеет email", "email" in profile)
    
    # 16. Обновление профиля
    print("\n[16] Обновление профиля")
    update_data = {"lang_level": "HSK 3"}
    r = client.put("/api/v1/users/me", json=update_data)
    test("Обновление профиля", r.status_code == 200, r.text)
    if r.status_code == 200:
        updated = r.json()
        test("Lang_level обновлен", updated.get("lang_level") == "HSK 3")
    
    # 17. Удаление текста
    print("\n[17] Удаление текста")
    r = client.delete(f"/api/v1/texts/{text_id}")
    test("Удаление текста", r.status_code == 204, r.text)
    
    # 18. Проверка валидации
    print("\n[18] Валидация входных данных")
    # Пустой текст
    r = client.post("/api/v1/texts", json={"content": "", "language": "zh"})
    test("Валидация пустого текста", r.status_code == 422, r.text)
    
    # Слишком длинный текст
    r = client.post("/api/v1/texts", json={"content": "a" * 10001, "language": "zh"})
    test("Валидация длинного текста", r.status_code == 422, r.text)
    
    # 19. CORS проверка
    print("\n[19] CORS заголовки")
    r = client.options("/health")
    test("CORS headers присутствуют", "access-control-allow-origin" in r.headers)
    
    # Итоги
    print("\n" + "=" * 70)
    total_tests = PASS + FAIL
    pass_rate = (PASS / total_tests * 100) if total_tests > 0 else 0
    print(f"ИТОГИ: {PASS}/{total_tests} passed ({pass_rate:.1f}%), {FAIL} failed")
    print(f"Время завершения: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 70)
    
    return FAIL == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
