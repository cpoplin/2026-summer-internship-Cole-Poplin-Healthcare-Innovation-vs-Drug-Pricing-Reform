import os
import json
import time
import requests
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor, as_completed

# Define theme colors matching the project guidelines (Sleek Dark Mode)
BG_BLUE = "#0A1128"       # Deep dark navy background
CARD_BG = "#132237"       # Lighter card/plot background
CARD_BORDER = "#1E2F5B"   # Subtle grid/border line
TEXT_WHITE = "#F4F6F9"    # Off-white text
TEXT_MUTED = "#8E9AAF"    # Muted slate/grey text
COLOR_TEAL = "#1A7FA1"    # Teal for Start-to-End return
COLOR_GOLD = "#C9A84C"    # Gold for Start-to-Low drawdown
COLOR_RED = "#E05C5C"     # Red for Peak-to-Trough drawdown

# Default hardcoded fallback data (fetched dynamically from SEC and FMP APIs)
# Contains 136 standard US-listed pharmaceutical and biotech companies with their current market cap
FALLBACK_PROFILES = {
    'WST': 23567332884, 'TAK': 49906134958, 'TEVA': 38169915814, 'VRTX': 119100729981, 
    'ASND': 14499330737, 'JAZZ': 14274043248, 'REGN': 63643900940, 'ALNY': 38671916769, 
    'RPRX': 23475464385, 'UTHR': 23156178487, 'BBIO': 13486009155, 'ARWR': 11276560678, 
    'MDGL': 11858678207, 'IONS': 12614887530, 'AXSM': 12684832319, 'SMMT': 11189548772, 
    'BMRN': 10939874400, 'KRYS': 10016631494, 'CORT': 8590596890, 'HALO': 8223439290, 
    'PTGX': 7585680793, 'KYMR': 8033276044, 'RYTM': 7208498692, 'SYRE': 5868606631, 
    'APGE': 8223468565, 'PTCT': 6813480387, 'MIRM': 5433993579, 'LEGN': 5453974496, 
    'CNTA': 6258059449, 'AMRX': 5259090726, 'CRSP': 5213057640, 'TGTX': 8216087589, 
    'ORKA': 3186875315, 'TVTX': 5142507370, 'DNTH': 3653751250, 'INDV': 4933405800, 
    'XENE': 4307376293, 'TNGX': 3576310212, 'KNSA': 4455036992, 'CRNX': 3824308800, 
    'DNLI': 3942349867, 'EWTX': 4131571200, 'CPRX': 3841532288, 'NAMS': 3622281480, 
    'ACAD': 3854245456, 'RLAY': 3043535074, 'TLX': 3448750359, 'VKTX': 4006271654, 
    'BEAM': 3470345292, 'GPCR': 2570927304, 'ARQT': 3296562465, 'GRDN': 2504964162, 
    'DYN': 3397198508, 'ELVN': 3362713182, 'LGND': 5556584573, 'ADPT': 2806851672, 
    'DFTX': 4015293506, 'TARS': 2806263540, 'RARE': 2869000245, 'SUPN': 2591043111, 
    'VERA': 2712675791, 'TRVI': 2510059258, 'NTLA': 1696062100, 'AUPH': 2283971520, 
    'KLRA': 2820643286, 'MLYS': 1695516543, 'CLDX': 2217733559, 'NKTR': 1311391141, 
    'AGIO': 2116891602, 'BCRX': 1982446110, 'LKFT': 1910356900, 'STOK': 1955643967, 
    'VRDN': 1568655745, 'NRIX': 1642766654, 'ANIP': 1874530638, 'RAPP': 1416837531, 
    'IOVA': 1585588422, 'SNDX': 1731528010, 'SRPT': 1835829391, 'AMLX': 1370274063, 
    'CAPR': 1342709847, 'SION': 1782986532, 'RXRX': 1409324378, 'URGN': 1705337490, 
    'AAPG': 1587814343, 'BCAX': 1365652910, 'VIR': 1700011898, 'GLUE': 1326526059, 
    'MLTX': 1592963554, 'PVLA': 1396816740, 'AVBP': 1563054584, 'MAZE': 1436718673, 
    'MPLT': 23201170, 'DMRA': 1464258155, 'AVLN': 1417125115, 'COAG': 58173921, 
    'ZBIO': 919058033, 'XERS': 1235995871, 'SPRY': 1016368887, 'CRVS': 1074540767, 
    'LXRX': 963461124, 'ETON': 920109305, 'COLL': 1122922297, 'PHAR': 931546388, 
    'ORIC': 937486097, 'CGEM': 1084610784, 'SPTX': 1002910913, 'PHAT': 869339310, 
    'JANX': 908666875, 'AMPH': 844582226, 'ODTX': 560280518, 'SANA': 925069074, 
    'ABUS': 879042810, 'OLMA': 943754485, 'ESPR': 656991552, 'VOR': 103014207, 
    'AVTX': 204197635, 'VRXA': 421395283, 'ZVRA': 754899623, 'RLMD': 500281969, 
    'NNNN': 715865472, 'LBRX': 879082767, 'DSGN': 852225410, 'IMMX': 531909108, 
    'ALLO': 504809648, 'TBPH': 870972554, 'ACRS': 587068520, 'BBOT': 605209171, 
    'TRAX': 623875772, 'RIGL': 660085757, 'SGP': 652441834, 'CADL': 493108751, 
    'GYRE': 594783614, 'IRWD': 624706335, 'TECX': 574849751, 'EIKN': 28093368
}

