import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
#ai attempt, less than superb
johnson_johnson = yf.Ticker("JNJ")
jj_monthly_data = johnson_johnson.history(start="1975-01-01", end="2009-12-01", interval="1mo")

pfizer = yf.Ticker("PFE")
pfizer_monthly_data = pfizer.history(start="1975-01-01", end="2009-12-01", interval="1mo")

abbott_laboratories = yf.Ticker("ABT")
abbott_monthly_data = abbott_laboratories.history(start="1975-01-01", end="2009-12-01", interval="1mo")

# ---- Market-cap weighted ETF simulation (rebalance yearly on Jan 1) ----
# Note: your provided dfs contain OHLCV but not market cap.
# So "market cap weights" are approximated by "price weights" (Close prices).
# If you add market cap series later, replace the weight computation accordingly.

def _prep_monthly_close(df: pd.DataFrame) -> pd.Series:
    s = df["Close"].copy()
    s.index = pd.to_datetime(s.index)
    s = s.sort_index()
    return s.rename(s.name)

jj_close = _prep_monthly_close(jj_monthly_data)
pfe_close = _prep_monthly_close(pfizer_monthly_data)
abbv_close = _prep_monthly_close(abbott_monthly_data)

prices = pd.concat(
    [jj_close, pfe_close, abbv_close],
    axis=1
)
prices.columns = ["JNJ", "PFE", "ABBV"]

# Keep only months where we have all three closes
prices = prices.dropna(how="any")

start_value = 100.0
initial_date = prices.index.min()
final_date = prices.index.max()

# Build list of rebalance dates: first available month observation on/after Jan 1 of each year
years = sorted(prices.index.year.unique())
rebalance_dates = []
for y in years:
    jan1 = pd.Timestamp(f"{y}-01-01")
    candidates = prices.index[prices.index >= jan1]
    if len(candidates) > 0:
        rebalance_dates.append(candidates[0])

# Remove duplicates and ensure within range
rebalance_dates = sorted(set(rebalance_dates))
rebalance_dates = [d for d in rebalance_dates if d >= initial_date and d <= final_date]

# ETF simulation state
shares = pd.Series(0.0, index=prices.columns)
current_value = start_value
etf_values = pd.Series(index=prices.index, dtype=float)

# Helper: compute "market-cap-like" weights (price weights)
def price_weights_at(date: pd.Timestamp) -> pd.Series:
    # We rebalance at the exact monthly timestamp in rebalance_dates
    row = prices.loc[date]
    w = row / row.sum()
    return w

# Run
for i, rd in enumerate(rebalance_dates):
    # Determine the segment end (next rebalance date, exclusive)
    next_rd = rebalance_dates[i + 1] if i + 1 < len(rebalance_dates) else None
    segment_mask = prices.index >= rd
    if next_rd is not None:
        segment_mask &= prices.index < next_rd

    segment_index = prices.index[segment_mask]
    if len(segment_index) == 0:
        continue

    # Rebalance at rd
    w = price_weights_at(rd)
    alloc = current_value * w
    px = prices.loc[rd]
    shares = alloc / px

    # Mark to market through the segment
    seg_prices = prices.loc[segment_index]
    etf_values.loc[segment_index] = (seg_prices * shares).sum(axis=1)

    # Update current_value at end of segment
    current_value = etf_values.loc[segment_index].iloc[-1]

# Basic sanity: fill any gaps at beginning (shouldn't be needed if start aligns)
etf_values = etf_values.dropna()

print(f"Simulated ETF value from {etf_values.index.min().date()} to {etf_values.index.max().date()}")
print(f"Starting capital: {start_value}")
print(f"Ending value: {etf_values.iloc[-1]:.4f}")

# Per-year weights display
rebalance_weights = []
for rd in rebalance_dates:
    w = price_weights_at(rd)
    rebalance_weights.append({"RebalanceDate": rd.date(), **w.to_dict()})
rebalance_weights_df = pd.DataFrame(rebalance_weights)
print("\nRebalance weights (price-weighted proxy for market cap):")
print(rebalance_weights_df)

# Plot ETF value
plt.style.use("seaborn-v0_8-darkgrid")
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(etf_values.index, etf_values.values, label="Market-cap weighted ETF (rebalance Jan 1)")
ax.set_title("Simulated Market-Cap Weighted ETF (Annual Jan 1 Rebalance)")
ax.set_ylabel("ETF Value ($)")
ax.set_xlabel("Date")
ax.legend()
plt.tight_layout()
plt.show()
