import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional

class MarketDataService:
    @staticmethod
    def get_stock_history(symbol: str, period: str = "1y", interval: str = "1d") -> Dict[str, Any]:
        """
        Fetch historical stock data (price & volume).
        """
        try:
            ticker = yf.Ticker(symbol)
            history = ticker.history(period=period, interval=interval)
            
            if history.empty:
                return {"error": f"No data found for symbol {symbol}"}
            
            # Format data for frontend (list of dictionaries)
            history.reset_index(inplace=True)
            history['Date'] = history['Date'].dt.strftime('%Y-%m-%d')
            data = history[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].to_dict('records')
            
            return {
                "symbol": symbol,
                "history": data
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_company_info(symbol: str) -> Dict[str, Any]:
        """
        Fetch company fundamentals.
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Extract key metrics
            return {
                "symbol": symbol,
                "name": info.get("longName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "marketCap": info.get("marketCap"),
                "peRatio": info.get("trailingPE"),
                "eps": info.get("trailingEps"),
                "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
                "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
                "description": info.get("longBusinessSummary")
            }
        except Exception as e:
            return {"error": str(e)}
