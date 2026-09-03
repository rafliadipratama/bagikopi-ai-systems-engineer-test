#!/usr/bin/env python3
"""
Data Cleaning & Loading Pipeline for PT Bagi Kopi Indonesia
AI Systems Engineer Technical Test

This script reads raw transaction data, performs quality checks, cleans anomalies,
exports cleaned CSV data, and loads it into an SQLite database.
"""

import os
import csv
import sqlite3
from datetime import datetime

# Define file paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_CSV_PATH = os.path.join(BASE_DIR, 'data', 'bk_transactions_raw.csv')
CLEAN_CSV_PATH = os.path.join(BASE_DIR, 'data', 'bk_transactions_clean.csv')
DB_PATH = os.path.join(BASE_DIR, 'database', 'bagikopi.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'sql', 'schema.sql')

def parse_datetime(dt_str):
    """Parse heterogeneous datetime string formats into standard datetime object."""
    dt_str = dt_str.strip()
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%d/%m/%Y %H:%M:%S',
        '%d/%m/%Y %H:%M',
        '%d %b %Y %I:%M %p',
        '%d %b %Y %H:%M'
    ]
    for fmt in formats:
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            pass
    raise ValueError(f"Unable to parse datetime: '{dt_str}'")

def clean_outlet(outlet_str):
    """Normalize outlet name (strip, single space, title case)."""
    return ' '.join(outlet_str.strip().split()).title()

def clean_entity(entity_str):
    """Normalize entity name (strip, title case)."""
    return entity_str.strip().title()

def clean_status(status_str):
    """Normalize payment status (strip, uppercase)."""
    return status_str.strip().upper()

def main():
    print("=" * 60)
    print("PT BAGI KOPI INDONESIA - DATA CLEANING & LOADING PIPELINE")
    print("=" * 60)

    if not os.path.exists(RAW_CSV_PATH):
        raise FileNotFoundError(f"Raw CSV file not found at: {RAW_CSV_PATH}")

    with open(RAW_CSV_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        raw_rows = list(reader)

    print(f"[+] Total raw rows read: {len(raw_rows)}")

    # Audit & Cleaning tracking
    seen_ids = set()
    duplicate_rows = []
    cleaned_rows = []
    math_discrepancies = []

    for idx, row in enumerate(raw_rows, start=1):
        tx_id = row['transaction_id'].strip()
        
        # 1. Deduplication Check
        if tx_id in seen_ids:
            duplicate_rows.append(row)
            continue
        seen_ids.add(tx_id)

        # 2. Datetime Parsing
        dt_obj = parse_datetime(row['datetime'])
        iso_dt = dt_obj.strftime('%Y-%m-%d %H:%M:%S')

        # 3. String Normalizations
        entity = clean_entity(row['entity'])
        outlet = clean_outlet(row['outlet'])
        status = clean_status(row['payment_status'])

        # 4. Numeric conversions & Math validation
        items = int(row['items'].strip())
        gross = float(row['gross_amount'].strip())
        discount = float(row['discount_amount'].strip())
        net = float(row['net_amount'].strip())

        if abs((gross - discount) - net) > 0.01:
            math_discrepancies.append((tx_id, gross, discount, net))

        cleaned_rows.append({
            'transaction_id': tx_id,
            'datetime': iso_dt,
            'entity': entity,
            'outlet': outlet,
            'items': items,
            'gross_amount': gross,
            'discount_amount': discount,
            'net_amount': net,
            'payment_status': status
        })

    print(f"[+] Duplicate rows removed: {len(duplicate_rows)}")
    print(f"[+] Clean deduplicated rows: {len(cleaned_rows)}")
    print(f"[+] Math discrepancies (gross - discount != net): {len(math_discrepancies)}")

    # Save Cleaned CSV
    fieldnames = ['transaction_id', 'datetime', 'entity', 'outlet', 'items', 
                  'gross_amount', 'discount_amount', 'net_amount', 'payment_status']
    
    os.makedirs(os.path.dirname(CLEAN_CSV_PATH), exist_ok=True)
    with open(CLEAN_CSV_PATH, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_rows)

    print(f"[✓] Cleaned dataset saved to: {CLEAN_CSV_PATH}")

    # Load into SQLite Database
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Read and execute schema
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)

    # Insert cleaned records
    insert_sql = '''
    INSERT INTO transactions (
        transaction_id, datetime, entity, outlet, items,
        gross_amount, discount_amount, net_amount, payment_status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    for r in cleaned_rows:
        cursor.execute(insert_sql, (
            r['transaction_id'],
            r['datetime'],
            r['entity'],
            r['outlet'],
            r['items'],
            r['gross_amount'],
            r['discount_amount'],
            r['net_amount'],
            r['payment_status']
        ))

    conn.commit()

    db_count = cursor.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    conn.close()

    print(f"[✓] SQLite database successfully populated: {DB_PATH}")
    print(f"[✓] Total records in DB table 'transactions': {db_count}")
    print("=" * 60)

if __name__ == '__main__':
    main()
