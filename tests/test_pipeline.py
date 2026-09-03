#!/usr/bin/env python3
"""
Automated Unit & Integration Tests for PT Bagi Kopi Data Pipeline
AI Systems Engineer Technical Test Validation
"""

import os
import sys
import unittest
import sqlite3
from datetime import datetime

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'scripts'))

from clean_and_load import parse_datetime, clean_outlet, clean_entity, clean_status

class TestDataPipeline(unittest.TestCase):

    def test_parse_datetime_iso(self):
        dt = parse_datetime("2026-09-02 17:13:00")
        self.assertEqual(dt, datetime(2026, 9, 2, 17, 13, 0))

    def test_parse_datetime_uk(self):
        dt = parse_datetime("01/09/2026 10:59")
        self.assertEqual(dt, datetime(2026, 9, 1, 10, 59, 0))

    def test_parse_datetime_ampm(self):
        dt = parse_datetime("11 Sep 2026 12:17 PM")
        self.assertEqual(dt, datetime(2026, 9, 11, 12, 17, 0))

    def test_clean_outlet_normalization(self):
        self.assertEqual(clean_outlet("DAGO"), "Dago")
        self.assertEqual(clean_outlet("dago"), "Dago")
        self.assertEqual(clean_outlet("  Dago  "), "Dago")
        self.assertEqual(clean_outlet("Buah  Batu"), "Buah Batu")

    def test_clean_entity(self):
        self.assertEqual(clean_entity("retail"), "Retail")
        self.assertEqual(clean_entity("ROASTERY"), "Roastery")

    def test_clean_status(self):
        self.assertEqual(clean_status("paid"), "PAID")
        self.assertEqual(clean_status("void"), "VOID")

    def test_database_integrity_and_queries(self):
        db_path = os.path.join(BASE_DIR, 'database', 'bagikopi.db')
        self.assertTrue(os.path.exists(db_path), "Database file should exist")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test total rows
        total_rows = cursor.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
        self.assertEqual(total_rows, 205, "Clean database should contain exactly 205 deduplicated records")
        
        # Test Q1: Retail Net Sales PAID
        q1_res = cursor.execute("""
            SELECT SUM(net_amount) FROM transactions 
            WHERE entity = 'Retail' AND payment_status = 'PAID'
        """).fetchone()[0]
        self.assertEqual(q1_res, 11657000.0, "Retail net sales (PAID) should equal 11,657,000")

        # Test Q2: Top Outlet Dago
        q2_res = cursor.execute("""
            SELECT outlet, COUNT(DISTINCT transaction_id) AS cnt 
            FROM transactions 
            WHERE entity = 'Retail' AND payment_status = 'PAID' 
            GROUP BY outlet ORDER BY cnt DESC LIMIT 1
        """).fetchone()
        self.assertEqual(q2_res[0], "Dago", "Top outlet should be Dago")
        self.assertEqual(q2_res[1], 45, "Top outlet Dago should have 45 unique transactions")

        # Test Q3: Overall ATV PAID
        q3_res = cursor.execute("""
            SELECT AVG(net_amount) FROM transactions 
            WHERE payment_status = 'PAID'
        """).fetchone()[0]
        self.assertAlmostEqual(q3_res, 445796.875, places=2, msg="Overall ATV should equal 445,796.88")
        
        conn.close()

if __name__ == '__main__':
    unittest.main()
