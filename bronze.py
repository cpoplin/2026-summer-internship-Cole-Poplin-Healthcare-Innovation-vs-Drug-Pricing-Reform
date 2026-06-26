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
def small_molecule_graph(data):
    bms_monthly_data = data["BMY"]
    pfizer_monthly_data = data["PFE"]
    abbvie_monthly_data = data["ABBV"]


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


def get_subsector_pct_change(tickers, data):
    pct_changes = {}
    for ticker in tickers:
        df = data.get(ticker)
        if df is not None and not df.empty:
            df_copy = df.copy()
            if df_copy.index.tz is not None:
                df_copy.index = df_copy.index.tz_localize(None)
            jan_data = df_copy[df_copy.index.month == 1].copy()
            jan_data["Percent_change"] = jan_data["Close"].pct_change() * 100
            jan_data.index = jan_data.index.strftime('%Y')
            pct_changes[ticker] = jan_data["Percent_change"]
            
    pct_df = pd.DataFrame(pct_changes)
    avg_change = pct_df.mean(axis=1)
    
    clean_df = avg_change.reset_index()
    clean_df.columns = ['Date', 'Percent_change']
    clean_df = clean_df.dropna(subset=['Percent_change']).reset_index(drop=True)
    return clean_df

def percent_change_graph(data):
    # Load subsector baskets
    small_molecule_tickers = ["BMY", "PFE", "ABBV"]
    complex_biologics_tickers = ["AMGN", "REGN", "NVO"]
    
    sm_clean = get_subsector_pct_change(small_molecule_tickers, data)
    cb_clean = get_subsector_pct_change(complex_biologics_tickers, data)

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

def complex_biologics_graph(data):
    amgen_monthly_data = data["AMGN"]
    rgn_monthly_data = data["REGN"]
    nn_monthly_data = data["NVO"]


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

def create_correlation_graph(data_dict):
    tickers = ["BMY", "PFE", "ABBV", "AMGN", "REGN", "NVO"]
    
    data = {}
    for ticker in tickers:
        df = data_dict.get(ticker)
        if df is not None and not df.empty:
            df_copy = df.copy()
            if df_copy.index.tz is not None:
                df_copy.index = df_copy.index.tz_localize(None)
            sliced_df = df_copy.loc["2000-01-01":"2026-01-01"]
            if not sliced_df.empty:
                data[ticker] = sliced_df["Close"]
            
    price_df = pd.DataFrame(data)
    if price_df.empty:
        print("Error: No price data downloaded.")
        return
        
    if price_df.index.tz is not None:
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
    p1_sm_perf = p1_small_avg.iloc[-1] - 100
    p1_cb_perf = p1_complex_avg.iloc[-1] - 100
    
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
    p2_sm_perf = p2_small_avg.iloc[-1] - 100
    p2_cb_perf = p2_complex_avg.iloc[-1] - 100
    
    # Create the figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), facecolor=NAVY)
    
    # Plot Period 1
    ax1.plot(p1_small_avg.index, p1_small_avg, color=TEAL, linewidth=2, label="Small Molecules Avg")
    ax1.plot(p1_complex_avg.index, p1_complex_avg, color=GOLD, linewidth=2, label="Complex Biologics Avg")
    ax1.grid(axis='y', linestyle='-', alpha=1.0, color=SLATE)
    ax1.set_axisbelow(True)
    ax1.legend(loc='upper left', framealpha=0.8, fontsize=9)
    ax1.set_title(f"The 'Patent Cliff' (2000–2005)\nSmall Molecules: {p1_sm_perf:+.1f}% | Complex Biologics: {p1_cb_perf:+.1f}%", fontsize=11, fontweight='bold', pad=15, color='white')
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
    ax2.set_title(f"The Inflation Reduction Act (2022–2025)\nSmall Molecules: {p2_sm_perf:+.1f}% | Complex Biologics: {p2_cb_perf:+.1f}%", fontsize=11, fontweight='bold', pad=15, color='white')
    ax2.tick_params(axis='both', colors='white', labelsize=10)
    ax2.set_facecolor(navy_opaque)
    ax2.set_xlabel("Date", color='white', fontsize=11)
    ax2.set_ylabel("Normalized Price Index (Start = 100)", color='white', fontsize=11)
    
    fig.suptitle("Subsector Comparison & Average Movement During Turmoil", fontsize=14, fontweight='bold', color='white')
    fig.autofmt_xdate()
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig('charts/correlation_graph.png', dpi=150, bbox_inches="tight")
    plt.close(fig)

