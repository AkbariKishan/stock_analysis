# StockMind AI 📈

**StockMind AI** is an institutional-grade stock analysis platform powered by AI. It combines **Technical Analysis**, **Fundamental Valuation**, and **Sentiment Intelligence** to deliver actionable investment insights.

![Dashboard Preview](https://images.unsplash.com/photo-1611974765270-ca1258634369?auto=format&fit=crop&q=80&w=1600&h=400)

## 🚀 Key Features

### 🔍 **S&P 100 AI Stock Screener** (NEW)
- Analyze all 100 S&P constituents in one click
- AI-powered ranking by investment score (0-100)
- Smart batch processing with rate limiting (respects Groq's 30 RPM)
- 1-hour caching for instant subsequent scans
- Top 10 opportunities highlighted with detailed summaries
- ~5-7 minutes for full scan, instant for cached results

### 📊 **Single Stock Deep Dive**
- **Senior Analyst AI**: Uses **Llama 3.3 70B (via Groq)** with a structured "Wall Street Rubric" for weighted analysis (Valuation 40%, Technicals 30%, Sentiment 30%)
- **5-Day Price Projection**: AI-generated daily price forecasts with reasoning
- **Minute-by-Minute Analysis**: Real-time technical indicators with 1m, 5m, 15m intervals for day trading
- **Dynamic Peer Benchmarking**: Auto-discovers industry peers for relative P/E valuation
- **Enriched Metrics**: Beta (risk), Volume Strength (conviction), 52-week range positioning

### 📈 **Advanced Technical Analysis**
- RSI, MACD, Bollinger Bands, SMA 20/50
- Volume strength analysis
- Trend detection with high-frequency support

### 💰 **Fundamental Intelligence**
- P/E ratio vs. industry average (dynamic peer discovery)
- EPS trends, Market Cap, Beta
- Business descriptions for context-aware analysis
- Annual financial performance (Revenue vs. Net Income)

### 📰 **AI-Powered Sentiment**
- Real-time Google News analysis
- LLM-driven sentiment scoring with reasoning
- Headline impact assessment

### 🎨 **Premium UI**
- Modern, dark-themed dashboard
- Interactive Plotly charts
- Progressive updates for screener mode
- Responsive design

## 🛠 Tech Stack

- **Core Logic**: Python, Pandas, TextBlob, yfinance, feedparser.
- **AI Engine**: **Groq API** running **Llama 3.3 70B**.
- **Frontend/UI**: Streamlit, Plotly.

## ⚡️ Quick Start

### Prerequisites
- Python 3.8+
- **Groq API Key** (Free from [console.groq.com](https://console.groq.com/keys))

### Configuration
1. Open `.env` in the root directory.
2. Add your key: `GROQ_API_KEY=gsk_...`

### Launch Analysis Dashboard

```bash
streamlit run streamlit_app.py
```

Open your browser to `http://localhost:8501`

### Usage

#### 📊 Single Stock Analysis
1. Select **"📊 Single Stock"** mode in the sidebar
2. Enter a ticker symbol (e.g., NVDA, AAPL, TSLA)
3. Choose your analysis period (1d to 5y) and interval (1m to 1d)
4. View comprehensive analysis including:
   - AI Buy/Sell/Hold recommendation with score
   - 5-day price projection
   - Technical indicators and charts
   - Fundamental metrics and peer comparison
   - News sentiment analysis

#### 🔍 S&P 100 Screener
1. Select **"🔍 S&P 100 Screener"** mode in the sidebar
2. Click **"🚀 Start Scan"** to analyze all 100 stocks
3. Watch real-time progress (~5-7 minutes for first scan)
4. Review:
   - Top 10 investment opportunities (ranked by AI score)
   - Full sortable table with all 100 stocks
   - Detailed metrics for each stock
5. Subsequent scans within 1 hour load instantly from cache

## 📊 Analysis Documentation

| Indicator | Description |
|-----------|-------------|
| **RSI** | Relative Strength Index (<30: Oversold, >70: Overbought). |
| **MACD** | Momentum indicator signaling trend reversals via crossovers. |
| **Sentiment** | NLP scoring of recent news headlines (Positive/Negative/Neutral). |
| **Fundamentals** | Valuation metrics (P/E, Market Cap) to assess long-term health. |

## 📜 License
MIT
