from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ArticleRequest(BaseModel):
    url: Optional[str] = None
    text: Optional[str] = None
    options: Optional[Dict[str, Any]] = {
        "summarize": False,
        "detailed_analysis": False,
        "fact_checking": False,
        "source_analysis": False
    }

class SourceInfo(BaseModel):
    domain: Optional[str] = None
    reputation: Optional[float] = None
    category: Optional[str] = None

class FactCheck(BaseModel):
    claim: str
    accurate: bool
    explanation: str
    sources: Optional[List[Dict[str, str]]] = None

class LinguisticAnalysis(BaseModel):
    scores: Dict[str, float]
    features: Dict[str, Any]

class ArticleResponse(BaseModel):
    is_fake: Optional[bool] = None
    confidence: float
    reasons: Optional[List[str]] = None
    summary: Optional[str] = None
    source_info: Optional[SourceInfo] = None
    fact_checks: Optional[List[FactCheck]] = None
    linguistic_analysis: Optional[LinguisticAnalysis] = None 