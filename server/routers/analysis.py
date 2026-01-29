from fastapi import APIRouter, HTTPException
from ..services.market_data import MarketDataService
from ..services.sentiment_analyzer import SentimentAnalyzerService
from ..services.technical_analysis import TechnicalAnalysisService

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
    
    # 3. Calculate Prediction Score (0-100)
    # Start with 50 (Neutral)
    score = 50
    signal = "Neutral"
    
    # Technical Factors
    if tech_indicators["rsi"] is not None:
        if tech_indicators["rsi"] < 30:
            score += 15  # Oversold (Buy signal)
        elif tech_indicators["rsi"] > 70:
            score -= 15  # Overbought (Sell signal)
            
    if tech_indicators["trend"] == "Bullish":
        score += 10
    else:
        score -= 10
        
    if tech_indicators["macd"] is not None and tech_indicators["macd_signal"] is not None:
        if tech_indicators["macd"] > tech_indicators["macd_signal"]:
            score += 10 # Bullish crossover
        else:
            score -= 10 # Bearish crossover

    # Sentiment Factors
    if "average_polarity" in sentiment_data:
        sentiment_score = sentiment_data["average_polarity"] * 20 # Scaled impact
        score += sentiment_score

    # Clamp score
    score = max(0, min(100, score))
    
    if score > 65:
        signal = "Strong Buy"
    elif score > 55:
        signal = "Buy"
    elif score < 35:
        signal = "Strong Sell"
    elif score < 45:
        signal = "Sell"
    else:
        signal = "Hold"

    return {
        "symbol": symbol,
        "prediction": {
            "score": round(score, 2),
            "signal": signal,
            "summary": f"Technical indicators suggest {tech_indicators['trend']} trend. Sentiment is {sentiment_data.get('overall_sentiment', 'Neutral')}."
        },
        "technical_indicators": tech_indicators,
        "sentiment": sentiment_data,
        "history": stock_data["history"][-30:] # Last 30 days for chart
    }
