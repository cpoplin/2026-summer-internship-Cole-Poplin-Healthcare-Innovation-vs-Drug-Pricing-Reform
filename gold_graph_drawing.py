import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import gold_data_engine as gold 
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
eli_csv_file_path = os.path.join(PROJECT_ROOT, "gold_csvs", "eli_lilly_data.csv")
pfizer_csv_file_path = os.path.join(PROJECT_ROOT, "gold_csvs", "pfizer_data.csv")
gold_charts_dir = os.path.join(PROJECT_ROOT, "gold_charts")

NAVY = "#0D1B2A"
SLATE = "#8FA3B1"
CYAN = "#00E5FF"
YELLOW = "#FFD700"
navy_opaque = (0.05, 0.10, 0.25, 0.95)

def get_data_and_graph():
    if not os.path.isfile(eli_csv_file_path):
        print("Creating Eli Lilly R&D and Revenue Data csv\n\n")
        os.makedirs(os.path.dirname(eli_csv_file_path), exist_ok=True)
        columns = ["Year", "Estimated RND Percent Small", "Estimated RND Percent Large", "Small Revenue %", "Large Revenue %"]
        df_rows = []
        for y in range(2009, 2027):
            print(f"-----Fetching data for {y}-----")
            percent_small, percent_large = gold.query_and_return_estimated_rnd_percentages("eli lilly", y)
            small_rev, large_rev, tot = gold.revenue_breakdown_and_rnd("eli lilly", y)
            percent_small = percent_small * 100
            percent_large = percent_large * 100
            df_rows.append([y, percent_small, percent_large, small_rev/tot * 100, large_rev/tot * 100])
        el_df = pd.DataFrame(df_rows, columns=columns)
        el_df.to_csv(eli_csv_file_path, index=False)
    else:
        print("Using Cached Eli Lilly R&D and Revenue Data")
        el_df = pd.read_csv(eli_csv_file_path)
    
    if not os.path.isfile(pfizer_csv_file_path):
        print("Creating Pfizer R&D and Revenue Data csv\n\n")
        os.makedirs(os.path.dirname(pfizer_csv_file_path), exist_ok=True)
        columns = ["Year", "Estimated RND Percent Small", "Estimated RND Percent Large", "Small Revenue %", "Large Revenue %"]
        df_rows = []
        for y in range(2014, 2027):
            print(f"-----Fetching data for {y}-----")
            percent_small, percent_large = gold.query_and_return_estimated_rnd_percentages("pfizer", y, test=True)
            small_rev, large_rev, tot = gold.revenue_breakdown_and_rnd("pfizer", y, test=True)
            percent_small = percent_small * 100
            percent_large = percent_large * 100
            df_rows.append([y, percent_small, percent_large, small_rev/tot * 100, large_rev/tot * 100])
        pf_df = pd.DataFrame(df_rows, columns=columns)
        pf_df.to_csv(pfizer_csv_file_path, index=False)
    else:
        print("Using Cached Pfizer R&D and Revenue Data")
        pf_df = pd.read_csv(pfizer_csv_file_path)

    # Graphing for el
    os.makedirs(gold_charts_dir, exist_ok=True)
    years = el_df["Year"]
    x = np.arange(len(years))
    width = 0.35

    fig, ax = plt.subplots(figsize=(14, 6.5), facecolor=NAVY)
    ax.set_facecolor(navy_opaque)

    ax.bar(x - width/2, el_df["Estimated RND Percent Small"], width, label="R&D % Spent on Small Molecules", color=CYAN)
    ax.bar(x + width/2, el_df["Small Revenue %"], width, label="Revenue % from Small Molecules", color=YELLOW)

    ax.set_title("Eli Lilly: Small Molecule R&D vs. Revenue Share (2008–2025)", fontsize=14, fontweight='bold', pad=15, color='white')
    ax.set_xlabel("Year", color='white', fontsize=11, labelpad=10)
    ax.set_ylabel("Percentage (%)", color='white', fontsize=11, labelpad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(years.astype(int), rotation=45, color='white')
    ax.tick_params(axis='both', colors='white', labelsize=10)

    ax.grid(axis='y', linestyle='-', alpha=0.5, color=SLATE)
    ax.set_axisbelow(True)
    ax.legend(loc='upper right', framealpha=0.8, fontsize=10)

    plt.tight_layout()
    chart_path = os.path.join(gold_charts_dir, "eli_lilly_graph.png")
    plt.savefig(chart_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Chart saved to {chart_path}")

    # Graphing for pfizer
    pf_years = pf_df["Year"]
    x_pf = np.arange(len(pf_years))

    fig, ax = plt.subplots(figsize=(14, 6.5), facecolor=NAVY)
    ax.set_facecolor(navy_opaque)

    ax.bar(x_pf - width/2, pf_df["Estimated RND Percent Small"], width, label="R&D % Spent on Small Molecules", color=CYAN)
    ax.bar(x_pf + width/2, pf_df["Small Revenue %"], width, label="Revenue % from Small Molecules", color=YELLOW)

    ax.set_title("Pfizer: Small Molecule R&D vs. Revenue Share", fontsize=14, fontweight='bold', pad=15, color='white')
    ax.set_xlabel("Year", color='white', fontsize=11, labelpad=10)
    ax.set_ylabel("Percentage (%)", color='white', fontsize=11, labelpad=10)
    ax.set_xticks(x_pf)
    ax.set_xticklabels(pf_years.astype(int), rotation=45, color='white')
    ax.tick_params(axis='both', colors='white', labelsize=10)

    ax.grid(axis='y', linestyle='-', alpha=0.5, color=SLATE)
    ax.set_axisbelow(True)
    ax.legend(loc='upper right', framealpha=0.8, fontsize=10)

    plt.tight_layout()
    chart_path = os.path.join(gold_charts_dir, "pfizer_graph.png")
    plt.savefig(chart_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Chart saved to {chart_path}")

if __name__ == "__main__":
    get_data_and_graph()