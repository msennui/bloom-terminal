import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go


# 1. Page Configuration (The Tab Title)
st.set_page_config(page_title="Market Eye", layout="wide")
# 2. The Sidebar (User Controls)
st.sidebar.header("User Input")
ticker = st.sidebar.text_input("Enter Ticker Symbol", "BTC-USD").upper()
time_frame = st.sidebar.selectbox("Select Time Frame", ["1mo", "3mo", "6mo", "1y", "5y"])
st.title(f"📊 Live Dashboard: {ticker}")

# 3. Fetch Data
def get_data(symbol, period):
    data = yf.download(symbol, period=period, interval="1d")
    # Flatten multi-level columns if needed
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data

# Get currency info
def get_currency(symbol):
    try:
        ticker = yf.Ticker(symbol)
        currency = ticker.info.get('currency', 'USD')
    except:
        currency = 'USD'
    return currency

# Currency symbol mapping
def get_currency_symbol(currency_code):
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'CHF': '₣',
        'CAD': 'C$',
        'AUD': 'A$',
    }
    return symbols.get(currency_code, currency_code)

# Format currency with appropriate spacing
def format_currency(amount, currency_symbol):
    if len(currency_symbol) == 1:  # Single char symbols (like $ € £)
        return f"{currency_symbol}{amount:.2f}"
    else:  # Multi-char symbols (like C$ A$)
        return f"{currency_symbol} {amount:.2f}"

try:
    df = get_data(ticker, time_frame)
    currency = get_currency(ticker)
    currency_symbol = get_currency_symbol(currency)
    
    # Calculate a quick metric (Current Price vs Yesterday)
    # Note: yfinance data usually has multi-level columns now, we flatten them for ease
    if not df.empty:
        # Drop NaN values to get the last valid price
        df_clean = df['Close'].dropna()
        if len(df_clean) >= 2:
            current_price = float(df_clean.iloc[-1])
            prev_price = float(df_clean.iloc[-2])
            delta = current_price - prev_price
            delta_percent = (delta / prev_price) * 100
            last_update = df_clean.index[-1].strftime("%Y-%m-%d %H:%M")
            
            # Display Big Metric at the top
            st.metric(label="Current Price", value=format_currency(current_price, currency_symbol), delta=f"{delta:.2f} ({delta_percent:.2f}%)", help=f"Last updated: {last_update}")
        else:
            st.error("Not enough valid data available.")
    else:
        st.error("No data found. Check the ticker symbol.")
except Exception as e:
    st.error(f"Error fetching data: {e}")

# 4. The Interactive Candle Chart
if not df.empty:
    df_chart = df.dropna()  # Remove rows with NaN values
    if not df_chart.empty:
        fig = go.Figure(data=[go.Candlestick(
            x=df_chart.index,
            open=df_chart['Open'],
            high=df_chart['High'],
            low=df_chart['Low'],
            close=df_chart['Close'],
            name=ticker
        )])
# Make it look pretty (Dark Mode compatible)
    fig.update_layout(
        title=f"{ticker} Price Action",
        xaxis_title="Date",
        yaxis_title=f"Price ({currency_symbol})",
        height=600
    )
    # Render the chart in the web app
    st.plotly_chart(fig, width='stretch')
    # 5. Show Raw Data (Optional)
    with st.expander("See Raw Data"):
        st.write(df.tail(10))