# LOG PROMPT AI & CATATAN VERIFIKASI (BAGIAN 3)
**PT BAGI KOPI INDONESIA - TECHNICAL TEST AI SYSTEMS ENGINEER**

Dokumen ini disusun untuk memenuhi persyaratan **Bagian 3: Penggunaan AI (wajib)**.

---

## 1. Log Prompt AI yang Digunakan

Berikut adalah daftar *prompt* utama yang digunakan selama proses pengerjaan tes teknis ini:

### Prompt 1: Eksplorasi Data Mentah & Identifikasi Masalah Kualitas
> *"Saya memiliki file data transaksi mentah `bk_transactions_raw.csv` dari sistem PT Bagi Kopi Indonesia dengan kolom: transaction_id, datetime, entity, outlet, items, gross_amount, discount_amount, net_amount, payment_status. Tolong buatkan skrip analisis data mentah menggunakan Python untuk mengecek: (1) duplikasi transaction_id, (2) variasi format datetime, (3) anomali penulisan string pada entity dan outlet, (4) validasi matematika net_amount = gross_amount - discount_amount, dan (5) distribusi payment_status."*

### Prompt 2: Pembersihan Data & Pemuatan ke Database SQLite
> *"Berdasarkan temuan audit kualitas data, buatkan skrip Python `clean_and_load.py` dan DDL SQL `schema.sql` untuk: (1) membersihkan data mentah, (2) melakukan normalisasi huruf kapital & whitespace pada outlet/entity, (3) mengonversi datetime beragam format ke standar ISO 8601, (4) mendeduplikasi baris berdasarkan transaction_id, (5) mengekspor data bersih ke `bk_transactions_clean.csv`, dan (6) memuat data bersih ke database SQLite `bagikopi.db` dengan skema tabel bertipe data yang tepat."*

### Prompt 3: Penyusunan Query SQL Bisnis & Verifikasi Skenario (PAID vs VOID)
> *"Tuliskan query SQL standar untuk menjawab 3 pertanyaan bisnis: (1) Total penjualan bersih Retail, (2) Outlet Retail transaksi unik terbanyak, (3) ATV Bagi Kopi secara keseluruhan. Pastikan untuk memperhitungkan status transaksi `PAID` vs `VOID` dan menyertakan breakdown entitas Retail vs Roastery."*

---

## 2. Titik Kekeliruan / Potensi Jawaban Menyesatkan dari AI & Langkah Verifikasinya

Dalam pengerjaan tes ini, terdapat **3 titik krusial** di mana hasil/query buatan AI berpotensi memberikan angka yang menyesatkan jika diterima secara mentah tanpa verifikasi:

---

### Titik 1: Pengelompokan Outlet Tanpa Normalisasi String (*Case & Whitespace Sensitivity*)

* **Deskripsi Masalah / Jawaban Menyesatkan AI**:
  Jika AI diminta menulis query `GROUP BY outlet` langsung pada data mentah, AI menghasilkan pengelompokan sebagai berikut:
  - `Riau`: 47 transaksi (tampak sebagai terbanyak!)
  - `Dago`: 26 transaksi
  - `DAGO`: 14 transaksi
  - `dago`: 9 transaksi
  
  Tanpa verifikasi, AI akan menyimpulkan bahwa **Outlet Riau** adalah outlet dengan transaksi terbanyak.

* **Cara Menangkap / Deteksi**:
  Pemeriksaan distribusi nilai unik pada kolom `outlet` menggunakan script Python audit (`Counter([r['outlet'] for r in rows])`) mengungkapkan adanya variasi kapitalisasi (`DAGO`, `Dago`, `dago`) serta *double space* pada `Buah  Batu`.

* **Langkah Verifikasi & Perbaikan**:
  Dibuat fungsi normalisasi string `clean_outlet()` (`' '.join(outlet.strip().split()).title()`).
  Setelah data dibersihkan dan digabungkan:
  - **Dago**: Total **49 transaksi mentah** (45 transaksi `PAID`).
  - **Riau**: Total **47 transaksi mentah** (39 transaksi `PAID`).
  
  **Kesimpulan yang Benar**: Outlet Retail terbanyak adalah **Dago** (45 transaksi unik PAID).

---

### Titik 2: Menyertakan Transaksi `VOID` dalam Perhitungan Penjualan & ATV

* **Deskripsi Masalah / Jawaban Menyesatkan AI**:
  Jika query AI tidak menyertakan filter `WHERE payment_status = 'PAID'`, maka 13 transaksi bertipe `VOID` (dibatalkan/tidak terjadi pembayaran) ikut terhitung sebagai pendapatan bisnis.
  
  *Dampak kesalahan jika VOID dihitung:*
  - Total Net Sales Retail dilaporkan **Rp 12.253.700,00** (padahal arus kas bersih nyata hanya **Rp 11.657.000,00**).
  - ATV Keseluruhan dilaporkan **Rp 420.437,56** (padahal ATV transaksi berhasil adalah **Rp 445.796,88**).

* **Cara Menangkap / Deteksi**:
  Memeriksa kolom `payment_status` dan mengomparasi hasil akumulasi keuangan antara Skenario A (`PAID` saja) dan Skenario B (`PAID` + `VOID`).

* **Langkah Verifikasi & Perbaikan**:
  Menerapkan klausa wajib `WHERE payment_status = 'PAID'` pada seluruh query analisis penjualan bisnis dan memberikan catatan transparan mengenai status `VOID`.

---

### Titik 3: Menyajikan ATV Keseluruhan Tanpa Breakdown Entitas (*B2C Retail vs B2B Roastery*)

* **Deskripsi Masalah / Jawaban Menyesatkan AI**:
  Jawaban polos AI untuk Pertanyaan 3 hanya memberikan satu angka: **Rp 445.796,88**.
  Secara matematika angka ini benar untuk rata-rata gabungan. Namun, secara analisis bisnis, angka ini **sangat menyesatkan** bagi manajemen kafe karena mencampurkan dua model bisnis yang sangat berbeda:
  - Retail (Kafe / B2C)
  - Roastery (Grosir / B2B)

* **Cara Menangkap / Deteksi**:
  Memeriksa deviasi standar dan rerata harga net per entitas.
  - ATV Retail (Kafe): **Rp 74.248,41** per transaksi (157 transaksi).
  - ATV Roastery (Grosir B2B): **Rp 2.112.457,14** per transaksi (35 transaksi).

* **Langkah Verifikasi & Perbaikan**:
  Menyajikan jawaban lengkap dengan klausa `GROUP BY entity` untuk memberikan gambaran kontekstual yang jelas kepada *stakeholder* bisnis.

---

## 3. Kesimpulan Verifikasi Hasil AI

Penggunaan AI sangat mempercepat pembuatan skrip dan query SQL, namun **kejujuran terhadap angka dan validasi independen** melalui skrip Python audit independen terbukti mutlak diperlukan untuk mencegah kesalahan interpretasi data bisnis.
