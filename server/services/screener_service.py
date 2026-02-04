import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Callable, Optional
from .market_data import MarketDataService
from .technical_analysis import TechnicalAnalysisService
from .sentiment_analyzer import SentimentAnalyzerService
from .llm_analysis import LLMAnalysisService

class ScreenerService:
    # S&P 100 constituents (as of 2024)
    SP100_TICKERS = [
        "AAPL", "ABBV", "ABT", "ACN", "ADBE", "AIG", "AMD", "AMGN", "AMT", "AMZN",
        "AVGO", "AXP", "BA", "BAC", "BK", "BKNG", "BLK", "BMY", "BRK.B", "C",
        "CAT", "CHTR", "CL", "CMCSA", "COF", "COP", "COST", "CRM", "CSCO", "CVS",
        "CVX", "DE", "DHR", "DIS", "DOW", "DUK", "EMR", "EXC", "F", "FDX",
        "GD", "GE", "GILD", "GM", "GOOG", "GOOGL", "GS", "HD", "HON", "IBM",
        "INTC", "JNJ", "JPM", "KO", "LIN", "LLY", "LMT", "LOW", "MA", "MCD",
        "MDLZ", "MDT", "MET", "META", "MMM", "MO", "MRK", "MS", "MSFT", "NEE",
        "NFLX", "NKE", "NVDA", "ORCL", "PEP", "PFE", "PG", "PM", "PYPL", "QCOM",
        "RTX", "SBUX", "SCHW", "SO", "SPG", "T", "TGT", "TMO", "TSLA", "TXN",
        "UNH", "UNP", "UPS", "USB", "V", "VZ", "WBA", "WFC", "WMT", "XOM"
    ]
    
    # In-memory cache: {symbol: {data, timestamp}}
    _analysis_cache = {}
    _CACHE_DURATION = 3600  # 1 hour in seconds
    
    @staticmethod
    def get_cached_analysis(symbol: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached analysis if still valid."""
        if symbol in ScreenerService._analysis_cache:
            cache_entry = ScreenerService._analysis_cache[symbol]
            age = time.time() - cache_entry["timestamp"]
            if age < ScreenerService._CACHE_DURATION:
                return cache_entry["data"]
        return None
    
    @staticmethod
    def cache_analysis(symbol: str, data: Dict[str, Any]):
        """Store analysis result in cache."""
        ScreenerService._analysis_cache[symbol] = {
            "data": data,
            "timestamp": time.time()
        }
    
    @staticmethod
    def analyze_single_stock(symbol: str) -> Dict[str, Any]:
        """
        Analyze a single stock using the full AI pipeline.
        Returns a dict with symbol, score, signal, summary, and error (if any).
        """
        try:
            # Fetch all data
            stock_data = MarketDataService.get_stock_history(symbol, period="3mo", interval="1d")
            if "error" in stock_data:
                return {"symbol": symbol, "error": stock_data["error"], "score": 0}
            
            fundamentals = MarketDataService.get_company_info(symbol)
            if "error" in fundamentals:
                return {"symbol": symbol, "error": fundamentals["error"], "score": 0}
            
            tech_indicators = TechnicalAnalysisService.calculate_indicators(stock_data["history"])
            if "error" in tech_indicators:
                return {"symbol": symbol, "error": tech_indicators["error"], "score": 0}
            
            sentiment_data = SentimentAnalyzerService.get_news_sentiment(symbol)
            
            # AI Analysis
            analysis_result = LLMAnalysisService.analyze_market_data(
                symbol, stock_data, tech_indicators, sentiment_data, fundamentals
            )
            
            if "error" in analysis_result:
                return {"symbol": symbol, "error": analysis_result["error"], "score": 0}
            
            # Return structured result
            return {
                "symbol": symbol,
                "score": analysis_result.get("score", 0),
                "signal": analysis_result.get("signal", "Hold"),
                "summary": analysis_result.get("summary", ""),
                "sector": fundamentals.get("sector", "N/A"),
                "price": tech_indicators.get("price", 0),
                "pe_ratio": fundamentals.get("peRatio"),
                "rsi": tech_indicators.get("rsi"),
                "error": None
            }
        except Exception as e:
            return {"symbol": symbol, "error": str(e), "score": 0}
    
    @staticmethod
    def screen_sp100(
        progress_callback: Optional[Callable[[int, int, Dict[str, Any]], None]] = None,
        stop_flag: Optional[Callable[[], bool]] = None
    ) -> List[Dict[str, Any]]:
        """
        Screen all S&P 100 stocks with intelligent batching.
        
        Args:
            progress_callback: Function called after each stock analysis (current, total, result)
            stop_flag: Function that returns True if screening should stop
        
        Returns:
            List of analysis results sorted by score (descending)
        """
        tickers = ScreenerService.SP100_TICKERS
        results = []
        total = len(tickers)
        
        for i in range(0, total, 10):
            # Check stop flag
            if stop_flag and stop_flag():
                break
            
            batch = tickers[i:i+10]
            
            for symbol in batch:
                # Check stop flag
                if stop_flag and stop_flag():
                    break
                
                # Check cache first
                cached = ScreenerService.get_cached_analysis(symbol)
                if cached:
                    results.append(cached)
                    if progress_callback:
                        progress_callback(len(results), total, cached)
                    continue
                
                # Analyze stock
                analysis = ScreenerService.analyze_single_stock(symbol)
                
                # Cache successful results
                if not analysis.get("error"):
                    ScreenerService.cache_analysis(symbol, analysis)
                
                results.append(analysis)
                
                # Update progress
                if progress_callback:
                    progress_callback(len(results), total, analysis)
            
            # Rate limit delay between batches (except last batch)
            if i + 10 < total and not (stop_flag and stop_flag()):
                time.sleep(20)  # 20 seconds to stay under 30 RPM
        
        # Sort by score (descending)
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results
    
    @staticmethod
    def get_top_stocks(n: int = 10) -> List[Dict[str, Any]]:
        """
        Get top N stocks from S&P 100 based on AI score.
        Uses cached results if available, otherwise runs full screen.
        """
        results = ScreenerService.screen_sp100()
        return results[:n]
