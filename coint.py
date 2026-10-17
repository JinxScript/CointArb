import requests
import time
import pandas as pd
from statsmodels.tsa.stattools import coint
curr_date = int(time.time() * 1000) 
start_date = curr_date - 14*24*60*60*1000 
url = "https://api-pub.bitfinex.com/v2/tickers?symbols=ALL"
reponse = requests.get(url)

#Checking the status code of the response
if reponse.status_code == 200:
    # use the built in json parser instead of eval() as execute arbitray code stings passed to it 
    symbols = reponse.json()

# Symbol filter 
symbols_filtered =[]

for elem in symbols:
    if elem[0].endswith("BTC"):
        symbols_filtered.append(elem)

final_df = pd.DataFrame()
for pair in symbols_filtered:
    time.sleep(3)
    r = requests.get(f"https://api-pub.bitfinex.com/v2/candles/trade:30m:{pair[0]}/hist?start={start_date}&end={curr_date}&sort=1&limit=1000")
    if r.status_code == 200:
        res = r.json()
        if len(res) > 660:
            df = pd.DataFrame(res, columns=["timestamp", "open", "close", "high", "low", "volume"])
            df.set_index("timestamp", inplace=True)
            final_df[pair[0]] = df["close"]

final_df.dropna(inplace=True)

for i in list(final_df):
    for j in list(final_df):
        if i != j:
            pair = i + '-' + j # type: ignore
            statistic, p_value, critical_values = coint(final_df[i], final_df[j]) # calcualtion of the cointegration test
            print(pair, "statistic:", statistic, "p-value:", p_value, "critical values:", critical_values)