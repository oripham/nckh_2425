# NCKH 2024–2025: Phân tích Cảm xúc và Xu hướng Chủ đề trên Mạng xã hội

## Giới thiệu

Đề tài nghiên cứu khoa học năm 2024–2025: **Phân tích cảm xúc và xu hướng chủ đề trên mạng xã hội** sử dụng mô hình **Multi-task PhoBERT**.

Mô hình thực hiện **3 tác vụ đồng thời** trên văn bản tiếng Việt:

| Tác vụ | Mô tả | Nhãn đầu ra |
|--------|-------|-------------|
| **Sentiment** | Phân tích cảm xúc | Positive / Negative / Neutral |
| **Topic** | Phân loại chủ đề | Cơ sở vật chất / Giảng viên / Sinh viên / Chương trình đào tạo |
| **Summary** | Tóm tắt trích xuất | Điểm số đánh giá câu quan trọng |

## Tải model

Model multi-task PhoBERT (~540MB) có thể tải từ:
- **Dropbox**: [Tải model tại đây](https://www.dropbox.com/scl/fo/m34gsy5852rnmzl1pornf/AHI8yqG_O7XiPXifh1k1_g4?rlkey=lz4f0yezizw0wbefgphptwi4e&st=7glfhky1&dl=0)

Hoặc sử dụng API online (không cần tải model):
- **HuggingFace Space**: [https://huggingface.co/spaces/oripham/npl-ml-backend](https://huggingface.co/spaces/oripham/npl-ml-backend)

## Cấu trúc thư mục

```
nckh_2425/
├── NCKH_NhomOanh.pdf        # Báo cáo nghiên cứu khoa học (PDF)
├── demo.py                  # ⭐ Script demo đơn giản (xem bên dưới)
├── README.md
├── be/                      # Backend (FastAPI) - mã nguồn đầy đủ
│   ├── server.py            # Server API
│   ├── untils.py            # Hàm tiện ích NLP
│   ├── models.py            # Pydantic models
│   ├── requirements.txt     # Thư viện Python
│   └── data/                # Dữ liệu CSV, stopwords
└── fe/                      # Frontend (React + Vite) - giao diện web
    ├── src/
    └── package.json
```

## Hướng dẫn chạy Demo

### Gọi API online (đơn giản, không cần GPU)

Chỉ cần cài thư viện `requests`:

```bash
pip install requests

# Chạy demo
python demo.py "Trường đại học có cơ sở vật chất rất tốt"
```


### Kết quả mẫu

──────────────────────────────────────────────────

⚙️  Chế độ: API (gọi HuggingFace Space)

  🎯 Cảm xúc (Sentiment) : Positive
──────────────────────────────────────────────────

✅ Hoàn tất!
```

## Tài liệu tham khảo

- Xem chi tiết trong file `NCKH_NhomOanh.pdf`
- API docs (khi server chạy): http://localhost:8000/docs
- HuggingFace Space: https://huggingface.co/spaces/oripham/npl-ml-backend
