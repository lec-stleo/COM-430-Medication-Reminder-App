from werkzeug.security import check_password_hash, generate_password_hash

from ..db import get_db


def create_user(username, email, password):
    db = get_db()
    # pbkdf2 is widely supported, which avoids platform-specific issues with scrypt.
    password_hash = generate_password_hash(password, method="pbkdf2:sha256")
    cursor = db.execute(
        """
        INSERT INTO users (username, email, password_hash)
        VALUES (?, ?, ?)
        """,
        (username, email, password_hash),
    )
    db.commit()
    return cursor.lastrowid


def get_user_by_username(username):
    db = get_db()
    return db.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,),
    ).fetchone()


def get_user_by_email(email):
    db = get_db()
    return db.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,),
    ).fetchone()


def get_user_by_id(user_id):
    db = get_db()
    return db.execute(
        "SELECT id, username, email, created_at FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()


def get_public_user_by_username(username):
    db = get_db()
    return db.execute(
        "SELECT id, username, email, created_at FROM users WHERE username = ?",
        (username,),
    ).fetchone()


def verify_user(username, password):
    user = get_user_by_username(username)
    if user and check_password_hash(user["password_hash"], password):
        return user
    return None
