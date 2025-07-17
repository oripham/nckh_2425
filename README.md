# NCKH 2025

Dự án phân tích cảm xúc và xu hướng chủ đề trên mạng xã hội.

## Cấu trúc dự án

- `fe/`: Frontend (React)
- `be/`: Backend (Python FastAPI hoặc framework khác)
- Các thư mục khác: dữ liệu, tài liệu, v.v.

## Yêu cầu

- Node.js >= 14.x
- Python >= 3.8
- Các package phụ thuộc được liệt kê trong `package.json` (frontend) và `requirements.txt` (backend)

## Hướng dẫn cài đặt

### 1. Cài đặt Frontend

```bash
cd fe
npm install
npm start
```

### 2. Cài đặt Backend

```bash
cd be
pip install -r requirements.txt
uvicorn main:app --reload
```

## Sử dụng

- Truy cập frontend tại: http://localhost:3000
- API backend chạy tại: http://127.0.0.1:8000

## Đóng góp

Vui lòng tạo pull request hoặc liên hệ nhóm phát triển để đóng góp cho dự án.

## Giấy phép

MIT License.
