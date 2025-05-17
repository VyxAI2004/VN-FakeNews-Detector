# Phát Hiện Tin Giả Tiếng Việt (Vietnamese Fake News Detection)

## Tổng quan (Overview)

Dự án này là hệ thống phát hiện tin giả dành cho nội dung tiếng Việt. Hệ thống sử dụng các kỹ thuật xử lý ngôn ngữ tự nhiên (NLP) và học sâu (LSTM) để phân tích và đánh giá tính chân thực của các bài báo và nội dung trên mạng.

## Cấu trúc dự án (Project Structure)

```
.
├── backend/                # Máy chủ API xử lý và phân tích bài viết
│   ├── main.py             # Điểm vào chính của API FastAPI
│   ├── services.py         # Các dịch vụ xử lý bài viết
│   ├── models.py           # Định nghĩa các model dữ liệu
│   ├── redis_client.py     # Quản lý bộ nhớ đệm Redis
│   ├── Crawl2.py           # Công cụ thu thập dữ liệu
│   ├── models/             # Lưu trữ các mô hình ML (Ở đây là mô hình tự train dựa trên các bài báo/tin tức ở Việt Nam)
│   ├── utils/              # Các tiện ích hỗ trợ
│   ├── Dockerfile          # Cấu hình Docker cho backend
│   └── requirements.txt    # Các thư viện Python cần thiết
│
├── frontend/               # Giao diện người dùng React
│   ├── public/             # Tài nguyên tĩnh 
│   ├── src/                # Mã nguồn React
│   ├── package.json        # Cấu hình và dependencies
│   └── README.md           # Hướng dẫn dành riêng cho frontend
│
└── preprocessed_data.csv   # Dữ liệu đã được tiền xử lý
```

## Công nghệ sử dụng (Technologies Used)

### Backend
- **FastAPI**: Framework API hiệu năng cao cho Python
- **PyTorch & Hugging Face Transformers**: Phát triển mô hình NLP
- **Redis**: Bộ nhớ đệm cho kết quả và quản lý trạng thái
- **Underthesea**: Thư viện NLP dành cho tiếng Việt
- **Docker**: Ảo hóa và triển khai

### Frontend
- **React**: Framework JavaScript cho UI
- **Bootstrap**: Thiết kế responsive
- **Chart.js**: Hiển thị dữ liệu trực quan
- **Axios**: Giao tiếp API

## Tính năng (Features)

- Phát hiện và phân loại tin giả trong nội dung tiếng Việt
- Phân tích mức độ tin cậy của bài viết
- Cung cấp thông tin chi tiết về các yếu tố khiến bài viết được phân loại là tin giả
- Giao diện người dùng thân thiện và dễ sử dụng
- API mở để tích hợp với các hệ thống khác

## Cài đặt (Installation)

### Yêu cầu hệ thống
- Python 3.8+
- Node.js 16+
- Redis

### Backend

```bash
# Đi đến thư mục backend
cd backend

# Cài đặt các gói phụ thuộc
pip install -r requirements.txt

# Khởi động máy chủ API
python main.py
```

### Frontend

```bash
# Đi đến thư mục frontend
cd frontend

# Cài đặt các gói phụ thuộc
npm install

# Khởi động ứng dụng React trong chế độ phát triển
npm start
```

## Docker

Để chạy toàn bộ hệ thống sử dụng Docker:

```bash
# Xây dựng và chạy các container
docker-compose up -d
```

## API Documentation

API được tự động tạo tài liệu bằng Swagger và có sẵn tại endpoint `/docs` sau khi khởi động backend.

Endpoint chính:
- `POST /api/detect_fake_news`: Phân tích nội dung và phát hiện tin giả

## Liên hệ (Contact)


---

*Dự án này là một phần của nỗ lực chống lại sự lan truyền của thông tin sai lệch trên internet và cải thiện chất lượng thông tin trong không gian kỹ thuật số tiếng Việt.* 