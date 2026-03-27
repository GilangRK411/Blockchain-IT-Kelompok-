# Dokumentasi Proyek Blockchain Sederhana

## Anggota Kelompok

### Ditya Wahyu Ramadhan - 5027221051

### Gilang Raya Kurniawan - 5027220145

---

## Output yang Harus Dikumpulkan

* Source code project
* Dokumentasi dalam format Markdown
* Screenshot pengujian (menggunakan Postman / Browser), masukkan ke dalam dokumentasi Markdown:

  * Penambahan transaksi
  * Proses mining
  * Reward miner
  * Validasi digital signature
  * Sinkronisasi antar-node

---

## Arsitektur Sistem

Sistem terdiri dari beberapa komponen utama:

* Blockchain: Menyimpan rantai blok dan transaksi
* Node: Instance server yang menjalankan blockchain
* Wallet: Digunakan untuk membuat public/private key
* API: Endpoint untuk interaksi menggunakan HTTP (Postman/Browser)

---

## Cara Menjalankan Program

1. Pastikan Python sudah terinstall
2. Install dependency:

   ```bash
   pip install flask requests ecdsa
   ```
3. Jalankan server:

   ```bash
   python nama_file.py -p 5000
   ```
4. Server akan berjalan di:

   ```
   http://127.0.0.1:5000
   ```

---

## Pengujian Menggunakan Postman

### 1. Pembuatan Wallet

**Endpoint:**

```
GET /wallet/new
```

**Deskripsi:**
Digunakan untuk membuat pasangan public key dan private key.

**Screenshot:**
<img width="1920" height="1080" alt="Screenshot (793)" src="https://github.com/user-attachments/assets/3b90aa79-39b1-4e43-b657-76f02023d628" />

---

### 2. Validasi Digital Signature

**Endpoint:**

```
POST /wallet/sign
```

**Body (JSON):**

```json
{
  "private_key": "PRIVATE_KEY",
  "recipient": "alamat_tujuan",
  "amount": 1000
}
```

**Deskripsi:**
Digunakan untuk membuat digital signature berdasarkan private key. Signature ini akan digunakan saat mengirim transaksi.

**Screenshot:**
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/9d882d35-8e55-4f6b-88a6-31a9d8cb7267" />

---

### 3. Penambahan Transaksi

**Endpoint:**

```
POST /transactions/new
```

**Body (JSON):**

```json
{
  "sender": "PUBLIC_KEY",
  "recipient": "alamat_tujuan",
  "amount": 10,
  "signature": "SIGNATURE"
}
```

**Deskripsi:**
Menambahkan transaksi baru ke dalam mempool (daftar transaksi sementara). Transaksi hanya akan ditambahkan jika digital signature valid.

**Screenshot:**
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/033f350b-3804-423a-bb99-6c96fc85f99a" />

---

### 4. Proses Mining

**Endpoint:**

```
GET /mine
```

**Deskripsi:**
Melakukan proses Proof of Work untuk membuat block baru. Semua transaksi dalam mempool akan dimasukkan ke dalam block.

**Screenshot:**
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/dd36eb5d-5d40-4b5c-96b6-51d5680c953b" />

---

### 5. Reward Miner

**Deskripsi:**
Saat proses mining berhasil, sistem secara otomatis memberikan reward kepada miner sebesar 10 coin.

Reward ditambahkan melalui transaksi khusus dengan:

* sender = "0"
* recipient = node_identifier

**Screenshot:**
<img width="390" height="107" alt="image" src="https://github.com/user-attachments/assets/1138e129-fe34-4aa4-bb53-b41bf1568672" />

---

### 6. Melihat Blockchain

**Endpoint:**

```
GET /chain
```

**Deskripsi:**
Menampilkan seluruh isi blockchain yang telah terbentuk.

**Screenshot:**
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/50ad3d38-7e69-4cd8-bc81-69345c93cd49" />

---

### 7. Sinkronisasi Antar-Node

#### a. Registrasi Node

**Endpoint:**

```
POST /nodes/register
```

**Body (JSON):**

```json
{
  "nodes": [
    "http://127.0.0.1:5001"
  ]
}
```

#### b. Konsensus (Sinkronisasi)

**Endpoint:**

```
GET /nodes/resolve
```

**Deskripsi:**
Node akan membandingkan blockchain miliknya dengan node lain, dan mengganti chain jika ditemukan chain yang lebih panjang dan valid.

**Screenshot:**
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/f1e2d2b0-5b53-4782-a551-8c440ad8f30f" />

---

## Alur Sistem

1. User membuat wallet
2. User melakukan signing transaksi
3. Transaksi dikirim ke jaringan
4. Miner melakukan proses mining
5. Block baru ditambahkan ke blockchain
6. Miner mendapatkan reward
7. Node melakukan sinkronisasi jika diperlukan

---

## Kesimpulan

Implementasi ini menunjukkan konsep dasar blockchain meliputi transaksi, validasi, mining, dan konsensus. Meskipun masih sederhana, sistem ini sudah mencerminkan mekanisme utama yang digunakan pada teknologi blockchain secara umum.

---
