import feedparser
import os
import json
from typing import List, Dict, Any
import ssl
from .utils import sanitize_data

# Fix for SSL certificate issues
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context


class SentimentAnalyzerService:
    @staticmethod
    def get_news_sentiment(symbol: str) -> Dict[str, Any]:
        """
        Fetch news headlines for the AI client to analyze sentiment.
        """
        rss_url = f"https://news.google.com/rss/search?q={symbol}+stock&hl=en-US&gl=US&ceid=US:en"
        
        try:
            feed = feedparser.parse(rss_url, agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            news_items = []
            
            for entry in feed.entries[:15]:  # Return more headlines for better AI analysis
                news_items.append({
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.published
                })
            
            if not news_items:
                return {
                    "symbol": symbol,
                    "news_count": 0,
                    "news": [],
                    "note": "No recent news found for this symbol."
                }

            return sanitize_data({
                "symbol": symbol,
                "news_count": len(news_items),
                "news": news_items,
                "analysis_instruction": "The AI client should analyze these headlines to determine overall market sentiment, polarity score (-1 to 1), and identify key themes."
            })
            
        except Exception as e:
            print(f"News Fetching Error: {e}")
            return {
                "symbol": symbol,
                "news_count": 0,
                "news": [],
                "error": str(e)
            }
