import re
import string
import underthesea
from typing import List, Set

# Danh sách stopwords tiếng Việt phổ biến
VIETNAMESE_STOPWORDS = {
    'và', 'của', 'cho', 'là', 'để', 'trong', 'với', 'có', 'được', 'không',
    'những', 'đã', 'các', 'từ', 'một', 'nhiều', 'về', 'đến', 'như', 'khi',
    'sau', 'này', 'bị', 'nên', 'theo', 'tại', 'vì', 'cũng', 'sẽ', 'nếu',
    'nhưng', 'vào', 'thì', 'còn', 'phải', 'hay', 'mà', 'đó', 'do', 'thế',
    'mới', 'ra', 'nói', 'làm', 'trên', 'tôi', 'bạn', 'họ', 'chúng', 'ta',
    'hơn', 'đang', 'rất', 'mình', 'thôi', 'đây', 'vậy', 'lại', 'ở', 'bởi',
    'rồi', 'tuy', 'tới', 'qua', 'lên', 'xuống', 'ngang', 'cùng', 'chung',
    'bao', 'giờ', 'biết', 'ai', 'mấy', 'vừa', 'thật', 'nhất', 'chỉ', 'vẫn',
    'ngoài', 'đôi', 'khác', 'mọi', 'ngày', 'đều', 'thường', 'việc', 'gì',
    'lúc', 'lần', 'tất', 'cả', 'hoặc', 'tiếp', 'theo', 'chuyện', 'dù', 'sao',
    'nơi', 'làm', 'thì', 'đâu', 'dưới', 'khắp', 'mỗi', 'vài', 'bằng', 'ngay',
    'tự', 'luôn', 'vẫn', 'quá', 'từng', 'đang', 'lúc', 'đã'
}

def preprocess_text(text: str, remove_stopwords: bool = False, 
                   lower_case: bool = True, word_tokenize: bool = False) -> str:

    if not text:
        return ""
    
    # Loại bỏ URL
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # Loại bỏ HTML tags
    text = re.sub(r'<.*?>', '', text)
    
    # Loại bỏ các ký tự đặc biệt và số
    text = re.sub(r'[^\w\s\.]', '', text)
    
    # Loại bỏ các khoảng trắng thừa
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Chuyển thành chữ thường
    if lower_case:
        text = text.lower()
    
    # Tách từ nếu cần
    if word_tokenize:
        text = ' '.join(underthesea.word_tokenize(text))
    
    # Loại bỏ stopwords nếu cần
    if remove_stopwords:
        words = text.split()
        filtered_words = [w for w in words if w.lower() not in VIETNAMESE_STOPWORDS]
        text = ' '.join(filtered_words)
    
    return text

def prepare_for_classification(text: str) -> str:

    # Giới hạn kích thước văn bản
    max_length = 1024
    
    # Xử lý văn bản cơ bản (giữ stopwords vì chúng có thể quan trọng cho việc phân loại)
    processed_text = preprocess_text(text, remove_stopwords=False, lower_case=True)
    
    # Tách thành các câu
    sentences = underthesea.sent_tokenize(processed_text)
    
    # Ưu tiên các câu đầu tiên và cuối cùng (thường chứa thông tin quan trọng)
    if len(sentences) > 10:
        important_sentences = sentences[:5] + sentences[-5:]
    else:
        important_sentences = sentences
    
    # Ghép lại thành văn bản
    processed_text = ' '.join(important_sentences)
    
    # Cắt văn bản nếu quá dài (để phù hợp với giới hạn mô hình)
    words = processed_text.split()
    if len(words) > max_length:
        processed_text = ' '.join(words[:max_length])
    
    return processed_text

def normalize_vietnamese_text(text: str) -> str:

    # Chuẩn hóa văn bản
    if not text:
        return ""
    
    # Loại bỏ khoảng trắng ở đầu và cuối
    text = text.strip()
    
    # Loại bỏ các dòng trống
    text = re.sub(r'\n\s*\n', '\n', text)
    
    # Thay thế nhiều khoảng trắng bằng một khoảng trắng
    text = re.sub(r'\s+', ' ', text)
    
    # Thêm dấu cách sau dấu câu nếu thiếu
    text = re.sub(r'([.,!?:;])([^\s])', r'\1 \2', text)
    
    # Loại bỏ khoảng trắng trước dấu câu
    text = re.sub(r'\s+([.,!?:;])', r'\1', text)
    
    return text

def extract_keywords(text: str, top_n: int = 10) -> List[str]:

    # Tiền xử lý văn bản
    processed_text = preprocess_text(text, remove_stopwords=True, lower_case=True, word_tokenize=True)
    
    # Tách từ và đếm tần suất
    words = processed_text.split()
    word_freq = {}
    
    for word in words:
        if len(word) > 1:  # Bỏ qua các từ quá ngắn
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sắp xếp theo tần suất và lấy top_n
    keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    return [word for word, _ in keywords] 