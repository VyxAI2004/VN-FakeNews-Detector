import re
import underthesea
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from typing import List, Dict, Any
import os
import numpy as np
from collections import Counter

# Đường dẫn tới mô hình tóm tắt (có thể thay đổi tùy thuộc vào cài đặt)
SUMMARIZER_MODEL_PATH = os.getenv("SUMMARIZER_MODEL_PATH", "VietAI/vit5-base-vietnews-summarization")

# Biến global để lưu trữ tokenizer và model sau khi load
_tokenizer = None
_model = None

def load_summarizer_model():
    """
    Tải mô hình tóm tắt nếu chưa được tải
    """
    global _tokenizer, _model
    
    if _tokenizer is None or _model is None:
        try:
            print(f"Đang tải mô hình tóm tắt từ {SUMMARIZER_MODEL_PATH}...")
            _tokenizer = AutoTokenizer.from_pretrained(SUMMARIZER_MODEL_PATH)
            _model = AutoModelForSeq2SeqLM.from_pretrained(SUMMARIZER_MODEL_PATH)
            
            # Chuyển sang GPU nếu có thể
            if torch.cuda.is_available():
                _model = _model.cuda()
            
            _model.eval()  # Đặt mô hình ở chế độ evaluation
            print(f"Đã tải xong mô hình tóm tắt!")
        except Exception as e:
            print(f"Lỗi khi tải mô hình tóm tắt: {str(e)}")
            # Nếu không tải được mô hình, sử dụng phương pháp trích xuất đơn giản
            _tokenizer = None
            _model = None

def summarize_text(text: str, max_length: int = 150) -> str:

    # Kiểm tra nếu văn bản quá ngắn
    if len(text.split()) < 30:
        return text
    
    try:
        # Tải mô hình nếu chưa tải
        load_summarizer_model()
        
        # Nếu đã tải mô hình, sử dụng mô hình để tóm tắt
        if _tokenizer is not None and _model is not None:
            return abstractive_summarization(text, max_length)
        else:
            # Nếu không, sử dụng phương pháp trích xuất đơn giản
            return extractive_summarization(text, max_length)
    except Exception as e:
        print(f"Lỗi khi tóm tắt văn bản: {str(e)}")
        # Fallback: Lấy 2 câu đầu tiên làm tóm tắt
        sentences = underthesea.sent_tokenize(text)
        return ' '.join(sentences[:2])

def abstractive_summarization(text: str, max_length: int = 150) -> str:

    # Chuẩn bị đầu vào cho mô hình
    input_text = "summarize: " + text  # Prefix cho tác vụ tóm tắt
    
    # Tokenize
    inputs = _tokenizer(input_text, return_tensors="pt", max_length=1024, truncation=True)
    if torch.cuda.is_available():
        inputs = {k: v.cuda() for k, v in inputs.items()}
    
    # Tạo tóm tắt
    with torch.no_grad():
        outputs = _model.generate(
            inputs["input_ids"],
            max_length=max_length, 
            no_repeat_ngram_size=3,
            num_beams=4,
            early_stopping=True
        )
    
    # Decode kết quả
    summary = _tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return summary

def extractive_summarization(text: str, max_length: int = 150) -> str:

    # Phân đoạn văn bản thành các câu
    sentences = underthesea.sent_tokenize(text)
    
    # Nếu có ít câu, trả về nguyên văn
    if len(sentences) <= 3:
        return text
    
    # Tiền xử lý các câu
    clean_sentences = [re.sub(r'[^\w\s]', '', s.lower()) for s in sentences]
    
    # Tính toán ma trận tương đồng giữa các câu
    similarity_matrix = np.zeros((len(sentences), len(sentences)))
    for i in range(len(sentences)):
        for j in range(len(sentences)):
            if i != j:
                # Đếm số từ chung giữa hai câu
                words_i = set(clean_sentences[i].split())
                words_j = set(clean_sentences[j].split())
                
                # Đảm bảo không chia cho 0
                if len(words_i) == 0 or len(words_j) == 0:
                    continue
                    
                # Tính hệ số Jaccard
                similarity = len(words_i.intersection(words_j)) / len(words_i.union(words_j))
                similarity_matrix[i][j] = similarity
    
    # Tính điểm cho mỗi câu (tổng tương đồng với các câu khác)
    scores = np.sum(similarity_matrix, axis=1)
    
    # Lấy top N câu có điểm cao nhất
    N = min(3, len(sentences))  # Tối đa 3 câu
    top_indices = np.argsort(scores)[-N:]
    top_indices = sorted(top_indices)  # Sắp xếp lại theo thứ tự xuất hiện
    
    # Ghép các câu đã chọn thành bản tóm tắt
    summary = ' '.join([sentences[i] for i in top_indices])
    
    # Đảm bảo không vượt quá max_length
    words = summary.split()
    if len(words) > max_length:
        summary = ' '.join(words[:max_length])
    
    return summary

def extract_main_points(text: str, num_points: int = 5) -> List[str]:

    # Phân đoạn văn bản thành các câu
    sentences = underthesea.sent_tokenize(text)
    
    # Nếu có quá ít câu
    if len(sentences) <= num_points:
        return sentences
    
    # Tiền xử lý các câu
    clean_sentences = [re.sub(r'[^\w\s]', '', s.lower()) for s in sentences]
    
    # Đếm tần suất của từng từ
    all_words = ' '.join(clean_sentences).split()
    word_freq = Counter(all_words)
    
    # Loại bỏ các từ phổ biến hoặc quá hiếm
    for word in list(word_freq.keys()):
        if word_freq[word] > len(sentences) * 0.8 or word_freq[word] < 2 or len(word) < 3:
            del word_freq[word]
    
    # Tính điểm cho mỗi câu dựa trên tần suất từ
    sentence_scores = np.zeros(len(sentences))
    for i, sentence in enumerate(clean_sentences):
        sentence_words = sentence.split()
        score = sum(word_freq.get(word, 0) for word in sentence_words) / max(1, len(sentence_words))
        
        # Ưu tiên các câu ở đầu và cuối
        position_bonus = 0
        if i < len(sentences) * 0.2 or i > len(sentences) * 0.8:
            position_bonus = 0.5
            
        sentence_scores[i] = score + position_bonus
    
    # Lấy top N câu có điểm cao nhất
    top_indices = np.argsort(sentence_scores)[-num_points:]
    top_indices = sorted(top_indices)  # Sắp xếp lại theo thứ tự xuất hiện
    
    # Lấy các câu đã chọn
    main_points = [sentences[i] for i in top_indices]
    
    return main_points

def generate_bullet_points(text: str, num_points: int = 5) -> List[str]:

    # Trích xuất các điểm chính
    main_points = extract_main_points(text, num_points)
    
    # Chuẩn hóa các điểm chính: ngắn gọn, rõ ràng
    bullet_points = []
    for i, point in enumerate(main_points):
        # Loại bỏ các từ nối ở đầu câu nếu có
        point = re.sub(r'^(tuy nhiên|nhưng|vì vậy|do đó|theo|bởi vì|ngoài ra|hơn nữa)', '', point, flags=re.IGNORECASE).strip()
        
        # Cắt câu nếu quá dài
        words = point.split()
        if len(words) > 20:
            point = ' '.join(words[:20]) + '...'
        
        # Đảm bảo viết hoa chữ cái đầu
        if point and len(point) > 0:
            point = point[0].upper() + point[1:]
            
        if point:
            bullet_points.append(point)
    
    return bullet_points 