# StockMind AI 📈

**StockMind AI** is a professional-grade stock analysis dashboard that combines **Technical** (RSI, MACD), **Fundamental** (Financials), and **Emotional** (News Sentiment) analysis to provide a comprehensive market edge.

![Dashboard Preview](https://images.unsplash.com/photo-1611974765270-ca1258634369?auto=format&fit=crop&q=80&w=1600&h=400)

## 🚀 Key Features

- **Agentic AI Analyst**: Uses **Llama 3.3 (via Groq)** to synthesize technical, sentiment, and fundamental data into a cohesive "Buy/Sell/Hold" signal.
- **Deep Fundamental Analysis**: Evaluates company health using **P/E Ratio**, **Market Cap**, and **EPS** trends.
- **AI-Powered Sentiment**: Real-time analysis of Google News headlines using NLP.
- **Interactive Visualizations**: 
    - **Price History**: 30-day area charts for technical trends.
    - **Financial Performance**: Annual Bar charts comparing **Revenue vs. Net Income**.
- **Live Market Data**: Real-time integration with Yahoo Finance.
- **Premium UI**: Modern, interactive dashboard built with **Streamlit** and **Plotly**.

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

## 📊 Analysis Documentation

| Indicator | Description |
|-----------|-------------|
| **RSI** | Relative Strength Index (<30: Oversold, >70: Overbought). |
| **MACD** | Momentum indicator signaling trend reversals via crossovers. |
| **Sentiment** | NLP scoring of recent news headlines (Positive/Negative/Neutral). |
| **Fundamentals** | Valuation metrics (P/E, Market Cap) to assess long-term health. |

## 📜 License
MIT
