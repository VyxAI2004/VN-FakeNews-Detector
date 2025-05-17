import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional, Tuple
import re
from urllib.parse import urlparse
import time

# Danh sách các User-Agent khác nhau để luân phiên sử dụng
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
]

def extract_article_content(source: str, is_url: bool = True) -> Dict[str, Any]:

    if is_url:
        return scrape_article_from_url(source)
    else:
        return analyze_text_content(source)

def scrape_article_from_url(url: str) -> Dict[str, Any]:

    # Phân tích domain để xác định nguồn báo
    domain = urlparse(url).netloc
    
    # Thiết lập request
    headers = {
        'User-Agent': USER_AGENTS[int(time.time()) % len(USER_AGENTS)],
        'Accept': 'text/html,application/xhtml+xml,application/xml',
        'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
        'Referer': f"https://{domain}"
    }
    
    try:
        # Gửi request lấy nội dung trang web
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Kiểm tra lỗi HTTP
        
        # Xử lý nếu không phải UTF-8
        if 'charset' in response.headers.get('content-type', '').lower():
            response.encoding = response.apparent_encoding
        
        # Parse HTML bằng BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Sử dụng thuật toán chung để trích xuất nội dung
        title, content, date, author = extract_general(soup)
        
        # Kiểm tra nếu nội dung quá ngắn
        if len(content.split()) < 20:
            title, content = extract_content_by_density(soup)
        
        return {
            'title': title,
            'content': content,
            'date': date,
            'author': author,
            'url': url,
            'domain': domain,
            'word_count': len(content.split())
        }
        
    except Exception as e:
        print(f"Lỗi khi trích xuất bài viết từ {url}: {str(e)}")
        # Trả về kết quả mặc định khi có lỗi
        return {
            'title': '',
            'content': '',
            'date': '',
            'author': '',
            'url': url,
            'domain': domain,
            'word_count': 0,
            'error': str(e)
        }

def extract_general(soup: BeautifulSoup) -> Tuple[str, str, str, str]:

    # Cố gắng lấy tiêu đề từ thẻ h1 hoặc meta
    title = ''
    title_elem = soup.select_one('h1')
    if title_elem:
        title = title_elem.text.strip()
    else:
        meta_title = soup.select_one('meta[property="og:title"]')
        if meta_title:
            title = meta_title.get('content', '')
    
    # Cố gắng lấy nội dung từ các thẻ p nằm trong main, article, hoặc div có id/class liên quan
    content_containers = soup.select('article, main, div.content, div.article, div.post, div#content, div.news-content')
    content = ''
    
    if content_containers:
        # Ưu tiên lấy từ container đầu tiên tìm thấy
        paragraphs = content_containers[0].select('p')
        content = ' '.join([p.text.strip() for p in paragraphs if not p.find('script') and len(p.text.strip()) > 20])
    
    # Nếu không tìm thấy trong container, lấy tất cả p có độ dài hợp lý
    if not content:
        paragraphs = soup.select('p')
        content = ' '.join([p.text.strip() for p in paragraphs if not p.find('script') and len(p.text.strip()) > 20])
    
    # Tìm ngày đăng
    date = ''
    date_patterns = [
        r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # 01/02/2022, 1-2-2022
        r'\d{1,2}\s+[a-zA-Z]+\s+\d{4}',   # 01 January 2022
        r'\d{4}[/-]\d{1,2}[/-]\d{1,2}'    # 2022/01/02
    ]
    
    for pattern in date_patterns:
        date_match = re.search(pattern, str(soup))
        if date_match:
            date = date_match.group(0)
            break
    
    # Tìm tác giả
    author = ''
    author_elems = soup.select('span.author, div.author, p.author, .byline')
    if author_elems:
        author = author_elems[0].text.strip()
    
    return title, content, date, author

def extract_content_by_density(soup: BeautifulSoup) -> Tuple[str, str]:

    # Lấy tiêu đề
    title = soup.title.text if soup.title else ''
    
    # Tính điểm cho các block có nhiều text
    blocks = {}
    for tag in soup.find_all(['div', 'article', 'section', 'main']):
        text_content = tag.get_text().strip()
        if len(text_content) < 100:  # Bỏ qua block quá ngắn
            continue
            
        # Tính tỷ lệ text/html
        html_length = len(str(tag))
        if html_length == 0:
            continue
            
        text_length = len(text_content)
        density = text_length / html_length
        
        # Ưu tiên các block có nhiều text và ít thẻ HTML
        score = text_length * density
        blocks[tag] = score
    
    # Lấy block có điểm cao nhất
    if blocks:
        best_block = max(blocks.items(), key=lambda x: x[1])[0]
        
        # Lấy nội dung từ các thẻ p trong block này
        paragraphs = best_block.find_all('p')
        if paragraphs:
            content = ' '.join([p.text.strip() for p in paragraphs if len(p.text.strip()) > 10])
        else:
            content = best_block.get_text().strip()
            
        return title, content
    
    return title, ''

def analyze_text_content(text: str) -> Dict[str, Any]:

    # Phân tách tiêu đề và nội dung nếu có thể
    lines = text.split('\n')
    title = lines[0].strip() if lines else ''
    content = text
    
    # Nếu dòng đầu tiên ngắn hơn 100 ký tự, xem như tiêu đề
    if len(title) < 100 and len(lines) > 1:
        content = '\n'.join(lines[1:]).strip()
    
    return {
        'title': title,
        'content': content,
        'date': '',
        'author': '',
        'url': '',
        'domain': '',
        'word_count': len(content.split())
    }