import feedparser
from textblob import TextBlob
from typing import List, Dict, Any
import ssl

# Fix for SSL certificate issues
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context


class SentimentAnalyzerService:
    @staticmethod
    def get_news_sentiment(symbol: str) -> Dict[str, Any]:
        """
        Fetch news from Google News RSS and analyze sentiment.
        """
        # Google News RSS URL
        rss_url = f"https://news.google.com/rss/search?q={symbol}+stock&hl=en-US&gl=US&ceid=US:en"
        
        try:
            # Use a browser-like User-Agent to avoid 403 Forbidden/Empty results
            feed = feedparser.parse(rss_url, agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            news_items = []
            total_polarity = 0
            count = 0
            
            for entry in feed.entries[:10]:  # Analyze top 10 news items
                title = entry.title
                link = entry.link
                published = entry.published
                
                # Analyze sentiment of the title
                analysis = TextBlob(title)
                polarity = analysis.sentiment.polarity
                subjectivity = analysis.sentiment.subjectivity
                
                total_polarity += polarity
                count += 1
                
                news_items.append({
                    "title": title,
                    "link": link,
                    "published": published,
                    "sentiment": {
                        "polarity": polarity,
                        "subjectivity": subjectivity,
                        "label": "Positive" if polarity > 0.1 else "Negative" if polarity < -0.1 else "Neutral"
                    }
                })
            
            avg_polarity = total_polarity / count if count > 0 else 0
            overall_sentiment = "Positive" if avg_polarity > 0.05 else "Negative" if avg_polarity < -0.05 else "Neutral"
            
            return {
                "symbol": symbol,
                "overall_sentiment": overall_sentiment,
                "average_polarity": avg_polarity,
                "news_count": count,
                "news": news_items
            }
            
        except Exception as e:
            return {"error": str(e)}
