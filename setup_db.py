import sqlite3

def setup_database():
    conn = sqlite3.connect('ideas.db')
    c = conn.cursor()

    # 投稿テーブルを作成
    c.execute('''
        CREATE TABLE IF NOT EXISTS ideas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            image BLOB,
            details TEXT,
            tags TEXT,
            likes INTEGER DEFAULT 0
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_database()
