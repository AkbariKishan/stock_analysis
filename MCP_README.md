# StockMind AI - MCP Server

> **✅ NO API KEY REQUIRED!** This MCP server uses YOUR client's LLM (Claude, ChatGPT, etc.) for analysis.

## What is this?

StockMind AI MCP Server provides professional-grade stock market data to AI assistants. The server fetches and structures technical, fundamental, and sentiment data - then YOUR AI assistant's LLM interprets it to generate investment recommendations.

**No Groq API key needed. No OpenAI API key needed. Just pure data + your AI's intelligence.**

## How It Works

1. **You ask your AI**: "Analyze AAPL stock"
2. **MCP server provides**: Technical indicators, fundamentals, news sentiment
3. **Your AI interprets**: Uses its own LLM to generate buy/sell/hold recommendations

## Setup (2 minutes)

### 1. Install Dependencies
```bash
cd /path/to/stock_analysis
pip install -r server/requirements.txt
```

### 2. Configure Your AI Client

#### For Claude Desktop:
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "stockmind": {
      "command": "python",
      "args": ["/path/to/stock_analysis/mcp_server.py"]
    }
  }
}
```

#### For Other MCP Clients:
Use the same configuration format. No environment variables needed!

### 3. Restart Your AI Client

### 4. Start Using
Ask your AI:
- "Analyze AAPL stock"
- "Compare AAPL, MSFT, and GOOGL"
- "Get market data for TSLA"

## Available Tools

### analyze_stock
Get comprehensive analysis data for any stock.
- **Input**: symbol (e.g., "AAPL"), optional period
- **Output**: Technical indicators, fundamentals, sentiment data
- **Your AI will**: Interpret the data and provide investment recommendations

### compare_stocks
Compare multiple stocks side-by-side.
- **Input**: list of symbols (e.g., ["AAPL", "MSFT", "GOOGL"])
- **Output**: Comparative data for all stocks
- **Your AI will**: Analyze and rank the stocks

### get_market_data
Get raw historical price and volume data.
- **Input**: symbol, optional period
- **Output**: Historical OHLCV data

## What Data Is Provided?

For each stock, the server provides:

**Technical Analysis**:
- RSI (with overbought/oversold interpretation)
- MACD, trend direction
- Moving averages (SMA 20, SMA 50)
- Bollinger Bands
- Volume strength
- 52-week price position

**Fundamental Analysis**:
- P/E ratio vs. industry average
- Market cap, Beta, EPS
- Sector and industry
- Company description
- 52-week high/low

**Sentiment Analysis**:
- News sentiment score (-1 to 1)
- Top 5 recent headlines
- Overall market mood
- AI-generated sentiment reasoning

## Privacy & Performance

- ✅ **No API keys required** - Uses your AI client's LLM
- ✅ **No data collection** - Everything runs locally
- ✅ **Free Yahoo Finance data** - Public market data only
- ✅ **Fast responses** - No external LLM API calls from server

## Example Usage

**In Claude Desktop:**
```
You: Analyze AAPL stock

Claude: [Calls analyze_stock tool, receives data]
Based on the analysis:
- Score: 75/100 (Buy)
- RSI: 45 (Neutral, healthy range)
- P/E: 28 vs Industry Avg: 32 (Undervalued by 12%)
- Sentiment: Positive (0.6) with 15 recent news articles
- Recommendation: BUY - Strong fundamentals with room to run...
```

## Troubleshooting

**Server won't start**:
- Check Python 3.8+ is installed
- Run `pip install -r server/requirements.txt`

**AI can't see the tools**:
- Verify absolute path in config is correct
- Restart your AI client after config changes
- Check for the 🔌 icon (Claude Desktop)

**Data seems outdated**:
- Yahoo Finance data updates during market hours
- Historical data is always available

## Support

For issues, please file a GitHub issue on the StockMind AI repository.
