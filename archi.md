# Cointegration Strategy Monitor

```python
while True:
    market_data = market_data_receiver()
    spread = spread_builder(market_data)
    signal = data_analyzer(spread)
    risk_state = risk_position_manager(signal)
    trade_executor(signal, risk_state)
```




Spread 
## Spread Calculation

Let `X₁` and `X₂` be two cointegrated price series. Estimate the hedge ratio `m`
with a linear regression of `X₂` on `X₁`, then calculate the spread as:

```text
spread = X₂ - m × X₁
```

USE Rolling OLS 

