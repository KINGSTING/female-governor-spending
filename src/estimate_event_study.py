#!/usr/bin/env python3
"""
Event study estimation using PanelOLS (linearmodels).
Drops absorbed dummies automatically and uses check_rank=False.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from linearmodels.panel import PanelOLS

# ============================================================
# CONFIGURATION
# ============================================================
DATA_DIR = "/home/jemarjohn/Documents/Research/female-governor-spending/data"
INPUT_CSV = os.path.join(DATA_DIR, "event_study_data.csv")
OUTPUT_DIR = os.path.join(DATA_DIR, "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Outcomes
OUTCOMES = ['log_healthexp', 'log_pubwelf']
CONTROLS = ['ira', 'totlocsrc', 'ENC_lt']

# ============================================================
# LOAD DATA
# ============================================================
print("Loading event study data...")
df = pd.read_csv(INPUT_CSV)
print(f"Loaded {len(df)} rows.")

# Fill missing event_time (never-treated) with a sentinel
df['event_time'] = df['event_time'].fillna(-999).astype(int)

# Ensure outcome and controls are numeric
for col in OUTCOMES + CONTROLS:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df = df.dropna(subset=OUTCOMES + CONTROLS)

# Set panel index
df = df.set_index(['lgu', 'year'])

# ============================================================
# SIMPLE DiD (pre/post) FOR COMPARISON
# ============================================================
print("\n--- Simple DiD (pre/post) ---")
did_results = {}
for outcome in OUTCOMES:
    exog = df[['treated'] + CONTROLS].assign(const=1)
    y = df[outcome]
    model = PanelOLS(y, exog, entity_effects=True, time_effects=True, drop_absorbed=True, check_rank=False)
    res = model.fit(cov_type='clustered', cluster_entity=True)
    did_results[outcome] = res
    print(f"\n{outcome}:")
    print(res)

# ============================================================
# EVENT STUDY USING LEADS/LAGS
# ============================================================
print("\n--- Event Study (leads/lags) ---")
event_results = {}
for outcome in OUTCOMES:
    # Use leads/lags dummies (excluding -1 to avoid collinearity)
    lead_lag_cols = [f'lead_lag_{t}' for t in [-3, -2, 0, 1, 2, 3]]
    lead_lag_cols = [c for c in lead_lag_cols if c in df.columns]
    exog = df[lead_lag_cols + CONTROLS].assign(const=1)
    y = df[outcome]
    model = PanelOLS(y, exog, entity_effects=True, time_effects=True, drop_absorbed=True, check_rank=False)
    res = model.fit(cov_type='clustered', cluster_entity=True)
    event_results[outcome] = res
    print(f"\n{outcome}:")
    print(res)

    # Extract coefficients for event study plot (only for variables that exist in params)
    coefs = {}
    se = {}
    for col in lead_lag_cols:
        if col in res.params.index:
            t = int(col.split('_')[-1])
            coefs[t] = res.params[col]
            se[t] = res.std_errors[col]
    # Add reference period -1 with coefficient 0
    coefs[-1] = 0
    se[-1] = 0

    # Sort by time
    times = sorted(coefs.keys())
    y_coef = [coefs[t] for t in times]
    y_ci = [1.96 * se[t] for t in times]

    # Create event study plot
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.7)
    ax.axvline(x=-0.5, color='black', linestyle='-', alpha=0.5, label='Election year (t=0)')
    ax.errorbar(times, y_coef, yerr=y_ci, fmt='o', capsize=5, color='steelblue', ecolor='lightgray', elinewidth=2)
    ax.set_xlabel('Years relative to first female governor election')
    ax.set_ylabel(f'Effect on {outcome}')
    ax.set_title(f'Event Study: Impact of Female Governor on {outcome}')
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, f'event_study_{outcome}.png'), dpi=150)
    plt.close()
    print(f"Saved plot to {OUTPUT_DIR}/event_study_{outcome}.png")

print("All event study estimation completed.")