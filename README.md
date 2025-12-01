# Book Learning API - Backend Server

Backend API server cho ứng dụng Book Learning được xây dựng bằng FastAPI.

## 📋 Mục lục

- [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
- [Cài đặt](#cài-đặt)
- [Cấu hình](#cấu-hình)
- [Chạy server](#chạy-server)
- [Database Migrations](#database-migrations)
- [API Documentation](#api-documentation)
- [Cấu trúc dự án](#cấu-trúc-dự-án)

## 🔧 Yêu cầu hệ thống

- Python 3.8 trở lên
- MySQL 5.7 trở lên (hoặc MariaDB)
- pip (Python package manager)

## 📦 Cài đặt

### 1. Clone repository

```bash
git clone <repository-url>
cd DACN2_backend
```

### 2. Tạo virtual environment

```bash
python3 -m venv venv
```

### 3. Kích hoạt virtual environment

**Linux/Mac:**

```bash
source venv/bin/activate
```

**Windows:**

```bash
venv\Scripts\activate
```

### 4. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

## ⚙️ Cấu hình

### 1. Tạo file `.env`

Tạo file `.env` trong thư mục gốc của project với nội dung:

```env
DATABASE_URL=mysql+pymysql://username:password@127.0.0.1:3306/booklearning
DB_USER=""
DB_PASS=""
DB_NAME=""
```

**Lưu ý:**

- Thay `username`, `password` bằng thông tin đăng nhập MySQL của bạn
- Thay `booklearning` bằng tên database bạn muốn sử dụng

### 2. Tạo database

Đăng nhập vào MySQL và tạo database:

```sql
CREATE DATABASE booklearning CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Để xóa tạo lại DB:

```sql
DROP DATABASE ten_co_so_du_lieu;
CREATE DATABASE ten_co_so_du_lieu_moi;

```

## 🚀 Chạy server

### Chạy server development

```bash
uvicorn app.main:app --reload
```

Server sẽ chạy tại: `http://localhost:8000`

### Chạy với các tùy chọn khác

```bash
# Chạy trên port khác
uvicorn app.main:app --reload --port 8001

# Chạy với host khác
uvicorn app.main:app --reload --host 0.0.0.0

# Chạy production (không có auto-reload)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🗄️ Database Migrations

Project sử dụng Alembic để quản lý database migrations.

### Tạo migration mới

```bash
alembic revision --autogenerate -m "mô tả thay đổi"
```

### Chạy migrations

```bash
# Chạy tất cả migrations chưa được áp dụng
alembic upgrade head

# Rollback về version trước
alembic downgrade -1

# Xem lịch sử migrations
alembic history

# Xem version hiện tại
alembic current
```

### Lưu ý

- Server sẽ tự động tạo các bảng khi khởi động (nếu chưa tồn tại) thông qua `Base.metadata.create_all()`
- Tuy nhiên, nên sử dụng Alembic migrations để quản lý schema một cách có kiểm soát

## 🌱 Seed Data

Trước khi seed cần xóa và tạo lại db:

```sql
DROP DATABASE ten_co_so_du_lieu;
CREATE DATABASE ten_co_so_du_lieu_moi;

```

Để populate database với dữ liệu mẫu, chạy script seed:

```bash
python seed_data.py
```

Render all embedding

```bash
python ./app/compute_all_embeddings.py
```

Script này sẽ tạo:

- 2 User Roles (admin, user)
- 3 Users (1 admin, 2 users)
- 6 Categories
- 3 Authors
- 4 Publishers
- 4 Books
- 2 Orders với Order Details
- 2 Summaries với Content Sections
- 3 Comments
- 2 Admin Comments

**Thông tin đăng nhập mẫu:**

- Admin: `admin@example.com` / `admin123`
- User 1: `writer@example.com` / `password123`
- User 2: `reader@example.com` / `password123`

## 📚 API Documentation

Khi server đang chạy, bạn có thể truy cập:

- **Swagger UI (Interactive API docs):** `http://localhost:8000/docs`
- **ReDoc (Alternative docs):** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`
