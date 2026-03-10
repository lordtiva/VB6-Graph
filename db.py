import sqlite3
import os

DB_NAME = "vb6_code.db"

def init_db():
    """Initializes the SQLite database with the code_nodes table."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS code_nodes (
            node_id TEXT PRIMARY KEY,
            node_type TEXT,
            file_path TEXT,
            code_content TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_node(node_id, node_type, file_path, code_content):
    """Saves or updates a code node in the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO code_nodes (node_id, node_type, file_path, code_content)
        VALUES (?, ?, ?, ?)
    """, (node_id, node_type, file_path, code_content))
    conn.commit()
    conn.close()

def get_node_code(node_id):
    """Retrieves the code content for a given node_id."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT code_content FROM code_nodes WHERE node_id = ?", (node_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None
