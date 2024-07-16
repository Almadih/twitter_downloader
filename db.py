import sqlite3

def db_connection():
    conn = sqlite3.connect('telegram_bot_users.db')
    c = conn.cursor()
    return conn, c

def init_db():
    conn,c = db_connection()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            file_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
    conn.commit()
    conn.close()
    


def add_download(user_id, file_name):
    conn,c = db_connection()
    c.execute('INSERT INTO downloads (user_id, file_name) VALUES (?, ?)', (user_id, file_name))
    conn.commit()
    conn.close()

def get_downloads_count():
    conn,c = db_connection()
    c.execute('SELECT COUNT(*) FROM downloads')
    count = c.fetchone()[0]
    conn.close()
    return count

def add_or_update_user(user_id, username, first_name, last_name):
    conn,c = db_connection()
    c.execute('''
        INSERT INTO users (user_id, username, first_name, last_name, last_active)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET
            username=excluded.username,
            first_name=excluded.first_name,
            last_name=excluded.last_name,
            last_active=CURRENT_TIMESTAMP
    ''', (user_id, username, first_name, last_name))
    conn.commit()
    conn.close()

def get_user_count():
    conn,c = db_connection()
    c.execute('SELECT COUNT(*) FROM users')
    count = c.fetchone()[0]
    conn.close()
    return count