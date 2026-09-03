-- ============================================================================
-- PT BAGI KOPI INDONESIA - BUSINESS QUESTIONS SQL QUERIES
-- Target Database: SQLite / DuckDB / PostgreSQL
-- Table: transactions
-- Note: Only completed transactions (payment_status = 'PAID') represent real sales.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- PERTANYAAN 1:
-- Total penjualan bersih (net) untuk entitas Retail selama periode data.
-- ----------------------------------------------------------------------------
SELECT 
    SUM(net_amount) AS total_net_sales_retail,
    SUM(gross_amount) AS total_gross_sales_retail,
    SUM(discount_amount) AS total_discount_retail,
    COUNT(*) AS total_paid_transactions
FROM transactions
WHERE entity = 'Retail' 
  AND payment_status = 'PAID';


-- ----------------------------------------------------------------------------
-- PERTANYAAN 2:
-- Outlet Retail dengan jumlah transaksi (unik) terbanyak (sebutkan outlet dan angkanya).
-- ----------------------------------------------------------------------------
SELECT 
    outlet,
    COUNT(DISTINCT transaction_id) AS total_unique_transactions,
    SUM(net_amount) AS total_outlet_net_sales
FROM transactions
WHERE entity = 'Retail' 
  AND payment_status = 'PAID'
GROUP BY outlet
ORDER BY total_unique_transactions DESC;


-- ----------------------------------------------------------------------------
-- PERTANYAAN 3:
-- Berapa rata-rata nilai transaksi (Average Transaction Value / ATV) Bagi Kopi secara keseluruhan?
-- ----------------------------------------------------------------------------
-- Query 3A: ATV Bagi Kopi Secara Keseluruhan (Combined Retail + Roastery)
SELECT 
    AVG(net_amount) AS overall_atv,
    SUM(net_amount) AS total_net_sales_all,
    COUNT(*) AS total_paid_transactions_all
FROM transactions
WHERE payment_status = 'PAID';

-- Query 3B: Breakdown ATV per Entitas (Retail vs Roastery) untuk Konteks Analisis Bisnis
SELECT 
    entity,
    AVG(net_amount) AS entity_atv,
    SUM(net_amount) AS total_net_sales,
    COUNT(*) AS total_paid_transactions
FROM transactions
WHERE payment_status = 'PAID'
GROUP BY entity
ORDER BY entity_atv DESC;
