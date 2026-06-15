import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf


#pull data on pharma etf PPH (VanEck Pharma ETF), 25 of the largest global pharma companies
pharma_etf = yf.Ticker("PPH")
weekly_data = pharma_etf.history(start="1975-01-01", interval="1wk")

#trying to figure out how to highlight important parts (legislation)
pharma_regulatory_dates = pd.to_datetime(
    [
        "2002-05-21",
        "2007-04-18",
        "2012-04-25",
        "2015-05-21",
        "2017-06-07",
        "2022-06-07", # PDUFA 7
    ]
)


plt.rcParams["font.family"] = "sans-serif"
plt.rcParams[
    "font.sans-serif"
] = "Helvetica, Arial, DejaVu Sans"  # Fallbacks for clean text
plt.rcParams["axes.unicode_minus"] = False

fig, ax = plt.subplots()
ax.plot(weekly_data.index, weekly_data["Close"])
ax.set_xlabel("Date")
ax.set_ylabel("Price")


for date in pharma_regulatory_dates:
    # Calculate the Monday (start of week) and Sunday (end of week)
    # dayofweek: Monday=0, Tuesday=1 ... Sunday=6
    start_of_week = date - pd.Timedelta(days=date.dayofweek)
    end_of_week = start_of_week + pd.Timedelta(days=6)

    # Highlight the full 7-day window on the plot
    # Using a soft red/crimson with a low alpha so it stays transparent
    ax.axvspan(start_of_week, end_of_week, color="#dc143c", alpha=0.3)

COLOR_SMALL = "#4A7BB0"  # Soft steel blue
COLOR_BIOLOGIC = "#D97D3A"  # Muted copper orange
COLOR_TEXT = "#2C3E50"  # Deep slate instead of pitch black for softer text
COLOR_GRID = "#EAECEE"
ax.grid(True, axis="y", linestyle="--", linewidth=0.7, color=COLOR_GRID, zorder=0)
ax.set_axisbelow(True)  # Ensures grid lines sit behind your data lines

# Remove the top and right borders (spines) completely
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)

# Lighten the bottom and left borders so they don't overpower the data
for spine in ["left", "bottom"]:
    ax.spines[spine].set_color("#BDC3C7")
    ax.spines[spine].set_linewidth(0.8)

# 7. Labels and Titles (Hierarchy is key)
ax.set_title(
    "Capital Allocation Trends: Pharmaceutical Sector",
    fontsize=16,
    fontweight="bold",
    pad=20,
    color=COLOR_TEXT,
    loc="left",  # Left-aligned titles look cleaner and more modern
)

ax.set_ylabel("Normalized Capital Investment", fontsize=11, color=COLOR_TEXT, labelpad=10)
ax.set_xlabel("Timeline (2026)", fontsize=11, color=COLOR_TEXT, labelpad=10)

# 8. Clean Ticks and Axis Formatting
ax.tick_params(axis="both", which="major", labelsize=10, colors=COLOR_TEXT)

# 9. Clean Legend Positioning
# Frameon=False removes the box around the legend labels
ax.legend(
    loc="upper left",
    frameon=False,
    fontsize=10,
    labelcolor=COLOR_TEXT,
    handlelength=1.5,
)

# 10. Perfect Layout Execution
plt.tight_layout()



plt.show()
