import httpx
import json

response = httpx.post(
    'http://localhost:8080/analyze',
    json={"text": "你好吗", "lang": "zh", "user_level": 1},
)
result = response.json()

with open('test_go_result.txt', 'w', encoding='utf-8') as f:
    f.write(f"Status: {result.get('status')}\n")
    f.write(f"Tokens count: {result.get('tokens_count')}\n")
    f.write(f"First token: {json.dumps(result['tokens'][0], ensure_ascii=False)}\n")
    f.write("All tokens:\n")
    for token in result['tokens']:
        f.write(f"  {token.get('value')}: positions={token.get('positions')}\n")

print("Result written to test_go_result.txt")
