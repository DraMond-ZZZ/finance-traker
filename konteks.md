# Arsitektur Web Pencatatan Keuangan

## 1. Deskripsi Project

Web Pencatatan Keuangan adalah aplikasi berbasis REST API yang digunakan untuk membantu pengguna mencatat dan mengelola transaksi keuangan, baik berupa **pemasukan (income)** maupun **pengeluaran (expense)**.

Aplikasi ini berfokus pada sisi backend dengan menggunakan REST API sebagai penghubung antara client dan database. Pengguna dapat menambahkan, melihat, mengubah, dan menghapus data transaksi keuangan.

Project ini dibuat untuk memenuhi kebutuhan tugas akhir Backend Development yang mengharuskan adanya database relational dengan minimal 5 tabel, REST API dengan method GET, POST, PUT/PATCH, dan DELETE, deployment ke Vercel, pengujian menggunakan Postman/Thunder Client, serta dokumentasi API.

---

## 2. Tujuan Sistem

Sistem ini memiliki beberapa tujuan utama:

- Mencatat pemasukan dan pengeluaran pengguna.
- Mengelompokkan transaksi berdasarkan kategori.
- Menyimpan metode pembayaran yang digunakan.
- Membantu pengguna mengatur batas anggaran berdasarkan kategori.
- Menyediakan REST API untuk mengelola seluruh data.
- Menyediakan database relational yang memiliki hubungan antar tabel.
- Menyediakan API yang dapat diakses secara online setelah deployment.

---

## 3. Arsitektur Sistem

Arsitektur sistem menggunakan pola **Client → REST API → Database**.

```text
                         ┌──────────────────────┐
                         │        CLIENT        │
                         │                      │
                         │ Browser / Postman    │
                         │ Thunder Client       │
                         └──────────┬───────────┘
                                    │
                              HTTP Request
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │        VERCEL        │
                         │                      │
                         │     REST API         │
                         │                      │
                         │ GET                  │
                         │ POST                 │
                         │ PUT / PATCH          │
                         │ DELETE               │
                         └──────────┬───────────┘
                                    │
                              Query / ORM
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       DATABASE       │
                         │                      │
                         │    PostgreSQL        │
                         │                      │
                         │ users                │
                         │ categories           │
                         │ transactions         │
                         │ payment_methods      │
                         │ budgets              │
                         └──────────────────────┘
```

Frontend tidak menjadi bagian wajib dari project karena fokus utama tugas adalah pengembangan backend dan REST API.

---

## 4. Komponen Sistem

### 4.1 Client

Client merupakan pihak yang melakukan request ke REST API.

Client dapat berupa:

- Browser
- Postman
- Thunder Client
- Frontend apabila nantinya dikembangkan

Client mengirimkan HTTP request kepada API dan menerima response dalam format JSON.

---

### 4.2 REST API Backend

Backend bertugas menerima request dari client, melakukan validasi data, menjalankan proses bisnis, kemudian berkomunikasi dengan database.

Method HTTP yang digunakan:

| Method | Fungsi |
|---|---|
| GET | Mengambil data |
| POST | Menambahkan data |
| PUT | Mengubah seluruh data |
| PATCH | Mengubah sebagian data |
| DELETE | Menghapus data |

Resource utama dalam sistem adalah `transactions` karena digunakan untuk mencatat pemasukan dan pengeluaran.

---

### 4.3 Database

Database menggunakan relational database yang terdiri dari minimal 5 tabel.

Tabel yang digunakan:

1. `users`
2. `categories`
3. `transactions`
4. `payment_methods`
5. `budgets`

Setiap tabel memiliki primary key dan tabel yang saling berhubungan menggunakan foreign key.

---

# 5. Struktur Database

## 5.1 Tabel Users

Tabel `users` digunakan untuk menyimpan data pengguna.

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | BIGINT | Primary Key |
| name | VARCHAR | Nama pengguna |
| email | VARCHAR | Email pengguna |
| password | VARCHAR | Password pengguna |

---

## 5.2 Tabel Categories

Tabel `categories` digunakan untuk mengelompokkan transaksi berdasarkan jenis atau kategori.

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | BIGINT | Primary Key |
| name | VARCHAR | Nama kategori |
| type | VARCHAR | `income` / `expense` |

