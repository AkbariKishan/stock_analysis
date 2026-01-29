import os
import json
from groq import Groq
from typing import Dict, Any

class LLMAnalysisService:
    @staticmethod
    def analyze_market_data(symbol: str, market_data: Dict[str, Any], technicals: Dict[str, Any], sentiment: Dict[str, Any], fundamentals: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize all market data into a cohesive analysis using Groq LLM.
        """
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return {
                "error": "GROQ_API_KEY not found",
                "score": 50,
                "signal": "Hold",
                "summary": "AI Analysis unavailable (Missing API Key). Falling back to basic analysis."
            }

        client = Groq(api_key=api_key)

        # Prepare context for the LLM
        context = {
            "symbol": symbol,
            "current_price": technicals.get("price"),
            "technicals": {
                "rsi": technicals.get("rsi"),
                "macd": technicals.get("macd"),
                "trend": technicals.get("trend"),
                "moving_average_50": technicals.get("sma_50")
            },
            "sentiment": {
                "score": sentiment.get("average_polarity"),
                "summary": sentiment.get("overall_sentiment"),
                "news_count": sentiment.get("news_count"),
                "top_headlines": [item["title"] for item in sentiment.get("news", [])[:5]]
            },
            "fundamentals": {
                "pe_ratio": fundamentals.get("peRatio"),
                "market_cap": fundamentals.get("marketCap"),
                "sector": fundamentals.get("sector"),
                "industry": fundamentals.get("industry")
            }
        }

        prompt = f"""
        You are a Senior Wall Street Stock Analyst. Your job is to analyze the following data for {symbol} and provide a Buy/Sell/Hold recommendation.
        
        DATA:
        {json.dumps(context, indent=2)}

        INSTRUCTIONS:
        1. Analyze the conflict or coherence between Technicals (RSI/MACD), News Sentiment, and Fundamentals.
        2. Consider Valuation: If P/E ratio is extremely high (>100) or low (<10), factor this into the risk.
        3. If RSI is Overbought but Fundamentals are rock solid and News is positive, it may still be a BUY.
        4. Provide a "score" from 0 (Strong Sell) to 100 (Strong Buy).
        5. Provide a specific "signal" (Strong Buy, Buy, Hold, Sell, Strong Sell).
        6. Provide a concise 2-sentence summary explaining WHY, referencing specific metrics (e.g. "Despite high P/E...").

        OUTPUT FORMAT (JSON ONLY):
        {{
            "score": <integer 0-100>,
            "signal": "<string>",
            "summary": "<string>"
        }}
        """

        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a financial analyst backend that outputs strictly JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=200,
                response_format={"type": "json_object"}
            )
            
            response_content = completion.choices[0].message.content
            return json.loads(response_content)

        except Exception as e:
            print(f"LLM Error: {e}")
            return {
                "error": str(e),
                "score": 50,
                "signal": "Hold",
                "summary": f"AI Analysis failed: {str(e)}"
            }
