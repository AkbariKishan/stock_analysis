# StockMind AI 📈

**StockMind AI** is an institutional-grade stock analysis platform powered by AI. It provides a dual-interface experience: a modern **Streamlit Dashboard** for deep dives and a **Model Context Protocol (MCP) Server** for direct integration with AI assistants like Claude Desktop.

![Dashboard Preview](https://images.unsplash.com/photo-1611974765270-ca1258634369?auto=format&fit=crop&q=80&w=1600&h=400)

## 🌟 Exclusive: Key-Free AI Analysis
StockMind AI features a cutting-edge **MCP Server** that requires **ZERO API keys**. By leveraging your AI client's internal intelligence, the server provides raw market intelligence that Claude or ChatGPT interprets to give you professional recommendations for free.

---

## 🚀 Key Features

### 🔌 **Institutional MCP Server** (Key-Free)
- **Direct Integration**: Use StockMind AI inside Claude Desktop or ChatGPT.
- **Natural Language**: Simply ask "Analyze NVDA" or "Compare Apple and Microsoft".
- **Deep Insights**: Returns technical indicators, relative valuation, and news headlines.
- **No Setup Cost**: Automatically uses your client's LLM for all analysis.

### 🔍 **S&P 100 AI Stock Screener**
- **One-Click Analysis**: Screen all 100 S&P constituents in under 6 minutes.
- **AI Ranking**: Stocks are scored (0-100) and ranked by investment quality.
- **Smart Caching**: 1-hour cache for instant subsequent scans.
- **Institutional Logic**: Respects rate limits while delivering high-throughput analysis.

### 📊 **Single Stock Deep Dive Dashboard**
- **Wall Street Rubric**: Weighted analysis (Valuation 40%, Technicals 30%, Sentiment 30%).
- **5-Day Price Projection**: AI-generated daily forecasts with detailed logic.
- **Real-Time Indicators**: RSI, MACD, Bollinger Bands, and Volume Strength.
- **Relative Valuation**: Auto-discovers industry peers for professional P/E benchmarking.

---

## ⚙️ Choose Your Interface

StockMind AI offers two ways to analyze the market:

### 1. Claude Desktop / MCP (Recommended)
**Best for**: Fast, free analysis within your chat interface.
- **Key Required**: None (Uses Claude's LLM)
- **Setup**: `npx @modelcontextprotocol/inspector python mcp_server.py`
- **Full Guide**: [MCP_README.md](MCP_README.md)

### 2. Streamlit Dashboard
**Best for**: Visual charts, financial history, and automated screening.
- **Key Required**: **Groq API Key** (Free from [console.groq.com](https://console.groq.com))
- **Command**: `streamlit run streamlit_app.py`
- **Features**: Interactive Plotly charts, S&P 100 screener, peer benchmarking.

---

## 🛠 Tech Stack

- **Intelligence**: Llama 3.3 70B (via Groq), Model Context Protocol (MCP).
- **Data Engine**: yfinance (Market Data), Google News RSS (Sentiment).
- **Frontend**: Streamlit, Plotly (Dynamic charts).
- **Backbone**: Python, Pandas, Feedparser.

## ⚡️ Quick Start

### 1. Install Dependencies
```bash
pip install -r server/requirements.txt
```

### 2. Configure (Dashboard Only)
If using the Streamlit Dashboard, create a `.env` file:
```env
GROQ_API_KEY=your_key_here
```

### 3. Launch
```bash
# For Dashboard
streamlit run streamlit_app.py

# For MCP Server
# Add to your Claude Desktop config (see MCP_SETUP.md)
```

## 📊 Analysis Documentation

| Indicator | Description |
|-----------|-------------|
| **Investment Score** | 0-100 quality rating (80+ is Strong Buy). |
| **RSI (14)** | Momentum indicator (<30: Oversold, >70: Overbought). |
| **MACD** | Trend reversal signals via crossovers. |
| **Relative P/E** | Valuation compared to 5-10 closest industry peers. |
| **Beta** | Volatility/Risk measurement relative to the market. |

## 📜 License
MIT
