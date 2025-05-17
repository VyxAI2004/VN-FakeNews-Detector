import requests
from bs4 import BeautifulSoup
import time
import csv
import random
import re
import os

# Lấy danh sách bài viết từ trang BBC Vietnamese
def get_article_links(base_url="https://www.bbc.com/vietnamese/topics/ckdxnx1x5rnt?page=8", pages=1):
    article_links = []
    
    # Thêm User-Agent để tránh bị chặn
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }
    
    for page in range(1, pages + 1):
        # Thêm tham số trang nếu cần
        page_url = base_url
        if page > 1:
            page_url = f"{base_url}/page/{page}"
        
        try:
            print(f"📄 Đang tải trang {page}/{pages}: {page_url}")
            response = requests.get(page_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f" Lỗi khi truy cập trang {page}: Mã trạng thái {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Tìm tất cả các liên kết
            all_links = soup.find_all('a', href=True)
            print(f"Tìm thấy {len(all_links)} liên kết trên trang {page}")
            
            # Pattern cho các bài viết BBC
            article_pattern = re.compile(r'/vietnamese/(articles/[a-zA-Z0-9]+|[a-z\-]+/[a-zA-Z0-9\-]+)$')
            
            for a_tag in all_links:
                href = a_tag.get('href', '')
                
                # Kiểm tra chỉ lấy các bài viết BBC Vietnamese
                if article_pattern.search(href):
                    # Đảm bảo URL đầy đủ
                    if href.startswith('/'):
                        full_url = f"https://www.bbc.com{href}"
                    else:
                        full_url = href
                    
                    # Thêm vào danh sách nếu chưa có
                    if full_url not in article_links:
                        article_links.append(full_url)
                        print(f"🔍 Đã tìm thấy liên kết bài viết: {full_url}")
            
            # Thời gian chờ giữa các trang
            if page < pages:
                delay = random.uniform(1, 3)
                print(f"⏱️ Chờ {delay:.2f} giây trước khi tải trang tiếp theo...")
                time.sleep(delay)
                
        except Exception as e:
            print(f" Lỗi khi tìm kiếm bài viết trang {page}: {e}")
    
    print(f"Tìm thấy tổng cộng {len(article_links)} bài viết.")
    return article_links

# Cào nội dung từ 1 bài viết
def scrape_article_content(article_url):
    try:
        # Thêm User-Agent để tránh bị chặn
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        }
        
        # Thêm timeout và thử lại nếu cần
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(article_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    break
                print(f" Lần thử {attempt+1}/{max_retries}: Mã trạng thái {response.status_code}")
                time.sleep(2)  # Chờ trước khi thử lại
            except Exception as retry_error:
                print(f" Lỗi khi thử lần {attempt+1}/{max_retries}: {retry_error}")
                time.sleep(2)
                if attempt == max_retries - 1:
                    raise  # Ném lỗi nếu đã thử hết số lần
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Tìm tiêu đề - thử nhiều lớp khác nhau (BBC selectors)
        title = None
        for title_class in ['article-headline', 'gs-c-promo-heading__title', 'bbc-1ff6jq7']:
            title_tag = soup.find(['h1', 'h2'], class_=lambda c: c and title_class in c)
            if title_tag:
                title = title_tag.get_text(strip=True)
                print(f"Đã tìm thấy tiêu đề sử dụng class='{title_class}'")
                break
        
        # Nếu không tìm thấy tiêu đề bằng class, hãy thử tìm thẻ h1 đầu tiên
        if not title:
            h1_tag = soup.find('h1')
            if h1_tag:
                title = h1_tag.get_text(strip=True)
                print(f"Đã tìm thấy tiêu đề từ thẻ h1")
            else:
                title = "Không có tiêu đề"
                print(f" Không tìm thấy tiêu đề cho bài viết: {article_url}")
        
        # Tìm nội dung - thử nhiều lớp khác nhau (BBC selectors)
        content = ""
        for content_class in ['bbc-19j92fr', 'bbc-1d18lk7', 'article-body-component', 'bbc-1cvxiy9']:
            content_container = soup.find(['div', 'article'], class_=lambda c: c and content_class in c)
            if content_container:
                content_tags = content_container.find_all(['p', 'div.text'])
                if content_tags:
                    content = '\n'.join(p.get_text(strip=True) for p in content_tags if p.get_text(strip=True))
                    print(f"Đã tìm thấy nội dung sử dụng class='{content_class}'")
                    break
        
        if not content:
            print(f" Không tìm thấy nội dung cho bài viết: {article_url}")
            return None
        
        full_text = f"{title}\n{content}"
        print(f"Đã cào bài viết thành công: {article_url}")
        return full_text
    
    except Exception as e:
        print(f" Lỗi khi cào bài viết {article_url}: {e}")
        return None

# Lưu dữ liệu vào file CSV
def save_to_csv(articles, website_url="https://www.bbc.com/vietnamese/", filename='articles.csv', append=True):
    if not articles:
        print(" Không có dữ liệu để lưu vào file CSV.")
        return
    
    # Kiểm tra file có tồn tại không
    file_exists = os.path.isfile(filename)
    
    # Quyết định mode mở file (append hay write)
    mode = 'a' if append and file_exists else 'w'
    
    with open(filename, mode=mode, encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['content', 'website', 'label'])
        
        # Chỉ ghi header nếu file mới hoặc không append
        if mode == 'w':
            writer.writeheader()
            
        for article in articles:
            writer.writerow({
                'content': article,
                'website': website_url,
                'label': 1 
            })
    
    print(f"Đã lưu {len(articles)} bài viết vào file {filename}")
    if mode == 'a':
        print(f"Dữ liệu được thêm vào file hiện có.")
    else:
        print(f"Đã tạo file mới.")

# Main
if __name__ == "__main__":
    print("Bắt đầu cào dữ liệu ")
    base_url = "https://www.bbc.com/vietnamese/topics/ckdxnx1x5rnt?page=8"
    
    links = get_article_links(base_url)
    
    if not links:
        print(" Không tìm thấy bài viết nào. Thoát chương trình.")
        exit()
    
    print(f"🔗 Tìm thấy {len(links)} bài viết. Bắt đầu cào nội dung...")
    
    articles = []
    max_articles = min(100, len(links))  # Giới hạn số bài cào
    
    for i, link in enumerate(links[:max_articles]):
        print(f"\n Đang cào bài {i+1}/{max_articles}: {link}")
        content = scrape_article_content(link)
        
        if content and len(content.split('\n')) > 1:  # Kiểm tra nội dung có hợp lệ
            articles.append(content)
            print(f"Đã cào bài thành công ({len(articles)}/{max_articles})")
        else:
            print(f" Bỏ qua bài không có nội dung hợp lệ: {link}")
        
        # Thêm thời gian chờ ngẫu nhiên để giảm nguy cơ bị chặn
        delay = random.uniform(2, 5)
        print(f" Chờ {delay:.2f} giây trước khi cào bài tiếp theo...")
        time.sleep(delay)
    
    # Hỏi người dùng có muốn append hay không
    append_option = input("Bạn có muốn thêm dữ liệu vào file có sẵn không? (y/n): ").lower() == 'y'
    
    save_to_csv(articles, "https://www.bbc.com/vietnamese/", append=append_option)
    print("\n🎉 Hoàn thành quá trình cào dữ liệu!") 