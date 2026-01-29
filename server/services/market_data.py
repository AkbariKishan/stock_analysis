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
            
            # 1. Handle MultiIndex (Slicing by Ticker)
            if isinstance(history.columns, pd.MultiIndex):
                try:
                    # Prefer .xs to slice the ticker level
                    history = history.xs(symbol, axis=1, level=1)
                except:
                    # Fallback: flatten columns
                    history.columns = [col[0] for col in history.columns]
            
            # 2. Reset index to get Date as a column
            history.reset_index(inplace=True)
            
            # 3. Ensure 'Date' is clean
            date_col = next((c for c in history.columns if 'date' in str(c).lower()), None)
            if date_col:
                history.rename(columns={date_col: 'Date'}, inplace=True)
            
            # 4. Defensive extraction of core columns (High Fidelity)
            data_map = {}
            for col in ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']:
                # Find matching column (case-insensitive)
                found_col = next((c for c in history.columns if str(c).lower() == col.lower()), None)
                if found_col:
                    series = history[found_col]
                    # If it's still a dataframe, pick the first column
                    if isinstance(series, pd.DataFrame):
                        series = series.iloc[:, 0]
                    # Convert to JSON compliant types
                    if col == 'Date':
                        data_map[col] = pd.to_datetime(series).dt.strftime('%Y-%m-%d').tolist()
                    elif col == 'Volume':
                        data_map[col] = pd.to_numeric(series, errors='coerce').fillna(0).astype(int).tolist()
                    else:
                        data_map[col] = pd.to_numeric(series, errors='coerce').fillna(0).astype(float).tolist()
                else:
                    data_map[col] = [0] * len(history) if col != 'Date' else [""] * len(history)

            # 5. Reconstruct as list of dicts
            data = []
            for i in range(len(history)):
                data.append({k: data_map[k][i] for k in data_map})
            
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

            # Extract Revenue and Net Income (handle potential key variations)
            dates = [d.strftime('%Y') for d in financials.columns]
            
            # Find the right key for Revenue and Net Income
            rev_key = next((k for k in financials.index if k.lower() in ['total revenue', 'operating revenue', 'total_revenue']), None)
            inc_key = next((k for k in financials.index if k.lower() in ['net income', 'net_income']), None)
            
            revenue = financials.loc[rev_key].values.tolist() if rev_key else [0] * len(dates)
            net_income = financials.loc[inc_key].values.tolist() if inc_key else [0] * len(dates)
            
            # Create list of dicts
            data = []
            for i in range(len(dates)):
                data.append({
                    "date": dates[i],
                    "revenue": float(revenue[i]) if i < len(revenue) and pd.notnull(revenue[i]) else 0,
                    "net_income": float(net_income[i]) if i < len(net_income) and pd.notnull(net_income[i]) else 0
                })
            
            # Sort by date ascending (chronological)
            data.sort(key=lambda x: x["date"])
            
            return sanitize_data(data)
        except Exception as e:
            print(f"Financials Error: {e}")
            return []
