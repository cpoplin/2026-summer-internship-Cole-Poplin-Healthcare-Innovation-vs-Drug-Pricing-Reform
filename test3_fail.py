import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

amgen = yf.Ticker("BMY")
amgen_monthly_data = amgen.history(start="1995-01-01", end="2026-01-01", interval="1mo")
amgen_yearly = amgen_monthly_data[amgen_monthly_data.index.month == 1].copy()
amgen_yearly["Percent_change"] = amgen_yearly["Close"].pct_change() * 100
# print(amgen_yearly.head())
amgen_clean = amgen_yearly.reset_index()
amgen_clean['Date'] = amgen_clean['Date'].dt.strftime('%Y')

regeneron = yf.Ticker("PFE")
rgn_monthly_data = regeneron.history(start="1995-01-01", end='2026-01-01', interval="1mo")
rgn_yearly = rgn_monthly_data[rgn_monthly_data.index.month == 1].copy()
rgn_yearly["Percent_change"] = rgn_yearly["Close"].pct_change() * 100
rgn_clean = rgn_yearly.reset_index()
rgn_clean['Date'] = rgn_clean['Date'].dt.strftime('%Y')


# ax = amgen_yearly.plot.bar(x="D y="Percent_change", color = 'blue', label="Bristol-Myers Squibb")


# 2. Plot using standard string column names for x and y
ax = amgen_clean.plot.bar(x='Date', y='Percent_change', color='blue', label="Bristol-Myers Squibb")
ax = rgn_clean.plot.bar(x='Date', y='Percent_change', color='red', label="Pfizer")
plt.show()