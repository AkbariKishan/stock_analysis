import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
import sys

from dotenv import load_dotenv, find_dotenv

# Add server directory to path to use existing services
sys.path.append(os.path.join(os.getcwd(), 'server'))

# Load environment variables
load_dotenv(find_dotenv())

from server.services.market_data import MarketDataService
from server.services.sentiment_analyzer import SentimentAnalyzerService
from server.services.technical_analysis import TechnicalAnalysisService
from server.services.llm_analysis import LLMAnalysisService

# Page Config
st.set_page_config(
    page_title="StockMind AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern look
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #161a24;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #2d3139;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #2d3139;
        border-radius: 10px;
    }
    .sentiment-pos { color: #00f5d4; }
    .sentiment-neg { color: #ff006e; }
    .sentiment-neu { color: #facc15; }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("📈 StockMind AI")
symbol = st.sidebar.text_input("Enter Ticker Symbol", value="NVDA").upper()

# Period & Interval selection
col_p, col_i = st.sidebar.columns(2)
with col_p:
    period = st.selectbox("Period", ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"], index=5)
with col_i:
    interval = st.selectbox("Interval", ["1m", "5m", "15m", "1h", "1d"], index=4)

# 1m interval safety check (yfinance limit)
if interval == "1m" and period not in ["1d", "5d", "7d"]:
    st.sidebar.warning("1m interval is limited to max 7 days. Switching period to 5d.")
    period = "5d"

st.sidebar.markdown("---")
st.sidebar.info("""
**StockMind AI** provides real-time technical, fundamental, and sentiment analysis powered by AI.
""")

if symbol:
    with st.spinner(f"Analyzing {symbol}..."):
        try:
            # 1. Fetch Data
            stock_data = MarketDataService.get_stock_history(symbol, period=period, interval=interval)
            if "error" in stock_data:
                st.error(f"Error fetching data for {symbol}: {stock_data['error']}")
            else:
                history_df = pd.DataFrame(stock_data["history"])
                history_df['Date'] = pd.to_datetime(history_df['Date'])
                history_df = history_df.sort_values('Date')
                
                sentiment_data = SentimentAnalyzerService.get_news_sentiment(symbol)
                tech_indicators = TechnicalAnalysisService.calculate_indicators(stock_data["history"])
                fundamentals = MarketDataService.get_company_info(symbol)
                financial_history = MarketDataService.get_financials(symbol)
                
                # AI Analysis
                analysis_result = LLMAnalysisService.analyze_market_data(
                    symbol, stock_data, tech_indicators, sentiment_data, fundamentals
                )
                
                # Layout
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Header Section
                    st.title(f"{symbol} Analysis")
                    st.subheader(f"${tech_indicators['price']:.2f}")
                    
                    # Prediction Card
                    score = analysis_result.get("score", 50)
                    signal = analysis_result.get("signal", "Hold")
                    summary = analysis_result.get("summary", "Analysis unavailable.")
                    
                    signal_color = "#00f5d4" if "Buy" in signal else "#ff006e" if "Sell" in signal else "#facc15"
                    st.markdown(f"""
                    <div style="background-color: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border-left: 5px solid {signal_color}; margin-bottom: 25px;">
                        <h2 style="margin:0; color:{signal_color};">{signal.upper()} (Score: {score})</h2>
                        <p style="font-size: 1.1em; color: #ddd; margin-top: 10px;">{summary}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Chart
                    st.write("### Price History & Volume")
                    
                    from plotly.subplots import make_subplots
                    
                    # Ensure data is strictly numeric, sorted, and converted to PURE LISTS
                    history_df = history_df.sort_values('Date').reset_index(drop=True)
                    
                    # Formatting for X-axis
                    is_intraday = interval in ['1m', '5m', '15m', '1h']
                    date_format = '%Y-%m-%d %H:%M' if is_intraday else '%Y-%m-%d'
                    plot_dates = history_df['Date'].dt.strftime(date_format).tolist()
                    
                    plot_close = pd.to_numeric(history_df['Close'], errors='coerce').tolist()
                    plot_volume = pd.to_numeric(history_df['Volume'], errors='coerce').tolist()
                    
                    # Audit check right before plotting
                    with st.expander("🔍 Chart Data Audit"):
                        st.write(f"**Prices (first 3):** {plot_close[:3]}")
                        st.write(f"**Volumes (first 3):** {plot_volume[:3]}")
                    
                    # Create subplot with secondary y-axis
                    fig = make_subplots(specs=[[{"secondary_y": True}]])
                    
                    # Volume Bars (Secondary Axis - Background)
                    fig.add_trace(go.Bar(
                        x=plot_dates,
                        y=plot_volume,
                        name='Volume',
                        marker_color='rgba(100, 100, 100, 0.2)',
                    ), secondary_y=True)
                    
                    # Price Line (Primary Axis)
                    fig.add_trace(go.Scatter(
                        x=plot_dates, 
                        y=plot_close, 
                        mode='lines', 
                        name='Price',
                        line=dict(color='#3b82f6', width=2),
                        fill='tozeroy',
                        fillcolor='rgba(59, 130, 246, 0.1)',
                    ), secondary_y=False)
                    
                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        margin=dict(l=0, r=0, t=10, b=0),
                        xaxis=dict(
                            showgrid=False, 
                            title=None,
                            type='date'
                        ),
                        yaxis=dict(
                            showgrid=True, 
                            gridcolor='rgba(255,255,255,0.1)', 
                            title=None,
                            side='left'
                        ),
                        yaxis2=dict(
                            showgrid=False,
                            showticklabels=False,
                            range=[0, max(plot_volume) * 4 if plot_volume else 1]
                        ),
                        height=400,
                        showlegend=False,
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Price Projection Section
                    if "projection" in analysis_result:
                        st.write("### AI Price Projection (Next 5 Days)")
                        proj_data = analysis_result["projection"]
                        proj_prices = proj_data.get("prices", [])
                        proj_reasoning = proj_data.get("reasoning", "")
                        
                        if proj_prices and len(proj_prices) == 5:
                            # Calculate next 5 business days
                            future_dates = []
                            current_dt = datetime.now()
                            while len(future_dates) < 5:
                                current_dt += timedelta(days=1)
                                if current_dt.weekday() < 5:  # Monday to Friday
                                    future_dates.append(current_dt.strftime('%Y-%m-%d'))
                            
                            fig_proj = go.Figure()
                            
                            # Add projection line
                            fig_proj.add_trace(go.Scatter(
                                x=future_dates,
                                y=proj_prices,
                                mode='lines+markers+text',
                                name='Projected Price',
                                text=[f"${p:.2f}" for p in proj_prices],
                                textposition="top center",
                                line=dict(color='#fbbf24', width=3, dash='dash'),
                                marker=dict(size=10, color='#fbbf24')
                            ))
                            
                            fig_proj.update_layout(
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                                margin=dict(l=0, r=0, t=30, b=0),
                                height=300,
                                xaxis=dict(showgrid=False),
                                yaxis=dict(
                                    showgrid=True, 
                                    gridcolor='rgba(255,255,255,0.1)',
                                    range=[min(proj_prices) * 0.98, max(proj_prices) * 1.02]
                                ),
                                showlegend=False
                            )
                            st.plotly_chart(fig_proj, use_container_width=True)
                            st.info(f"**Projection Logic:** {proj_reasoning}")
                        else:
                            st.warning("AI Price Projection data is incomplete.")

                    # Debug Info
                    with st.expander("🛠 Debug: Raw Market Data"):
                        st.write("**Data Types:**")
                        st.write(history_df.dtypes.to_dict())
                        st.write("**Last 5 Rows:**")
                        st.dataframe(history_df.tail())
                        if "projection" in analysis_result:
                            st.write("**Raw Projection:**")
                            st.json(analysis_result["projection"])
                    
                    # News Section
                    st.write("### Recent News Analysis")
                    if sentiment_data.get('reasoning'):
                        st.info(f"**AI Sentiment Insight:** {sentiment_data['reasoning']}")
                    
                    for news_item in sentiment_data.get('news', [])[:5]:
                        with st.expander(f"{news_item['title']}"):
                            st.write(f"**Published:** {news_item['published']}")
                            st.link_button("Read Article", news_item['link'])

                with col2:
                    # Metrics Grid
                    st.write("### Key Metrics")
                    m_col1, m_col2, m_col3 = st.columns(3)
                    with m_col1:
                        st.metric("RSI (14)", f"{tech_indicators.get('rsi', 0):.1f}")
                        st.metric("P/E Ratio", f"{fundamentals.get('peRatio', 0):.1f}" if fundamentals.get('peRatio') else "N/A")
                    with m_col2:
                        st.metric("Sentiment", sentiment_data.get('overall_sentiment', 'Neutral').capitalize())
                        avg_pe = fundamentals.get('industry_pe_average', 0)
                        pe_vs = fundamentals.get('pe_ratio_vs_industry', 'Fair')
                        st.metric("Industry P/E", f"{avg_pe:.1f}", delta=pe_vs, delta_color="inverse" if pe_vs == "Overvalued" else "normal")
                    with m_col3:
                        st.metric("Beta", f"{fundamentals.get('beta', 0):.2f}" if fundamentals.get('beta') else "N/A")
                        st.metric("Vol Strength", f"{tech_indicators.get('volume_strength', 1.0):.1f}x")
                    
                    if fundamentals.get('peers_used'):
                        st.caption(f"**Industry Peers:** {', '.join(fundamentals['peers_used'])}")
                    
                    # Technical Data
                    st.write("### Technical Indicators")
                    tech_table = {
                        "Indicator": ["SMA 50", "MACD", "BB Upper", "BB Lower"],
                        "Value": [
                            f"${tech_indicators.get('sma_50', 0):.2f}",
                            f"{tech_indicators.get('macd', 0):.2f}",
                            f"${tech_indicators.get('bb_upper', 0):.2f}",
                            f"${tech_indicators.get('bb_lower', 0):.2f}"
                        ]
                    }
                    st.table(pd.DataFrame(tech_table))
                    
                    # Financials Chart
                    if financial_history:
                        st.write("### Financials")
                        fin_df = pd.DataFrame(financial_history)
                        
                        # Convert to pure lists to prevent index-mapping issues
                        fin_dates = fin_df['date'].tolist()
                        fin_rev = pd.to_numeric(fin_df['revenue'], errors='coerce').tolist()
                        fin_inc = pd.to_numeric(fin_df['net_income'], errors='coerce').tolist()
                        
                        # Audit check for Financials
                        with st.expander("🔍 Financials Data Audit"):
                            st.write(f"**Revenue (first 2):** {fin_rev[:2]}")
                            st.write(f"**Net Income (first 2):** {fin_inc[:2]}")
                        
                        fig_fin = go.Figure()
                        fig_fin.add_trace(go.Bar(
                            x=fin_dates,
                            y=fin_rev,
                            name='Revenue',
                            marker_color='#3b82f6'
                        ))
                        fig_fin.add_trace(go.Bar(
                            x=fin_dates,
                            y=fin_inc,
                            name='Net Income',
                            marker_color='#10b981'
                        ))
                        
                        fig_fin.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            margin=dict(l=0, r=0, t=10, b=0),
                            height=300,
                            barmode='group',
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                            xaxis=dict(showgrid=False),
                            yaxis=dict(
                                showgrid=True, 
                                gridcolor='rgba(255,255,255,0.1)',
                                tickformat=".2s", # SI format
                            )
                        )
                        # Proactively replace G with B for billions in the UI labels
                        fig_fin.update_layout(yaxis_ticksuffix="B", yaxis_tickformat=".2s")
                        # Note: Plotly's .2s uses G for Giga. To get B, we'll keep .2s and explain or 
                        # scale. Actually, a cleaner way is to just set the tickformat to skip the G.
                        fig_fin.update_yaxes(tickformat=".2s")
                        
                        # Let's use a more explicit approach to ensure 'B' shows up
                        fig_fin.update_layout(
                            yaxis=dict(
                                tickformat=".3s",
                                ticksuffix="", # Default
                            )
                        )
                        st.plotly_chart(fig_fin, use_container_width=True)

        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
            st.exception(e)
else:
    st.info("Enter a stock ticker in the sidebar to begin analysis.")
