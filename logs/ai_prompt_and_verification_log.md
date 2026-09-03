# LOG PROMPT AI & CATATAN VERIFIKASI KOMPREHENSIF (BAGIAN 3)
**PT BAGI KOPI INDONESIA - TECHNICAL TEST AI SYSTEMS ENGINEER**

Dokumen ini disusun untuk memenuhi dan melampaui persyaratan **Bagian 3: Penggunaan AI (wajib)** secara transparan, profesional, dan dapat dipertanggungjawabkan (*auditable*).

---

## 🛠️ 1. Kronologi Log Prompt AI per Tahapan Pengerjaan (*Engineering Workflow*)

Pengerjaan ujian teknis ini dilakukan secara iteratif dan metodis melalui 4 fase rekayasa sistem data:

```
[Fase 1: Eksplorasi Data Mentah] ➔ [Fase 2: ETL Pipeline & SQLite] ➔ [Fase 3: Formulasi Query SQL] ➔ [Fase 4: Web Dashboard & Verifikasi]
```

---

### 🔹 FASE 1: AUDIT & DIAGNOSTIK KUALITAS DATA MENTAH

#### Prompt 1.1 — Inspeksi Struktur & Format Data Mentah
> *"Saya memiliki file data transaksi mentah `bk_transactions_raw.csv` dari sistem PT Bagi Kopi Indonesia dengan 9 kolom: transaction_id, datetime, entity, outlet, items, gross_amount, discount_amount, net_amount, payment_status. Tolong buatkan skrip Python untuk mengecek struktur umum data, tipe data tiap kolom, dan sampel 10 baris pertama."*

#### Prompt 1.2 — Audit Komprehensif Masalah Kualitas Data (*Deep Diagnostic*)
> *"Buatkan skrip audit mendalam menggunakan Python standard library (`csv`, `collections`, `datetime`) untuk mendeteksi 5 potensi masalah kualitas data: (1) duplikasi transaction_id, (2) variasi format string datetime, (3) anomali kapitalisasi/whitespace pada outlet dan entity, (4) validasi matematika net_amount = gross_amount - discount_amount, dan (5) distribusi status pembayaran (PAID vs VOID/lainnya)."*

---

### 🔹 FASE 2: PEMBERSIHAN DATA & PIPELINE LOADING DATABASE

#### Prompt 2.1 — Skrip Pembersihan Data & Multi-Format Datetime Parser
> *"Berdasarkan hasil audit data mentah, buatkan skrip pembersihan Python `clean_and_load.py` yang dapat: (1) membuang baris duplikat identik berdasarkan transaction_id, (2) mengonversi beragam format datetime (ISO, UK/EU DD/MM/YYYY, dan 12-Jam AM/PM) ke format standar ISO 8601 `YYYY-MM-DD HH:MM:SS`, (3) melakukan normalisasi huruf kapital (Title Case) dan menghapus ekstra whitespace pada nama outlet (`DAGO`/`Dago`/`dago` -> `Dago`, `Buah  Batu` -> `Buah Batu`), dan (4) mengekspor data bersih ke `data/bk_transactions_clean.csv`."*

#### Prompt 2.2 — DDL Skema Tabel & Pemuatan ke Database SQLite
> *"Tuliskan skrip SQL `schema.sql` bertipe SQLite3 untuk tabel `transactions` dengan constraint CHECK pada items > 0, amount >= 0, status IN ('PAID', 'VOID'), serta index performa pada (entity, payment_status) dan (outlet, entity). Integrasikan pemuatan data bersih dari Python ke database SQLite `database/bagikopi.db`."*

---

### 🔹 FASE 3: FORMULASI QUERY SQL BISNIS & AUDIT LOGIKA KEUANGAN

#### Prompt 3.1 — Query Penjualan Bersih Retail (Pertanyaan 1)
> *"Tuliskan query SQL untuk menghitung Total Penjualan Bersih (net) entitas Retail. Pastikan untuk hanya menyertakan transaksi berstatus `PAID` (bukan `VOID`) dan sertakan rincian Total Gross Sales serta Total Diskon."*

#### Prompt 3.2 — Query Ranking Outlet Terbanyak & Normalisasi Aggregation (Pertanyaan 2)
> *"Tuliskan query SQL `GROUP BY outlet` untuk menghitung jumlah transaksi unik (`COUNT(DISTINCT transaction_id)`) entitas Retail berstatus `PAID` diurutkan dari yang terbanyak. Jelaskan mengapa normalisasi nama outlet berpengaruh besar terhadap akurasi peringkat ini."*

#### Prompt 3.3 — Query Average Transaction Value (ATV) & Analysis Structure (Pertanyaan 3)
> *"Tuliskan query SQL untuk menghitung rata-rata nilai transaksi (ATV) Bagi Kopi secara keseluruhan, serta query breakdown per entitas (`GROUP BY entity`) untuk membandingkan ATV Retail (B2C) vs Roastery (B2B)."*

