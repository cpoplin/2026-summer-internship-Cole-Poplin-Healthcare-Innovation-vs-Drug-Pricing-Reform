import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
BG_COLOR = '#0d1b2a'

Schering_Plough = yf.Ticker("NVDA")
sp_monthly_data = Schering_Plough.history(start="1975-01-01", end="2009-12-01", interval="1mo")

print(sp_monthly_data.head())