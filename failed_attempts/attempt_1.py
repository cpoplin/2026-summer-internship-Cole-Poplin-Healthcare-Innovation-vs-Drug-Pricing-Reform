import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import pharma_profits_data
BG_COLOR = '#0d1b2a'

df = pd.DataFrame(pharma_profits_data.pharma_profits_data)

#print("Operating profits in each distinction")
#print(df)

plt.style.use('dark_background')
fig, ax = plt.subplots()

ax.plot(df["Year"], df["Small Molecules ($B)"], label="Small Molecules ($B)")
ax.plot(df["Year"], df["Complex Biologics ($B)"], label="Complex Biologics ($B)")
fig.patch.set_facecolor(BG_COLOR)
ax.legend()

plt.show()
