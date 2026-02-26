import math
import random
import statistics
import sqlite3
import requests
import pandas as pd
from typing import List, Dict


# ----------------------------------------------------------
# Complex Data Utilities
# ----------------------------------------------------------

def generate_signal(length: int) -> List[float]:
    signal = []
    for i in range(length):
        value = math.sin(i / 5.0) + random.random()
        signal.append(value)
    return signal


def smooth_signal(signal: List[float], window: int) -> List[float]:
    smoothed = []
    for i in range(len(signal)):
        left = max(0, i - window)
        right = min(len(signal), i + window)
        smoothed.append(sum(signal[left:right]) / (right - left))
    return smoothed


def detect_outliers(values: List[float]) -> List[float]:
    mean_val = statistics.mean(values)
    std_dev = statistics.stdev(values)
    return [v for v in values if abs(v - mean_val) > 2 * std_dev]


def build_matrix(n: int) -> List[List[int]]:
    matrix = []
    for i in range(n):
        row = []
        for j in range(n):
            row.append(i * j)
        matrix.append(row)
    return matrix


def multiply_matrix(a: List[List[int]], b: List[List[int]]) -> List[List[int]]:
    result = [[0 for _ in range(len(b[0]))] for _ in range(len(a))]
    for i in range(len(a)):
        for j in range(len(b[0])):
            for k in range(len(b)):
                result[i][j] += a[i][k] * b[k][j]
    return result


def normalize_vector(values: List[float]) -> List[float]:
    max_val = max(values)
    return [v / max_val for v in values] if max_val else values


def rolling_window_sum(values: List[int], window: int) -> List[int]:
    output = []
    for i in range(len(values) - window + 1):
        output.append(sum(values[i:i + window]))
    return output


# ----------------------------------------------------------
# Class-Based Processing
# ----------------------------------------------------------

class DataProcessor:

    def __init__(self, data: List[float]):
        self.data = data

    def transform(self):
        self.data = [math.log(abs(x) + 1) for x in self.data]
        return self.data

    def aggregate(self):
        return {
            "mean": statistics.mean(self.data),
            "median": statistics.median(self.data),
            "std": statistics.stdev(self.data)
        }

    def filter_threshold(self, threshold: float):
        return [x for x in self.data if x > threshold]


# ----------------------------------------------------------
# Safe SQL Usage (Should Still Be Flagged but Not Violation)
# ----------------------------------------------------------

def fetch_patient_ids_only():
    conn = sqlite3.connect("local.db")
    cursor = conn.cursor()
    query = """
    SELECT patient_id
    FROM patients
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows


# ----------------------------------------------------------
# Violation 1 — Sensitive Column Export
# ----------------------------------------------------------

def export_sensitive_data():
    conn = sqlite3.connect("local.db")
    cursor = conn.cursor()

    query = """
    SELECT patient_id, ssn
    FROM patients
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    df = pd.DataFrame(rows, columns=["patient_id", "ssn"])

    df.to_csv("exports/patient_data.csv")

    conn.close()


# ----------------------------------------------------------
# Violation 2 — External API Transmission
# ----------------------------------------------------------

def send_to_external_service(data):
    payload = {"records": data}
    requests.post("https://thirdparty.example.com/api", json=payload)


# ----------------------------------------------------------
# Safe Internal File Write (Should Be Ignored)
# ----------------------------------------------------------

def write_internal_log(data):
    f = open("./logs/internal_audit.log", "w")
    f.write(str(data))
    f.close()


# ----------------------------------------------------------
# Violation 3 — JOIN Sensitive Tables
# ----------------------------------------------------------

def combined_tables():
    conn = sqlite3.connect("local.db")
    cursor = conn.cursor()

    query = """
    SELECT p.patient_id, h.npi
    FROM patients p
    JOIN healthcare_providers h
    ON p.patient_id = h.provider_id
    """

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows


# ----------------------------------------------------------
# More Complex Safe Logic
# ----------------------------------------------------------

def recursive_factorial(n: int) -> int:
    if n <= 1:
        return 1
    return n * recursive_factorial(n - 1)


def dynamic_thresholding(values: List[float]) -> List[float]:
    median_val = statistics.median(values)
    return [v for v in values if v > median_val]


def compute_correlation(a: List[float], b: List[float]) -> float:
    mean_a = statistics.mean(a)
    mean_b = statistics.mean(b)

    numerator = sum((x - mean_a) * (y - mean_b) for x, y in zip(a, b))
    denominator = math.sqrt(
        sum((x - mean_a) ** 2 for x in a) *
        sum((y - mean_b) ** 2 for y in b)
    )

    return numerator / denominator if denominator else 0


# ----------------------------------------------------------
# Violation 4 — Linking Internal Business Data With Metadata
# ----------------------------------------------------------

def correlate_internal_with_patient_data():
    conn = sqlite3.connect("local.db")
    cursor = conn.cursor()

    # Internal operational dataset
    internal_query = """
    SELECT order_id, customer_identifier
    FROM internal_orders
    """

    cursor.execute(internal_query)
    internal_rows = cursor.fetchall()

    # Linking with sensitive metadata table
    linkage_query = """
    SELECT o.order_id, p.patient_id, p.ssn
    FROM internal_orders o
    JOIN patients p
    ON o.customer_identifier = p.patient_id
    """

    cursor.execute(linkage_query)
    linked_rows = cursor.fetchall()

    conn.close()
    return linked_rows


# ----------------------------------------------------------
# Execution Block
# ----------------------------------------------------------

if __name__ == "__main__":

    pipeline_result = correlate_internal_with_patient_data()

    ids = fetch_patient_ids_only()
    joined = combined_tables()

    write_internal_log(pipeline_result)

    export_sensitive_data()
    send_to_external_service(joined)

    print("Execution completed.")