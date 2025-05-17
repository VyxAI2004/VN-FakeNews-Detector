import os
import json
import time
from typing import Dict, Any, Optional
import redis

class RedisClient:

    def __init__(self):
        """Khởi tạo kết nối Redis từ biến môi trường hoặc giá trị mặc định"""
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        redis_password = os.getenv("REDIS_PASSWORD", None)
        redis_db = int(os.getenv("REDIS_DB", 0))
        
        # Cache TTL (time-to-live) mặc định = 1 ngày (86400 giây)
        self.cache_ttl = int(os.getenv("REDIS_CACHE_TTL", 86400)) 
        
        # Khởi tạo kết nối tới Redis
        try:
            self.redis = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                db=redis_db,
                decode_responses=True,  # Tự động decode bytes -> str
                socket_timeout=5,
                socket_connect_timeout=5
            )
            # Test kết nối
            self.redis.ping()
            print(f"Đã kết nối thành công tới Redis tại {redis_host}:{redis_port}")
        except redis.exceptions.ConnectionError as e:
            print(f" Không thể kết nối tới Redis: {str(e)}")
            # Tạo đối tượng giả lập để tránh lỗi
            self.redis = None
    
    def ping(self) -> bool:
        """Kiểm tra kết nối tới Redis"""
        if self.redis is None:
            return False
        try:
            return self.redis.ping()
        except:
            return False
    
    def get_cached_analysis(self, url: str) -> Optional[Dict[str, Any]]:

        if not self.ping():
            return None
        
        # Tạo key cho Redis dựa trên URL
        cache_key = f"news_analysis:{url}"
        
        try:
            # Kiểm tra xem có cache không
            cached_data = self.redis.get(cache_key)
            if not cached_data:
                return None
            
            # Parse dữ liệu JSON từ cache
            result = json.loads(cached_data)
            print(f" Lấy thành công kết quả phân tích từ cache cho URL: {url}")
            return result
        except Exception as e:
            print(f" Lỗi khi truy xuất cache: {str(e)}")
            return None
    
    def cache_article_analysis(self, url: str, analysis_result: Dict[str, Any]) -> bool:

        if not self.ping():
            return False
        
        # Tạo key cho Redis dựa trên URL
        cache_key = f"news_analysis:{url}"
        
        try:
            # Thêm timestamp vào kết quả
            analysis_result["cached_at"] = int(time.time())
            
            # Convert dict thành JSON string
            json_data = json.dumps(analysis_result)
            
            # Lưu vào Redis với TTL
            self.redis.setex(cache_key, self.cache_ttl, json_data)
            print(f"Đã lưu kết quả phân tích vào cache cho URL: {url}")
            return True
        except Exception as e:
            print(f" Lỗi khi lưu kết quả phân tích vào cache: {str(e)}")
            return False
    
    def clear_cache(self, pattern: str = "news_analysis:*") -> int:

        if not self.ping():
            return 0
        
        try:
            # Tìm tất cả các key theo pattern
            keys = self.redis.keys(pattern)
            
            # Không có key nào để xóa
            if not keys:
                return 0
            
            # Xóa các key
            deleted = self.redis.delete(*keys)
            print(f"🧹 Đã xóa {deleted} key khỏi cache")
            return deleted
        except Exception as e:
            print(f" Lỗi khi xóa cache: {str(e)}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:

        if not self.ping():
            return {"connected": False}
        
        try:
            # Đếm số lượng key theo pattern
            news_analysis_keys = len(self.redis.keys("news_analysis:*"))
            
            # Lấy thông tin bộ nhớ từ Redis
            info = self.redis.info("memory")
            
            return {
                "connected": True,
                "total_keys": news_analysis_keys,
                "memory_used_human": info.get("used_memory_human", "N/A"),
                "memory_peak_human": info.get("used_memory_peak_human", "N/A"),
                "cache_ttl_seconds": self.cache_ttl
            }
        except Exception as e:
            print(f" Lỗi khi lấy thống kê cache: {str(e)}")
            return {"connected": True, "error": str(e)}

# Tạo singleton instance để sử dụng trong toàn ứng dụng
redis_client = RedisClient() 