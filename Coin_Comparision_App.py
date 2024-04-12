import requests
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import plotly.express as px

@st.cache_data
def get_coins_list():
    url = "https://api.coingecko.com/api/v3/coins/list"
    response = requests.get(url)
    if response.ok:
        coins = response.json()
        return coins
    else:
        st.error("Error fetching the coins list.")
        return []

@st.cache_data
def get_coin_history(coin_id, from_timestamp, to_timestamp):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart/range"
    params = {
        "vs_currency": "usd",
        "from": str(int(from_timestamp)),
        "to": str(int(to_timestamp))
    }
    response = requests.get(url, params=params)
    if response.ok:
        data = response.json()
        prices = data.get("prices", [])
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms').dt.date
        return df.drop(columns=["timestamp"])
    else:
        st.error(f"Error fetching the historical data for {coin_id}.")
        return pd.DataFrame(columns=["date", "price"])

def main():
    st.title("CryptoTracker - Comparison Tool")
    coins = get_coins_list()
    coin_ids = {coin['name']: coin['id'] for coin in coins}  # Dictionary for ID lookup

    st.sidebar.header("Parameters")
    selected_coin1 = st.sidebar.selectbox("Select the first cryptocurrency", options=coin_ids.keys())
    selected_coin2 = st.sidebar.selectbox("Select the second cryptocurrency", options=coin_ids.keys())

    time_options = {
        "1 Week": 7,
        "1 Month": 30,
        "1 Year": 365,
        "5 Years": 1825
    }
    time_frame = st.sidebar.selectbox("Choose the time frame:", options=time_options.keys())

    today = datetime.now().date()
    delta_days = time_options[time_frame]
    start_date = today - timedelta(days=delta_days)
    end_date = today

    # Button to trigger comparison
    if st.button('Compare'):
        from_timestamp = datetime.combine(start_date, datetime.min.time()).timestamp()
        to_timestamp = datetime.combine(end_date, datetime.max.time()).timestamp()

        df1 = get_coin_history(coin_ids[selected_coin1], from_timestamp, to_timestamp)
        df2 = get_coin_history(coin_ids[selected_coin2], from_timestamp, to_timestamp)

        if not df1.empty and not df2.empty:
            fig = px.line(title=f'Price Comparison of {selected_coin1} vs {selected_coin2}')
            fig.add_scatter(x=df1['date'], y=df1['price'], mode='lines', name=selected_coin1)
            fig.add_scatter(x=df2['date'], y=df2['price'], mode='lines', name=selected_coin2)
            fig.update_layout(xaxis_title='Date', yaxis_title='Price in USD', template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("No data available for the selected cryptocurrencies and date range.")

if __name__ == "__main__":
    main()
