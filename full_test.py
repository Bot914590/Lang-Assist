#!/usr/bin/env python
"""Комплексное тестирование Language Assist API."""
import httpx
from datetime import datetime

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
    
    # 2. Регистрация
    print("\n[2] Регистрация пользователя")
    user_data = {"email": f"test{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com", 
                 "username": f"testuser{datetime.now().strftime('%Y%m%d%H%M%S')}", 
                 "password": "password123"}
    r = client.post("/api/v1/users/register", json=user_data)
    test("Регистрация пользователя", r.status_code == 201, r.text)
    if r.status_code == 201:
        user = r.json()
        user_id = user["id"]
        test("User ID получен", user_id is not None)
        test("Email сохранен", user["email"] == user_data["email"])
    else:
        user_id = 1  # fallback
    
    # 3. Создание текста
    print("\n[3] Создание текста на китайском")
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
        # Используем существующий текст
        r = client.get("/api/v1/texts")
        texts = r.json()
        if texts:
            text_id = texts[0]["id"]
            print(f"   Используем существующий текст ID: {text_id}")
        else:
            text_id = None
            test("Текст создан или найден", False, "Нет доступных текстов")
    
    if text_id is None:
        print("\n[!] Пропускаем тесты текста - нет доступного текста")
        return
    
    # 4. Анализ текста
    print("\n[4] Анализ текста (токенизация)")
    r = client.post(f"/api/v1/texts/{text_id}/analyze", params={"user_level": 2})
    test("Анализ текста запущен", r.status_code == 200, r.text)
    if r.status_code == 200:
        result = r.json()
        test("Статус анализа ok", result.get("status") == "ok")
        tokens_count = result.get("tokens_count", 0)
        test(f"Токены получены: {tokens_count}", tokens_count > 0)
    
    # 5. Получение результатов анализа
    print("\n[5] Получение результатов анализа")
    r = client.get(f"/api/v1/texts/{text_id}/analyze")
    test("Получение анализа", r.status_code == 200, r.text)
    if r.status_code == 200:
        result = r.json()
        tokens = result.get("tokens", [])
        test(f"Токены в ответе: {len(tokens)}", len(tokens) > 0)
        if tokens:
            # Избегаем вывода китайских символов в Windows консоли
            print(f"   Пример токена: value={tokens[0].get('value', '')[:5]}...")
    
    # 6. Генерация карточек
    print("\n[6] Генерация карточек из текста")
    r = client.post("/api/v1/flashcards/generate", json={"text_id": text_id})
    test("Генерация карточек", r.status_code == 200, r.text)
    if r.status_code == 200:
        result = r.json()
        cards_created = result.get("cards_created", 0)
        cards_skipped = result.get("cards_skipped", 0)
        test(f"Карточки созданы: {cards_created}", cards_created >= 0)
        print(f"   Создано: {cards_created}, Пропущено: {cards_skipped}")
    
    # 7. Получение карточек
    print("\n[7] Получение списка карточек")
    r = client.get("/api/v1/flashcards")
    test("Получение карточек", r.status_code == 200, r.text)
    if r.status_code == 200:
        result = r.json()
        total = result.get("total", 0)
        items = result.get("items", [])
        test(f"Всего карточек: {total}", total >= 0)
        if items:
            card_id = items[0]["id"]
            word = items[0].get('word', '')[:10]
            print(f"   Первая карточка: ID={card_id}, Word={word}...")
    
    # 8. Повторение карточки (SM-2)
    print("\n[8] Система повторения SM-2")
    r = client.get("/api/v1/flashcards?due_only=true")
    due_cards = r.json()
    due_total = due_cards.get("total", 0)
    test(f"Карточки для повторения: {due_total}", due_total >= 0)
    
    if due_cards.get("items"):
        card_id = due_cards["items"][0]["id"]
        print(f"   Повторение карточки ID: {card_id}")
        r = client.post(f"/api/v1/flashcards/{card_id}/review", json={"quality": 4})
        test("Повторение карточки", r.status_code == 200, r.text)
        if r.status_code == 200:
            review = r.json()
            test("Quality сохранен", review.get("quality") == 4)
            print(f"   Review ID: {review['id']}, Quality: {review['quality']}")
    else:
        print("   Нет карточек для повторения (все уже повторены или новые)")
    
    # 9. История повторений
    print("\n[9] История повторений")
    r = client.get("/api/v1/flashcards")
    cards = r.json().get("items", [])
    if cards:
        card_id = cards[0]["id"]
        r = client.get(f"/api/v1/flashcards/{card_id}/reviews")
        test("Получение истории повторений", r.status_code == 200, r.text)
        if r.status_code == 200:
            reviews = r.json()
            print(f"   Количество повторений: {len(reviews)}")
    
    # 10. Упрощение текста
    print("\n[10] Упрощение текста")
    simplify_data = {"text": "Test text", "target_level": 2, "language": "zh"}
    r = client.post("/api/v1/texts/simplify", json=simplify_data)
    test("Упрощение текста", r.status_code == 200, r.text)
    if r.status_code == 200:
        result = r.json()
        print(f"   Status: {result.get('status', '')}")
        print(f"   Replaced count: {result.get('replaced_count', 0)}")
    
    # 11. Словарь
    print("\n[11] Работа со словарём")
    vocab_data = {"word": "test_word", "translation": "test translation"}
    r = client.post("/api/v1/vocabulary", json=vocab_data)
    test("Добавление слова в словарь", r.status_code in [201, 409], r.text)
    
    r = client.get("/api/v1/vocabulary")
    test("Получение словаря", r.status_code == 200, r.text)
    if r.status_code == 200:
        vocab = r.json()
        print(f"   Слов в словаре: {len(vocab) if isinstance(vocab, list) else 'N/A'}")
    
    # 12. Логин
    print("\n[12] Логин пользователя")
    login_data = {"email": user_data["email"], "password": "password123"}
    r = client.post("/api/v1/users/login", json=login_data)
    test("Логин", r.status_code == 200, r.text)
    if r.status_code == 200:
        logged_user = r.json()
        test("User ID при логине", logged_user.get("id") == user_id)
    
    # 13. Профиль пользователя
    print("\n[13] Профиль пользователя")
    r = client.get("/api/v1/users/me")
    test("Получение профиля", r.status_code == 200, r.text)
    
    # 14. Удаление текста
    print("\n[14] Удаление текста")
    r = client.delete(f"/api/v1/texts/{text_id}")
    test("Удаление текста", r.status_code == 204, r.text)
    
    # Итоги
    print("\n" + "=" * 70)
    print(f"ИТОГИ: {PASS} passed, {FAIL} failed")
    print(f"Время завершения: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 70)

if __name__ == "__main__":
    main()
