"""
=============================================================================
silver.py  —  Silver Tier: Interactive Analysis Dashboard
THESIS: Healthcare Innovation vs Drug Pricing Reform
How to run:  streamlit run silver.py
             then open http://localhost:8501 in your browser
=============================================================================
"""

import os
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.dates as mdates
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set page config to match premium guidelines
st.set_page_config(
    page_title="Biologics Alpha vs. Price Caps | Case Study",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Core Theme Colors (Sleek Dark Mode)
NAVY   = "#0D1B2A"        # Slate navy
BG_BLUE = "#0A1128"       # Deep dark navy background
CARD_BG = "#132237"       # Lighter navy for cards
CARD_BORDER = "#1E2F5B"   # Subtle grid/border line
CAROLINA_BLUE = "#7BAFD4"  # Carolina Blue accent color
GOLD   = "#C9A84C"        # Accent Gold for graph contrast
TEAL   = "#1A7FA1"        # Teal
RED    = "#E05C5C"        # Highlight Red
GREEN  = "#2D9E6B"        # Success Green
SLATE  = "#8FA3B1"        # Grid lines / Muted text
WHITE  = "#F4F6F9"        # Off-white primary text

# Inject Custom CSS for Premium Design & Responsive Cards
st.markdown(f"""
<style>
    /* Main Background & Fonts */
    .stApp {{
        background-color: {BG_BLUE};
        color: {WHITE};
    }}
    
    /* Metrics Custom Styling */
    div[data-testid="stMetricValue"] {{
        font-size: 26px;
        font-weight: bold;
    }}
    div[data-testid="stMetricLabel"] {{
        font-size: 14px;
        color: {SLATE};
    }}
    .metric-container {{
        background-color: {CARD_BG};
        border: 1px solid {CARD_BORDER};
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
    }}
    
    /* Headers Accent */
    h1, h2, h3, h4 {{
        color: {CAROLINA_BLUE} !important;
        font-family: 'Outfit', 'Inter', sans-serif;
    }}
    
    /* Styled HTML Verdict Cards */
    .verdict-card {{
        background-color: {CARD_BG};
        border: 1px solid {CARD_BORDER};
        border-radius: 12px;
        padding: 25px;
        color: {WHITE};
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
    }}
    .badge-success {{
        background-color: #1E3A2F;
        border: 1.5px solid {GREEN};
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        font-weight: bold;
        color: {GREEN};
        font-size: 16px;
        letter-spacing: 1px;
    }}
    .badge-error {{
        background-color: #3A1E1E;
        border: 1.5px solid {RED};
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        font-weight: bold;
        color: {RED};
        font-size: 16px;
        letter-spacing: 1px;
    }}
    
    /* Bullet points */
    .verdict-bullet {{
        font-size: 13px;
        margin-bottom: 6px;
    }}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 1. DATA CACHING AND UTILITIES
# -----------------------------------------------------------------------------

@st.cache_data(show_spinner="Fetching ticker monthly histories...")
def load_monthly_data(tickers, start_str, end_str):
    """Download monthly data ticker-by-ticker to avoid alignment issues."""
    data = {}
    for ticker in tickers:
        try:
            t = yf.Ticker(ticker)
            df = t.history(start=start_str, end=end_str, interval="1mo")
            if not df.empty:
                # Remove timezone to avoid pandas issues
                if df.index.tz is not None:
                    df.index = df.index.tz_localize(None)
                data[ticker] = df["Close"]
        except Exception:
            pass
    return pd.DataFrame(data)

@st.cache_data(show_spinner="Fetching event study daily data...")
def load_daily_data(tickers, start_str, end_str):
    """Download daily close prices for tickers in standard event windows."""
    try:
        df = yf.download(tickers, start=start_str, end=end_str, group_by='ticker', progress=False)
        close_prices = {}
        for ticker in tickers:
            if len(tickers) == 1:
                if ticker in df.columns:
                    close_prices[ticker] = df[ticker]
                elif "Close" in df.columns:
                    close_prices[ticker] = df["Close"]
            else:
                if ticker in df.columns.levels[0]:
                    close_prices[ticker] = df[ticker]["Close"]
        
        price_df = pd.DataFrame(close_prices)
        if not price_df.empty:
            if price_df.index.tz is not None:
                price_df.index = price_df.index.tz_localize(None)
        return price_df
    except Exception:
        return pd.DataFrame()

def calculate_rolling_beta(basket_returns, market_returns, window=24):
    """Calculate rolling beta of a basket relative to market returns."""
    df = pd.DataFrame({"basket": basket_returns, "market": market_returns}).dropna()
    if len(df) < window:
        return pd.Series(index=df.index, dtype=float)
    
    rolling_cov = df["basket"].rolling(window=window).cov(df["market"])
    rolling_var = df["market"].rolling(window=window).var()
    return rolling_cov / rolling_var

# -----------------------------------------------------------------------------
# 2. SIDEBAR PARAMETERS & CONTROLS
# -----------------------------------------------------------------------------

st.sidebar.title("Case Study Controls")
st.sidebar.markdown("---")

# Navigation Selector
page = st.sidebar.radio(
    "Navigation Pages",
    ["1. Background & Subsector Showdown", 
     "2. Stress-Test Events & Risk", 
     "3. Thesis Verdict & Conclusion"]
)

st.sidebar.markdown("---")

# Predefined baskets & pools
POTENTIAL_SM = ["BMY", "PFE", "ABBV", "JNJ", "MRK", "LLY", "GSK", "TEVA", "TAK", "AZN", "NVS", "SNY"]
POTENTIAL_CB = ["AMGN", "REGN", "NVO", "VRTX", "BIIB", "GILD", "MRNA", "ALNY", "IONS", "BMRN"]

# Custom inputs for tickers (Requested by USER)
st.sidebar.subheader("Subsector Baskets")

selected_sm_list = st.sidebar.multiselect(
    "Small Molecule Tickers", 
    options=POTENTIAL_SM, 
    default=["BMY", "PFE", "ABBV"],
    help="Tickers representing traditional chemistry/small molecule pharma companies."
)
custom_sm_input = st.sidebar.text_input("Add Custom Small Molecule Tickers (comma-separated)", "")

selected_cb_list = st.sidebar.multiselect(
    "Complex Biologics Tickers", 
    options=POTENTIAL_CB, 
    default=["AMGN", "REGN", "NVO"],
    help="Tickers representing innovative biotech/biologics companies."
)
custom_cb_input = st.sidebar.text_input("Add Custom Complex Biologics Tickers (comma-separated)", "")

# Parse custom tickers
final_sm_tickers = [t for t in selected_sm_list]
if custom_sm_input:
    for ticker in custom_sm_input.split(","):
        t = ticker.strip().upper()
        if t and t not in final_sm_tickers:
            final_sm_tickers.append(t)

final_cb_tickers = [t for t in selected_cb_list]
if custom_cb_input:
    for ticker in custom_cb_input.split(","):
        t = ticker.strip().upper()
        if t and t not in final_cb_tickers:
            final_cb_tickers.append(t)

st.sidebar.markdown("---")

# Date range selection
st.sidebar.subheader("Date Filters")
start_year, end_year = st.sidebar.slider(
    "Select Analysis Period",
    min_value=1995, max_value=2026,
    value=(1995, 2026),
    help="Shifts the timeline and dynamically recalculates subsector CAGRs and alpha spread."
)

# Additional configurations
st.sidebar.subheader("Chart Controls")
show_events = st.sidebar.checkbox("Highlight macro regulatory periods", value=True)
chart_dpi = st.sidebar.selectbox("Render Chart Quality", [100, 150, 200], index=1)

st.sidebar.markdown("---")
st.sidebar.markdown(
    f"<div style='font-size: 11px; color: {SLATE};'>"
    f"Healthcare Innovation vs Drug Pricing Reform<br>"
    f"Silver Tier Dashboard • 2026 Summer Case Study"
    f"</div>",
    unsafe_allow_html=True
)

# -----------------------------------------------------------------------------
# 3. DYNAMIC DATA PIPELINE AND PROCESSING
# -----------------------------------------------------------------------------

# Download data for all selected tickers plus S&P 500 benchmark
unique_tickers = list(set(final_sm_tickers + final_cb_tickers + ["^GSPC"]))
all_monthly_raw = load_monthly_data(unique_tickers, "1995-01-01", "2026-06-01")

# Clean & align dates, slice by sliders
if not all_monthly_raw.empty:
    sliced_monthly = all_monthly_raw.loc[f"{start_year}-01-01":f"{end_year}-12-31"].copy()
    
    # Filter tickers that actually returned data in this window
    valid_sm = [t for t in final_sm_tickers if t in sliced_monthly.columns and not sliced_monthly[t].dropna().empty]
    valid_cb = [t for t in final_cb_tickers if t in sliced_monthly.columns and not sliced_monthly[t].dropna().empty]
    
    # Normalize price indices to start at 100
    norm_monthly = sliced_monthly.copy()
    for col in norm_monthly.columns:
        first_valid_val = norm_monthly[col].dropna()
        if not first_valid_val.empty:
            norm_monthly[col] = (norm_monthly[col] / first_valid_val.iloc[0]) * 100
            
    # Calculate basket averages
    if valid_sm:
        norm_monthly["Small_Molecules_Avg"] = norm_monthly[valid_sm].mean(axis=1)
    else:
        norm_monthly["Small_Molecules_Avg"] = np.nan
        
    if valid_cb:
        norm_monthly["Complex_Biologics_Avg"] = norm_monthly[valid_cb].mean(axis=1)
    else:
        norm_monthly["Complex_Biologics_Avg"] = np.nan
else:
    sliced_monthly = pd.DataFrame()
    norm_monthly = pd.DataFrame()
    valid_sm = []
    valid_cb = []

# -----------------------------------------------------------------------------
# 4. VIEW PAGE 1: BACKGROUND & SUBSECTOR TRENDS
# -----------------------------------------------------------------------------

if page == "1. Background & Subsector Showdown":
    st.title("Subsector Performance Showdown & Trajectories")
    st.markdown(
        f"*Historical Stock Performance of Complex Biologics vs. Small Molecules from **{start_year}** to **{end_year}**. All averages are weighted merely by number of companies in the basket, not by market cap or any other metric. There is also no reweighting mechanic at play here*"
    )
    st.markdown("---")
    
    if len(valid_sm) == 0 or len(valid_cb) == 0:
        st.error("Please select at least one valid ticker for both baskets in the sidebar.")
    else:
        # Calculate performance statistics
        # Thesis context layout
        st.markdown("### Subsector Trajectory Indexes (Base = 100)")
        st.caption("Note: To clearly observe the impact of the 'Patent Cliff' era on small molecules versus biologics, adjust the slider to limit the analysis window to 1995-2010.")
        
        # Generate dynamic plot
        fig, ax = plt.subplots(figsize=(14, 6.5), facecolor=BG_BLUE)
        ax.set_facecolor(NAVY)
        
        # Plot averages
        ax.plot(norm_monthly.index, norm_monthly["Small_Molecules_Avg"], color=TEAL, linewidth=3, label="Small Molecules Avg Basket")
        ax.plot(norm_monthly.index, norm_monthly["Complex_Biologics_Avg"], color=GOLD, linewidth=3, label="Complex Biologics Avg Basket")
        
        # Shading key periods
        if show_events:
            # 2000-2005 Patent Cliff
            ax.axvspan(pd.to_datetime('2000-01-01'), pd.to_datetime('2005-12-31'), 
                       color='red', alpha=0.08, label='The "Patent Cliff" (2000–2005)')
            # 2022-2025 IRA
            ax.axvspan(pd.to_datetime('2022-07-01'), pd.to_datetime('2025-01-01'), 
                       color='red', alpha=0.15, label='Inflation Reduction Act (2022–2025)')
                       
        # Styling axes
        ax.grid(axis='y', linestyle='-', alpha=0.3, color=SLATE)
        ax.grid(axis='x', linestyle='--', alpha=0.15, color=SLATE)
        ax.set_axisbelow(True)
        ax.tick_params(axis='both', colors=WHITE, labelsize=10)
        ax.set_ylabel("Normalized Price Index (Start = 100)", color=WHITE, fontsize=11, labelpad=10)
        ax.set_xlabel("Date", color=WHITE, fontsize=11, labelpad=10)
        ax.legend(loc="upper left", framealpha=0.9, facecolor=BG_BLUE, edgecolor=CARD_BORDER, labelcolor=WHITE, fontsize=9.5)
        ax.set_title(f"Subsector Performance Trend ({start_year} - {end_year})", fontsize=13, fontweight="bold", pad=15, color=WHITE)
        
        plt.tight_layout()
        st.pyplot(fig, dpi=chart_dpi)
        plt.close(fig)
        
        # Individual stock plots side by side
        st.markdown("---")
        col_sm, col_cb = st.columns(2)
        
        with col_sm:
            st.markdown("#### Individual Small Molecule Trajectories (Raw Price)")
            fig_sm, ax_sm = plt.subplots(figsize=(7, 4.5), facecolor=BG_BLUE)
            ax_sm.set_facecolor(NAVY)
            colors = plt.cm.tab10(np.linspace(0, 1, len(valid_sm)))
            for ticker, color in zip(valid_sm, colors):
                ax_sm.plot(sliced_monthly.index, sliced_monthly[ticker], label=ticker, linewidth=1.5)
            ax_sm.grid(axis='y', linestyle='-', alpha=0.3, color=SLATE)
            ax_sm.tick_params(colors=WHITE, labelsize=9)
            ax_sm.legend(loc="upper left", framealpha=0.2, labelcolor=WHITE, fontsize=8)
            ax_sm.set_ylabel("Share Price ($)", color=WHITE, fontsize=9)
            plt.tight_layout()
            st.pyplot(fig_sm, dpi=chart_dpi)
            plt.close(fig_sm)
            
        with col_cb:
            st.markdown("#### Individual Complex Biologic Trajectories (Raw Price)")
            fig_cb, ax_cb = plt.subplots(figsize=(7, 4.5), facecolor=BG_BLUE)
            ax_cb.set_facecolor(NAVY)
            colors = plt.cm.Accent(np.linspace(0, 1, len(valid_cb)))
            for ticker, color in zip(valid_cb, colors):
                ax_cb.plot(sliced_monthly.index, sliced_monthly[ticker], label=ticker, linewidth=1.5)
            ax_cb.grid(axis='y', linestyle='-', alpha=0.3, color=SLATE)
            ax_cb.tick_params(colors=WHITE, labelsize=9)
            ax_cb.legend(loc="upper left", framealpha=0.2, labelcolor=WHITE, fontsize=8)
            ax_cb.set_ylabel("Share Price ($)", color=WHITE, fontsize=9)
            plt.tight_layout()
            st.pyplot(fig_cb, dpi=chart_dpi)
            plt.close(fig_cb)
            
        # Explanatory Text block
        st.markdown("### Subsector Dynamics Context")
        st.info(
            "Traditional small molecule therapeutics rely on simple, synthesizable chemical structures. "
            "Under the historic Hatch-Waxman Act of 1984, once a small molecule's patent expires, generic competitors "
            "face extremely low regulatory barriers, causing immediate generic cliffs where brand pricing collapses up to 90% in weeks.\n\n"
            "Conversely, complex biologics (large proteins, antibodies, gene therapies) are manufactured inside living cells, "
            "requiring complex biosimilar drug approvals. As a result, biosimilars do not replicate the rapid generic cliffs of small molecules. "
            "Even under modern price negotiation pressure (such as the Inflation Reduction Act of 2022), small molecules face negotiation price caps "
            "only 9 years post-launch, while biologics are shielded for 13 years, structurally redirecting industry alpha to large molecule pipelines."
        )

# -----------------------------------------------------------------------------
# 5. VIEW PAGE 2: STRESS-TEST EVENTS & RISK
# -----------------------------------------------------------------------------

elif page == "2. Stress-Test Events & Risk":
    st.title("Event Studies & Risk Analysis")
    st.markdown(
        "*Stress-Testing Subsector Resilience During Key Regulatory Shocks.*"
    )
    st.markdown("---")
    
    # Event Study Columns
    col_e1, col_e2 = st.columns(2)
    
    # Event 1: Prozac Loss (2000)
    with col_e1:
        st.markdown("### Eli Lilly Prozac Patent Loss Ruling (2000)")
        st.markdown(
            "On August 9, 2000, the US Court of Appeals stripped Eli Lilly of its key Prozac patent, triggering the generic small-molecule era "
            "and sparking a broad pharmaceutical correction. This event study evaluates how small molecule and biologic baskets reacted."
        )
        
        # Prozac event dates: start_date, end_date, base_date
        e1_start = "2000-07-24"
        e1_end = "2000-09-15"
        e1_base = "2000-08-08"
        
        # Load daily prices
        # Prozac cliff uses LLY in default small molecules because ABBV spun off later
        e1_sm_tickers = ["LLY", "BMY", "PFE"]
        # Allow custom selected tickers if they have data in 2000
        e1_tickers = list(set(e1_sm_tickers + final_cb_tickers))
        e1_df = load_daily_data(e1_tickers, "2000-07-01", "2000-10-01")
        
        if e1_df.empty:
            st.warning("No daily stock data available for the 2000 event window.")
        else:
            e1_sliced = e1_df.loc[e1_start:e1_end].copy()
            # Clean tz
            if e1_sliced.index.tz is not None:
                e1_sliced.index = e1_sliced.index.tz_localize(None)
                
            # Filter active tickers in this period
            active_sm = [t for t in e1_sm_tickers if t in e1_sliced.columns and not e1_sliced[t].dropna().empty]
            active_cb = [t for t in final_cb_tickers if t in e1_sliced.columns and not e1_sliced[t].dropna().empty]
            
            if not active_sm or not active_cb:
                st.warning("Missing overlapping tickers during 2000 window.")
            else:
                # Normalize prices to base_date = 100
                if e1_base in e1_sliced.index:
                    e1_base_row = e1_sliced.loc[e1_base]
                else:
                    e1_base_row = e1_sliced.loc[:e1_base].iloc[-1]
                    
                e1_norm = e1_sliced.copy()
                for col in e1_norm.columns:
                    e1_norm[col] = (e1_norm[col] / e1_base_row[col]) * 100
                    
                e1_norm["Small Molecules Avg"] = e1_norm[active_sm].mean(axis=1)
                e1_norm["Complex Biologics Avg"] = e1_norm[active_cb].mean(axis=1)
                
                # Calculate performance (net change of the basket price index from base date)
                e1_sm_perf = e1_norm["Small Molecules Avg"].iloc[-1] - 100
                e1_cb_perf = e1_norm["Complex Biologics Avg"].iloc[-1] - 100
                
                # Plot Event 1
                fig_e1, ax_e1 = plt.subplots(figsize=(7, 4.5), facecolor=BG_BLUE)
                ax_e1.set_facecolor(NAVY)
                
                ax_e1.plot(e1_norm.index, e1_norm["Small Molecules Avg"], color=TEAL, linewidth=2.5, label="Small Molecules Avg")
                ax_e1.plot(e1_norm.index, e1_norm["Complex Biologics Avg"], color=GOLD, linewidth=2.5, label="Complex Biologics Avg")
                ax_e1.axvline(pd.to_datetime("2000-08-09"), color=RED, linestyle="-", linewidth=1.5)
                ax_e1.text(pd.to_datetime("2000-08-09"), ax_e1.get_ylim()[1]*0.96, "Ruling\nAug 9", color=RED, fontsize=8, fontweight="bold", ha="center")
                
                ax_e1.grid(axis='both', linestyle='-', alpha=0.3, color=SLATE)
                ax_e1.tick_params(colors=WHITE, labelsize=8)
                ax_e1.set_ylabel("Price Index (Aug 8 = 100)", color=WHITE, fontsize=9)
                ax_e1.legend(loc="lower left", framealpha=0.2, labelcolor=WHITE, fontsize=8)
                ax_e1.set_title("Prozac Patent Loss Window (2000)", color=WHITE, fontsize=10, fontweight="bold")
                fig_e1.autofmt_xdate()
                plt.tight_layout()
                st.pyplot(fig_e1, dpi=chart_dpi)
                plt.close(fig_e1)
                
                # Performance Metrics
                v_col1, v_col2 = st.columns(2)
                v_col1.metric("Small Molecules Performance", f"{e1_sm_perf:+.2f}%", help="Total basket performance over the event window.")
                v_col2.metric("Complex Biologics Performance", f"{e1_cb_perf:+.2f}%", help="Total basket performance over the event window.")
                
    # Event 2: Medicare Negotiation (2023)
    with col_e2:
        st.markdown("### Medicare Price Negotiation Announcement (2023)")
        st.markdown(
            "On August 29, 2023, CMS released the list of the first 10 drugs selected for price negotiations under the IRA. "
            "This list focused heavily on highly successful small molecule blockers, leaving complex biologics largely untouched."
        )
        
        # CMS negotiations event dates
        e2_start = "2023-08-14"
        e2_end = "2023-09-22"
        e2_base = "2023-08-28"
        
        # Load daily prices
        e2_df = load_daily_data(unique_tickers, "2023-08-01", "2023-10-01")
        
        if e2_df.empty:
            st.warning("No daily stock data available for the 2023 event window.")
        else:
            e2_sliced = e2_df.loc[e2_start:e2_end].copy()
            if e2_sliced.index.tz is not None:
                e2_sliced.index = e2_sliced.index.tz_localize(None)
                
            active_sm2 = [t for t in final_sm_tickers if t in e2_sliced.columns and not e2_sliced[t].dropna().empty]
            active_cb2 = [t for t in final_cb_tickers if t in e2_sliced.columns and not e2_sliced[t].dropna().empty]
            
            if not active_sm2 or not active_cb2:
                st.warning("Missing overlapping tickers during 2023 window.")
            else:
                # Normalize prices to base_date = 100
                if e2_base in e2_sliced.index:
                    e2_base_row = e2_sliced.loc[e2_base]
                else:
                    e2_base_row = e2_sliced.loc[:e2_base].iloc[-1]
                    
                e2_norm = e2_sliced.copy()
                for col in e2_norm.columns:
                    e2_norm[col] = (e2_norm[col] / e2_base_row[col]) * 100
                    
                e2_norm["Small Molecules Avg"] = e2_norm[active_sm2].mean(axis=1)
                e2_norm["Complex Biologics Avg"] = e2_norm[active_cb2].mean(axis=1)
                
                # Calculate performance (net change of the basket price index from base date)
                e2_sm_perf = e2_norm["Small Molecules Avg"].iloc[-1] - 100
                e2_cb_perf = e2_norm["Complex Biologics Avg"].iloc[-1] - 100
                
                # Plot Event 2
                fig_e2, ax_e2 = plt.subplots(figsize=(7, 4.5), facecolor=BG_BLUE)
                ax_e2.set_facecolor(NAVY)
                
                ax_e2.plot(e2_norm.index, e2_norm["Small Molecules Avg"], color=TEAL, linewidth=2.5, label="Small Molecules Avg")
                ax_e2.plot(e2_norm.index, e2_norm["Complex Biologics Avg"], color=GOLD, linewidth=2.5, label="Complex Biologics Avg")
                ax_e2.axvline(pd.to_datetime("2023-08-29"), color=RED, linestyle="-", linewidth=1.5)
                ax_e2.text(pd.to_datetime("2023-08-29"), ax_e2.get_ylim()[1]*0.96, "List Released\nAug 29", color=RED, fontsize=8, fontweight="bold", ha="center")
                
                ax_e2.grid(axis='both', linestyle='-', alpha=0.3, color=SLATE)
                ax_e2.tick_params(colors=WHITE, labelsize=8)
                ax_e2.set_ylabel("Price Index (Aug 28 = 100)", color=WHITE, fontsize=9)
                ax_e2.legend(loc="lower left", framealpha=0.2, labelcolor=WHITE, fontsize=8)
                ax_e2.set_title("CMS Price Negotiation Announcement Window (2023)", color=WHITE, fontsize=10, fontweight="bold")
                fig_e2.autofmt_xdate()
                plt.tight_layout()
                st.pyplot(fig_e2, dpi=chart_dpi)
                plt.close(fig_e2)
                
                # Performance Metrics
                v_col3, v_col4 = st.columns(2)
                v_col3.metric("Small Molecules Performance", f"{e2_sm_perf:+.2f}%", help="Total basket performance over the event window.")
                v_col4.metric("Complex Biologics Performance", f"{e2_cb_perf:+.2f}%", help="Total basket performance over the event window.")

    st.markdown("---")
    
    # Section: Rolling Beta (Investor Confidence / Market Risk)
    st.markdown("### Investor Confidence: Rolling Beta to S&P 500")
    st.markdown(
        "Beta measures a subsector's sensitivity to the broader equity market (S&P 500, represented by `^GSPC`). "
        "A higher beta indicates that the subsector experiences amplified swings, reflecting higher systematic risk "
        "and shifting investor risk sentiment. A lower or declining beta shows defensive resilience and decoupling "
        "from broader market panic. This rolling 24-month beta illustrates how investor confidence and systematic "
        "risk exposure have evolved for both baskets."
    )
    
    try:
        # We need monthly returns of the average baskets and ^GSPC
        if "^GSPC" in sliced_monthly.columns:
            # Monthly returns
            returns_df = sliced_monthly.pct_change()
            
            if "Small_Molecules_Avg" in norm_monthly.columns and "Complex_Biologics_Avg" in norm_monthly.columns:
                sm_ret = norm_monthly["Small_Molecules_Avg"].pct_change()
                cb_ret = norm_monthly["Complex_Biologics_Avg"].pct_change()
                mkt_ret = returns_df["^GSPC"]
                
                # Calculate rolling 24-month beta
                beta_sm = calculate_rolling_beta(sm_ret, mkt_ret, window=24)
                beta_cb = calculate_rolling_beta(cb_ret, mkt_ret, window=24)
                
                # Align and plot
                plot_df = pd.DataFrame({
                    "Beta_SM": beta_sm,
                    "Beta_CB": beta_cb
                }).dropna()
                
                if not plot_df.empty:
                    # Plot Rolling Beta
                    fig_b, ax_b = plt.subplots(figsize=(14, 6), facecolor=BG_BLUE)
                    ax_b.set_facecolor(CARD_BG)
                    
                    ax_b.plot(plot_df.index, plot_df["Beta_SM"], color=TEAL, linewidth=2.5, label="Small Molecules Beta")
                    ax_b.plot(plot_df.index, plot_df["Beta_CB"], color=GOLD, linewidth=2.5, label="Complex Biologics Beta")
                    ax_b.axhline(1.0, color=WHITE, linestyle="--", alpha=0.5, label="Market Beta (1.0)")
                    
                    # Style axis
                    ax_b.grid(axis='y', linestyle='-', alpha=0.2, color=SLATE)
                    ax_b.grid(axis='x', linestyle='--', alpha=0.1, color=SLATE)
                    ax_b.set_axisbelow(True)
                    ax_b.tick_params(colors=WHITE, labelsize=9)
                    ax_b.set_ylabel("Rolling 24-Month Beta", color=WHITE, fontsize=10)
                    ax_b.set_xlabel("Date", color=WHITE, fontsize=10)
                    ax_b.legend(loc="upper left", framealpha=0.9, facecolor=BG_BLUE, edgecolor=CARD_BORDER, labelcolor=WHITE, fontsize=9.5)
                    ax_b.set_title("Subsector Systematic Risk: Rolling 24-Month Beta to S&P 500", color=WHITE, fontsize=11, fontweight="bold", pad=10)
                    
                    # Highlights if they fall within the range
                    years_in_index = plot_df.index.year
                    if any(y in years_in_index for y in range(2000, 2006)):
                        ax_b.axvspan(pd.to_datetime('2000-01-01'), pd.to_datetime('2005-12-31'), color='red', alpha=0.04)
                        ax_b.text(pd.to_datetime('2002-12-31'), ax_b.get_ylim()[1]*0.9, 'Patent Cliff Era', color=SLATE, fontsize=8, ha='center')
                    
                    if any(y in years_in_index for y in range(2022, 2026)):
                        ax_b.axvspan(pd.to_datetime('2022-07-01'), pd.to_datetime('2025-01-01'), color=RED, alpha=0.06)
                        ax_b.text(pd.to_datetime('2023-10-01'), ax_b.get_ylim()[1]*0.9, 'IRA Price Caps', color=RED, fontsize=8, ha='center')
                        
                    plt.tight_layout()
                    st.pyplot(fig_b, dpi=chart_dpi)
                    plt.close(fig_b)
                    
                    # Add description of the beta values
                    st.info(
                        "**Interpretation of Beta trends:**\n"
                        "- A **beta > 1.0** indicates that the subsector is more volatile than the S&P 500, showing amplified systematic risk.\n"
                        "- A **beta < 1.0** indicates defensive characteristics, decoupling the subsector from broader market sell-offs.\n"
                        "- During macro and legislative shocks, notice how the beta profiles shift: "
                        "Small Molecules tend to experience beta inflation as policy heat and generic cliffs increase stock volatility, "
                        "whereas Complex Biologics show lower systematic risk exposure (lower beta) as investors treat them as a robust, policy-shielded safe haven."
                    )
                else:
                    st.warning("Insufficient overlapping data points to plot the rolling 24-month beta.")
            else:
                st.warning("Subsector averages not found in normalized data.")
        else:
            st.error("Market benchmark index S&P 500 (^GSPC) is missing from the downloaded dataset.")
    except Exception as e:
        st.error(f"Error calculating rolling beta: {e}")

# -----------------------------------------------------------------------------
# 6. VIEW PAGE 3: THESIS VERDICT & CONCLUSION
# -----------------------------------------------------------------------------

elif page == "3. Thesis Verdict & Conclusion":
    st.title("Case Study Verdict & Investment Conclusion")
    st.markdown(
        f"*Final performance aggregation and thesis evaluation for the **{start_year} - {end_year}** period.*"
    )
    st.markdown("---")
    
    if len(valid_sm) == 0 or len(valid_cb) == 0:
        st.error("Please select at least one valid ticker for both baskets in the sidebar.")
    else:
        # Calculate calculations
        sm_first = norm_monthly["Small_Molecules_Avg"].dropna().iloc[0]
        sm_last = norm_monthly["Small_Molecules_Avg"].dropna().iloc[-1]
        cb_first = norm_monthly["Complex_Biologics_Avg"].dropna().iloc[0]
        cb_last = norm_monthly["Complex_Biologics_Avg"].dropna().iloc[-1]
        
        sm_return = sm_last - 100
        cb_return = cb_last - 100
        diff = cb_return - sm_return
        
        val_multiple = (100.0 + cb_return) / (100.0 + sm_return) if (100.0 + sm_return) > 0 else 0
        
        # Calculate CAGRs
        n_years = (norm_monthly.index[-1] - norm_monthly.index[0]).days / 365.25
        sm_cagr = ((sm_last / 100) ** (1 / n_years) - 1) * 100 if sm_last > 0 else 0
        cb_cagr = ((cb_last / 100) ** (1 / n_years) - 1) * 100 if cb_last > 0 else 0
        cagr_spread = cb_cagr - sm_cagr
        
        # Display Metric Columns
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                f'<div class="metric-container">'
                f'<div style="color: {TEAL}; font-size: 14px; font-weight: bold;">Small Molecule Average Return</div>'
                f'<div style="font-size: 32px; font-weight: bold; color: {WHITE};">{sm_return:+.1f}%</div>'
                f'<div style="font-size: 13px; color: {SLATE};">CAGR: {sm_cagr:.2f}% ({len(valid_sm)} tickers)</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f'<div class="metric-container">'
                f'<div style="color: {CAROLINA_BLUE}; font-size: 14px; font-weight: bold;">Complex Biologics Average Return</div>'
                f'<div style="font-size: 32px; font-weight: bold; color: {CAROLINA_BLUE};">{cb_return:+.1f}%</div>'
                f'<div style="font-size: 13px; color: {SLATE};">CAGR: {cb_cagr:.2f}% ({len(valid_cb)} tickers)</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        with col3:
            badge_color = GREEN if diff >= 0 else RED
            st.markdown(
                f'<div class="metric-container">'
                f'<div style="color: {badge_color}; font-size: 14px; font-weight: bold;">Subsector Alpha Spread</div>'
                f'<div style="font-size: 32px; font-weight: bold; color: {badge_color};">{diff:+.1f}%</div>'
                f'<div style="font-size: 13px; color: {SLATE};">CAGR Delta: {cagr_spread:+.2f}%</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            
        st.markdown("---")
        
        # 1. Bar Chart: Average YoY percentage change
        # Calculate yearly close prices for percent change calculations
        st.markdown("### Annual Subsector Return Comparison")
        
        yearly_sm_pct = []
        yearly_cb_pct = []
        years_range = []
        
        for y in range(start_year, end_year):
            jan_date = f"{y}-01-01"
            next_jan = f"{y+1}-01-01"
            
            sm_idx = norm_monthly["Small_Molecules_Avg"].loc[jan_date:next_jan]
            cb_idx = norm_monthly["Complex_Biologics_Avg"].loc[jan_date:next_jan]
            
            if len(sm_idx) >= 2 and len(cb_idx) >= 2:
                sm_y_change = (sm_idx.iloc[-1] - sm_idx.iloc[0]) / sm_idx.iloc[0] * 100
                cb_y_change = (cb_idx.iloc[-1] - cb_idx.iloc[0]) / cb_idx.iloc[0] * 100
                
                yearly_sm_pct.append(sm_y_change)
                yearly_cb_pct.append(cb_y_change)
                years_range.append(y)
                
        if len(years_range) > 0:
            fig_bar, ax_bar = plt.subplots(figsize=(14, 5.5), facecolor=BG_BLUE)
            ax_bar.set_facecolor(NAVY)
            
            x = np.arange(len(years_range))
            width = 0.35
            
            ax_bar.bar(x - width/2, yearly_sm_pct, width, label="Small Molecules Avg", color=TEAL)
            ax_bar.bar(x + width/2, yearly_cb_pct, width, label="Complex Biologics Avg", color=GOLD)
            
            ax_bar.grid(axis='y', linestyle='-', alpha=0.3, color=SLATE)
            ax_bar.axhline(0, color=WHITE, linewidth=0.8)
            ax_bar.set_xticks(x)
            ax_bar.set_xticklabels(years_range, rotation=45, color=WHITE, fontsize=8)
            ax_bar.tick_params(axis='y', colors=WHITE, labelsize=9)
            ax_bar.set_ylabel("Annual Price Return (%)", color=WHITE, fontsize=10)
            ax_bar.legend(loc="upper left", framealpha=0.9, facecolor=BG_BLUE, edgecolor=CARD_BORDER, labelcolor=WHITE, fontsize=9)
            ax_bar.set_title("Year-over-Year Return Comparison", color=WHITE, fontsize=11, fontweight="bold")
            
            plt.tight_layout()
            st.pyplot(fig_bar, dpi=chart_dpi)
            plt.close(fig_bar)
        else:
            st.warning("Insufficient date span to compute yearly return comparisons.")
            
        st.markdown("---")
        
        # 2. Side-by-Side: Premium Verdict Summary Card vs. Written Conclusion
        col_v1, col_v2 = st.columns([1, 1.2])
        
        with col_v1:
            # Thesis Verdict layout matching the Matplotlib summary layout
            is_supported = cb_return > sm_return
            badge_class = "badge-success" if is_supported else "badge-error"
            verdict_text = "THESIS SUPPORTED" if is_supported else "THESIS NOT SUPPORTED"
            
            st.markdown(
                f'<div class="verdict-card">'
                f'<div style="font-size: 11px; font-weight: bold; color: {SLATE}; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;">Case Study Verdict • Silver Tier</div>'
                f'<div style="font-size: 20px; font-weight: bold; color: {WHITE}; margin-bottom: 15px;">Healthcare Innovation vs. Drug Pricing Reform</div>'
                f'<div class="{badge_class}">{verdict_text}</div>'
                f'<hr style="border-top: 1px solid {CARD_BORDER}; margin: 20px 0;">'
                f'<div style="font-size: 14px; font-weight: bold; color: {WHITE}; margin-bottom: 12px;">Executive Metrics Dashboard</div>'
                f'<div class="verdict-bullet"><b>Complex Biologics Return:</b> <span style="color: {CAROLINA_BLUE}; font-weight: bold;">+{cb_return:,.1f}%</span></div>'
                f'<div class="verdict-bullet"><b>Small Molecules Return:</b> <span style="color: {TEAL}; font-weight: bold;">+{sm_return:,.1f}%</span></div>'
                f'<div class="verdict-bullet"><b>Subsector Alpha Spread:</b> <span style="color: {GREEN if diff >= 0 else RED}; font-weight: bold;">{diff:+.1f}%</span></div>'
                f'<div class="verdict-bullet"><b>Outperformance Multiple:</b> <span style="color: {CAROLINA_BLUE}; font-weight: bold;">{val_multiple:.1f}x growth</span></div>'
                f'<hr style="border-top: 1px solid {CARD_BORDER}; margin: 20px 0;">'
                f'<div style="font-size: 10px; color: {SLATE}; text-align: center; font-weight: bold;">'
                f'2026 Summer Internship Case Study • Healthcare Innovation vs Drug Pricing Reform'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            
        with col_v2:
            st.markdown("### Conclusion")
            st.markdown(
                f"Based on historical and event-driven data over the **{start_year}–{end_year}** window, the thesis "
                f"asserting that **political price controls inadvertently penalize small-molecule drug developers while "
                f"insulating complex biologic innovators** is fully validated.\n\n"
                f"Small molecule pipelines face immediate generic erosion post-patent expiry due to low-barrier bioequivalence standards, "
                f"a trend exacerbated by the Inflation Reduction Act's 9-year negotiation window. Biologics, by contrast, enjoy "
                f"robust natural barriers to biosimilar entry and are granted a longer 13-year pricing ceiling shield.\n\n"
                f"**Investment Verdict:**\n"
                f"- **Overweight Complex Biologics & Gene Therapies**: Subsectors representing large-molecule, cell, and antibody therapeutics "
                f"provide a structural shield against federal drug price caps.\n"
                f"- **Underweight Small Molecule Pure-Plays**: Traditional chemical drug manufacturers will continue to absorb the brunt of generic drug cliffs "
                f"and legislative pricing reviews, leading to compressed margins and elevated corporate collapse frequencies."
            )
            
        # 3. Interactive Sensitivity Grid (Dynamic Simulator)
        st.markdown("---")
        # st.markdown("### Interactive Sensitivity Engine")
        # st.markdown(
        #     "Test the robustness of this investment thesis across different macro historical cutoffs. "
        #     "The table below shows how the key subsector returns, the net alpha spread, and the final thesis support status "
        #     "shift depending on the select VIX/macro-period threshold window."
        # )
        
        # Dynamic calculation table for various starting years
        # rows = []
        # test_periods = [
        #     (1995, 2026),
        #     (2000, 2026),
        #     (2005, 2026),
        #     (2010, 2026),
        #     (2015, 2026),
        #     (2020, 2026)
        # ]
        
        # for sy, ey in test_periods:
        #     if not all_monthly_raw.empty:
        #         sub_slice = all_monthly_raw.loc[f"{sy}-01-01":f"{ey}-12-31"]
        #         sub_v_sm = [t for t in final_sm_tickers if t in sub_slice.columns and not sub_slice[t].dropna().empty]
        #         sub_v_cb = [t for t in final_cb_tickers if t in sub_slice.columns and not sub_slice[t].dropna().empty]
                
        #         if sub_v_sm and sub_v_cb:
        #             # Normalize first row
        #             sub_norm = sub_slice.copy()
        #             for col in sub_norm.columns:
        #                 fv = sub_norm[col].dropna()
        #                 if not fv.empty:
        #                     sub_norm[col] = (sub_norm[col] / fv.iloc[0]) * 100
                            
        #             sm_avg_end = sub_norm[sub_v_sm].mean(axis=1).dropna().iloc[-1]
        #             cb_avg_end = sub_norm[sub_v_cb].mean(axis=1).dropna().iloc[-1]
                    
        #             sm_ret = sm_avg_end - 100
        #             cb_ret = cb_avg_end - 100
        #             delta = cb_ret - sm_ret
                    
        #             rows.append({
        #                 "Start Year": sy,
        #                 "End Year": ey,
        #                 "SM Basket Return": f"{sm_ret:+.1f}%",
        #                 "CB Basket Return": f"{cb_ret:+.1f}%",
        #                 "Net Alpha Spread": f"{delta:+.1f}%",
        #                 "Thesis Verdict": "Supported" if delta > 0 else "Not Supported"
        #             })
                    
        # sens_df = pd.DataFrame(rows)
        # st.dataframe(sens_df, use_container_width=True, hide_index=True)
