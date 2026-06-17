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
# def create_bar_graph_from_df(df):
    


#     #highlight the patent cliff created by the hatch wexman act
#     plt.axvspan(pd.to_datetime('2000-01-01'), pd.to_datetime('2005-12-31'), 
#                 color='red', alpha=0.2, label='The "Patent Cliff"')

#     #highlight the IRA
#     plt.axvspan(pd.to_datetime('2022-07-01'), pd.to_datetime('2025-01-01'), 
                # color='red', alpha=0.2, label='The Inflation Reduction Act')
def small_molecule_graph():
    bms = yf.Ticker("BMY")
    bms_monthly_data = bms.history(start="1995-01-01", end="2026-01-01", interval="1mo")

    pfizer = yf.Ticker("PFE")
    pfizer_monthly_data = pfizer.history(start="1995-01-01", end='2026-01-01', interval="1mo")

    abbvie = yf.Ticker("ABBV")
    abbvie_monthly_data = abbvie.history(start="1995-01-01", end="2026-01-01", interval="1mo")


    #print(jj_monthly_data.head())
    #make all three lines on the same plot
    # fig, ax= plt.subplots(1, 1, sharex=True)
    fig =plt.figure(facecolor=NAVY)
    plt.plot(bms_monthly_data.index, bms_monthly_data["Close"], color='blue', label="Bristol-Myers Squibb")
    plt.plot(pfizer_monthly_data.index, pfizer_monthly_data["Close"], color='red', label="Pfizer")
    plt.plot(abbvie_monthly_data.index, abbvie_monthly_data["Close"], color = 'green', label="Abbott Laboratories")

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
    plt.savefig('charts/small_molecules.png', dpi=150, bbox_inches="tight")
    #plt.show()


def percent_change_graph():
    # Load data for Bristol-Myers Squibb (BMY)
    pfizer = yf.Ticker("PFE")
    pfizer_monthly_data = pfizer.history(start="1995-01-01", end="2026-01-01", interval="1mo")
    pfizer_yearly = pfizer_monthly_data[pfizer_monthly_data.index.month == 1].copy()
    pfizer_yearly["Percent_change"] = pfizer_yearly["Close"].pct_change() * 100
    pfizer_clean = pfizer_yearly.reset_index()
    pfizer_clean['Date'] = pfizer_clean['Date'].dt.strftime('%Y')

    # Load data for Novo Nordisk (NVO)
    novo_nordisk = yf.Ticker("NVO")
    nn_monthly_data = novo_nordisk.history(start="1995-01-01", end="2026-01-01", interval="1mo")
    nn_yearly = nn_monthly_data[nn_monthly_data.index.month == 1].copy()
    nn_yearly["Percent_change"] = nn_yearly["Close"].pct_change() * 100
    nn_clean = nn_yearly.reset_index()
    nn_clean['Date'] = nn_clean['Date'].dt.strftime('%Y')

    # Create figure and 2 side-by-side subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), facecolor=NAVY)
    
    # --- Plot 1: Pfizer ---
    pfizer_clean.plot.bar(x='Date', y='Percent_change', color='blue', label="Pfizer", ax=ax1)
    #print(pfizer_clean.tail(10))
    # Visual config for subplot 1
    ax1.grid(axis='y', linestyle='-', alpha=1.0, color=SLATE)
    ax1.set_axisbelow(True)
    ax1.legend(loc='upper left', framealpha=0.8, fontsize=9)
    ax1.set_title("Pfizer Percent Change", fontsize=10, fontweight='bold', pad=15, color='white')
    ax1.tick_params(axis='both', colors='white', labelsize=11)
    ax1.set_xticks(range(1, len(pfizer_clean), 4))
    ax1.set_xticklabels(pfizer_clean['Date'].iloc[1::4], rotation=0)
    ax1.set_facecolor(navy_opaque)
    ax1.set_xlabel("Date", color='white', fontsize=11)
    ax1.set_ylabel("Percent Change (%)", color='white', fontsize=11)

    # Highlights for subplot 1
    idx_2000_1 = pfizer_clean[pfizer_clean['Date'] == '2000'].index[0]
    idx_2005_1 = pfizer_clean[pfizer_clean['Date'] == '2005'].index[0]
    ax1.axvspan(idx_2000_1 + 0.5, idx_2005_1 + 1.5, color='red', alpha=0.2, label='The "Patent Cliff"')

    idx_2022_1 = pfizer_clean[pfizer_clean['Date'] == '2022'].index[0]
    idx_2025_1 = pfizer_clean[pfizer_clean['Date'] == '2025'].index[0]
    ax1.axvspan(idx_2022_1 + 0.5, idx_2025_1 + 1.5, color='red', alpha=0.2, label='The Inflation Reduction Act')


    # --- Plot 2: Novo Nordisk ---
    nn_clean.plot.bar(x='Date', y='Percent_change', color='green', label="Novo Nordisk", ax=ax2)

    # Visual config for subplot 2
    ax2.grid(axis='y', linestyle='-', alpha=1.0, color=SLATE)
    ax2.set_axisbelow(True)
    ax2.legend(loc='upper left', framealpha=0.8, fontsize=9)
    ax2.set_title("Novo Nordisk Percent Change", fontsize=10, fontweight='bold', pad=15, color='white')
    ax2.tick_params(axis='both', colors='white', labelsize=11)
    ax2.set_xticks(range(1, len(nn_clean), 4))
    ax2.set_xticklabels(nn_clean['Date'].iloc[1::4], rotation=0)
    ax2.set_facecolor(navy_opaque)
    ax2.set_xlabel("Date", color='white', fontsize=11)
    ax2.set_ylabel("Percent Change (%)", color='white', fontsize=11)

    # Highlights for subplot 2
    idx_2000_2 = nn_clean[nn_clean['Date'] == '2000'].index[0]
    idx_2005_2 = nn_clean[nn_clean['Date'] == '2005'].index[0]
    ax2.axvspan(idx_2000_2 - 0.5, idx_2005_2 + 0.5, color='red', alpha=0.2, label='The "Patent Cliff"')

    idx_2022_2 = nn_clean[nn_clean['Date'] == '2022'].index[0]
    idx_2025_2 = nn_clean[nn_clean['Date'] == '2025'].index[0]
    ax2.axvspan(idx_2022_2 - 0.5, idx_2025_2 + 0.5, color='red', alpha=0.2, label='The Inflation Reduction Act')
    fig.suptitle("Percent Change Comparison", fontsize=14, fontweight='bold', color='white')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig('charts/percent_change_bar.png', dpi=150, bbox_inches="tight")
    #plt.show()