Contoh kategori:

- Gaji
- Makanan
- Transportasi
- Belanja
- Hiburan
- Lainnya

---

## 5.3 Tabel Transactions

Tabel `transactions` merupakan tabel utama untuk menyimpan transaksi keuangan.

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | BIGINT | Primary Key |
| user_id | BIGINT | Foreign Key → users.id |
| category_id | BIGINT | Foreign Key → categories.id |
| payment_method_id | BIGINT | Foreign Key → payment_methods.id |
| type | VARCHAR | `income` / `expense` |
| amount | DECIMAL | Jumlah uang |
| description | TEXT | Keterangan transaksi |
| transaction_date | DATE | Tanggal transaksi |

Contoh transaksi:

```json
{
  "type": "expense",
  "amount": 25000,
  "description": "Makan siang"
}
```

---

## 5.4 Tabel Payment Methods

Tabel `payment_methods` digunakan untuk menyimpan metode pembayaran.

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | BIGINT | Primary Key |
| name | VARCHAR | Nama metode pembayaran |

Contoh:

- Cash
- Bank
- E-Wallet
- QRIS

---

## 5.5 Tabel Budgets

Tabel `budgets` digunakan untuk menyimpan anggaran pengeluaran pengguna.

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | BIGINT | Primary Key |
| user_id | BIGINT | Foreign Key → users.id |
| category_id | BIGINT | Foreign Key → categories.id |
| amount | DECIMAL | Jumlah anggaran |
| month | INTEGER | Bulan |
| year | INTEGER | Tahun |

---

# 6. Relasi Antar Tabel

Relasi database:

```text
users
  │
  ├──────────────< transactions >────────────── categories
  │                       │
  │                       │
  │                       └──────────────> payment_methods
  │
  └──────────────< budgets >────────────────── categories
```

### Detail relasi

- Satu `user` dapat memiliki banyak `transactions`.
- Satu `category` dapat digunakan oleh banyak `transactions`.
- Satu `payment_method` dapat digunakan oleh banyak `transactions`.
- Satu `user` dapat memiliki banyak `budgets`.
- Satu `category` dapat memiliki banyak `budgets`.

---

# 7. REST API Endpoint

## Transactions

Resource utama memiliki CRUD lengkap.

### Get All Transactions

```http
GET /api/transactions
```

Digunakan untuk mengambil seluruh data transaksi.

### Get Transaction By ID

```http
GET /api/transactions/:id
```

Digunakan untuk mengambil satu transaksi berdasarkan ID.

### Create Transaction

```http
POST /api/transactions
```

Request body:

```json
{
  "user_id": 1,
  "category_id": 2,
  "payment_method_id": 1,
  "type": "expense",
  "amount": 25000,
  "description": "Makan siang",
  "transaction_date": "2026-10-19"
}
```

### Update Transaction

```http
PUT /api/transactions/:id
```

Digunakan untuk mengubah data transaksi.

### Delete Transaction

```http
DELETE /api/transactions/:id
```

Digunakan untuk menghapus transaksi.

---

# 8. Endpoint Lain

## Users

```http
GET     /api/users
GET     /api/users/:id
POST    /api/users
PUT     /api/users/:id
DELETE  /api/users/:id
```

## Categories

```http
GET     /api/categories
GET     /api/categories/:id
POST    /api/categories
PUT     /api/categories/:id
DELETE  /api/categories/:id
```

## Payment Methods

```http
GET     /api/payment-methods
GET     /api/payment-methods/:id
POST    /api/payment-methods
PUT     /api/payment-methods/:id
DELETE  /api/payment-methods/:id
```

## Budgets

```http
GET     /api/budgets
GET     /api/budgets/:id
POST    /api/budgets
PUT     /api/budgets/:id
DELETE  /api/budgets/:id
```

---

# 9. Format Response API

Response API menggunakan format JSON.

### Success

```json
{
  "message": "Transaksi berhasil ditambahkan",
  "data": {
    "id": 1,
    "type": "expense",
    "amount": 25000,
    "description": "Makan siang"
  }
}
```

### Error

```json
{
  "error": "Transaksi tidak ditemukan"
}
```

