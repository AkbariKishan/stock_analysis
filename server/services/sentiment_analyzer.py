import feedparser
import os
import json
from typing import List, Dict, Any
import ssl
from groq import Groq
from .utils import sanitize_data

# Fix for SSL certificate issues
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context


class SentimentAnalyzerService:
    @staticmethod
    def get_news_sentiment(symbol: str) -> Dict[str, Any]:
        """
        Fetch news from Google News RSS and analyze sentiment using Groq LLM.
        """
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return {
                "symbol": symbol,
                "overall_sentiment": "Neutral",
                "average_polarity": 0,
                "news_count": 0,
                "news": [],
                "error": "GROQ_API_KEY not found"
            }

        client = Groq(api_key=api_key)
        rss_url = f"https://news.google.com/rss/search?q={symbol}+stock&hl=en-US&gl=US&ceid=US:en"
        
        try:
            feed = feedparser.parse(rss_url, agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            news_items = []
            titles = []
            
            for entry in feed.entries[:10]:
                titles.append(entry.title)
                news_items.append({
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.published
                })
            
            if not titles:
                return {
                    "symbol": symbol,
                    "overall_sentiment": "Neutral",
                    "average_polarity": 0,
                    "news_count": 0,
                    "news": []
                }

            # LLM Sentiment Prompt
            prompt = f"""
            Analyze the market sentiment for the stock {symbol} based on these news headlines:
            {json.dumps(titles, indent=2)}

            OUTPUT FORMAT (JSON ONLY):
            {{
                "overall_sentiment": "Positive/Negative/Neutral",
                "average_polarity": <float between -1.0 and 1.0>,
                "reasoning": "<short explanation of the sentiment>"
            }}
            """

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a financial sentiment analysis expert. Output ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            res = json.loads(completion.choices[0].message.content)
            
            return sanitize_data({
                "symbol": symbol,
                "overall_sentiment": res.get("overall_sentiment", "Neutral"),
                "average_polarity": res.get("average_polarity", 0),
                "news_count": len(news_items),
                "news": news_items,
                "reasoning": res.get("reasoning", "")
            })
            
        except Exception as e:
            print(f"Sentiment Analysis Error: {e}")
            return {
                "symbol": symbol,
                "overall_sentiment": "Neutral",
                "average_polarity": 0,
                "news_count": 0,
                "news": [],
                "error": str(e)
            }
