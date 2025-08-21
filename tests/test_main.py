import sys
import os
import pytest
import json
from fastapi.testclient import TestClient


# Добавляем корневую директорию в sys.path, чтобы можно было импортировать app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app  # теперь импорт должен работать


client = TestClient(app)

# Очистка users.json перед тестами
@pytest.fixture(scope="module", autouse=True)
def clear_users_file():
    if os.path.exists("users.json"):
        os.remove("users.json")
    yield
    if os.path.exists("users.json"):
        os.remove("users.json")

def test_register_user():
    response = client.post("/register", data={"username": "testuser", "password": "password123"},
        follow_redirects=False)
    # Проверяем редирект
    assert response.status_code in (302, 307)
    # Проверяем, что пользователь добавился в users.json
    with open("users.json", "r", encoding="utf-8") as f:
        users = json.load(f)
    assert any(user["login"] == "testuser" for user in users)

def test_login_user_success():
    # Сначала регистрируем пользователя
    client.post("/register", data={"username": "loginuser", "password": "pass123"}, follow_redirects=False)
    response = client.post("/login", data={"username": "loginuser", "password": "pass123"}, follow_redirects=False)
    assert response.status_code in (302, 307)
    # Проверка наличия cookie сессии
    assert "session" in response.cookies

def test_login_user_fail():
    response = client.post("/login", data={"username": "nonexistent", "password": "wrong"}, follow_redirects=False)
    assert response.status_code in (302, 307)
    # При неправильном логине/пароле редирект на /no_reg
    assert response.headers["location"] == "/no_reg"

def test_get_all_users():
    # Добавляем несколько пользователей
    client.post("/register", data={"username": "user1", "password": "123"}, follow_redirects=False)
    client.post("/register", data={"username": "user2", "password": "456"}, follow_redirects=False)
    response = client.get("/users")
    assert response.status_code == 200
    users = response.json()
    assert any(user["login"] == "user1" for user in users)
    assert any(user["login"] == "user2" for user in users)