HTTP status code yang digunakan:

| Status | Keterangan |
|---|---|
| 200 | Request berhasil |
| 201 | Data berhasil dibuat |
| 400 | Input tidak valid |
| 404 | Data tidak ditemukan |
| 500 | Server error |

---

# 10. Struktur Backend

Struktur folder backend yang digunakan:

```text
finance-tracker/
│
├── src/
│   ├── controllers/
│   │   ├── userController.js
│   │   ├── transactionController.js
│   │   ├── categoryController.js
│   │   ├── paymentController.js
│   │   └── budgetController.js
│   │
│   ├── routes/
│   │   ├── userRoutes.js
│   │   ├── transactionRoutes.js
│   │   ├── categoryRoutes.js
│   │   ├── paymentRoutes.js
│   │   └── budgetRoutes.js
│   │
│   ├── models/
│   │   ├── User.js
│   │   ├── Transaction.js
│   │   ├── Category.js
│   │   ├── PaymentMethod.js
│   │   └── Budget.js
│   │
│   ├── middleware/
│   │   └── errorHandler.js
│   │
│   ├── config/
│   │   └── database.js
│   │
│   └── app.js
│
├── .env
├── .gitignore
├── package.json
├── vercel.json
└── README.md
```

---

# 11. Alur Pencatatan Transaksi

Contoh ketika pengguna mencatat pengeluaran:

```text
User
 │
 │ POST /api/transactions
 ▼
REST API
 │
 ├── Validasi data
 │
 ├── Cek user
 │
 ├── Cek category
 │
 ├── Cek payment method
 │
 ▼
Database
 │
 └── INSERT transaction
 │
 ▼
REST API
 │
 │ Response JSON
 ▼
Client
```

---

# 12. Deployment

Backend akan di-deploy menggunakan **Vercel**.

```text
GitHub Repository
       │
       ▼
     Vercel
       │
       ▼
Public API URL
       │
       ▼
Postman / Thunder Client
```

Database menggunakan database online seperti PostgreSQL pada layanan yang dapat diakses melalui internet.

Environment variable digunakan untuk menyimpan konfigurasi database dan secret key.

Contoh:

```env
DATABASE_URL=your_database_url
JWT_SECRET=your_secret
```

File `.env` tidak boleh dimasukkan ke repository GitHub.

---

# 13. Pengujian

Setiap endpoint akan diuji menggunakan Postman atau Thunder Client.

Pengujian meliputi:

- GET seluruh data
- GET data berdasarkan ID
- POST data baru
- PUT/PATCH data
- DELETE data
- Pengujian input tidak valid
- Pengujian data yang tidak ditemukan

Bukti pengujian dapat berupa screenshot request dan response atau export collection.

---

# 14. Dokumentasi

Dokumentasi project akan dibuat dalam `README.md`.

Isi dokumentasi:

1. Deskripsi project
2. Tujuan sistem
3. Arsitektur sistem
4. ERD/database
5. Daftar endpoint
6. Request dan response setiap endpoint
7. Status code
8. URL deployment
9. Cara menjalankan project secara lokal
10. Bukti pengujian API

---

# 15. Teknologi yang Digunakan

| Teknologi | Fungsi |
|---|---|
| Node.js | Runtime backend |
| Express.js | Framework REST API |
| PostgreSQL | Relational database |
| Vercel | Deployment backend |
| Postman / Thunder Client | Testing API |
| GitHub | Repository project |
| DrawSQL / dbdiagram.io | Membuat ERD |

---

# 16. Kesimpulan Arsitektur

Web Pencatatan Keuangan menggunakan arsitektur **Client → REST API → Database**. Sistem memiliki lima tabel utama yaitu `users`, `categories`, `transactions`, `payment_methods`, dan `budgets` yang saling berelasi menggunakan foreign key.

Resource `transactions` digunakan sebagai resource utama dan menyediakan operasi CRUD lengkap untuk mencatat pemasukan dan pengeluaran. REST API menggunakan method GET, POST, PUT/PATCH, dan DELETE serta mengembalikan response dalam format JSON.

Backend akan diuji menggunakan Postman atau Thunder Client dan di-deploy ke Vercel agar API dapat diakses secara publik.