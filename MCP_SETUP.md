# MCP Server Setup Guide

## Installation

1. **Install MCP SDK**:
```bash
pip install mcp>=0.9.0
```

Or install all dependencies:
```bash
pip install -r server/requirements.txt
```

2. **Verify Environment**:
Ensure your `.env` file contains:
```
GROQ_API_KEY=gsk_your_key_here
```

## Running the MCP Server

### Standalone Mode
```bash
python mcp_server.py
```

### With MCP Inspector (for testing)
```bash
npx @modelcontextprotocol/inspector python mcp_server.py
```

## Connecting to Claude Desktop

> **IMPORTANT**: You must use your own Groq API key. Get a free key at [console.groq.com](https://console.groq.com/keys)

1. **Locate Claude Desktop config**:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. **Add StockMind AI server**:
```json
{
  "mcpServers": {
    "stockmind": {
      "command": "python",
      "args": ["/Users/snehakotai/stock_analysis/mcp_server.py"],
      "env": {
        "GROQ_API_KEY": "YOUR_OWN_GROQ_API_KEY_HERE"
      }
    }
  }
}
```

**Note**: Replace `YOUR_OWN_GROQ_API_KEY_HERE` with your personal Groq API key (starts with `gsk_`). Do NOT share this key publicly.

3. **Restart Claude Desktop**

4. **Verify connection**: Look for the 🔌 icon in Claude Desktop

## Available Resources

- `stock://screener/sp100` - S&P 100 screener results (top 10)
- `stock://analysis/AAPL` - Full analysis for Apple
- `stock://projection/TSLA` - 5-day projection for Tesla
- `stock://market-data/NVDA` - Market data for NVIDIA

## Available Tools

### analyze_stock
Analyze a single stock with AI.

**Example**:
```
Analyze AAPL stock
```

### screen_sp100
Run S&P 100 screener.

**Example**:
```
Show me the top 10 stocks from S&P 100
```

### get_price_projection
Get 5-day price forecast.

**Example**:
```
What's the 5-day price projection for TSLA?
```

### compare_stocks
Compare multiple stocks.

**Example**:
```
Compare AAPL, MSFT, and GOOGL
```

## Troubleshooting

### Server won't start
- Check Python version (3.8+ required)
- Verify all dependencies installed: `pip install -r server/requirements.txt`
- Ensure GROQ_API_KEY is set in environment

### Claude Desktop can't connect
- Verify absolute path in config is correct
- Check Claude Desktop logs
- Restart Claude Desktop after config changes

### Rate limiting errors
- S&P 100 screener uses caching (1 hour TTL)
- Individual stock analyses are not cached by default
- Groq free tier: 30 requests/minute, 14,400/day
