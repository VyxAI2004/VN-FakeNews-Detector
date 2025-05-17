import os
import torch
import underthesea
import re
from typing import List, Dict, Any
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from fastapi import HTTPException

from utils import (
    extract_article_content,
    preprocess_text,
    prepare_for_classification,
    summarize_text,
    generate_bullet_points
)

from models import SourceInfo, LinguisticAnalysis
from redis_client import redis_client

# Tải mô hình và tokenizer
try:
    # Đường dẫn tới mô hình đã train
    MODEL_PATH = os.getenv("MODEL_PATH", "./models/phobert_news_classifier")
    
    if not os.path.exists(MODEL_PATH):
        print(f"CẢNH BÁO: Thư mục mô hình {MODEL_PATH} không tồn tại")
        print("Vui lòng đặt mô hình đã train vào thư mục này")
        print("Cấu trúc thư mục cần có: config.json, pytorch_model.bin, tokenizer_config.json, tokenizer.json, v.v.")
        model = None
        tokenizer = None
    else:
        # Tải mô hình từ thư mục local
        print(f"Đang tải mô hình từ {MODEL_PATH}...")
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        model.eval()  # Đặt mô hình ở chế độ evaluation
        print("Đã tải mô hình thành công!")
except Exception as e:
    print(f"Lỗi khi tải mô hình: {str(e)}")
    # Fallback để không gây lỗi khi khởi động API
    model = None
    tokenizer = None

# Hàm kiểm tra kết nối tới Redis
def check_redis():

    if not redis_client.ping():
        print("")
    return redis_client  # Vẫn trả về redis_client cho dù kết nối thất bại

# Hàm dự đoán tin thật/giả
def classify_article(text: str):

    if model is None or tokenizer is None:
        raise HTTPException(status_code=500, detail="Mô hình chưa được tải")
        
    # Chuẩn bị văn bản cho mô hình
    text = prepare_for_classification(text)
    
    # Tokenize và chuyển thành tensor
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=256)
    
    # Dự đoán
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Lấy kết quả
    logits = outputs.logits
    probabilities = torch.softmax(logits, dim=1)
    prediction = logits.argmax().item()
    confidence = probabilities[0][prediction].item()
    
    # Xác định tin thật hay giả (giả định 0 là tin thật, 1 là tin giả)
    is_fake = prediction == 1
    
    # Tạo lý do (đơn giản trong ví dụ này, cần cải thiện hơn)
    reasons = generate_reasons(text, is_fake, confidence)
    
    return {
        "is_fake": is_fake,
        "confidence": confidence,
        "reasons": reasons
    }

def generate_reasons(text: str, is_fake: bool, confidence: float) -> List[str]:

    reasons = []
    
    # Phân tích ngôn ngữ cơ bản
    words = text.split()
    sentences = underthesea.sent_tokenize(text)
    
    # Các từ chỉ báo cho tin giả
    fake_indicators = ['sốc', 'giật gân', 'không thể tin', 'bạn sẽ bất ngờ', 
                      'chấn động', 'tiết lộ', 'bí mật', 'kinh hoàng']
    
    # Các từ chỉ báo cho tin thật
    real_indicators = ['nghiên cứu', 'theo', 'nhà khoa học', 'chuyên gia', 
                      'phỏng vấn', 'số liệu', 'thống kê', 'nguồn tin']
    
    if is_fake:
        # Lý do cho tin giả
        if confidence > 0.8:
            reasons.append(f"Mô hình có độ tin cậy cao ({confidence*100:.1f}%) rằng đây là tin giả.")
        
        # Kiểm tra các từ chỉ báo tin giả
        fake_words = [word for word in fake_indicators if word in text.lower()]
        if fake_words:
            reasons.append(f"Bài viết chứa các từ ngữ cảm xúc và giật gân: {', '.join(fake_words)}.")
        
        # Kiểm tra độ dài câu
        avg_sent_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        if avg_sent_length > 30:
            reasons.append(f"Bài viết có câu dài bất thường (trung bình {avg_sent_length:.1f} từ mỗi câu).")
            
    else:
        # Lý do cho tin thật
        if confidence > 0.8:
            reasons.append(f"Mô hình có độ tin cậy cao ({confidence*100:.1f}%) rằng đây là tin thật.")
        
        # Kiểm tra các từ chỉ báo tin thật
        real_words = [word for word in real_indicators if word in text.lower()]
        if real_words:
            reasons.append(f"Bài viết sử dụng ngôn ngữ nghiêm túc và trích dẫn: {', '.join(real_words)}.")
            
        # Kiểm tra độ dài nội dung
        if len(words) > 200:
            reasons.append("Bài viết có độ dài hợp lý và nội dung chi tiết.")
    
    # Nếu không có lý do cụ thể nào
    if not reasons:
        if is_fake:
            reasons.append("Nội dung bài viết có các dấu hiệu không đáng tin cậy.")
        else:
            reasons.append("Nội dung bài viết có cấu trúc và từ ngữ đáng tin cậy.")
    
    return reasons

