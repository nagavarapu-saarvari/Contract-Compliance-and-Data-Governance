import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# connect to default postgres database
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname="postgres",
    user=DB_USER,
    password=DB_PASSWORD
)

conn.autocommit = True
cursor = conn.cursor()

# create database
cursor.execute(
    "SELECT 1 FROM pg_database WHERE datname = %s",
    (DB_NAME,)
)

exists = cursor.fetchone()

if not exists:
    print(f"Creating database: {DB_NAME}")
    cursor.execute(f"CREATE DATABASE {DB_NAME}")
else:
    print(f"Database {DB_NAME} already exists")


cursor.close()
conn.close()


# connect to the newly created database
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

cursor = conn.cursor()

# create documents table
cursor.execute("""
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    filename TEXT,
    file_data BYTEA,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# create rules table
cursor.execute("""
CREATE TABLE IF NOT EXISTS rules (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    rule_id TEXT,
    rule_json JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

conn.commit()

cursor.close()
conn.close()

print("Database and tables created successfully.")