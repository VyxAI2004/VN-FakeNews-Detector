FROM python:3.10-slim

WORKDIR /app

# Cài đặt dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Cài đặt underthesea và tải các tài nguyên
RUN python -c "import underthesea; underthesea.word_tokenize('Xin chào')"

# Cài đặt thư viện NLTK và tải các tài nguyên
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Copy code
COPY . .

# Tạo thư mục cho models nếu không tồn tại
RUN mkdir -p models/phobert_news_classifier

# Mở port API
EXPOSE 8000

# Chạy ứng dụng
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 