def analyze_source(url: str) -> SourceInfo:

    if not url:
        return SourceInfo()
    
    # Lấy tên miền từ URL
    domain = None
    try:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
    except Exception:
        domain = url.split('/')[2] if url.startswith(('http://', 'https://')) else None
    
    # Đây là một bản giả lập đơn giản, trong thực tế cần có database/API về độ tin cậy của nguồn
    reputation = None
    category = None
    
    # Danh sách các domain tin cậy (ví dụ)
    trusted_domains = [
        'vnexpress.net',
        'tuoitre.vn',
        'thanhnien.vn',
        'vietnamnet.vn',
        'dantri.com.vn',
        'nhandan.vn',
        'vov.vn',
        'vtc.vn',
        'baochinhphu.vn',
        'cand.com.vn',
        'laodong.vn',
        'plo.vn',
        'congan.com.vn',
        'sggp.org.vn',
        'baoquocte.vn',
        'tienphong.vn',
        'baogiaothong.vn',
        'bnews.vn',
        'baomoi.com', 
        'zingnews.vn',
        'cafef.vn',
        'cafebiz.vn',
        'soha.vn',
        'kenh14.vn']

    # Danh sách các domain ít tin cậy (ví dụ)
    less_trusted_domains = ['blogspot.com', 'wordpress.com', 'facebook.com', 'youtube.com']
    
    if domain:
        # Gán độ tin cậy dựa trên tên miền
        if any(td in domain for td in trusted_domains):
            reputation = 8.5  # 0-10
            category = "Báo chính thống"
        elif any(ltd in domain for ltd in less_trusted_domains):
            reputation = 5.0
            category = "Blog/Mạng xã hội"
        else:
            reputation = 6.0  # Giá trị mặc định
            category = "Khác"
    
    return SourceInfo(
        domain=domain,
        reputation=reputation,
        category=category
    )

