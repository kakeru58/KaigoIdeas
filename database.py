import sqlite3
import boto3
import os
from botocore.exceptions import ClientError

# Amazon S3設定
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)
BUCKET_NAME = os.getenv("BUCKET_NAME")

# S3にファイルをアップロードする関数
def upload_file_to_s3(local_path, s3_path):
    s3.upload_file(local_path, BUCKET_NAME, s3_path)
    return s3_path

# S3からファイルをダウンロードする関数
def download_file_from_s3(s3_path, local_path):
    try:
        s3.download_file(BUCKET_NAME, s3_path, local_path)
    except ClientError as e:
        if e.response['Error']['Code'] != '404':
            raise

# データベースディレクトリの設定
DB_DIR = "DB"
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

DATABASE_PATH = os.path.join(DB_DIR, 'ideas.db')

# S3からデータベースファイルをダウンロード
download_file_from_s3('ideas.db', DATABASE_PATH)

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def setup_database():
    conn = get_db_connection()
    c = conn.cursor()
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

def add_post(title, image, details, tags):
    conn = get_db_connection()
    c = conn.cursor()
    tags_str = ','.join(tags)
    c.execute('INSERT INTO ideas (title, image, details, tags) VALUES (?, ?, ?, ?)', (title, image, details, tags_str))
    conn.commit()
    conn.close()

def update_likes(post_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('UPDATE ideas SET likes = likes + 1 WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()

def get_all_posts():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM ideas').fetchall()
    conn.close()
    return posts

def search_posts(query):
    conn = get_db_connection()
    query = f"%{query}%"
    posts = conn.execute('SELECT * FROM ideas WHERE title LIKE ? OR details LIKE ? OR tags LIKE ?', (query, query, query)).fetchall()
    conn.close()
    return posts

def get_all_tags():
    conn = get_db_connection()
    tags = conn.execute('SELECT tags FROM ideas').fetchall()
    conn.close()
    unique_tags = set()
    for tag in tags:
        unique_tags.update(tag['tags'].split(','))
    return list(unique_tags)
