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


def get_subsector_pct_change(tickers):
    pct_changes = {}
    for ticker in tickers:
        t = yf.Ticker(ticker)
        df = t.history(start="1995-01-01", end="2026-01-01", interval="1mo")
        if not df.empty:
            df.index = df.index.tz_localize(None)
            jan_data = df[df.index.month == 1].copy()
            jan_data["Percent_change"] = jan_data["Close"].pct_change() * 100
            jan_data.index = jan_data.index.strftime('%Y')
            pct_changes[ticker] = jan_data["Percent_change"]
            
    pct_df = pd.DataFrame(pct_changes)
    avg_change = pct_df.mean(axis=1)
    
    clean_df = avg_change.reset_index()
    clean_df.columns = ['Date', 'Percent_change']
    clean_df = clean_df.dropna(subset=['Percent_change']).reset_index(drop=True)
    return clean_df

def percent_change_graph():
    # Load subsector baskets
    small_molecule_tickers = ["BMY", "PFE", "ABBV"]
    complex_biologics_tickers = ["AMGN", "REGN", "NVO"]
    
    sm_clean = get_subsector_pct_change(small_molecule_tickers)
    cb_clean = get_subsector_pct_change(complex_biologics_tickers)

    # Create figure and 2 side-by-side subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), facecolor=NAVY)
    
    # Helper to find year index
    def get_year_idx(df, year_str):
        indices = df[df['Date'] == year_str].index
        if len(indices) > 0:
            return indices[0]
        return None

    # --- Plot 1: Small Molecules ---
    sm_clean.plot.bar(x='Date', y='Percent_change', color=TEAL, label="Small Molecules (Avg)", ax=ax1)
    # Visual config for subplot 1
    ax1.grid(axis='y', linestyle='-', alpha=1.0, color=SLATE)
    ax1.set_axisbelow(True)
    ax1.set_title("Small Molecules Avg Percent Change", fontsize=10, fontweight='bold', pad=15, color='white')
    ax1.tick_params(axis='both', colors='white', labelsize=11)
    ax1.set_xticks(range(1, len(sm_clean), 4))
    ax1.set_xticklabels(sm_clean['Date'].iloc[1::4], rotation=0)
    ax1.set_facecolor(navy_opaque)
    ax1.set_xlabel("Date", color='white', fontsize=11)
    ax1.set_ylabel("Percent Change (%)", color='white', fontsize=11)

    # Highlights for subplot 1
    idx_2000_1 = get_year_idx(sm_clean, '2000')
    idx_2005_1 = get_year_idx(sm_clean, '2005')
    if idx_2000_1 is not None and idx_2005_1 is not None:
        ax1.axvspan(idx_2000_1 + 0.5, idx_2005_1 + 1.5, color='red', alpha=0.2, label='The "Patent Cliff"')

    idx_2022_1 = get_year_idx(sm_clean, '2022')
    idx_2025_1 = get_year_idx(sm_clean, '2025')
    if idx_2022_1 is not None and idx_2025_1 is not None:
        ax1.axvspan(idx_2022_1 + 0.5, idx_2025_1 + 1.5, color='red', alpha=0.2, label='The Inflation Reduction Act')
    ax1.legend(loc='upper left', framealpha=0.8, fontsize=9)

    # --- Plot 2: Complex Biologics ---
    cb_clean.plot.bar(x='Date', y='Percent_change', color=GOLD, label="Complex Biologics (Avg)", ax=ax2)

    # Visual config for subplot 2
    ax2.grid(axis='y', linestyle='-', alpha=1.0, color=SLATE)
    ax2.set_axisbelow(True)
    ax2.set_title("Complex Biologics Avg Percent Change", fontsize=10, fontweight='bold', pad=15, color='white')
    ax2.tick_params(axis='both', colors='white', labelsize=11)
    ax2.set_xticks(range(1, len(cb_clean), 4))
    ax2.set_xticklabels(cb_clean['Date'].iloc[1::4], rotation=0)
    ax2.set_facecolor(navy_opaque)
    ax2.set_xlabel("Date", color='white', fontsize=11)
    ax2.set_ylabel("Percent Change (%)", color='white', fontsize=11)

    # Highlights for subplot 2
    idx_2000_2 = get_year_idx(cb_clean, '2000')
    idx_2005_2 = get_year_idx(cb_clean, '2005')
    if idx_2000_2 is not None and idx_2005_2 is not None:
        ax2.axvspan(idx_2000_2 + 0.5, idx_2005_2 + 1.5, color='red', alpha=0.2, label='The "Patent Cliff"')

    idx_2022_2 = get_year_idx(cb_clean, '2022')
    idx_2025_2 = get_year_idx(cb_clean, '2025')
    if idx_2022_2 is not None and idx_2025_2 is not None:
        ax2.axvspan(idx_2022_2 + 0.5, idx_2025_2 + 1.5, color='red', alpha=0.2, label='The Inflation Reduction Act')
    ax2.legend(loc='upper left', framealpha=0.8, fontsize=9)

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
    # plt.show() 

