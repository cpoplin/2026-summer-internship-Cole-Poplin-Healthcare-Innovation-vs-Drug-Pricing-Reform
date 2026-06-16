import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
"""My idea here is to make a plot of some of the more significant failed small molecule companies, to show the downward trajectory of that industry,
this, combined with the fact that the majority of the historically large small molecule companies are exitting that subsector, or in the very least
diversifying, should paint the picture for that subsector"""
# Schering_Plough = yf.Ticker("SGP")
# sp_monthly_data = Schering_Plough.history(start="1975-01-01", end="2009-12-01", interval="1mo")

# Forest_Laboratories  = yf.Ticker("FRX")
# fl_monthly_data = Forest_Laboratories.history(start="1975-01-01", end="2009-12-01", interval="1mo")

# Achaogen = yf.Ticker("AKAOQ")
# achaogen_monthly_data = Achaogen.history(start="1975-01-01", end="2009-12-01", interval="1mo")


# #print(jj_monthly_data.head())
# #make all three lines on the same plot
# fig, ax= plt.subplots(1, 1, sharex=True)

# ax.plot(sp_monthly_data.index, sp_monthly_data["Close"], color='blue', label="Johnson & Johnson")
# ax.plot(fl_monthly_data.index, fl_monthly_data["Close"], color='red', label="Pfizer")
# ax.plot(achaogen_monthly_data.index, achaogen_monthly_data["Close"], color = 'green', label="Abbott Laboratories")

# ax.set_title("Schering Plough")
# ax.set_title("Forest Laboratories")
# ax.set_title("Achaogen")

# fig.autofmt_xdate()

# plt.show()


import os
import pandas_datareader as pdr

# You must register for a free API key at tiingo.com
os.environ['TIINGO_API_KEY'] = 'YOUR_TIINGO_API_KEY'

tickers = ['AKAO', 'FRX', 'SGP']

# Fetch historical data (adjust dates as needed)
df = pdr.get_data_tiingo(tickers, start='1990-01-01', end='2020-01-01')

# Extract adjusted close prices into a clean Date vs. Ticker matrix
price_matrix = df['adjClose'].unstack(level='symbol')

print(price_matrix.dropna(how='all'))