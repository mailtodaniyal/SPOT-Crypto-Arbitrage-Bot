import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Crypto Arbitrage Bot (Static Demo)", layout="wide")
st.title("🧪 SPOT Crypto Arbitrage Bot - Demo Version")

pair = "BTC/USDT"
threshold = st.slider("Profit Threshold (%)", min_value=0.1, max_value=5.0, value=1.0)
refresh_interval = st.slider("Refresh Interval (seconds)", min_value=5, max_value=60, value=10)
start = st.toggle("Start Demo")

mock_data = pd.DataFrame([
    {'Exchange': 'Binance', 'Bid': 27050.00, 'Ask': 27060.00},
    {'Exchange': 'KuCoin', 'Bid': 27080.00, 'Ask': 27090.00},
    {'Exchange': 'Kraken', 'Bid': 27030.00, 'Ask': 27040.00}
])

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

while start:
    with placeholder.container():
        st.subheader(f"📊 Static Prices for {pair}")
        st.dataframe(mock_data, use_container_width=True)

        arb_df = find_arbitrage(mock_data, threshold)
        if not arb_df.empty:
            st.success("✅ Arbitrage Opportunities Found")
            st.dataframe(arb_df, use_container_width=True)
        else:
            st.info("⚠️ No profitable arbitrage found at the moment.")

    time.sleep(refresh_interval)
