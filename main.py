import requests
import time
from pyfinance.ols import PandasRollingOLS
import pandas as pd

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
    spread[pairs] = data[pair1] - rolling_ols.beta['feature1'] * data[pair2]
    spread.dropna(inplace=True)
    return spread

while True:
    data = get_market_data(pairs)
    spreads = get_spreads(data)
    time.sleep(30*60) 
