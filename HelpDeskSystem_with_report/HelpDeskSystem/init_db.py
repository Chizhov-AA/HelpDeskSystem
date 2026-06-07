from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "database"
DB_PATH = DB_DIR / "helpdesk.db"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"
DATA_PATH = BASE_DIR / "sql" / "sample_data.sql"


def initialize_database():
    DB_DIR.mkdir(exist_ok=True)

    if DB_PATH.exists():
        DB_PATH.unlink()

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.executescript(DATA_PATH.read_text(encoding="utf-8"))
        conn.commit()

    print(f"База данных создана: {DB_PATH}")


if __name__ == "__main__":
    initialize_database()
