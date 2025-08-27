# Use this file to run changes to the database schema or data
# (You have to run this manually - it's just a temp file of sorts)
from book_api.persistence import get_db_connection

# Update `responses` table to add a boolean `batch` column, default False
with get_db_connection() as conn:
    cursor = conn.cursor()

    pass  # Replace with your SQL as needed

    conn.commit()
