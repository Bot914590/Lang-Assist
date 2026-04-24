#!/usr/bin/env python
"""Проверка CORS."""
import httpx

# Проверка CORS для разных endpoints
endpoints = [
    "http://localhost:8000/health",
    "http://localhost:8000/api/v1/texts",
    "http://localhost:8000/api/v1/flashcards",
]

for url in endpoints:
    print(f"\n{url}:")
    r = httpx.options(url)
    print(f"  Status: {r.status_code}")
    print(f"  CORS: {r.headers.get('access-control-allow-origin', 'NOT SET')}")
    print(f"  Methods: {r.headers.get('access-control-allow-methods', 'NOT SET')}")
