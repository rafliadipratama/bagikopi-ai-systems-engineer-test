-- Schema DDL for PT Bagi Kopi Indonesia Transaction Database
-- Database: SQLite3

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

-- Indexes for optimal analytical query performance
CREATE INDEX idx_entity_status ON transactions(entity, payment_status);
CREATE INDEX idx_outlet_entity ON transactions(outlet, entity);
CREATE INDEX idx_payment_status ON transactions(payment_status);