def load_api_key():
    """Load FMP API key from local environment file."""
    try:
        with open("apikey.env") as f:
            for line in f:
                if line.strip().startswith("API_KEY="):
                    return line.strip().split("=")[1]
    except Exception:
        pass
    return None

def fetch_live_profiles(api_key):
    """Fetch live ticker profiles from SEC and FMP API dynamically."""
    print("Attempting to fetch live tickers and market caps from APIs...")
    # Fetch all SEC registered companies
    sec_url = "https://www.sec.gov/files/company_tickers.json"
    headers = {"User-Agent": "HealthcareIntern cwp72@domain.com"}
    try:
        res = requests.get(sec_url, headers=headers, timeout=5)
        if res.status_code != 200:
            return None
        sec_data = res.json()
    except Exception as e:
        print(f"SEC API fetch failed: {e}")
        return None

    # Filter for pharma & biotech keywords
    keywords = ["PHARM", "BIOTECH", "THERAPEUTIC", "BIOPHARM"]
    filtered_tickers = []
    for k, v in sec_data.items():
        title = v['title'].upper()
        ticker = v['ticker']
        if any(kw in title for kw in keywords):
            # Standard US symbols
            if ticker.isalpha() and 3 <= len(ticker) <= 4:
                filtered_tickers.append(ticker)
                
    # Fetch profiles from FMP in parallel
    profiles = {}
    def fetch_profile(ticker):
        url_prof = f"https://financialmodelingprep.com/stable/profile?symbol={ticker}&apikey={api_key}"
        try:
            res_prof = requests.get(url_prof, timeout=5)
            if res_prof.status_code == 200:
                data = res_prof.json()
                if isinstance(data, list) and len(data) > 0:
                    p = data[0]
                    if p.get("marketCap") is not None:
                        return p.get("symbol"), p.get("marketCap")
        except Exception:
            pass
        return None

    # Limit to maximum workers to avoid overwhelming the server
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_profile, t): t for t in filtered_tickers}
        for future in as_completed(futures):
            res = future.result()
            if res:
                symbol, mcap = res
                profiles[symbol] = mcap
                
    if len(profiles) > 0:
        print(f"Successfully fetched {len(profiles)} live profiles from APIs.")
        return profiles
    return None