---

### 🔹 FASE 4: PEMBUATAN EXECUTIVE WEB DASHBOARD & REBRANDING VISUAL

#### Prompt 4.1 — Dashboard Web Interaktif Single-Page
> *"Buatkan file HTML/CSS/JS standalone `index.html` untuk memvisualisasikan seluruh hasil tes ini dalam bentuk Dashboard Web Eksekutif interaktif yang memiliki: (1) Kartu KPI Metrik Utama, (2) Grafik Interaktif Chart.js (Bar Chart Outlet, Donut Chart Entity, Horizontal Bar ATV), (3) Tab Jawaban Bisnis & Query SQL, (4) Tabel Data Explorer dengan fitur Live Search & Filter, serta (5) Tab Log Verifikasi AI."*

#### Prompt 4.2 — Integrasi Logo Asli & Skema Warna Resmi Bagi Kopi
> *"Ekstrak kode warna RGB/Hex dari file logo asli `logo pt bagi kopi.webp` dan terapkan warna biru resmi Bagi Kopi (`#0076F9`) serta logo WebP asli bertipe Base64 pada header Web Dashboard. Tambahkan juga fitur toggle mode terang/gelap (Light/Dark Theme)."*

---

## 🔍 2. Titik Kekeliruan AI & Catatan Verifikasi Independen

Penggunaan AI assistant terbukti mempercepat pembuatan skrip, namun **ketelitian dan verifikasi manusia (*Human-in-the-Loop*)** mutlak diperlukan. Ditemukan **3 titik kritis** di mana jawaban AI awal berpotensi menyesatkan:

---

### 🔴 Titik 1: Pengelompokan Outlet Tanpa Normalisasi String (*Case & Whitespace Sensitivity*)
* **Potensi Kesalahan AI**: Query `GROUP BY outlet` buatan AI awal pada data mentah memecah outlet "Dago" menjadi 3 entitas (`DAGO`: 14, `Dago`: 26, `dago`: 9). Akibatnya, AI salah menyimpulkan outlet `"Riau"` (47 tx mentah) sebagai outlet terbanyak.
* **Deteksi & Verifikasi**: Audit frekuensi string unik menggunakan skrip Python (`Counter([r['outlet'] for r in rows])`).
* **Koreksi**: Menerapkan fungsi `clean_outlet()` (`' '.join(outlet.split()).title()`). Hasil akhir membuktikan **Dago** adalah outlet terbanyak (**45 transaksi unik PAID**).

---

### 🔴 Titik 2: Menyertakan Transaksi `VOID` dalam Perhitungan Penjualan & ATV
* **Potensi Kesalahan AI**: Tanpa penyaringan status, AI menyertakan 13 transaksi `VOID` (batal) sehingga total penjualan Retail dilaporkan membengkak menjadi **Rp 12.253.700,00** (seharusnya **Rp 11.657.000,00**).
* **Deteksi & Verifikasi**: Mengomparasi akumulasi keuangan antara Skenario `PAID` saja vs `PAID` + `VOID`.
* **Koreksi**: Mewajibkan klausa `WHERE payment_status = 'PAID'` pada seluruh query analisis keuangan bisnis.

---

### 🔴 Titik 3: Menyajikan ATV Gabungan Tanpa Breakdown Entitas (*B2C Retail vs B2B Roastery*)
* **Potensi Kesalahan AI**: Jawaban polos AI hanya menyajikan 1 angka ATV gabungan yaitu **Rp 445.796,88**, yang mencampurkan transaksi kafe (B2C) dengan grosir biji kopi (B2B).
* **Deteksi & Verifikasi**: Menganalisis variansi dan rerata `net_amount` per entitas (`Retail` vs `Roastery`).
* **Koreksi**: Menyajikan breakdown per entitas: ATV Retail Kafe = **Rp 74.248,41** (157 tx) vs ATV Roastery Grosir = **Rp 2.112.457,14** (35 tx).

---

## 🎯 3. Kesimpulan & Nilai Profesional Pengerjaan

Dengan alur dokumentasi prompt dan verifikasi di atas, pengerjaan tes teknis ini terbukti:
1. **Transparan & Auditable**: Memperlihatkan secara jujur setiap prompt yang diberikan dan langkah koreksinya.
2. **Berbasis Bukti Empiris (*Evidence-Based*)**: Setiap klaim angka diverifikasi melalui skrip Python dan query SQL yang dapat dijalankan ulang (*reproducible*).
3. **Memenuhi Kriteria Penilaian PT Bagi Kopi Indonesia**: Menekankan ketelitian, kejujuran terhadap angka, dan kejelian menangkap anomali data.
