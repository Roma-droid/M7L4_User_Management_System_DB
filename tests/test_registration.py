import pytest
import sqlite3
import os
from registration.registration import create_db, add_user, authenticate_user, display_users

@pytest.fixture(scope="module")
def setup_database():
    """Фикстура для настройки базы данных перед тестами и её очистки после."""
    create_db()
    yield
    try:
        os.remove('users.db')
    except PermissionError:
        pass

@pytest.fixture
def connection():
    """Фикстура для получения соединения с базой данных и его закрытия после теста."""
    conn = sqlite3.connect('users.db')
    yield conn
    conn.close()


def test_create_db(setup_database, connection):
    """Тест создания базы данных и таблицы пользователей."""
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    table_exists = cursor.fetchone()
    assert table_exists, "Таблица 'users' должна существовать в базе данных."

def test_add_new_user(setup_database, connection):
    """Тест добавления нового пользователя."""
    add_user('testuser', 'testuser@example.com', 'password123')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='testuser';")
    user = cursor.fetchone()
    assert user, "Пользователь должен быть добавлен в базу данных."


def test_add_existing_user(setup_database, connection):
    """Тест добавления пользователя с уже существующим логином возвращает False."""
    result1 = add_user('existinguser', 'exist@example.com', 'pass1')
    result2 = add_user('existinguser', 'exist2@example.com', 'pass2')
    assert result1 is True
    assert result2 is False


def test_authenticate_success(setup_database):
    """Тест успешной аутентификации пользователя."""
    add_user('authuser', 'auth@example.com', 'securepwd')
    assert authenticate_user('authuser', 'securepwd') is True


def test_authenticate_nonexistent(setup_database):
    """Тест аутентификации несуществующего пользователя возвращает False."""
    assert authenticate_user('no_such_user', 'nopass') is False


def test_authenticate_wrong_password(setup_database):
    """Тест аутентификации существующего пользователя с неправильным паролем."""
    add_user('authuser2', 'a2@example.com', 'rightpass')
    assert authenticate_user('authuser2', 'wrongpass') is False


def test_display_users_output(setup_database, capsys):
    """Тест отображения списка пользователей печатает логины и email'ы."""
    # Добавим пару пользователей
    add_user('disp1', 'd1@example.com', 'p1')
    add_user('disp2', 'd2@example.com', 'p2')
    display_users()
    captured = capsys.readouterr()
    out = captured.out
    assert 'Логин: disp1' in out
    assert 'd1@example.com' in out
    assert 'Логин: disp2' in out
    assert 'd2@example.com' in out

# Возможные варианты тестов:
"""
Тест добавления пользователя с существующим логином.
Тест успешной аутентификации пользователя.
Тест аутентификации несуществующего пользователя.
Тест аутентификации пользователя с неправильным паролем.
Тест отображения списка пользователей.
"""