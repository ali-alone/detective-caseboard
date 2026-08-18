import os
import sys
import sqlite3

def _default_db_path():
    """Store the database next to the executable/script, not in a bundled temp dir."""
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "caseboard.db")


DATABASE_NAME = _default_db_path()


def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nodes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            x REAL NOT NULL,
            y REAL NOT NULL
        )    
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS connections(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_a_id INTEGER NOT NULL,
            node_b_id INTEGER NOT NULL,
            label TEXT DEFAULT '',
            FOREIGN KEY(node_a_id) REFERENCES nodes(id),
            FOREIGN KEY(node_b_id) REFERENCES nodes(id)
        )
    """)

    conn.commit()
    conn.close()
    
    
def save_node(name, x, y):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO nodes(name, x, y) VALUES (?,?,?)",
        (name, x ,y)
    )
    conn.commit()
    node_id = cursor.lastrowid
    conn.close()
    return node_id

def update_node_pos(node_id, x ,y):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE nodes SET x = ? , y = ? WHERE id = ? ",
        (x,y,node_id)
    )
    conn.commit()
    conn.close()
    
    
def update_node_name(node_id, name):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE nodes SET name = ? WHERE id = ?",
        (name, node_id)
    )
    conn.commit()
    conn.close()


def load_nodes():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, x ,y FROM nodes")
    nodes = cursor .fetchall()
    
    conn.close()
    return nodes


def save_connection(node_a_id, node_b_id, label=""):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO connections(node_a_id, node_b_id, label) VALUES (?,?,?)",
        (node_a_id, node_b_id, label)
    )
    conn.commit()
    connection_id = cursor.lastrowid
    conn.close()
    return connection_id


def load_connections():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id, node_a_id, node_b_id, label FROM connections")
    connections = cursor.fetchall()

    conn.close()
    return connections


def update_connection_label(connection_id, label):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE connections SET label = ? WHERE id = ?",
        (label, connection_id)
    )
    conn.commit()
    conn.close()


def delete_node(node_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM connections WHERE node_a_id = ? OR node_b_id = ?",
        (node_id, node_id)
    )
    cursor.execute("DELETE FROM nodes WHERE id = ?", (node_id,))

    conn.commit()
    conn.close()


def delete_connection(connection_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM connections WHERE id = ?", (connection_id,))

    conn.commit()
    conn.close()
