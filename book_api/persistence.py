from sqlite3 import connect

DB_PATH = "book_api/persistence.db"


def get_db_connection():
    """Create a database connection to the SQLite database."""
    conn = connect(DB_PATH)
    return conn


def setup_database():
    """Create the necessary tables in the database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instructions TEXT,
            input TEXT,
            output TEXT,
            model TEXT NOT NULL,
            cached_input_tokens INTEGER NOT NULL,
            uncached_input_tokens INTEGER NOT NULL,
            reasoning_output_tokens INTEGER NOT NULL,
            nonreasoning_output_tokens INTEGER NOT NULL,
            batch BOOLEAN DEFAULT FALSE,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()


def persist_response(response):
    """
    Persist the response statistics in the database.

    Args:
        response (dict): A dictionary containing the response statistics.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO responses (
            instructions, input, output, model,
            cached_input_tokens, uncached_input_tokens,
            reasoning_output_tokens, nonreasoning_output_tokens,
            batch
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            response.get("instructions", None),
            response.get("input", None),
            response.get("output", None),
            response.get("model", "unknown"),
            response.get("cached_input_tokens", 0),
            response.get("uncached_input_tokens", 0),
            response.get("reasoning_output_tokens", 0),
            response.get("nonreasoning_output_tokens", 0),
            response.get("batch", False),
        ))
        conn.commit()