def complex_biologics_graph():
    amgen = yf.Ticker("AMGN")
    amgen_monthly_data = amgen.history(start="1995-01-01", end="2026-01-01", interval="1mo")

    regeneron = yf.Ticker("REGN")
    rgn_monthly_data = regeneron.history(start="1995-01-01", end='2026-01-01', interval="1mo")

    novo_nordisk = yf.Ticker("NVO")
    nn_monthly_data = novo_nordisk.history(start="1995-01-01", end="2026-01-01", interval="1mo")


    #print(jj_monthly_data.head())
    #make all three lines on the same plot
    # fig, ax= plt.subplots(1, 1, sharex=True)
    fig =plt.figure(facecolor=NAVY)
    plt.plot(amgen_monthly_data.index, amgen_monthly_data["Close"], color='blue', label="Amgen")
    plt.plot(rgn_monthly_data.index, rgn_monthly_data["Close"], color='red', label="Regeneron")
    plt.plot(nn_monthly_data.index, nn_monthly_data["Close"], color = 'green', label="Novo Nordisk")

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
    plt.title("Complex Biologic Stocks", fontsize=14, fontweight='bold', pad=15, color='white')
    plt.tick_params(axis='both', colors='white', labelsize=11) #changes the numbers on the axes
    plt.gca().set_facecolor(navy_opaque) #changes the background color of the chart portion
    fig.autofmt_xdate()


    plt.tight_layout()
    plt.savefig('charts/complex_biologics.png', dpi=150, bbox_inches="tight")
    plt.show() 

def main():
    small_molecule_graph()
    percent_change_graph()
    complex_biologics_graph()

main()

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
# pfe_yearly = _yearly_jan_close(rgn_monthly_data)
# abbott_yearly = _yearly_jan_close(nn_monthly_data)

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



