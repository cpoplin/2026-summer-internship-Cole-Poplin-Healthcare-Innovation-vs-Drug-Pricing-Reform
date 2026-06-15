import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

johnson_johnson = yf.Ticker("JNJ")
jj_monthly_data = johnson_johnson.history(start="1975-01-01", end="2009-12-01", interval="1mo")

pfizer = yf.Ticker("PFE")
pfizer_monthly_data = pfizer.history(start="1975-01-01", end="2009-12-01", interval="1mo")

abbott_laboratories = yf.Ticker("ABT")
abbott_monthly_data = abbott_laboratories.history(start="1975-01-01", end="2009-12-01", interval="1mo")


#print(jj_monthly_data.head())
#make all three lines on the same plot
fig, ax= plt.subplots(1, 1, sharex=True)

ax.plot(jj_monthly_data.index, jj_monthly_data["Close"], color='blue', label="Johnson & Johnson")
ax.plot(pfizer_monthly_data.index, pfizer_monthly_data["Close"], color='red', label="Pfizer")
ax.plot(abbott_monthly_data.index, abbott_monthly_data["Close"], color = 'green', label="Abbott Laboratories")

ax.set_title("Johnson & Johnson")
ax.set_title("Pfizer")
ax.set_title("Abbott Laboratories")

fig.autofmt_xdate()

plt.show()
