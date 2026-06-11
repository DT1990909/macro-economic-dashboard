"""
Macro Economic Dashboard
========================
A four-panel dashboard tracking key UK macro indicators — CPI inflation,
Bank Rate, GDP growth, and unemployment — with trend annotations and a
plain-English economic summary.

Runs out-of-the-box on bundled illustrative data modelled on the broad
shape of the UK 2019–2025 cycle (pandemic shock, inflation spike, rate
hiking cycle, normalisation). Swap in live data by pointing the loader
at the ONS or FRED APIs — see README.

Usage:
    python macro_dashboard.py

Author: Daryl | Research & Data Analyst
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

np.random.seed(42)


# ----------------------------------------------------------------------
# 1. Data — illustrative series shaped on the recent UK cycle
# ----------------------------------------------------------------------
def build_dataset():
    dates = pd.date_range("2019-01-01", "2025-12-01", freq="MS")
    n = len(dates)
    t = np.arange(n)

    # CPI inflation (%): ~2% pre-2021, spike to ~11% in 2022, easing after
    cpi = (2.0
           + 9.0 * np.exp(-0.5 * ((t - 45) / 9) ** 2)     # 2022 spike
           - 1.2 * np.exp(-0.5 * ((t - 16) / 5) ** 2)     # 2020 dip
           + np.random.normal(0, 0.15, n))

    # Bank Rate (%): near zero, then a hiking cycle, then plateau/cuts
    bank_rate = np.clip(np.where(t < 38, 0.35,
                        np.where(t < 56, 0.35 + (t - 38) * 0.27, 5.25)),
                        0.1, 5.25)
    bank_rate = np.where(t > 70, np.maximum(5.25 - (t - 70) * 0.08, 3.75),
                         bank_rate)

    # GDP growth (% q/q, monthly interpolated): COVID crash and rebound
    gdp = (0.3
           - 20 * np.exp(-0.5 * ((t - 15) / 1.6) ** 2)    # 2020 Q2 crash
           + 16 * np.exp(-0.5 * ((t - 18) / 2.0) ** 2)    # rebound
           + np.random.normal(0, 0.25, n))

    # Unemployment (%): rises with COVID, falls in tight labour market
    unemp = (4.0
             + 1.3 * np.exp(-0.5 * ((t - 20) / 6) ** 2)
             - 0.4 * np.exp(-0.5 * ((t - 40) / 10) ** 2)
             + 0.3 * (t > 60) * (t - 60) / 24
             + np.random.normal(0, 0.05, n))

    return pd.DataFrame({"CPI Inflation (%)": cpi,
                         "Bank Rate (%)": bank_rate,
                         "GDP Growth (% q/q)": gdp,
                         "Unemployment (%)": unemp}, index=dates)


# ----------------------------------------------------------------------
# 2. Dashboard
# ----------------------------------------------------------------------
PANEL_STYLE = {
    "CPI Inflation (%)":  {"color": "#b03a3a", "target": 2.0,
                           "target_label": "BoE 2% target"},
    "Bank Rate (%)":      {"color": "#2c5f8a", "target": None},
    "GDP Growth (% q/q)": {"color": "#2c8a5f", "target": 0.0,
                           "target_label": "Zero growth"},
    "Unemployment (%)":   {"color": "#8a5f2c", "target": None},
}


def plot_dashboard(df):
    fig, axes = plt.subplots(2, 2, figsize=(13, 8))
    fig.suptitle("UK Macro Dashboard — Illustrative Data",
                 fontsize=15, fontweight="bold")

    for ax, col in zip(axes.flat, df.columns):
        style = PANEL_STYLE[col]
        ax.plot(df.index, df[col], color=style["color"], linewidth=1.8)
        if style["target"] is not None:
            ax.axhline(style["target"], color="grey", linestyle="--",
                       linewidth=1, alpha=0.7)
            ax.text(df.index[2], style["target"], style["target_label"],
                    fontsize=8, color="grey", va="bottom")
        latest = df[col].iloc[-1]
        ax.scatter([df.index[-1]], [latest], color=style["color"], zorder=5)
        ax.annotate(f"{latest:.1f}", (df.index[-1], latest),
                    textcoords="offset points", xytext=(8, 0),
                    fontsize=10, fontweight="bold", color=style["color"])
        ax.set_title(col, fontsize=11)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.grid(alpha=0.25)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig("macro_dashboard.png", dpi=150)
    print("Saved: macro_dashboard.png")


# ----------------------------------------------------------------------
# 3. Plain-English summary
# ----------------------------------------------------------------------
def economic_summary(df):
    latest = df.iloc[-1]
    yr_ago = df.iloc[-13]
    print("\nECONOMIC SUMMARY (latest readings)")
    print("=" * 58)
    for col in df.columns:
        now, then = latest[col], yr_ago[col]
        direction = "up" if now > then else "down"
        print(f"  {col:<22} {now:5.1f}  ({direction} from {then:.1f} a year ago)")

    print("\nNARRATIVE")
    print("-" * 58)
    infl = latest["CPI Inflation (%)"]
    rate = latest["Bank Rate (%)"]
    if infl > 2.5 and rate > 4:
        stance = "restrictive: inflation remains above target."
    elif infl <= 2.5 and rate > 4:
        stance = ("transitioning: inflation is near target while policy "
                  "remains tight, opening room for cuts.")
    else:
        stance = "accommodative."
    print(f"  Policy stance looks {stance}")
    print("  Replace the bundled data with live ONS/FRED feeds for a")
    print("  production dashboard (see README for the API pattern).")


# ----------------------------------------------------------------------
if __name__ == "__main__":
    df = build_dataset()
    print(f"Dataset: {len(df)} monthly observations, "
          f"{df.index[0]:%b %Y} to {df.index[-1]:%b %Y}")
    plot_dashboard(df)
    economic_summary(df)
