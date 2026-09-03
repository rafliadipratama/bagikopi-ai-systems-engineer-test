#!/usr/bin/env python3
"""
Script to execute business queries against bagikopi.db and format results.
"""

import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'database', 'bagikopi.db')

def format_rupiah(val):
    if val is None:
        return "Rp 0,00"
    return f"Rp {val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def main():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}. Please run clean_and_load.py first.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 70)
    print("PT BAGI KOPI INDONESIA - BUSINESS ANALYTICS REPORT")
    print("=" * 70)

    # Q1
    print("\n--- PERTANYAAN 1: TOTAL PENJUALAN BERSIH (NET) RETAIL ---")
    q1_sql = """
    SELECT 
        SUM(net_amount) AS total_net,
        SUM(gross_amount) AS total_gross,
        SUM(discount_amount) AS total_discount,
        COUNT(*) AS total_tx
    FROM transactions
    WHERE entity = 'Retail' AND payment_status = 'PAID';
    """
    row = cursor.execute(q1_sql).fetchone()
    print(f"Total Net Sales (Retail - PAID)  : {format_rupiah(row[0])}")
    print(f"Total Gross Sales (Retail - PAID): {format_rupiah(row[1])}")
    print(f"Total Discount (Retail - PAID)   : {format_rupiah(row[2])}")
    print(f"Total Transactions (Retail - PAID): {row[3]}")

    # Q2
    print("\n--- PERTANYAAN 2: OUTLET RETAIL DENGAN TRANSAKSI UNIK TERBANYAK ---")
    q2_sql = """
    SELECT 
        outlet,
        COUNT(DISTINCT transaction_id) AS total_unique_tx,
        SUM(net_amount) AS total_net_sales
    FROM transactions
    WHERE entity = 'Retail' AND payment_status = 'PAID'
    GROUP BY outlet
    ORDER BY total_unique_tx DESC;
    """
    rows = cursor.execute(q2_sql).fetchall()
    print(f"{'No.':<4} {'Nama Outlet':<20} {'Jumlah Transaksi (Unik)':<25} {'Total Penjualan Bersih':<25}")
    print("-" * 75)
    for i, r in enumerate(rows, start=1):
        print(f"{i:<4} {r[0]:<20} {r[1]:<25} {format_rupiah(r[2]):<25}")

    # Q3
    print("\n--- PERTANYAAN 3: RATA-RATA NILAI TRANSAKSI (ATV) BAGI KOPI ---")
    q3a_sql = """
    SELECT 
        AVG(net_amount) AS overall_atv,
        SUM(net_amount) AS total_net,
        COUNT(*) AS total_tx
    FROM transactions
    WHERE payment_status = 'PAID';
    """
    row = cursor.execute(q3a_sql).fetchone()
    print(f"Average Transaction Value (ATV Overall) : {format_rupiah(row[0])}")
    print(f"Total Net Sales (All Entites)           : {format_rupiah(row[1])}")
    print(f"Total Transactions (All Entities)       : {row[2]}")

    print("\nBREAKDOWN ATV PER ENTITAS (RETAIL VS ROASTERY):")
    q3b_sql = """
    SELECT 
        entity,
        AVG(net_amount) AS entity_atv,
        SUM(net_amount) AS total_net,
        COUNT(*) AS total_tx
    FROM transactions
    WHERE payment_status = 'PAID'
    GROUP BY entity
    ORDER BY entity_atv DESC;
    """
    rows_ent = cursor.execute(q3b_sql).fetchall()
    print(f"{'Entitas':<15} {'ATV (Rata-rata)':<25} {'Total Net Sales':<25} {'Jumlah Transaksi':<18}")
    print("-" * 83)
    for r in rows_ent:
        print(f"{r[0]:<15} {format_rupiah(r[1]):<25} {format_rupiah(r[2]):<25} {r[3]:<18}")

    print("\n" + "=" * 70)
    conn.close()

if __name__ == '__main__':
    main()