def analyze_linguistics(text: str) -> LinguisticAnalysis:

    # Tạo các điểm số phân tích ngôn ngữ
    scores = {
        "objectivity": 0.0,  # 0-10
        "formal_language": 0.0,
        "credibility": 0.0,
        "clarity": 0.0,
        "consistency": 0.0
    }
    
    # Tính toán các điểm số (đơn giản hóa)
    words = text.split()
    sentences = underthesea.sent_tokenize(text)
    
    # Phân tích độ rõ ràng, dựa trên độ dài câu
    avg_sent_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
    clarity_score = 10 - min(abs(avg_sent_length - 15) * 0.5, 5)  # Câu 15 từ là tối ưu
    scores["clarity"] = clarity_score
    
    # Phân tích ngôn ngữ trang trọng/chính thức
    formal_words = ["nghiên cứu", "phân tích", "theo", "trích dẫn", "chứng minh", "kết quả"]
    informal_words = ["cực kỳ", "siêu", "khủng", "đỉnh", "bá đạo", "chất"]
    
    formal_count = sum(1 for word in words if any(fw in word.lower() for fw in formal_words))
    informal_count = sum(1 for word in words if any(fw in word.lower() for fw in informal_words))
    
    formal_ratio = formal_count / max(1, formal_count + informal_count)
    scores["formal_language"] = min(formal_ratio * 10, 10)
    
    # Tính điểm khách quan
    subjective_words = ["tuyệt vời", "kinh hoàng", "đáng sợ", "tồi tệ", "thất vọng"]
    subjective_count = sum(1 for word in words if any(sw in word.lower() for sw in subjective_words))
    subjective_ratio = subjective_count / max(len(words), 1)
    scores["objectivity"] = min((1 - subjective_ratio) * 15, 10)  # Ít từ chủ quan hơn = khách quan hơn
    
    # Độ đáng tin cậy (đơn giản hóa)
    scores["credibility"] = (scores["formal_language"] + scores["objectivity"]) / 2
    
    # Tính toán nhất quán
    scores["consistency"] = 8.0  # Giá trị mặc định
    
    # Các tính năng khác của bài viết
    features = {
        "word_count": len(words),
        "sentence_count": len(sentences),
        "avg_sentence_length": avg_sent_length,
        "has_numbers": bool(re.search(r'\d', text)),
        "has_quotes": '"' in text or '"' in text or '"' in text,
        "reading_time_minutes": len(words) / 200  # Tốc độ đọc trung bình
    }
    
    return LinguisticAnalysis(
        scores={k: round(v, 2) for k, v in scores.items()},
        features=features
    )

def process_article_request(request_data):

    # Kiểm tra đầu vào
    if not request_data.url and not request_data.text:
        raise HTTPException(status_code=400, detail="Vui lòng cung cấp URL hoặc nội dung bài viết")
    
    # Kiểm tra cache nếu có URL
    redis = check_redis()
    if request_data.url and redis.ping():
        cached_result = redis.get_cached_analysis(request_data.url)
        if cached_result:
            return cached_result
    
    # Trích xuất nội dung từ URL hoặc sử dụng text đã cung cấp
    article_data = None
    content = ""
    
    # Ưu tiên sử dụng text nếu được cung cấp
    if request_data.text:
        content = request_data.text
        article_data = extract_article_content(content, is_url=False)
    # Nếu không có text nhưng có URL, scrape nội dung từ URL
    elif request_data.url:
        article_data = extract_article_content(request_data.url, is_url=True)
        content = article_data['content']
    
    # Kiểm tra nếu nội dung quá ngắn
    if len(content.split()) < 10:
        raise HTTPException(status_code=400, detail="Nội dung quá ngắn để phân tích")
    
    # Phân loại nội dung
    classification = classify_article(content)
    
    # Khởi tạo kết quả cơ bản
    result = {
        "is_fake": classification["is_fake"],
        "confidence": classification["confidence"],
        "reasons": classification["reasons"]
    }
    
    # Tùy chọn tóm tắt
    if request_data.options and request_data.options.get("summarize", False):
        result["summary"] = summarize_text(content)
    
    # Tùy chọn phân tích nguồn
    if request_data.options and request_data.options.get("source_analysis", False) and request_data.url:
        result["source_info"] = analyze_source(request_data.url).dict()
    
    # Tùy chọn phân tích ngôn ngữ chi tiết
    if request_data.options and request_data.options.get("detailed_analysis", False):
        result["linguistic_analysis"] = analyze_linguistics(content).dict()
    
    # Tùy chọn kiểm tra sự thật
    if request_data.options and request_data.options.get("fact_checking", False):
        # Đây chỉ là dữ liệu mẫu, trong thực tế cần gọi API hoặc có cơ sở dữ liệu fact-checking
        result["fact_checks"] = [
            {
                "claim": "Đây là một claim được trích xuất từ bài viết.",
                "accurate": not classification["is_fake"],
                "explanation": "Giải thích về tính chính xác của claim này.",
                "sources": [
                    {"name": "Nguồn tham khảo 1", "url": "https://example.com/source1"}
                ]
            }
        ]
    
    # Lưu vào cache nếu có URL
    if request_data.url and redis.ping():
        redis.cache_article_analysis(request_data.url, result)
    
    return result 