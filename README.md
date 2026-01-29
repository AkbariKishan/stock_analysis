# StockMind AI 📈

**StockMind AI** is a professional-grade stock analysis dashboard that combines **Technical** (RSI, MACD), **Fundamental** (Financials), and **Emotional** (News Sentiment) analysis to provide a comprehensive market edge.

![Dashboard Preview](https://images.unsplash.com/photo-1611974765270-ca1258634369?auto=format&fit=crop&q=80&w=1600&h=400)

## 🚀 Key Features

- **Smart Prediction Engine**: Aggregates multiple data points into a clear 0-100 Buy/Sell score.
- **AI-Powered Sentiment**: Uses Natural Language Processing (NLP) to analyze real-time Google News headlines.
- **Interactive Charts**: Responsive area charts visualizing 30-day price history.
- **Live Market Data**: Real-time integration with Yahoo Finance.
- **Premium UI**: Glassmorphism design system built with React & Tailwind CSS.

## 🛠 Tech Stack

- **Backend**: Python, FastAPI, Pandas, TextBlob, yfinance, feedparser.
- **Frontend**: React, Vite, Recharts, Framer Motion, Tailwind CSS.

## ⚡️ Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+

### One-Command Start
We've included a script to launch both the backend and frontend instantly:

```bash
./run.sh
```

### Manual Setup

**Backend**
```bash
source venv/bin/activate
uvicorn server.main:app --reload
```

**Frontend**
```bash
cd client
npm run dev
```

## 📊 Analysis Documentation

| Indicator | Description |
|-----------|-------------|
| **RSI** | Relative Strength Index. <30 is Oversold (Bullish), >70 is Overbought (Bearish). |
| **MACD** | Trend-following momentum indicator. Crossovers signal trend reversals. |
| **Sentiment** | NLP scoring of recent news. Positive news boosts the prediction score. |

## 📜 License
MIT
