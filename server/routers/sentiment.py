from fastapi import APIRouter, HTTPException
from ..services.sentiment_analyzer import SentimentAnalyzerService

router = APIRouter(prefix="/api/sentiment", tags=["sentiment"])

@router.get("/{symbol}")
async def get_sentiment(symbol: str):
    """
    Get sentiment analysis for a stock symbol based on news.
    """
    result = SentimentAnalyzerService.get_news_sentiment(symbol)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result
