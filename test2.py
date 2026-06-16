import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import os

CHART_DIR = os.path.join(os.path.dirname(__file__), "..", "charts")

NAVY   = "#0D1B2A"
GOLD   = "#C9A84C"
RED    = "#E05C5C"
GREEN  = "#2D9E6B"
SLATE  = "#8FA3B1"
WHITE  = "#F4F6F9"
TEAL   = "#1A7FA1"

navy_opaque = (0.05, 0.10, 0.25, 0.95)

Bristol_Myers_Squibb = yf.Ticker("BMY")
bms_monthly_data = Bristol_Myers_Squibb.history(start="1995-01-01", end="2025-12-01", interval="1mo")

pfizer = yf.Ticker("PFE")
pfizer_monthly_data = pfizer.history(start="1995-01-01", end='2025-12-01', interval="1mo")

abbott_laboratories = yf.Ticker("ABT")
abbott_monthly_data = abbott_laboratories.history(start="1995-01-01", end="2025-12-01", interval="1mo")


#print(jj_monthly_data.head())
#make all three lines on the same plot
# fig, ax= plt.subplots(1, 1, sharex=True)
fig =plt.figure(facecolor=NAVY)
plt.plot(bms_monthly_data.index, bms_monthly_data["Close"], color='blue', label="Bristol-Myers Squibb")
plt.plot(pfizer_monthly_data.index, pfizer_monthly_data["Close"], color='red', label="Pfizer")
plt.plot(abbott_monthly_data.index, abbott_monthly_data["Close"], color = 'green', label="Abbott Laboratories")

# ax.set_title("Johnson & Johnson")
# ax.set_title("Pfizer")
# ax.set_title("Abbott Laboratories")

#highlight the patent cliff created by the hatch wexman act
plt.axvspan(pd.to_datetime('2000-01-01'), pd.to_datetime('2005-12-31'), 
            color='red', alpha=0.2, label='The "Patent Cliff"')

#highlight the IRA
plt.axvspan(pd.to_datetime('2022-07-01'), pd.to_datetime('2025-01-01'), 
            color='red', alpha=0.2, label='The Inflation Reduction Act')

#visual config, most self explanatory
plt.grid(axis='y', linestyle='-', alpha=1.0, color=SLATE)
plt.gca().set_axisbelow(True) # Ensures grid lines sit behind your data lines
plt.legend(loc='upper left', framealpha=0.8, fontsize=9)
plt.title("Small Molecule Stocks", fontsize=14, fontweight='bold', pad=15, color='white')
plt.tick_params(axis='both', colors='white', labelsize=11) #changes the numbers on the axes
plt.gca().set_facecolor(navy_opaque) #changes the background color of the chart portion
fig.autofmt_xdate()


plt.tight_layout()
plt.savefig('my_pharma_plot.png', dpi=150, bbox_inches="tight")
plt.show()



# #I assume I want something that shows percentage change

# # ---- Percentage change per year (Jan 1 -> Jan 1) ----
# # Build yearly series using the first available monthly close on/after Jan 1 for each year,
# # then compute YoY % change between consecutive years.

# def _yearly_jan_close(monthly_df: pd.DataFrame) -> pd.Series:
#     s = monthly_df["Close"].copy()
#     s.index = pd.to_datetime(s.index)
#     s = s.sort_index()

#     yearly = {}
#     for y in sorted(s.index.year.unique()):
#         jan1 = pd.Timestamp(f"{y}-01-01")
#         candidates = s.index[s.index >= jan1]
#         if len(candidates) == 0:
#             continue
#         first_on_or_after = candidates[0]
#         yearly[pd.Timestamp(f"{y}-01-01")] = s.loc[first_on_or_after]

#     return pd.Series(yearly).sort_index().rename(s.name)

# jj_yearly = _yearly_jan_close(jj_monthly_data)
# pfe_yearly = _yearly_jan_close(pfizer_monthly_data)
# abbott_yearly = _yearly_jan_close(abbott_monthly_data)

# yearly_prices = pd.concat(
#     [jj_yearly.rename("JNJ"), pfe_yearly.rename("PFE"), abbott_yearly.rename("ABT")],
#     axis=1,
# ).dropna(how="any")

# pct_change_per_year = yearly_prices.pct_change(periods=1) * 100

# print("Yearly (Jan 1 -> Jan 1) % change per year:")
# print(pct_change_per_year)

# # Optional plot
# fig2, ax2 = plt.subplots(1, 1, sharex=True)
# ax2.plot(pct_change_per_year.index, pct_change_per_year["JNJ"], color="blue", label="Johnson & Johnson")
# ax2.plot(pct_change_per_year.index, pct_change_per_year["PFE"], color="red", label="Pfizer")
# ax2.plot(pct_change_per_year.index, pct_change_per_year["ABT"], color="green", label="Abbott Laboratories")
# ax2.axhline(0, color="black", linewidth=1)
# ax2.set_title("Yearly % Change (Jan 1 -> Jan 1)")
# ax2.set_ylabel("% change vs prior Jan 1")
# ax2.set_xlabel("Year")
# ax2.legend()
# fig2.autofmt_xdate()

# plt.show()



