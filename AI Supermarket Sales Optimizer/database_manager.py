import json
import sqlite3

def read_rag(db_path="inventory.db"):
    """Reads inventory catalog facts from SQLite database and returns formatted JSON."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM inventory")
    rows = cursor.fetchall()
    conn.close()

    inventory_list = [dict(row) for row in rows]
    return json.dumps(inventory_list, indent=2)