def create_summary(data_dict):
    import matplotlib.patches as patches
    # Load subsector baskets
    small_molecule_tickers = ["BMY", "PFE", "ABBV"]
    complex_biologics_tickers = ["AMGN", "REGN", "NVO"]
    
    data = {}
    for ticker in small_molecule_tickers + complex_biologics_tickers:
        df = data_dict.get(ticker)
        if df is not None and not df.empty:
            df_copy = df.copy()
            if df_copy.index.tz is not None:
                df_copy.index = df_copy.index.tz_localize(None)
            data[ticker] = df_copy["Close"]
            
    price_df = pd.DataFrame(data)
    if price_df.empty:
        print("Error: No price data downloaded for summary.")
        return
        
    # --- Period 1: Patent Cliff (2000-01-01 to 2005-12-31) ---
    p1_df = price_df.loc["2000-01-01":"2005-12-31"].copy()
    p1_df.dropna(how='all', axis=1, inplace=True)
    p1_norm = p1_df.copy()
    for col in p1_norm.columns:
        first_val = p1_norm[col].dropna()
        if not first_val.empty:
            p1_norm[col] = (p1_norm[col] / first_val.iloc[0]) * 100
            
    p1_sm = [t for t in small_molecule_tickers if t in p1_norm.columns]
    p1_cb = [t for t in complex_biologics_tickers if t in p1_norm.columns]
    
    p1_sm_avg = p1_norm[p1_sm].mean(axis=1)
    p1_cb_avg = p1_norm[p1_cb].mean(axis=1)
    
    p1_sm_perf = p1_sm_avg.iloc[-1] - 100
    p1_cb_perf = p1_cb_avg.iloc[-1] - 100
    
    # --- Period 2: Inflation Reduction Act (2022-07-01 to 2025-01-01) ---
    p2_df = price_df.loc["2022-07-01":"2025-01-01"].copy()
    p2_df.dropna(how='all', axis=1, inplace=True)
    p2_norm = p2_df.copy()
    for col in p2_norm.columns:
        first_val = p2_norm[col].dropna()
        if not first_val.empty:
            p2_norm[col] = (p2_norm[col] / first_val.iloc[0]) * 100
            
    p2_sm = [t for t in small_molecule_tickers if t in p2_norm.columns]
    p2_cb = [t for t in complex_biologics_tickers if t in p2_norm.columns]
    
    p2_sm_avg = p2_norm[p2_sm].mean(axis=1)
    p2_cb_avg = p2_norm[p2_cb].mean(axis=1)
    
    p2_sm_perf = p2_sm_avg.iloc[-1] - 100
    p2_cb_perf = p2_cb_avg.iloc[-1] - 100
    
    # --- Overall Period (1995-01-01 to 2026-01-01) ---
    overall_norm = price_df.copy()
    for col in overall_norm.columns:
        first_val = overall_norm[col].dropna()
        if not first_val.empty:
            overall_norm[col] = (overall_norm[col] / first_val.iloc[0]) * 100
            
    sm_cols = [t for t in small_molecule_tickers if t in overall_norm.columns]
    cb_cols = [t for t in complex_biologics_tickers if t in overall_norm.columns]
    
    overall_sm_avg = overall_norm[sm_cols].mean(axis=1)
    overall_cb_avg = overall_norm[cb_cols].mean(axis=1)
    
    overall_sm_perf = overall_sm_avg.iloc[-1] - 100
    overall_cb_perf = overall_cb_avg.iloc[-1] - 100
    diff = overall_cb_perf - overall_sm_perf
    
    print(f"Summary Metrics Calculated:")
    print(f"  Patent Cliff (2000-2005): CB {p1_cb_perf:+.2f}%, SM {p1_sm_perf:+.2f}%")
    print(f"  IRA Turmoil (2022-2025): CB {p2_cb_perf:+.2f}%, SM {p2_sm_perf:+.2f}%")
    print(f"  Overall Gain (1995-2026): CB {overall_cb_perf:+.2f}%, SM {overall_sm_perf:+.2f}%")
    print(f"  Alpha Spread: {diff:+.2f}%")
    
    # --- Design Layout Configuration ---
    BG_BLUE = "#0A1128"       # Dark deep blue background
    CARD_BG = "#132237"       # Lighter navy for the content cards
    CARD_BORDER = "#1E2F5B"   # Border for cards
    ACCENT_AMBER = "#D48C46"  # Premium bronze/copper/amber (replaces old gold)
    TEXT_MUTED = "#8E9AAF"    # Muted slate/grey
    
    fig = plt.figure(figsize=(12, 6.5))
    fig.patch.set_facecolor(BG_BLUE)
    ax = fig.add_subplot(111)
    ax.set_facecolor(BG_BLUE)
    ax.axis("off")
    
    # Left-aligned dashboard header
    ax.text(0.05, 0.94, "C A S E   S T U D Y   V E R D I C T   •   B R O N Z E   T I E R", 
            transform=ax.transAxes, ha="left", va="top", fontsize=8.5, 
            fontweight="bold", color=ACCENT_AMBER)
            
    ax.text(0.05, 0.88, "Healthcare Innovation vs. Drug Pricing Reform", 
            transform=ax.transAxes, ha="left", va="top", 
            fontsize=16, color=WHITE, fontweight="bold")
            
    ax.text(0.05, 0.82, "Long-term performance analysis of Complex Biologics vs. Small Molecule subsectors", 
            transform=ax.transAxes, ha="left", va="top", 
            fontsize=10, color=TEXT_MUTED)
            
    # Horizontal Divider Line below header
    header_divider = plt.Line2D([0.05, 0.95], [0.77, 0.77], transform=ax.transAxes,
                                 color=CARD_BORDER, linewidth=1.0, alpha=0.8)
    ax.add_line(header_divider)
    
    # --- Left Column: Vertical Metric Cards ---
    card_w = 0.42
    card_h = 0.11
    # Positions: y_bottom for 4 cards
    y_positions = [0.60, 0.45, 0.30, 0.15]
    
    val_multiple = (100.0 + overall_cb_perf) / (100.0 + overall_sm_perf)
    
    stats_data = [
        {
            "val": f"+{overall_cb_perf:,.0f}%",
            "val_color": ACCENT_AMBER,
            "title": "Complex Biologics Gain",
            "subtitle": f"1995–2026 | vs +{overall_sm_perf:,.0f}% for Small Molecules"
        },
        {
            "val": f"{val_multiple:.1f}x",
            "val_color": ACCENT_AMBER,
            "title": "Healthcare Alpha Spread",
            "subtitle": f"Biologic stock value grew {val_multiple:.1f}x as compared to \nSmall Molecules"
        },
        {
            "val": f"{p1_cb_perf:+.1f}%",
            "val_color": GREEN,
            "title": "Patent Cliff (2000–2005)",
            "subtitle": f"Biologics gained vs {p1_sm_perf:+.1f}% for Small Molecules"
        },
        {
            "val": f"{p2_cb_perf:+.1f}%",
            "val_color": GREEN,
            "title": "IRA Turmoil (2022–2025)",
            "subtitle": f"Biologics gained vs {p2_sm_perf:+.1f}% for Small Molecules"
        }
    ]
    
    for y_bottom, card in zip(y_positions, stats_data):
        # Draw rounded card container
        card_rect = patches.FancyBboxPatch((0.05, y_bottom), card_w, card_h,
                                           transform=ax.transAxes,
                                           facecolor=CARD_BG, edgecolor=CARD_BORDER,
                                           linewidth=1.0, boxstyle="round,pad=0.0,rounding_size=0.015")
        ax.add_patch(card_rect)
        
        # Center the value on the left side of the card
        ax.text(0.115, y_bottom + 0.055, card["val"], transform=ax.transAxes,
                ha="center", va="center", fontsize=13.0,
                fontweight="bold", color=card["val_color"])
                
        # Draw vertical separator line inside the card
        sep_line = plt.Line2D([0.18, 0.18], [y_bottom + 0.02, y_bottom + 0.09],
                              transform=ax.transAxes, color=CARD_BORDER, linewidth=0.8)
        ax.add_line(sep_line)
        
        # Left-align the description labels on the right side of the card
        ax.text(0.20, y_bottom + 0.07, card["title"], transform=ax.transAxes,
                ha="left", va="center", fontsize=9.5,
                fontweight="bold", color=WHITE)
        ax.text(0.20, y_bottom + 0.035, card["subtitle"], transform=ax.transAxes,
                ha="left", va="center", fontsize=6.0,
                color=TEXT_MUTED)
                
    # --- Right Column: Verdict Summary Card ---
    verdict_rect = patches.FancyBboxPatch((0.52, 0.15), 0.43, 0.56,
                                         transform=ax.transAxes,
                                         facecolor=CARD_BG, edgecolor=CARD_BORDER,
                                         linewidth=1.0, boxstyle="round,pad=0.0,rounding_size=0.015")
    ax.add_patch(verdict_rect)
    
    # Verdict tag header
    ax.text(0.735, 0.66, "EVALUATION VERDICT", transform=ax.transAxes,
            ha="center", va="center", fontsize=8.5, fontweight="bold", color=TEXT_MUTED)
            
    # Badge background
    is_supported = overall_cb_perf > overall_sm_perf
    badge_bg = "#1E3A2F" if is_supported else "#3A1E1E"
    badge_fg = GREEN if is_supported else RED
    verdict_lbl = "✓  THESIS SUPPORTED" if is_supported else "✗  THESIS NOT SUPPORTED"
    
    badge_rect = patches.FancyBboxPatch((0.58, 0.58), 0.31, 0.055,
                                        transform=ax.transAxes,
                                        facecolor=badge_bg, edgecolor=badge_fg,
                                        linewidth=1.0, boxstyle="round,pad=0.0,rounding_size=0.01")
    ax.add_patch(badge_rect)
    
    ax.text(0.735, 0.607, verdict_lbl, transform=ax.transAxes,
            ha="center", va="center", fontsize=10, fontweight="bold", color=badge_fg)
            
    # Verdict divider line
    verdict_divider = plt.Line2D([0.55, 0.92], [0.54, 0.54], transform=ax.transAxes,
                                 color=CARD_BORDER, linewidth=0.8)
    ax.add_line(verdict_divider)
    
    # Narrative Header & Body
    ax.text(0.735, 0.505, "Executive Summary", transform=ax.transAxes,
            ha="center", va="center", fontsize=10.5, fontweight="bold", color=WHITE)
            
    conclusion = (
        f"Across the 1995–2026 sample, Complex Biologics (AMGN, REGN,\n"
        f"NVO) delivered an overwhelming +{overall_cb_perf:,.1f}% return,\n"
        f"outperforming Small Molecules (BMY, PFE, ABBV) by +{diff:,.1f}%.\n\n"
        f"Crucially, during periods of turmoil where small molecules crashed, \ncomplex biologics"
        f" remained unaffected or even reacted positively:\n"
        f"• Gained {p1_cb_perf:+.1f}% during the Patent Cliff (vs {p1_sm_perf:+.1f}% for SM)\n"
        f"• Gained {p2_cb_perf:+.1f}% during the IRA pressure (vs {p2_sm_perf:+.1f}% for SM)\n\n"
        f"The next generation of healthcare alpha structurally resides\n"
        f"in Complex Biologics."
    )
    ax.text(0.55, 0.46, conclusion, transform=ax.transAxes,
            ha="left", va="top", fontsize=7.5, color=WHITE,
            linespacing=1.3)
            
    # Footer
    ax.text(0.5, 0.06,
            "2026 Summer Internship  •  Healthcare Innovation vs Drug Pricing Reform  •  Bronze Tier",
            transform=ax.transAxes, ha="center", va="center",
            fontsize=8, fontweight="bold", color=TEXT_MUTED)
            
    plt.savefig('charts/verdict_summary.png', dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  Saved: charts/verdict_summary.png")

def medicare_negot_event():
    # Load subsector baskets
    small_molecule_tickers = ["BMY", "PFE", "ABBV"]
    complex_biologics_tickers = ["AMGN", "REGN", "NVO"]
    tickers = small_molecule_tickers + complex_biologics_tickers
    
    print("Downloading daily data for Medicare Negotiation Event...")
    df = yf.download(tickers, start="2023-08-01", end="2023-10-01", group_by='ticker', progress=False)

    close_data = {}
    for ticker in tickers:
        if ticker in df.columns.levels[0]:
            close_series = df[ticker]["Close"].copy()
            if close_series.index.tz is not None:
                close_series.index = close_series.index.tz_localize(None)
            close_data[ticker] = close_series

    df_prices = pd.DataFrame(close_data)

    # Event window: August 14, 2023 to September 22, 2023
    start_date = "2023-08-14"
    end_date = "2023-09-22"
    df_prices = df_prices.loc[start_date:end_date]

    # Normalize to Monday, Aug 28, 2023 (the day before the selection announcement)
    base_date = "2023-08-28"
    if base_date in df_prices.index:
        base_row = df_prices.loc[base_date]
    else:
        base_row = df_prices.loc[:"2023-08-28"].iloc[-1]
        base_date = base_row.name

    normalized = df_prices.copy()
    for col in normalized.columns:
        normalized[col] = (normalized[col] / base_row[col]) * 100

    normalized["Small Molecules Avg"] = normalized[small_molecule_tickers].mean(axis=1)
    normalized["Complex Biologics Avg"] = normalized[complex_biologics_tickers].mean(axis=1)

    # Calculate post-event daily volatility (standard deviation of daily returns) from Aug 29 to Sep 22
    daily_returns = df_prices.pct_change()
    post_event_returns = daily_returns.loc["2023-08-29":end_date]

    sm_vol = post_event_returns[small_molecule_tickers].mean(axis=1).std() * 100
    cb_vol = post_event_returns[complex_biologics_tickers].mean(axis=1).std() * 100

    # Plotting using consistent visual styling
    fig, ax = plt.subplots(figsize=(12, 6.5), facecolor=NAVY)
    ax.set_facecolor(navy_opaque)

    # Plot individual stocks as thin dashed lines
    # for t in small_molecule_tickers:
    #     ax.plot(normalized.index, normalized[t], color=TEAL, alpha=0.3, linestyle="--", label=f"{t} (Indiv)")
    # for t in complex_biologics_tickers:
    #     ax.plot(normalized.index, normalized[t], color=GOLD, alpha=0.3, linestyle="--", label=f"{t} (Indiv)")

    # Plot basket averages
    ax.plot(normalized.index, normalized["Small Molecules Avg"], color=TEAL, linewidth=3, label="Small Molecules Avg")
    ax.plot(normalized.index, normalized["Complex Biologics Avg"], color=GOLD, linewidth=3, label="Complex Biologics Avg")

    # Draw vertical line for the announcement
    ax.axvline(pd.to_datetime("2023-08-29"), color=RED, linestyle="-", linewidth=2.0, label="CMS Price Negotiation List (Aug 29)")
    ax.text(pd.to_datetime("2023-08-29"), 105.5, "Announcement Date\nAug 29, 2023", color=RED, fontsize=9.5, fontweight="bold", ha="center")

    # Visual customizations
    ax.grid(axis='both', linestyle='-', alpha=0.5, color=SLATE)
    ax.set_axisbelow(True)
    ax.tick_params(axis='both', colors='white', labelsize=10)
    ax.set_xlabel("Date", color='white', fontsize=11, labelpad=10)
    ax.set_ylabel("Price Index (Aug 28 = 100)", color='white', fontsize=11, labelpad=10)

    title_text = "Event Study: Medicare Drug Price Negotiation Announcement (Aug–Sept 2023)\n" \
                 f"Post-Announcement Volatility (Daily SD of Basket): Small Molecules {sm_vol:.2f}% vs. Complex Biologics {cb_vol:.2f}%"
    ax.set_title(title_text, fontsize=12, fontweight='bold', pad=15, color='white')

    # De-duplicate legend
    handles, labels = ax.get_legend_handles_labels()
    unique_labels = {}
    for h, l in zip(handles, labels):
        if "Indiv" not in l:
            unique_labels[l] = h
    ax.legend(unique_labels.values(), unique_labels.keys(), loc='lower left', framealpha=0.8, fontsize=9)

    fig.autofmt_xdate()
    plt.tight_layout()
    
    os.makedirs('charts', exist_ok=True)
    plt.savefig('charts/medicare_negot_event.png', dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  Saved: charts/medicare_negot_event.png")

def patent_cliff_event():
    # Load subsector baskets for 2000
    # ABBV is replaced with LLY (Eli Lilly) since ABBV did not exist in 2000
    small_molecule_tickers = ["LLY", "BMY", "PFE"]
    complex_biologics_tickers = ["AMGN", "REGN", "NVO"]
    tickers = small_molecule_tickers + complex_biologics_tickers
    
    print("Downloading daily data for Prozac Patent Cliff Event...")
    df = yf.download(tickers, start="2000-07-01", end="2000-10-01", group_by='ticker', progress=False)

    close_data = {}
    for ticker in tickers:
        if ticker in df.columns.levels[0]:
            close_series = df[ticker]["Close"].copy()
            if close_series.index.tz is not None:
                close_series.index = close_series.index.tz_localize(None)
            close_data[ticker] = close_series

    df_prices = pd.DataFrame(close_data)

    # Event window: July 24, 2000 to September 15, 2000
    start_date = "2000-07-24"
    end_date = "2000-09-15"
    df_prices = df_prices.loc[start_date:end_date]

    # Normalize to Tuesday, Aug 8, 2000 (the day before the court ruling)
    base_date = "2000-08-08"
    if base_date in df_prices.index:
        base_row = df_prices.loc[base_date]
    else:
        base_row = df_prices.loc[:"2000-08-08"].iloc[-1]
        base_date = base_row.name

    normalized = df_prices.copy()
    for col in normalized.columns:
        normalized[col] = (normalized[col] / base_row[col]) * 100

    normalized["Small Molecules Avg"] = normalized[small_molecule_tickers].mean(axis=1)
    normalized["Complex Biologics Avg"] = normalized[complex_biologics_tickers].mean(axis=1)

    # Calculate post-event daily volatility (standard deviation of daily returns) from Aug 9 to Sep 15
    daily_returns = df_prices.pct_change()
    post_event_returns = daily_returns.loc["2000-08-09":end_date]

    sm_vol = post_event_returns[small_molecule_tickers].mean(axis=1).std() * 100
    cb_vol = post_event_returns[complex_biologics_tickers].mean(axis=1).std() * 100

    # Plotting using consistent visual styling
    fig, ax = plt.subplots(figsize=(12, 6.5), facecolor=NAVY)
    ax.set_facecolor(navy_opaque)

    # Plot individual stocks as thin dashed lines
    # for t in small_molecule_tickers:
    #     ax.plot(normalized.index, normalized[t], color=TEAL, alpha=0.3, linestyle="--", label=f"{t} (Indiv)")
    # for t in complex_biologics_tickers:
    #     ax.plot(normalized.index, normalized[t], color=GOLD, alpha=0.3, linestyle="--", label=f"{t} (Indiv)")

    # Plot basket averages
    ax.plot(normalized.index, normalized["Small Molecules Avg"], color=TEAL, linewidth=3, label="Small Molecules Avg")
    ax.plot(normalized.index, normalized["Complex Biologics Avg"], color=GOLD, linewidth=3, label="Complex Biologics Avg")

    # Draw vertical line for the announcement
    ax.axvline(pd.to_datetime("2000-08-09"), color=RED, linestyle="-", linewidth=2.0, label="Eli Lilly Prozac Patent Loss (Aug 9)")
    ax.text(pd.to_datetime("2000-08-09"), 105.5, "Court Ruling Date\nAug 9, 2000", color=RED, fontsize=9.5, fontweight="bold", ha="center")

    # Visual customizations
    ax.grid(axis='both', linestyle='-', alpha=0.5, color=SLATE)
    ax.set_axisbelow(True)
    ax.tick_params(axis='both', colors='white', labelsize=10)
    ax.set_xlabel("Date", color='white', fontsize=11, labelpad=10)
    ax.set_ylabel("Price Index (Aug 8 = 100)", color='white', fontsize=11, labelpad=10)

    title_text = "Event Study: Eli Lilly Prozac Patent Loss Ruling (July–Sept 2000)\n" \
                 f"Post-Announcement Volatility (Daily SD of Basket): Small Molecules {sm_vol:.2f}% vs. Complex Biologics {cb_vol:.2f}%"
    ax.set_title(title_text, fontsize=12, fontweight='bold', pad=15, color='white')

    # De-duplicate legend
    handles, labels = ax.get_legend_handles_labels()
    unique_labels = {}
    for h, l in zip(handles, labels):
        if "Indiv" not in l:
            unique_labels[l] = h
    ax.legend(unique_labels.values(), unique_labels.keys(), loc='lower left', framealpha=0.8, fontsize=9)

    fig.autofmt_xdate()
    plt.tight_layout()
    
    os.makedirs('charts', exist_ok=True)
    plt.savefig('charts/patent_cliff_event.png', dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  Saved: charts/patent_cliff_event.png")

def main():
    # Load subsector baskets
    small_molecule_tickers = ["BMY", "PFE", "ABBV"]
    complex_biologics_tickers = ["AMGN", "REGN", "NVO"]
    all_tickers = small_molecule_tickers + complex_biologics_tickers
    
    data = {}
    for ticker in all_tickers:
        t = yf.Ticker(ticker)
        df = t.history(start="1995-01-01", end="2026-01-01", interval="1mo")
        data[ticker] = df
        
    small_molecule_graph(data)
    percent_change_graph(data)
    complex_biologics_graph(data)
    create_correlation_graph(data)
    create_summary(data)
    medicare_negot_event()
    patent_cliff_event()

if __name__ == "__main__":
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



