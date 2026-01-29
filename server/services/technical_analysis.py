import pandas as pd
import numpy as np
from typing import Dict, Any, List
from .utils import sanitize_data

class TechnicalAnalysisService:
    @staticmethod
    def calculate_indicators(history_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate technical indicators (RSI, MACD, SMA, Bollinger Bands) from historical data.
        """
        if not history_data:
            return {"error": "No data provided"}

        df = pd.DataFrame(history_data)
        
        # Ensure correct types
        df['Close'] = pd.to_numeric(df['Close'])
        
        # 1. Simple Moving Averages (SMA)
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        # 2. RSI (Relative Strength Index)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # 3. MACD (Moving Average Convergence Divergence)
        exp12 = df['Close'].ewm(span=12, adjust=False).mean()
        exp26 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp12 - exp26
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # 4. Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        df['BB_Upper'] = df['BB_Middle'] + (df['Close'].rolling(window=20).std() * 2)
        df['BB_Lower'] = df['BB_Middle'] - (df['Close'].rolling(window=20).std() * 2)
        
        # 5. Volume Analysis
        avg_vol = df['Volume'].rolling(window=20).mean()
        latest_vol = df['Volume'].iloc[-1]
        vol_strength = latest_vol / avg_vol.iloc[-1] if not avg_vol.empty and avg_vol.iloc[-1] > 0 else 1.0
        
        # Get latest values
        latest = df.iloc[-1]
        
        return sanitize_data({
            "rsi": latest['RSI'],
            "macd": latest['MACD'],
            "macd_signal": latest['Signal_Line'],
            "sma_50": latest['SMA_50'],
            "sma_20": latest['SMA_20'],
            "bb_upper": latest['BB_Upper'],
            "bb_lower": latest['BB_Lower'],
            "price": latest['Close'],
            "avg_volume": avg_vol.iloc[-1],
            "volume_strength": vol_strength,
            "trend": "Bullish" if latest['Close'] > latest['SMA_50'] else "Bearish"
        })
