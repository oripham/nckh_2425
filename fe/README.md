# Frontend Setup Instructions

## Yêu cầu hệ thống
- Node.js 14.0.0 trở lên
- npm (Node package manager)

## Cài đặt

1. Cài đặt các thư viện cần thiết:
```bash
npm install
```

## Cấu trúc thư mục
```
fe/
├── public/              # Thư mục chứa các file tĩnh
├── src/                 # Mã nguồn chính
│   ├── components/      # Các component React
│   │   ├── EmotionStats.jsx
│   │   ├── PostList.jsx
│   │   ├── TopicFilter.jsx
│   │   └── DateRangePicker.jsx
│   ├── App.jsx         # Component gốc
│   └── main.jsx        # Điểm khởi đầu ứng dụng
├── package.json        # Cấu hình dự án và dependencies
└── README.md          # Tài liệu hướng dẫn
```

## Chạy ứng dụng

1. Khởi động server phát triển:
```bash
npm start
```

Ứng dụng sẽ chạy tại địa chỉ: http://localhost:3000

## Tính năng chính

1. Hiển thị danh sách bài đăng
   - Lọc theo chủ đề
   - Lọc theo khoảng thời gian
   - Phân trang
   - Link đến bài đăng gốc

2. Thống kê cảm xúc
   - Biểu đồ phân bố cảm xúc
   - Biểu đồ tỷ lệ cảm xúc
   - Biểu đồ xu hướng cảm xúc theo thời gian

3. Bộ lọc
   - Chọn chủ đề
   - Chọn khoảng thời gian
   - Áp dụng bộ lọc cho cả danh sách bài đăng và thống kê

## Lưu ý
- Đảm bảo backend server đang chạy tại http://127.0.0.1:8000
- Các API endpoint được cấu hình trong các component tương ứng
- Sử dụng Material-UI cho giao diện người dùng
- Sử dụng Recharts cho các biểu đồ
