-- ============================================================================
-- SQL Script: Schema Creation & Data Loading Instructions
-- Target Database: SQLite3 / DuckDB / PostgreSQL
-- ============================================================================

-- 1. Create Schema
DROP TABLE IF EXISTS transactions;

CREATE TABLE transactions (
    transaction_id TEXT PRIMARY KEY,
    datetime TEXT NOT NULL,
    entity TEXT NOT NULL,
    outlet TEXT NOT NULL,
    items INTEGER NOT NULL CHECK (items > 0),
    gross_amount REAL NOT NULL CHECK (gross_amount >= 0),
    discount_amount REAL NOT NULL CHECK (discount_amount >= 0),
    net_amount REAL NOT NULL CHECK (net_amount >= 0),
    payment_status TEXT NOT NULL CHECK (payment_status IN ('PAID', 'VOID'))
);

-- 2. Indexes
CREATE INDEX idx_entity_status ON transactions(entity, payment_status);
CREATE INDEX idx_outlet_entity ON transactions(outlet, entity);
CREATE INDEX idx_payment_status ON transactions(payment_status);

-- 3. Data Loading Command (SQLite CLI Example):
-- .mode csv
-- .import data/bk_transactions_clean.csv transactions --skip 1

-- 4. Data Loading Command (DuckDB Example):
-- CREATE TABLE transactions AS SELECT * FROM read_csv_auto('data/bk_transactions_clean.csv');
