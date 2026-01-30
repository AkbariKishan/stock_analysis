import yfinance as yf
import pandas as pd
import time
from typing import Dict, Any, Optional
from .utils import sanitize_data

class MarketDataService:
    # Cache for industry stats: { sector: { "avg": float, "peers": list, "timestamp": float } }
    _industry_cache = {}
    _CACHE_DURATION = 86400  # 24 hours in seconds

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
            # Determine if we should include time (intra-day)
            is_intraday = interval in ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h']
            date_format = '%Y-%m-%d %H:%M:%S' if is_intraday else '%Y-%m-%d'

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
                        data_map[col] = pd.to_datetime(series).dt.strftime(date_format).tolist()
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
    def get_industry_stats(symbol: str, sector_key: str, industry_key: str) -> Dict[str, Any]:
        """
        Dynamically calculate industry average P/E ratios by discovering sector/industry leaders.
        """
        # Use industry_key or sector_key as cache key
        cache_key = industry_key or sector_key or "general"
        current_time = time.time()
        
        if cache_key in MarketDataService._industry_cache:
            cache_entry = MarketDataService._industry_cache[cache_key]
            if current_time - cache_entry["timestamp"] < MarketDataService._CACHE_DURATION:
                return {
                    "industry_pe_average": cache_entry["avg"],
                    "peers": cache_entry["peers"]
                }

        peers = []
        try:
            # Try fetching industry leaders
            if industry_key:
                industry_obj = yf.Industry(industry_key)
                if hasattr(industry_obj, 'top_companies') and not industry_obj.top_companies.empty:
                    peers = industry_obj.top_companies.index.tolist()[:8]
            
            # Fallback to sector leaders
            if not peers and sector_key:
                sector_obj = yf.Sector(sector_key)
                if hasattr(sector_obj, 'top_companies') and not sector_obj.top_companies.empty:
                    peers = sector_obj.top_companies.index.tolist()[:8]
            
            # Remove target symbol and limit
            if symbol in peers:
                peers.remove(symbol)
            peers = peers[:6]
            
            if not peers:
                return {"industry_pe_average": 20.0, "peers": []}

            # Fetch P/E ratios for peers
            tickers = yf.Tickers(" ".join(peers))
            pe_ratios = []
            valid_peers = []
            
            for p_symbol in peers:
                try:
                    p_info = tickers.tickers[p_symbol].info
                    pe = p_info.get("trailingPE") or p_info.get("forwardPE")
                    if pe and pe > 0:
                        pe_ratios.append(pe)
                        valid_peers.append(p_symbol)
                except:
                    continue
            
            avg_pe = sum(pe_ratios) / len(pe_ratios) if pe_ratios else 20.0
            
            # Store in cache
            MarketDataService._industry_cache[cache_key] = {
                "avg": round(avg_pe, 2),
                "peers": valid_peers,
                "timestamp": current_time
            }
            
            return {
                "industry_pe_average": round(avg_pe, 2),
                "peers": valid_peers
            }
        except Exception as e:
            print(f"Dynamic Industry Stats Error: {e}")
            return {"industry_pe_average": 20.0, "peers": []}

    @staticmethod
    def get_company_info(symbol: str) -> Dict[str, Any]:
        """
        Fetch company fundamentals with fully dynamic sector peer discovery.
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            sector = info.get("sector")
            industry = info.get("industry")
            pe_ratio = info.get("trailingPE")
            
            industry_key = info.get("industryKey")
            sector_key = info.get("sectorKey")
            
            # Dynamic Industry Stats using yfinance discovery
            industry_stats = MarketDataService.get_industry_stats(symbol, sector_key, industry_key)
            avg_pe = industry_stats["industry_pe_average"]
            peers = industry_stats["peers"]
            
            # Calculate relative valuation
            pe_vs_industry = "Fair"
            if pe_ratio and avg_pe:
                if pe_ratio < avg_pe * 0.8:
                    pe_vs_industry = "Undervalued"
                elif pe_ratio > avg_pe * 1.2:
                    pe_vs_industry = "Overvalued"
            
            return sanitize_data({
                "symbol": symbol,
                "name": info.get("longName"),
                "sector": sector,
                "industry": industry,
                "marketCap": info.get("marketCap"),
                "peRatio": pe_ratio,
                "industry_pe_average": avg_pe,
                "pe_ratio_vs_industry": pe_vs_industry,
                "peers_used": peers,
                "eps": info.get("trailingEps"),
                "beta": info.get("beta"),
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
