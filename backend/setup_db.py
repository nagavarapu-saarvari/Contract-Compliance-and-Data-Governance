import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DATA_DB = os.getenv("DATA_DB")

# ==========================================================
# CREATE DATABASE FUNCTION
# ==========================================================

def create_database(db_name):

    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname="postgres",
        user=DB_USER,
        password=DB_PASSWORD
    )

    conn.autocommit = True
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM pg_database WHERE datname = %s",
        (db_name,)
    )

    exists = cursor.fetchone()

    if not exists:
        print(f"Creating database: {db_name}")
        cursor.execute(f"CREATE DATABASE {db_name}")
    else:
        print(f"Database {db_name} already exists")

    cursor.close()
    conn.close()


# ==========================================================
# CREATE MAIN APPLICATION TABLES
# ==========================================================

def create_main_tables():

    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    cursor = conn.cursor()

    # documents table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id SERIAL PRIMARY KEY,
        filename TEXT,
        file_data BYTEA,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # rules table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rules (
        id SERIAL PRIMARY KEY,
        document_id INTEGER REFERENCES documents(id),
        rule_id TEXT,
        rule_json JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(document_id, rule_id)
    );
    """)

    conn.commit()

    cursor.close()
    conn.close()

    print("Main application tables created.")


# ==========================================================
# CREATE PATIENT DATABASE TABLES
# ==========================================================

def create_patient_tables():

    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DATA_DB,
        user=DB_USER,
        password=DB_PASSWORD
    )

    cursor = conn.cursor()

    # Patients table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        patient_id SERIAL PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        ssn TEXT,
        dob DATE,
        email TEXT,
        phone TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Healthcare providers
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS healthcare_providers (
        provider_id SERIAL PRIMARY KEY,
        provider_name TEXT,
        npi TEXT,
        hospital_name TEXT,
        email TEXT,
        phone TEXT
    );
    """)

    # Appointments
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        appointment_id SERIAL PRIMARY KEY,
        patient_id INTEGER REFERENCES patients(patient_id),
        provider_id INTEGER REFERENCES healthcare_providers(provider_id),
        appointment_date TIMESTAMP,
        reason TEXT,
        status TEXT
    );
    """)

    # Medical records
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medical_records (
        record_id SERIAL PRIMARY KEY,
        patient_id INTEGER REFERENCES patients(patient_id),
        diagnosis TEXT,
        treatment TEXT,
        prescription TEXT,
        record_date TIMESTAMP
    );
    """)

    # Billing
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS billing (
        bill_id SERIAL PRIMARY KEY,
        patient_id INTEGER REFERENCES patients(patient_id),
        amount NUMERIC,
        billing_date TIMESTAMP,
        payment_status TEXT
    );
    """)

    conn.commit()

    cursor.close()
    conn.close()

    print("Patient database tables created.")


# ==========================================================
# MAIN EXECUTION
# ==========================================================

# Create both databases
create_database(DB_NAME)
create_database(DATA_DB)

# Create tables
create_main_tables()
create_patient_tables()

print("Database setup completed successfully.")