import os
import json
from typing import Dict, Any, Optional, Callable

class LLMAnalysisServiceMCP:
    """
    LLM Analysis Service that can use either:
    1. Groq API (for Streamlit UI)
    2. MCP Client's LLM (for MCP server)
    """
    
    @staticmethod
    async def analyze_market_data_mcp(
        symbol: str, 
        market_data: Dict[str, Any], 
        technicals: Dict[str, Any], 
        sentiment: Dict[str, Any], 
        fundamentals: Dict[str, Any],
        llm_sampler: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Synthesize all market data into a cohesive analysis using MCP client's LLM.
        
        Args:
            symbol: Stock ticker symbol
            market_data: Historical price data
            technicals: Technical indicators
            sentiment: News sentiment data
            fundamentals: Company fundamentals
            llm_sampler: MCP sampling function (if None, falls back to Groq)
        """
        
        # Prepare context
        curr_price = technicals.get("price", 0)
        high_52 = fundamentals.get("fiftyTwoWeekHigh", 0)
        low_52 = fundamentals.get("fiftyTwoWeekLow", 0)
        range_pos = (curr_price - low_52) / (high_52 - low_52) if (high_52 - low_52) > 0 else 0.5

        context = {
            "symbol": symbol,
            "current_price": curr_price,
            "technicals": {
                "rsi": technicals.get("rsi"),
                "macd": technicals.get("macd"),
                "trend": technicals.get("trend"),
                "vol_strength": technicals.get("volume_strength", 1.0),
                "moving_average_50": technicals.get("sma_50"),
                "price_relative_to_52w_pos": round(range_pos * 100, 2)
            },
            "sentiment": {
                "score": sentiment.get("average_polarity"),
                "summary": sentiment.get("overall_sentiment"),
                "news_count": sentiment.get("news_count"),
                "top_headlines": [item["title"] for item in sentiment.get("news", [])[:5]]
            },
            "fundamentals": {
                "pe_ratio": fundamentals.get("peRatio"),
                "pe_ratio_vs_industry": fundamentals.get("pe_ratio_vs_industry"),
                "industry_pe_average": fundamentals.get("industry_pe_average"),
                "market_cap": fundamentals.get("marketCap"),
                "eps": fundamentals.get("eps"),
                "beta": fundamentals.get("beta"),
                "description": fundamentals.get("description", "")[:200]
            }
        }

        prompt = f"""
        You are a Senior Wall Street Equity Analyst. Analyze {symbol} using this data:

        {json.dumps(context, indent=2)}

        ANALYSIS GUIDELINES:
        1. Technicals
        - Use RSI to assess overbought (>70) or oversold (<30) conditions.
        - Use MACD and trend to assess momentum and direction.
        - If technical data is missing or unclear, state this and de‑emphasize technicals.

        2. Sentiment
        - Use sentiment.score (range -1 to 1) and sentiment.summary to judge market mood.
        - Incorporate news_count and top_headlines only as supporting context (do not just repeat titles).

        3. Fundamentals & Valuation (NEW: Relative P/E Focus)
        - **PRIORITIZE relative valuation**: Compare pe_ratio to industry_pe_average (from fundamentals).
            - pe_ratio significantly < industry_pe_average (e.g., <80%): Potentially undervalued (bullish).
            - pe_ratio significantly > industry_pe_average (e.g., >120%): Potentially overvalued (bearish).
            - Use pe_ratio_vs_industry label if provided for quick context.
        - Consider absolute P/E as secondary:
            - Very low absolute P/E (<10) may indicate undervaluation or fundamental risk (e.g., cyclical downturn).
            - Very high absolute P/E (>100) may indicate overvaluation or high growth expectations.
        - Factor in sector/industry context (e.g., tech often has higher P/Es than utilities).
        - If industry_pe_average or other fundamentals are missing/incomplete, note this and de-emphasize valuation signals.

        4. 5-Day Price Projection
        - Based on current trends, valuation, and sentiment, estimate the daily closing price for the next 5 business days.
        - Be realistic and factor in volatility (beta).
        - If technicals are extremely overbought and sentiment is cooling, project a pullback.
        - If fundamentals are strong and price is recovering, project an uptrend.

        5. Resolving Conflicts
        - If RSI is overbought but fundamentals are strong (e.g., pe_ratio << industry_pe_average) and sentiment is clearly positive, a BUY can still be justified, but note the near‑term technical risk.
        - If signals strongly disagree (e.g., very negative sentiment but strong relative valuation), explain which dimension you prioritize and why (short‑term vs long‑term view).
        - If most signals are weak, noisy, or contradictory, prefer HOLD.

        6. Scoring & Signals
        - Assign a numeric "score" from 0 to 100:
            0-20  = Strong Sell
            21-40 = Sell
            41-60 = Hold
            61-80 = Buy
            81-100 = Strong Buy
        - Ensure "signal" is consistent with the score bands above.

        7. Summary
        - Provide a concise summary of at most 2 sentences.
        - Explicitly reference key metrics driving the decision (e.g., "RSI=75 (overbought), pe_ratio=18 vs industry_pe_average=25 (undervalued), sentiment.score=0.4").

        OUTPUT REQUIREMENTS (STRICT JSON ONLY):
        - Return a single JSON object.
        - Do NOT include any prose before or after the JSON.
        - Use these exact keys and value types:

        {{
        "score": <integer between 0 and 100>,
        "signal": "<one of: 'Strong Buy', 'Buy', 'Hold', 'Sell', 'Strong Sell'>",
        "summary": "<string, max 2 sentences, referencing specific metrics>",
        "projection": {{
            "prices": [<float for day 1>, <float for day 2>, <float for day 3>, <float for day 4>, <float for day 5>],
            "reasoning": "<1-sentence logic for the projected price movement>"
        }}
        }}

        Now produce the JSON output only.
        """

        # Use MCP sampler if provided, otherwise fall back to Groq
        if llm_sampler:
            try:
                # Use MCP client's LLM
                response = await llm_sampler(
                    messages=[
                        {"role": "system", "content": "You are a financial analyst backend that outputs strictly JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500
                )
                
                response_content = response.content
                
                # Parse JSON response
                analysis = json.loads(response_content)
                return analysis
                
            except Exception as e:
                return {
                    "error": f"MCP LLM sampling failed: {str(e)}",
                    "score": 50,
                    "signal": "Hold",
                    "summary": "AI Analysis unavailable. Please check MCP connection."
                }
        else:
            # Fallback to Groq (for Streamlit)
            from groq import Groq
            
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                return {
                    "error": "GROQ_API_KEY not found",
                    "score": 50,
                    "signal": "Hold",
                    "summary": "AI Analysis unavailable (Missing API Key)."
                }
            
            client = Groq(api_key=api_key)
            
            try:
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a financial analyst backend that outputs strictly JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=500,
                    response_format={"type": "json_object"}
                )
                
                response_content = completion.choices[0].message.content
                analysis = json.loads(response_content)
                return analysis
                
            except Exception as e:
                return {
                    "error": f"Groq API error: {str(e)}",
                    "score": 50,
                    "signal": "Hold",
                    "summary": "AI Analysis failed. Please try again."
                }
