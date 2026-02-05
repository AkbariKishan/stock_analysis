#!/usr/bin/env python3
"""
StockMind AI MCP Server

Exposes stock analysis capabilities through the Model Context Protocol (MCP).
Uses the MCP client's LLM (Claude, ChatGPT, etc.) for analysis - NO API KEY REQUIRED!

This server provides raw market data and technical/fundamental/sentiment analysis.
The MCP client's LLM interprets this data to generate investment recommendations.
"""

import asyncio
import json
import os
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent

# Add server directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'server'))

from dotenv import load_dotenv
load_dotenv()

from server.services.market_data import MarketDataService
from server.services.technical_analysis import TechnicalAnalysisService
from server.services.sentiment_analyzer import SentimentAnalyzerService

# Initialize MCP server
app = Server("stockmind-ai")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def analyze_stock_data(symbol: str, period: str = "3mo", interval: str = "1d") -> dict:
    """
    Gather all stock data without LLM analysis.
    The MCP client's LLM will interpret this data.
    """
    # Fetch data
    stock_data = MarketDataService.get_stock_history(symbol, period=period, interval=interval)
    if "error" in stock_data:
        return {"error": stock_data["error"]}
    
    fundamentals = MarketDataService.get_company_info(symbol)
    tech_indicators = TechnicalAnalysisService.calculate_indicators(stock_data["history"])
    sentiment_data = SentimentAnalyzerService.get_news_sentiment(symbol)
    
    # Calculate additional metrics
    curr_price = tech_indicators.get("price", 0)
    high_52 = fundamentals.get("fiftyTwoWeekHigh", 0)
    low_52 = fundamentals.get("fiftyTwoWeekLow", 0)
    range_pos = (curr_price - low_52) / (high_52 - low_52) if (high_52 - low_52) > 0 else 0.5
    
    return {
        "symbol": symbol,
        "current_price": curr_price,
        "technicals": {
            "rsi": tech_indicators.get("rsi"),
            "rsi_interpretation": "Overbought" if tech_indicators.get("rsi", 50) > 70 else "Oversold" if tech_indicators.get("rsi", 50) < 30 else "Neutral",
            "macd": tech_indicators.get("macd"),
            "trend": tech_indicators.get("trend"),
            "sma_20": tech_indicators.get("sma_20"),
            "sma_50": tech_indicators.get("sma_50"),
            "bb_upper": tech_indicators.get("bb_upper"),
            "bb_lower": tech_indicators.get("bb_lower"),
            "volume_strength": tech_indicators.get("volume_strength", 1.0),
            "52_week_position_pct": round(range_pos * 100, 2)
        },
        "fundamentals": {
            "pe_ratio": fundamentals.get("peRatio"),
            "industry_pe_average": fundamentals.get("industry_pe_average"),
            "pe_ratio_vs_industry": fundamentals.get("pe_ratio_vs_industry"),
            "market_cap": fundamentals.get("marketCap"),
            "beta": fundamentals.get("beta"),
            "eps": fundamentals.get("eps"),
            "sector": fundamentals.get("sector"),
            "industry": fundamentals.get("industry"),
            "description": fundamentals.get("description", "")[:300],
            "52_week_high": high_52,
            "52_week_low": low_52
        },
        "sentiment": {
            "overall": sentiment_data.get("overall_sentiment"),
            "score": sentiment_data.get("average_polarity"),
            "news_count": sentiment_data.get("news_count"),
            "top_headlines": [item["title"] for item in sentiment_data.get("news", [])[:5]],
            "reasoning": sentiment_data.get("reasoning", "")
        },
        "analysis_prompt": f"""
Based on the above data for {symbol}, provide:
1. Investment Score (0-100): 0-20=Strong Sell, 21-40=Sell, 41-60=Hold, 61-80=Buy, 81-100=Strong Buy
2. Signal: Strong Buy/Buy/Hold/Sell/Strong Sell
3. Summary: 2-sentence analysis referencing specific metrics
4. 5-Day Price Projection: Estimate daily closing prices for next 5 business days with reasoning

Consider:
- Technicals: RSI overbought/oversold, MACD momentum, trend direction
- Fundamentals: P/E vs industry average (undervalued if <80%, overvalued if >120%)
- Sentiment: News polarity and market mood
- Risk: Beta for volatility assessment
        """
    }

