import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional
from .utils import sanitize_data

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
            
            return sanitize_data({
                "symbol": symbol,
                "history": data
            })
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
            return sanitize_data({
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
            })
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_financials(symbol: str) -> Dict[str, Any]:
        """
        Fetch historical revenue and income for plotting.
        """
        try:
            ticker = yf.Ticker(symbol)
            financials = ticker.financials
            
            if financials.empty:
                return []

            # Extract Revenue and Net Income
            dates = [d.strftime('%Y') for d in financials.columns]
            revenue = financials.loc['Total Revenue'].values.tolist() if 'Total Revenue' in financials.index else []
            net_income = financials.loc['Net Income'].values.tolist() if 'Net Income' in financials.index else []
            
            # Create list of dicts for Recharts
            data = []
            for i in range(len(dates)):
                data.append({
                    "date": dates[i],
                    "revenue": revenue[i] if i < len(revenue) else 0,
                    "net_income": net_income[i] if i < len(net_income) else 0
                })
            
            # Sort by date ascending
            data.sort(key=lambda x: x["date"])
            
            return sanitize_data(data)
        except Exception as e:
            print(f"Financials Error: {e}")
            return []
