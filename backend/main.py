import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Any

from models import ArticleRequest, ArticleResponse
from services import check_redis, process_article_request

# FastAPI
app = FastAPI(
    title="Fake News Detector API",
    description="API để phát hiện tin giả trong tiếng Việt",
    version="1.0.0"
)

# Thêm CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    # API kiểm tra tin giả tiếng Việt
    return {"message": "API kiểm tra tin giả tiếng Việt", "status": "active"}

@app.get("/health")
async def health_check():
    #Kiểm tra trạng thái hệ thống
    from services import model, tokenizer
    redis_status = check_redis().ping()
    model_status = model is not None and tokenizer is not None
    
    return {
        "status": "healthy" if redis_status and model_status else "degraded",
        "components": {
            "redis": "connected" if redis_status else "disconnected",
            "model": "loaded" if model_status else "not_loaded"
        }
    }

@app.post("/api/detect_fake_news", response_model=ArticleResponse)
async def detect_fake_news(request: ArticleRequest, redis: Optional[Any] = Depends(check_redis)):

    result = process_article_request(request)
    return ArticleResponse(**result)

if __name__ == "__main__":
    
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
