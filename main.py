import requests
import time
from pyfinance.ols import PandasRollingOLS
import pandas as pd
from typing import cast
from trade import Trade, get_current_prices
pairs = ['tLTCBTC', 'tSOLBTC']

def get_market_data(pairs):
    curr_date = int(time.time() * 1000) 
    start_date = curr_date - 14*24*60*60*1000 
    final_df = pd.DataFrame()
    for pair in pairs:
        time.sleep(3)
        r = requests.get(f"https://api-pub.bitfinex.com/v2/candles/trade:30m:{pair}/hist?start={start_date}&end={curr_date}&sort=1&limit=1000")
        if r.status_code == 200:
            res = r.json()
            if len(res) > 660:
                df = pd.DataFrame(res, columns=["timestamp", "open", "close", "high", "low", "volume"])
                df.set_index("timestamp", inplace=True)
                final_df[pair] = df["close"]

    final_df.dropna(inplace=True)
    return final_df

#Spread calculation function
def get_spreads(data):
    if len(data.columns) < 2:
        raise ValueError(f"Expected data for at least 2 pairs, got {len(data.columns)}. Check the Bitfinex responses.")
    spread = pd.DataFrame()
    pair1 = list(data)[0]
    pair2 = list(data)[1]
    pairs = pair1+ '-'+pair2
    rolling_ols = PandasRollingOLS( y = data[pair2],x =data[pair1], window=20)
    hedge_ratios = rolling_ols.beta['feature1']
    spread[pairs] = data[pair2] - hedge_ratios * data[pair1]
    spread.dropna(inplace=True)
    return spread, hedge_ratios

def get_zscore(spread, w=40):
    std = spread.rolling(center=False, window=w).std()
    mean = spread.rolling(center=False, window=w).mean()
    x= spread.rolling(center=False, window=1).mean()
    zscore = (x - mean)/std
    zscore.dropna(inplace=True)
    return zscore

trader = Trade()

while True:
    data = get_market_data(pairs)
    spreads, hedge_ratios = get_spreads(data)
    pair1, pair2 = data.columns[:2]
    pair_name = f"{data.columns[0]}-{data.columns[1]}"
    zscore = cast(float, get_zscore(spreads)[pair_name].iat[-1])
    print(f"Z-score for {pair_name}: {zscore}")
    current_prices = get_current_prices([pair1, pair2])
    print(f"Current prices: {pair1}={current_prices[pair1]}, {pair2}={current_prices[pair2]}")

    if not trader.is_open:
        if zscore > 2:
            trader.open_spread("short", pair1, pair2, hedge_ratios.dropna().iloc[-1], current_prices)
        elif zscore < -2:
            trader.open_spread("long", pair1, pair2, hedge_ratios.dropna().iloc[-1], current_prices)

    if trader.is_open:
        pnl = trader.get_pnl(current_prices)
        print(f"Unrealized paper P/L: {pnl:.8f} BTC")

    time.sleep(30*60) 
