-- ============================================================================
-- PT BAGI KOPI INDONESIA - DUCKDB HIGH-PERFORMANCE ANALYTICAL QUERIES
-- High-speed OLAP queries executing directly against CSV / Parquet / Memory
-- ============================================================================

-- 1. Create In-Memory Table Directly from Clean CSV
CREATE TABLE IF NOT EXISTS duck_transactions AS 
SELECT * FROM read_csv_auto('data/bk_transactions_clean.csv');

-- ----------------------------------------------------------------------------
-- PERTANYAAN 1 (DUCKDB):
-- Total Penjualan Bersih (Net) Entitas Retail
-- ----------------------------------------------------------------------------
SELECT 
    SUM(net_amount) AS total_net_sales_retail,
    SUM(gross_amount) AS total_gross_sales_retail,
    SUM(discount_amount) AS total_discount_retail
FROM read_csv_auto('data/bk_transactions_clean.csv')
WHERE entity = 'Retail' AND payment_status = 'PAID';

-- ----------------------------------------------------------------------------
-- PERTANYAAN 2 (DUCKDB):
-- Outlet Retail Transaksi Unik Terbanyak
-- ----------------------------------------------------------------------------
SELECT 
    outlet,
    COUNT(DISTINCT transaction_id) AS total_unique_transactions,
    SUM(net_amount) AS total_outlet_net_sales
FROM read_csv_auto('data/bk_transactions_clean.csv')
WHERE entity = 'Retail' AND payment_status = 'PAID'
GROUP BY outlet
ORDER BY total_unique_transactions DESC;

-- ----------------------------------------------------------------------------
-- PERTANYAAN 3 (DUCKDB):
-- Overall ATV & Structural Entity Breakdown
-- ----------------------------------------------------------------------------
SELECT 
    entity,
    AVG(net_amount) AS entity_atv,
    SUM(net_amount) AS total_net_sales,
    COUNT(*) AS total_paid_transactions
FROM read_csv_auto('data/bk_transactions_clean.csv')
WHERE payment_status = 'PAID'
GROUP BY entity
ORDER BY entity_atv DESC;
