# Backend Setup Instructions

## Yêu cầu hệ thống
- Python 3.8 trở lên
- pip (Python package manager)

## Cài đặt

1. Tạo môi trường ảo (khuyến nghị):
```bash
python -m venv venv
```

2. Kích hoạt môi trường ảo:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

3. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

4. Tạo file .env và thêm API key:
```bash
OPENAI_API_KEY_3=your_api_key_here
```

## Cấu trúc thư mục
```
be/
├── data/                  # Thư mục chứa dữ liệu
│   ├── Utc2Confessions.csv
│   ├── Utc2NoiChiaSeCamXuc.csv
│   ├── Utc2Zone.csv
│   ├── DienDanNgheSVNoi.csv
│   └── vietnamese-stopwords.txt
├── fine_tuned_model/      # Thư mục chứa model đã fine-tune
├── server.py             # File chính của server
├── untils.py             # Các hàm tiện ích
├── models.py             # Định nghĩa các model
└── requirements.txt      # Danh sách các thư viện cần thiết
```

## Chạy server

1. Đảm bảo đã kích hoạt môi trường ảo

2. Chạy server:
```bash
python server.py
```

Server sẽ chạy tại địa chỉ: http://127.0.0.1:8000

## API Endpoints

1. GET `/posts`
   - Lấy danh sách bài đăng
   - Parameters:
     - page: số trang
     - limit: số bài đăng mỗi trang
     - selected_page: trang nguồn (0-3)
     - topic: chủ đề
     - start_date: ngày bắt đầu
     - end_date: ngày kết thúc

2. GET `/sentiment-trend`
   - Lấy dữ liệu xu hướng cảm xúc
   - Parameters:
     - start_date: ngày bắt đầu
     - end_date: ngày kết thúc
     - topic: chủ đề

3. POST `/sentiment`
   - Phân tích cảm xúc của bài đăng

4. POST `/word-analysis`
   - Phân tích từ ngữ trong bài đăng

5. POST `/school-summary`
   - Tổng hợp thông tin về trường học

## Lưu ý
- Đảm bảo tất cả file CSV đã được đặt trong thư mục `data/`
- Model đã fine-tune phải được đặt trong thư mục `fine_tuned_model/`
- File `vietnamese-stopwords.txt` phải có trong thư mục `data/` 