def create_correlation_graph():
    tickers = ["BMY", "PFE", "ABBV", "AMGN", "REGN", "NVO"]
    
    data = {}
    for ticker in tickers:
        t = yf.Ticker(ticker)
        df = t.history(start="2000-01-01", end="2026-01-01", interval="1mo")
        if not df.empty:
            data[ticker] = df["Close"]
            
    price_df = pd.DataFrame(data)
    if price_df.empty:
        print("Error: No price data downloaded.")
        return
        
    price_df.index = price_df.index.tz_localize(None)
    
    # Period 1: Patent Cliff (2000-01-01 to 2005-12-31)
    p1_df = price_df.loc["2000-01-01":"2005-12-31"].copy()
    p1_df.dropna(how='all', axis=1, inplace=True)
    
    p1_norm = p1_df.copy()
    for col in p1_norm.columns:
        first_val = p1_norm[col].dropna()
        if not first_val.empty:
            p1_norm[col] = (p1_norm[col] / first_val.iloc[0]) * 100
            
    p1_small = [t for t in ["BMY", "PFE", "ABBV"] if t in p1_norm.columns]
    p1_complex = [t for t in ["AMGN", "REGN", "NVO"] if t in p1_norm.columns]
    
    p1_small_avg = p1_norm[p1_small].mean(axis=1)
    p1_complex_avg = p1_norm[p1_complex].mean(axis=1)
    p1_corr = p1_small_avg.corr(p1_complex_avg)
    
    # Period 2: Inflation Reduction Act (2022-07-01 to 2025-01-01)
    p2_df = price_df.loc["2022-07-01":"2025-01-01"].copy()
    p2_df.dropna(how='all', axis=1, inplace=True)
    
    p2_norm = p2_df.copy()
    for col in p2_norm.columns:
        first_val = p2_norm[col].dropna()
        if not first_val.empty:
            p2_norm[col] = (p2_norm[col] / first_val.iloc[0]) * 100
            
    p2_small = [t for t in ["BMY", "PFE", "ABBV"] if t in p2_norm.columns]
    p2_complex = [t for t in ["AMGN", "REGN", "NVO"] if t in p2_norm.columns]
    
    p2_small_avg = p2_norm[p2_small].mean(axis=1)
    p2_complex_avg = p2_norm[p2_complex].mean(axis=1)
    p2_corr = p2_small_avg.corr(p2_complex_avg)
    
    # Create the figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), facecolor=NAVY)
    
    # Plot Period 1
    ax1.plot(p1_small_avg.index, p1_small_avg, color=TEAL, linewidth=2, label="Small Molecules Avg")
    ax1.plot(p1_complex_avg.index, p1_complex_avg, color=GOLD, linewidth=2, label="Complex Biologics Avg")
    ax1.grid(axis='y', linestyle='-', alpha=1.0, color=SLATE)
    ax1.set_axisbelow(True)
    ax1.legend(loc='upper left', framealpha=0.8, fontsize=9)
    ax1.set_title(f"The 'Patent Cliff' (2000–2005)\nCorrelation: {p1_corr:+.2f}", fontsize=11, fontweight='bold', pad=15, color='white')
    ax1.tick_params(axis='both', colors='white', labelsize=10)
    ax1.set_facecolor(navy_opaque)
    ax1.set_xlabel("Date", color='white', fontsize=11)
    ax1.set_ylabel("Normalized Price Index (Start = 100)", color='white', fontsize=11)
    
    # Plot Period 2
    ax2.plot(p2_small_avg.index, p2_small_avg, color=TEAL, linewidth=2, label="Small Molecules Avg")
    ax2.plot(p2_complex_avg.index, p2_complex_avg, color=GOLD, linewidth=2, label="Complex Biologics Avg")
    ax2.grid(axis='y', linestyle='-', alpha=1.0, color=SLATE)
    ax2.set_axisbelow(True)
    ax2.legend(loc='upper left', framealpha=0.8, fontsize=9)
    ax2.set_title(f"The Inflation Reduction Act (2022–2025)\nCorrelation: {p2_corr:+.2f}", fontsize=11, fontweight='bold', pad=15, color='white')
    ax2.tick_params(axis='both', colors='white', labelsize=10)
    ax2.set_facecolor(navy_opaque)
    ax2.set_xlabel("Date", color='white', fontsize=11)
    ax2.set_ylabel("Normalized Price Index (Start = 100)", color='white', fontsize=11)
    
    fig.suptitle("Subsector Correlation & Average Movement During Turmoil", fontsize=14, fontweight='bold', color='white')
    fig.autofmt_xdate()
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig('charts/correlation_graph.png', dpi=150, bbox_inches="tight")
    plt.close(fig)

def main():
    small_molecule_graph()
    percent_change_graph()
    complex_biologics_graph()
    create_correlation_graph()

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