def main():
    api_key = load_api_key()
    profiles = None
    if api_key:
        profiles = fetch_live_profiles(api_key)
        
    if not profiles:
        print("Falling back to pre-defined dataset of 136 tickers.")
        profiles = FALLBACK_PROFILES

    tickers = list(profiles.keys())
    print(f"Downloading historical stock price data for {len(tickers)} tickers via yfinance...")
    
    # Download monthly historical close prices (split-adjusted) from 2000-01-01 to 2026-06-01
    # Monthly data is clean, fast, and handles historical alignments robustly.
    data = yf.download(tickers, start="2000-01-01", end="2026-06-01", interval="1mo")
    close_prices = data["Close"]
    
    # Dictionary to store collapse counts per year
    collapses_start_to_end = {}
    collapses_start_to_low = {}
    collapses_peak_to_trough = {}
    
    for ticker in tickers:
        if ticker not in close_prices.columns:
            continue
        
        s = close_prices[ticker].dropna()
        if s.empty:
            continue
            
        current_mcap = profiles[ticker]
        current_price = s.iloc[-1]
        
        if current_price <= 0:
            continue
            
        # Shares outstanding estimated from current profile data
        shares_outstanding = current_mcap / current_price
        
        # Group by calendar year
        by_year = s.groupby(s.index.year)
        for year, y_data in by_year:
            # Exclude current incomplete year 2026 if it doesn't have enough data points
            if year >= 2026 or len(y_data) < 2:
                continue
                
            start_val = y_data.iloc[0]
            end_val = y_data.iloc[-1]
            min_val = y_data.min()
            
            # Start of year market capitalization
            starting_mcap = start_val * shares_outstanding
            
            # Condition: Company previously worth at least $50 million
            if starting_mcap >= 50_000_000:
                # 1. Start-to-End Return (Year End vs Year Start <= -50%)
                if (end_val - start_val) / start_val <= -0.50:
                    collapses_start_to_end[year] = collapses_start_to_end.get(year, 0) + 1
                    
                # 2. Start-to-Low Return (Lowest Close vs Year Start <= -50%)
                if (min_val - start_val) / start_val <= -0.50:
                    collapses_start_to_low[year] = collapses_start_to_low.get(year, 0) + 1
                    
                # 3. Peak-to-Trough Drawdown (Max drawdown within that year >= 50%)
                roll_max = y_data.cummax()
                drawdown = (y_data - roll_max) / roll_max
                max_dd = drawdown.min()
                if max_dd <= -0.50:
                    collapses_peak_to_trough[year] = collapses_peak_to_trough.get(year, 0) + 1

    # Prepare DataFrame
    years = sorted(list(set(
        list(collapses_start_to_end.keys()) + 
        list(collapses_start_to_low.keys()) + 
        list(collapses_peak_to_trough.keys())
    )))
    
    results = pd.DataFrame(index=years)
    results["Start_to_End"] = results.index.map(lambda y: collapses_start_to_end.get(y, 0))
    results["Start_to_Low"] = results.index.map(lambda y: collapses_start_to_low.get(y, 0))
    results["Peak_to_Trough"] = results.index.map(lambda y: collapses_peak_to_trough.get(y, 0))
    
    print("\nCollapses Per Year Table:")
    print(results)
    
    # ── GENERATE PREMIUM VISUALIZATION ──────────────────────────────────────────
    print("Generating premium visualization...")
    fig = plt.figure(figsize=(14, 7.5), facecolor=BG_BLUE)
    ax = fig.add_subplot(111)
    ax.set_facecolor(CARD_BG)
    
    # Plot definitions
    ax.plot(results.index, results["Start_to_End"], color=COLOR_TEAL, linewidth=2.5, 
            marker='o', markersize=6, label="Start-to-End Collapse (Year Return \u2264 -50%)")
    ax.plot(results.index, results["Start_to_Low"], color=COLOR_GOLD, linewidth=2.5, 
            marker='s', markersize=6, label="Start-to-Low Collapse (Max Drawdown vs Jan 1 \u2264 -50%)")
    ax.plot(results.index, results["Peak_to_Trough"], color=COLOR_RED, linewidth=2.5, 
            marker='^', markersize=6, label="Peak-to-Trough Collapse (Max Intra-Year Drawdown \u2264 -50%)")
    
    # Format axes and gridlines
    ax.grid(axis='y', linestyle='-', alpha=0.3, color=TEXT_MUTED)
    ax.grid(axis='x', linestyle='--', alpha=0.15, color=TEXT_MUTED)
    ax.set_axisbelow(True)
    
    # Ticks and limits
    ax.set_xticks(results.index)
    ax.set_xticklabels(results.index, rotation=45, color=TEXT_WHITE, fontsize=10)
    ax.tick_params(axis='y', colors=TEXT_WHITE, labelsize=10)
    ax.set_xlim(results.index[0] - 0.5, results.index[-1] + 0.5)
    
    # Title and labels
    ax.set_title("Historical Pharmaceutical & Biotech Stock Collapses (2000–2025)", 
                 fontsize=15, fontweight='bold', pad=20, color=TEXT_WHITE)
    ax.set_xlabel("Year", color=TEXT_WHITE, fontsize=12, labelpad=10)
    ax.set_ylabel("Number of Corporate Collapses", color=TEXT_WHITE, fontsize=12, labelpad=10)
    
    # Highlights & annotations for major macro events
    # 2008 GFC
    ax.axvspan(2007.8, 2008.2, color='white', alpha=0.08)
    ax.text(2008, ax.get_ylim()[1]*0.9, "GFC\n2008", color=TEXT_MUTED, fontsize=9, 
            fontweight="bold", ha="center", va="center", bbox=dict(facecolor=BG_BLUE, alpha=0.6, boxstyle="round,pad=0.3"))
            
    # 2018 Rate hikes & market corrections
    ax.axvspan(2017.8, 2018.2, color='white', alpha=0.08)
    ax.text(2018, ax.get_ylim()[1]*0.9, "Hikes\n2018", color=TEXT_MUTED, fontsize=9, 
            fontweight="bold", ha="center", va="center", bbox=dict(facecolor=BG_BLUE, alpha=0.6, boxstyle="round,pad=0.3"))
            
    # 2021-2023 Post-COVID bubble burst & Inflation Reduction Act (IRA)
    ax.axvspan(2020.8, 2023.2, color=COLOR_RED, alpha=0.06)
    ax.text(22, ax.get_ylim()[1]*0.9, "Post-COVID Bear Market\n& IRA Legislation\n(2021-2023)", 
            color=COLOR_RED, fontsize=9, fontweight="bold", ha="center", va="center", 
            bbox=dict(facecolor=BG_BLUE, alpha=0.6, boxstyle="round,pad=0.3"))
            
    # Legend setup
    ax.legend(loc='upper left', framealpha=0.9, facecolor=BG_BLUE, edgecolor=CARD_BORDER, 
              labelcolor=TEXT_WHITE, fontsize=10.5)
              
    # Add a custom subtitle block inside the figure
    fig.text(0.5, 0.01, 
             "Methodology: Filters US-listed pharma/biotech companies. 'Collapse' defined as starting/peak market cap \u2265 $50M and loss \u2265 50% in that year.", 
             transform=fig.transFigure, ha="center", va="center", fontsize=9, color=TEXT_MUTED, fontstyle="italic")
             
    plt.tight_layout()
    
    # Save the chart
    os.makedirs("charts", exist_ok=True)
    chart_path = "pharma_collapses.png"
    plt.savefig(chart_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {chart_path}")

if __name__ == "__main__":
    main()
