# Technical Test AI Systems Engineer - PT Bagi Kopi Indonesia

Dokumen ini berisi solusi lengkap, skrip pembersihan data, pengolahan database, analisis pertanyaan bisnis, serta log penggunaan dan verifikasi AI untuk ujian teknis **AI Systems Engineer** di **PT Bagi Kopi Indonesia**.

---

## 📋 Ringkasan Eksekutif

| Indikator / Aspek | Nilai / Keterangan |
| :--- | :--- |
| **Total Baris Mentah (`bk_transactions_raw.csv`)** | 219 baris |
| **Jumlah Baris Duplikat Dieliminasi** | 14 baris (100% duplikat identik) |
| **Total Baris Data Bersih** | 205 baris |
| **Jumlah Transaksi Berhasil (`PAID`)** | 192 transaksi (157 Retail, 35 Roastery) |
| **Jumlah Transaksi Dibatalkan (`VOID`)** | 13 transaksi (semua entitas Retail) |
| **Periode Data Transaksi** | 01 September 2026 s.d. 14 September 2026 |
| **Database yang Penggunaannya Digunakan** | SQLite 3 (`database/bagikopi.db`) |

---

## 🛠️ Struktur Repositori

```text
bagikopi-test/
├── README.md                           # Laporan Utama & Dokumentasi Lengkap
├── data/
│   ├── bk_transactions_raw.csv         # Dataset mentah awal
│   └── bk_transactions_clean.csv       # Dataset hasil pembersihan (Cleaned CSV)
├── database/
│   └── bagikopi.db                     # Database SQLite berisi tabel transactions
├── scripts/
│   ├── clean_and_load.py               # Skrip Python pembersihan data & loading ke DB
│   └── run_queries.py                  # Skrip Python eksekusi query bisnis & formatting
├── sql/
│   ├── schema.sql                      # DDL Schema tabel database SQLite
│   ├── clean_and_load.sql              # Dokumentasi alur pembersihan & pemuatan SQL
│   └── business_questions.sql          # Query SQL resmi untuk 3 Pertanyaan Bisnis
└── logs/
    └── ai_prompt_and_verification_log.md # Log Prompt AI & Catatan Verifikasi (Bagian 3)
```

---

## 🆑 Bagian 1: Pembersihan & Pemuatan Data

### 1. Temuan Masalah Kualitas Data & Keputusan Penanganannya

Berdasarkan audit komprehensif terhadap `bk_transactions_raw.csv`, ditemukan 4 masalah utama kualitas data:

| No | Masalah Kualitas Data | Cara Mendeteksinya | Keputusan & Penanganannya |
| :-: | :--- | :--- | :--- |
| **1** | **Duplikasi Baris Transaksi** *(14 baris duplikat)* | Pengecekan frekuensi `transaction_id` menggunakan Python (`Counter`). Ditemukan 14 ID transaksi muncul 2x dengan data identik (misal: `TRX1009`, `TRX1116`, `TRX1198`). | Mengeliminasi baris duplikat dan mempertahankan **1 record pertama** (*deduplication by `transaction_id`*). |
| **2** | **Inkonsistensi Format Datetime** | Pengecekan format string pada kolom `datetime`. Terdapat variasi: ISO (`2026-09-02 17:13:00`), UK/EU (`01/09/2026 10:59`), dan 12-Jam AM/PM (`11 Sep 2026 12:17 PM`). | Mengonversi seluruh variasi string datetime ke **format standar ISO 8601** (`YYYY-MM-DD HH:MM:SS`) menggunakan parser bertingkat. |
| **3** | **Inkonsistensi Penulisan Nama Outlet & Entity** | Audit string unik menunjukkan variasi kapitalisasi pada outlet (`DAGO`, `Dago`, `dago`) serta spasi ganda (`Buah  Batu`). | Menerapkan normalisasi string: penyesuaian huruf kapital (*Title Case*) dan penghapusan ekstra whitespace (`' '.join(outlet.split()).title()`). |
| **4** | **Status Transaksi Batal (`VOID`)** | Pengecekan kolom `payment_status` menemukan 13 transaksi bernilai Rp 596.700 berstatus `VOID`. | Tetap memasukkan data `VOID` ke database untuk integritas audit trail, tetapi **memfilter hanya status `PAID`** saat menghitung pendapatan dan ATV bisnis. |

---

### 2. Skrip Pemuatan ke Database (`scripts/clean_and_load.py`)

Data yang telah dibersihkan dimasukkan ke dalam database SQLite (`database/bagikopi.db`) menggunakan skema berikut:

```sql
-- DDL Tabel Database (sql/schema.sql)
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
```

---

## 📊 Bagian 2: Jawaban Tiga Pertanyaan Bisnis

### Pertanyaan 1: Total Penjualan Bersih (Net) Entitas Retail

* **Jawaban & Angka**: **Rp 11.657.000,00** *(Rp 11,657 Juta)*
* **Detail Rincian**:
  * Total Penjualan Kotor (Gross): Rp 12.032.000,00
  * Total Diskon: Rp 375.000,00
  * Total Penjualan Bersih (Net): Rp 11.657.000,00
  * Total Transaksi Berhasil (`PAID`): 157 transaksi

#### Query SQL (Pertanyaan 1):
```sql
SELECT 
    SUM(net_amount) AS total_net_sales_retail
FROM transactions
WHERE entity = 'Retail' 
  AND payment_status = 'PAID';
```

