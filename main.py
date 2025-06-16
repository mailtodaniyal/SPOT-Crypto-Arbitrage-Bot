import streamlit as st
import ccxt
import time
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Crypto Arbitrage Bot", layout="wide")
st.title("🔁 SPOT Crypto Arbitrage Bot (Demo)")

exchanges_list = ['binance', 'kucoin', 'kraken']
pair = st.text_input("Enter Trading Pair (e.g., BTC/USDT)", "BTC/USDT")
threshold = st.slider("Profit Threshold (%)", min_value=0.1, max_value=5.0, value=1.0)
refresh_interval = st.slider("Refresh Interval (seconds)", min_value=5, max_value=60, value=15)
start = st.toggle("Start Arbitrage Bot")

def load_exchanges():
    ex_objs = {}
    for ex in exchanges_list:
        try:
            if ex == 'binance':
                exchange = ccxt.binance({
                    'apiKey': os.getenv('BINANCE_API_KEY'),
                    'secret': os.getenv('BINANCE_SECRET_KEY')
                })
            elif ex == 'kucoin':
                exchange = ccxt.kucoin({
                    'apiKey': os.getenv('KUCOIN_API_KEY'),
                    'secret': os.getenv('KUCOIN_SECRET_KEY'),
                    'password': os.getenv('KUCOIN_PASSPHRASE')
                })
            elif ex == 'kraken':
                exchange = ccxt.kraken({
                    'apiKey': os.getenv('KRAKEN_API_KEY'),
                    'secret': os.getenv('KRAKEN_SECRET_KEY')
                })
            else:
                continue

            exchange.load_markets()
            if pair in exchange.symbols:
                ex_objs[ex] = exchange
        except Exception as e:
            print(f"Error loading {ex}: {e}")
    return ex_objs

def get_prices(exchanges, symbol):
    data = []
    for name, ex in exchanges.items():
        try:
            ticker = ex.fetch_ticker(symbol)
            ask = ticker['ask']
            bid = ticker['bid']
            if ask and bid:
                data.append({
                    'Exchange': name,
                    'Bid': bid,
                    'Ask': ask
                })
        except Exception as e:
            print(f"Error fetching data from {name}: {e}")
            continue
    return pd.DataFrame(data)

def find_arbitrage(df, threshold_percent):
    opportunities = []
    for i, row_a in df.iterrows():
        for j, row_b in df.iterrows():
            if i != j:
                buy_ex = row_a['Exchange']
                sell_ex = row_b['Exchange']
                buy_price = row_a['Ask']
                sell_price = row_b['Bid']
                profit = sell_price - buy_price
                profit_pct = (profit / buy_price) * 100
                if profit_pct >= threshold_percent:
                    opportunities.append({
                        'Buy From': buy_ex,
                        'Sell To': sell_ex,
                        'Buy Price': buy_price,
                        'Sell Price': sell_price,
                        'Profit (%)': round(profit_pct, 2)
                    })
    return pd.DataFrame(opportunities)

placeholder = st.empty()
exchanges = load_exchanges()

while start:
    with placeholder.container():
        st.subheader(f"Live Prices for {pair}")
        prices_df = get_prices(exchanges, pair)
        st.dataframe(prices_df, use_container_width=True)
        if not prices_df.empty:
            arb_df = find_arbitrage(prices_df, threshold)
            if not arb_df.empty:
                st.success("✅ Arbitrage Opportunities Found")
                st.dataframe(arb_df, use_container_width=True)
            else:
                st.info("⚠️ No profitable arbitrage found at the moment.")
    time.sleep(refresh_interval)
