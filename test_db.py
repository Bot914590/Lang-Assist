#!/usr/bin/env python
"""Проверка БД и тест регистрации."""
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from models.models import Account

# Проверка структуры БД
engine = create_engine('sqlite:///./user.db')
inspector = inspect(engine)

print("Таблицы:", inspector.get_table_names())

if 'accounts' in inspector.get_table_names():
    print("\nКолонки accounts:")
    for col in inspector.get_columns('accounts'):
        print(f"  {col['name']} - {col['type']} (nullable: {col['nullable']})")

# Тест создания пользователя
Session = sessionmaker(bind=engine)
session = Session()

print("\n--- Тест создания пользователя ---")
user = Account(email='testdb@example.com', username='testdbuser', lang_level='HSK 2')
user.set_password('password123')

try:
    session.add(user)
    session.commit()
    print(f"User created! ID: {user.id}, Email: {user.email}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    session.rollback()

# Проверка существующих пользователей
print("\n--- Существующие пользователи ---")
users = session.query(Account).all()
for u in users:
    print(f"  ID: {u.id}, Email: {u.email}, Username: {u.username}")

session.close()