> **Catatan Validasi Bisnis**: Jika transaksi `VOID` (13 transaksi bernilai Rp 596.700) ikut dihitung secara keliru, angka penjualan akan membengkak menjadi Rp 12.253.700,00. Oleh karena itu, penyaringan status `PAID` mutlak diperlukan.

---

### Pertanyaan 2: Outlet Retail dengan Jumlah Transaksi (Unik) Terbanyak

* **Jawaban & Angka**: Outlet **Dago** dengan **45 transaksi (unik)**.
* **Peringkat Lengkap Outlet Retail**:

| Peringkat | Nama Outlet | Jumlah Transaksi Unik (`PAID`) | Total Penjualan Bersih (Net) |
| :-: | :--- | :-: | :--- |
| **1** | **Dago** | **45** | **Rp 3.503.800,00** |
| **2** | **Riau** | **39** | **Rp 2.866.000,00** |
| **3** | **Ciumbuleuit** | **38** | **Rp 2.655.400,00** |
| **4** | **Buah Batu** | **35** | **Rp 2.631.800,00** |

#### Query SQL (Pertanyaan 2):
```sql
SELECT 
    outlet,
    COUNT(DISTINCT transaction_id) AS total_unique_transactions
FROM transactions
WHERE entity = 'Retail' 
  AND payment_status = 'PAID'
GROUP BY outlet
ORDER BY total_unique_transactions DESC;
```

> **Pentingnya Pembersihan Data**: Sebelum dilakukan pembersihan data, outlet Dago terpecah menjadi 3 entitas (`DAGO`: 14, `Dago`: 26, `dago`: 9). Tanpa normalisasi, outlet Riau (47 transaksi mentah) seolah-olah terlihat paling atas. Setelah normalisasi huruf kapital (*Title Case*), outlet **Dago** terbukti sebagai outlet terbanyak.

---

### Pertanyaan 3: Rata-Rata Nilai Transaksi (ATV) Bagi Kopi Secara Keseluruhan

* **Jawaban & Angka**: **Rp 445.796,88** per transaksi.
* **Detail Rincian Keseluruhan**:
  * Total Penjualan Bersih (Net) Keseluruhan: Rp 85.593.000,00
  * Total Transaksi Berhasil (`PAID`): 192 transaksi
  * Formula: `Rp 85.593.000,00 / 192 = Rp 445.796,875`

#### Query SQL (Pertanyaan 3A - Overall ATV):
```sql
SELECT 
    AVG(net_amount) AS overall_atv
FROM transactions
WHERE payment_status = 'PAID';
```

#### Breakdown Kontekstual Per Entitas (Pertanyaan 3B):
Untuk kebutuhan analisis bisnis operasional yang valid, berikut adalah pemisahan ATV berdasarkan entitas bisnis:

| Entitas | Tipe Bisnis | ATV (Rata-rata) | Total Penjualan Bersih | Jumlah Transaksi |
| :--- | :--- | :--- | :--- | :--- |
| **Roastery** | B2B (Grosir Biji Kopi) | **Rp 2.112.457,14** | Rp 73.936.000,00 | 35 |
| **Retail** | B2C (Kafe / Outlet) | **Rp 74.248,41** | Rp 11.657.000,00 | 157 |
| **GABUNGAN** | **Bagi Kopi Overall** | **Rp 445.796,88** | **Rp 85.593.000,00** | **192** |

#### Query SQL (Pertanyaan 3B - Entity Breakdown):
```sql
SELECT 
    entity,
    AVG(net_amount) AS entity_atv,
    SUM(net_amount) AS total_net_sales,
    COUNT(*) AS total_paid_transactions
FROM transactions
WHERE payment_status = 'PAID'
GROUP BY entity
ORDER BY entity_atv DESC;
```

> **Penjelasan Validasi Bisnis**: ATV gabungan (Rp 445.796,88) jauh lebih tinggi daripada ATV kafe retail (Rp 74.248,41) karena terdorong nilai transaksi B2B Roastery yang besar. Menyajikan breakdown entitas sangat penting agar manajemen tidak salah menginterpretasikan performa belanja konsumen kafe retail.

---

## 🤖 Bagian 3: Penggunaan AI & Verifikasi (Wajib)

Dokumen lengkap log AI dan langkah verifikasi tersedia di [`logs/ai_prompt_and_verification_log.md`](file:///Users/user/bagikopi-test/logs/ai_prompt_and_verification_log.md).

### Ringkasan Titik Koreksi AI:
1. **Normalisasi String Outlet**: Mencegah kesalahan AI yang membagi outlet "Dago" menjadi 3 entitas terpisah.
2. **Penyaringan Status VOID**: Mencegah AI memasukkan 13 transaksi batal ke dalam perhitungan arus kas bisnis.
3. **Analisis Struktur Entitas Bisnis**: Memverifikasi pemisahan ATV B2C Retail (Rp 74.248) vs B2B Roastery (Rp 2.112.457).

---

## 🚀 Cara Menjalankan Pipeline (*Reproducibility*)

Untuk menjalankan seluruh pipeline pembersihan data, pembuatan database, dan pencetakan laporan bisnis:

### 1. Jalankan Skrip Cleaning & Loading Database
```bash
python3 scripts/clean_and_load.py
```

### 2. Jalankan Skrip Eksekusi Query Bisnis
```bash
python3 scripts/run_queries.py
```

### 3. Eksekusi via SQLite CLI (Opsional)
```bash
sqlite3 database/bagikopi.db < sql/business_questions.sql
```
