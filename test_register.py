#!/usr/bin/env python
"""Тест регистрации через API."""
import httpx

# Тест регистрации
body = {
    "email": "api@example.com",
    "username": "apiuser",
    "password": "password123"
}

try:
    r = httpx.post("http://localhost:8000/api/v1/users/register", json=body, timeout=30)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"Error: {e}")
