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

> **✅ NO API KEY REQUIRED!** The MCP server uses your AI client's LLM for analysis.

1. **Locate Claude Desktop config**:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. **Add StockMind AI server**:
```json
{
  "mcpServers": {
    "stockmind": {
      "command": "python",
      "args": ["/absolute/path/to/stock_analysis/mcp_server.py"]
    }
  }
}
```

**Note**: Replace `/absolute/path/to/stock_analysis/mcp_server.py` with the actual absolute path on your system.

3. **Restart Claude Desktop**

4. **Verify connection**: Look for the 🔌 icon in Claude Desktop

## Available Resources

- `stock://analysis/AAPL` - Complete analysis data for Apple
- `stock://market-data/NVDA` - Historical market data for NVIDIA

## Available Tools

### analyze_stock
Get comprehensive stock analysis data (technical, fundamental, sentiment).

**Example**:
```
Analyze AAPL stock
```

### compare_stocks
Compare multiple stocks side-by-side.

**Example**:
```
Compare AAPL, MSFT, and GOOGL
```

### get_market_data
Get raw historical price and volume data.

**Example**:
```
Get market data for TSLA over the past 6 months
```

## Troubleshooting

### Server won't start
- Check Python version (3.8+ required)
- Verify all dependencies installed: `pip install -r server/requirements.txt`

### Claude Desktop can't connect
- Verify absolute path in config is correct
- Check Claude Desktop logs
- Restart Claude Desktop after config changes

### Data seems outdated
- Yahoo Finance data updates during market hours
- Historical data is always available
- News sentiment refreshes with each request
