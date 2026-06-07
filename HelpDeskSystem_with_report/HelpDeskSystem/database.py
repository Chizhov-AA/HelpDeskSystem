import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database" / "helpdesk.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def fetch_all(query, params=()):
    with get_connection() as conn:
        return conn.execute(query, params).fetchall()


def execute(query, params=()):
    with get_connection() as conn:
        cursor = conn.execute(query, params)
        conn.commit()
        return cursor.lastrowid


def get_departments():
    return fetch_all("SELECT id, name FROM departments ORDER BY name")


def get_users():
    return fetch_all("""
        SELECT u.id, u.full_name, d.name AS department, u.phone, u.email
        FROM users u
        JOIN departments d ON d.id = u.department_id
        ORDER BY u.id
    """)


def get_engineers():
    return fetch_all("""
        SELECT id, full_name, position, phone, email
        FROM engineers
        ORDER BY id
    """)


def get_requests(status=None, search_text=""):
    query = """
        SELECT r.id, r.title, r.priority, r.status, r.created_at,
               u.full_name AS user_name, d.name AS department
        FROM requests r
        JOIN users u ON u.id = r.user_id
        JOIN departments d ON d.id = u.department_id
        WHERE 1 = 1
    """
    params = []

    if status and status != "Все":
        query += " AND r.status = ?"
        params.append(status)

    if search_text:
        query += " AND (r.title LIKE ? OR r.description LIKE ? OR u.full_name LIKE ?)"
        like_value = f"%{search_text}%"
        params.extend([like_value, like_value, like_value])

    query += " ORDER BY r.id DESC"
    return fetch_all(query, params)


def get_assignments():
    return fetch_all("""
        SELECT a.id, r.title AS request_title, e.full_name AS engineer_name,
               a.assign_date, a.comment
        FROM assignments a
        JOIN requests r ON r.id = a.request_id
        JOIN engineers e ON e.id = a.engineer_id
        ORDER BY a.id DESC
    """)


def add_request(title, description, priority, user_id):
    return execute("""
        INSERT INTO requests (title, description, priority, status, user_id)
        VALUES (?, ?, ?, 'Новая', ?)
    """, (title, description, priority, user_id))


def assign_engineer(request_id, engineer_id, comment):
    execute("""
        INSERT INTO assignments (request_id, engineer_id, comment)
        VALUES (?, ?, ?)
    """, (request_id, engineer_id, comment))
    execute("""
        UPDATE requests
        SET status = 'В работе'
        WHERE id = ? AND status = 'Новая'
    """, (request_id,))


def update_request_status(request_id, status):
    execute("""
        UPDATE requests
        SET status = ?
        WHERE id = ?
    """, (status, request_id))


def get_statistics():
    return fetch_all("""
        SELECT status, COUNT(*) AS count
        FROM requests
        GROUP BY status
        ORDER BY count DESC
    """)
