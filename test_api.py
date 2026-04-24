#!/usr/bin/env python
"""Тестирование API Language Assist."""
import httpx
import json

BASE_URL = "http://localhost:8000"

def test_api():
    client = httpx.Client(base_url=BASE_URL, timeout=30.0)
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ LANGUAGE ASSIST API")
    print("=" * 60)
    
    # 1. Health check
    print("\n1. Проверка health endpoint...")
    r = client.get("/health")
    print(f"   Status: {r.status_code}, Response: {r.json()}")
    
    # 2. Регистрация пользователя
    print("\n2. Регистрация пользователя...")
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123"
    }
    r = client.post("/api/v1/users/register", json=user_data)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        user = r.json()
        print(f"   User: {user}")
        user_id = user['id']
    elif r.status_code == 400:
        print(f"   Error: {r.json()}")
        user_id = 1  # Используем дефолтного
    else:
        print(f"   Error: {r.text}")
        user_id = 1
    
    # 3. Создание текста
    print("\n3. Создание текста на китайском...")
    text_data = {
        "content": "我喜欢学习中文。今天天气很好。我们去公园玩。",
        "language": "zh"
    }
    r = client.post("/api/v1/texts", json=text_data)
    print(f"   Status: {r.status_code}")
    if r.status_code == 201:
        text = r.json()
        text_id = text['id']
        print(f"   Text ID: {text_id}, Content: {text['content'][:50]}...")
    else:
        print(f"   Error: {r.text}")
        # Пробуем получить существующие тексты
        r = client.get("/api/v1/texts")
        texts = r.json()
        if texts:
            text_id = texts[0]['id']
            print(f"   Using existing text ID: {text_id}")
        else:
            print("   No texts available, skipping further tests")
            return
    
    # 4. Анализ текста
    print("\n4. Анализ текста (токенизация)...")
    r = client.post(f"/api/v1/texts/{text_id}/analyze", params={"user_level": 2})
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        result = r.json()
        print(f"   Tokens count: {result.get('tokens_count', 0)}")
        print(f"   Tokens created: {result.get('tokens_created', 0)}")
    else:
        print(f"   Error: {r.text}")
    
    # 5. Получение результатов анализа
    print("\n5. Получение результатов анализа...")
    r = client.get(f"/api/v1/texts/{text_id}/analyze")
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        result = r.json()
        tokens = result.get('tokens', [])
        print(f"   Tokens: {len(tokens)} found")
        for t in tokens[:5]:
            print(f"      - {t['value']} (known: {t.get('is_known', False)})")
    else:
        print(f"   Error: {r.text}")
    
    # 6. Генерация карточек
    print("\n6. Генерация карточек из текста...")
    r = client.post("/api/v1/flashcards/generate", json={"text_id": text_id})
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        result = r.json()
        print(f"   Cards created: {result.get('cards_created', 0)}")
        print(f"   Cards skipped: {result.get('cards_skipped', 0)}")
        cards = result.get('flashcards', [])
        if cards:
            print(f"   First card: {cards[0]['word']}")
    else:
        print(f"   Error: {r.text}")
    
    # 7. Получение карточек
    print("\n7. Получение списка карточек...")
    r = client.get("/api/v1/flashcards")
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        result = r.json()
        items = result.get('items', [])
        print(f"   Total cards: {result.get('total', 0)}")
        if items:
            card_id = items[0]['id']
            print(f"   First card ID: {card_id}, Word: {items[0]['word']}")
    else:
        print(f"   Error: {r.text}")
        card_id = 1
    
    # 8. Повторение карточки (SM-2)
    print("\n8. Тестирование системы повторения (SM-2)...")
    r = client.get("/api/v1/flashcards?due_only=true")
    due_cards = r.json()
    print(f"   Cards due for review: {due_cards.get('total', 0)}")
    
    if due_cards.get('items'):
        card_id = due_cards['items'][0]['id']
        print(f"   Reviewing card ID: {card_id}")
        r = client.post(f"/api/v1/flashcards/{card_id}/review", json={"quality": 4})
        print(f"   Review Status: {r.status_code}")
        if r.status_code == 200:
            review = r.json()
            print(f"   Review ID: {review['id']}, Quality: {review['quality']}")
    else:
        print("   No cards due for review")
    
    # 9. Упрощение текста
    print("\n9. Тестирование упрощения текста...")
    simplify_data = {
        "text": "我喜欢学习中文。今天天气很好。",
        "target_level": 2,
        "language": "zh"
    }
    r = client.post("/api/v1/texts/simplify", json=simplify_data)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        result = r.json()
        print(f"   Original: {result.get('original_text', '')}")
        print(f"   Simplified: {result.get('simplified_text', '')}")
    else:
        print(f"   Error: {r.text}")
    
    # 10. Словарь
    print("\n10. Работа со словарём...")
    vocab_data = {"word": "学习", "translation": "учить, изучать"}
    r = client.post("/api/v1/vocabulary", json=vocab_data)
    print(f"   Add word Status: {r.status_code}")
    if r.status_code == 201:
        print(f"   Word added: {r.json()}")
    
    r = client.get("/api/v1/vocabulary")
    print(f"   Get vocabulary Status: {r.status_code}")
    if r.status_code == 200:
        vocab = r.json()
        print(f"   Total words: {len(vocab) if isinstance(vocab, list) else 'N/A'}")
    
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)

if __name__ == "__main__":
    test_api()