# ============================================================================
# RESOURCES
# ============================================================================

@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available stock analysis resources."""
    return [
        Resource(
            uri="stock://analysis/{symbol}",
            name="Stock Analysis Data",
            mimeType="application/json",
            description="Complete technical, fundamental, and sentiment data for any stock (e.g., stock://analysis/AAPL). The client's LLM will interpret this data."
        ),
        Resource(
            uri="stock://market-data/{symbol}",
            name="Raw Market Data",
            mimeType="application/json",
            description="Historical price and volume data (e.g., stock://market-data/NVDA)"
        )
    ]

@app.read_resource()
async def read_resource(uri: str) -> str:
    """Read a specific stock analysis resource."""
    
    if uri.startswith("stock://analysis/"):
        symbol = uri.split("/")[-1].upper()
        data = analyze_stock_data(symbol)
        return json.dumps(data, indent=2)
    
    elif uri.startswith("stock://market-data/"):
        symbol = uri.split("/")[-1].upper()
        stock_data = MarketDataService.get_stock_history(symbol, period="1y", interval="1d")
        if "error" in stock_data:
            return json.dumps({"error": stock_data["error"]}, indent=2)
        
        return json.dumps({
            "symbol": symbol,
            "history": stock_data["history"][-30:]  # Last 30 days
        }, indent=2)
    
    else:
        return json.dumps({"error": f"Unknown resource URI: {uri}"}, indent=2)

# ============================================================================
# TOOLS
# ============================================================================

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available stock analysis tools."""
    return [
        Tool(
            name="analyze_stock",
            description="Get comprehensive stock analysis data (technical, fundamental, sentiment). The client's LLM will interpret this data to provide investment recommendations. No API key required!",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, TSLA, NVDA)"
                    },
                    "period": {
                        "type": "string",
                        "description": "Analysis period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y)",
                        "default": "3mo"
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="compare_stocks",
            description="Compare multiple stocks side-by-side. Returns technical, fundamental, and sentiment data for all stocks. The client's LLM will provide comparative analysis.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbols": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of stock ticker symbols (e.g., ['AAPL', 'MSFT', 'GOOGL'])"
                    }
                },
                "required": ["symbols"]
            }
        ),
        Tool(
            name="get_market_data",
            description="Get raw historical price and volume data for a stock.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "period": {
                        "type": "string",
                        "description": "Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y)",
                        "default": "1mo"
                    }
                },
                "required": ["symbol"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute a stock analysis tool."""
    
    try:
        if name == "analyze_stock":
            symbol = arguments["symbol"].upper()
            period = arguments.get("period", "3mo")
            
            data = analyze_stock_data(symbol, period=period)
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        elif name == "compare_stocks":
            symbols = [s.upper() for s in arguments["symbols"]]
            comparisons = []
            
            for symbol in symbols:
                data = analyze_stock_data(symbol)
                comparisons.append(data)
            
            result = {
                "comparison": comparisons,
                "note": "Use the client's LLM to analyze and compare these stocks based on the provided data."
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_market_data":
            symbol = arguments["symbol"].upper()
            period = arguments.get("period", "1mo")
            
            stock_data = MarketDataService.get_stock_history(symbol, period=period, interval="1d")
            if "error" in stock_data:
                return [TextContent(type="text", text=json.dumps({"error": stock_data["error"]}, indent=2))]
            
            return [TextContent(type="text", text=json.dumps({
                "symbol": symbol,
                "period": period,
                "history": stock_data["history"]
            }, indent=2))]
        
        else:
            return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}, indent=2))]
    
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}, indent=2))]

# ============================================================================
# MAIN
# ============================================================================

async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
