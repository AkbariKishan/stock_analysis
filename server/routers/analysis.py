from fastapi import APIRouter, HTTPException
from ..services.market_data import MarketDataService
from ..services.sentiment_analyzer import SentimentAnalyzerService
from ..services.technical_analysis import TechnicalAnalysisService
from ..services.llm_analysis import LLMAnalysisService

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

@router.get("/{symbol}")
async def get_analysis(symbol: str):
    """
    Get comprehensive analysis including technical indicators, sentiment, and prediction.
    """
    # 1. Fetch Data
    stock_data = MarketDataService.get_stock_history(symbol, period="1y")
    if "error" in stock_data:
        raise HTTPException(status_code=404, detail=stock_data["error"])
        
    sentiment_data = SentimentAnalyzerService.get_news_sentiment(symbol)
    
    # 2. Tech Analysis
    tech_indicators = TechnicalAnalysisService.calculate_indicators(stock_data["history"])

    analysis_result = LLMAnalysisService.analyze_market_data(symbol, stock_data, tech_indicators, sentiment_data)
    
    # If LLM fails (missing key), fallback to basic logic would be implemented here or handled by the service returning specific structure
    score = analysis_result.get("score", 50)
    signal = analysis_result.get("signal", "Hold")
    summary = analysis_result.get("summary", "Analysis unavailable.")

    return {
        "symbol": symbol,
        "prediction": {
            "score": score,
            "signal": signal,
            "summary": summary
        },
        "technical_indicators": tech_indicators,
        "sentiment": sentiment_data,
        "history": stock_data["history"][-30:] # Last 30 days for chart
    }
