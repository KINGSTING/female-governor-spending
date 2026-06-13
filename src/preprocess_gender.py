#!/usr/bin/env python3
"""
Preprocess data for gender event study: identify first change in governor sex,
create event time relative to that change, and generate leads/lags dummies.
Output: event_study_data.csv ready for DiD analysis.
"""

import os
import pandas as pd
import numpy as np

# ============================================================
# CONFIGURATION
# ============================================================
DATA_DIR = "/home/jemarjohn/Documents/Research/female-governor-spending/data"
INPUT_FILE = os.path.join(DATA_DIR, "comelec_fiscal", "fiscal+electoral_data_July 2025.xlsx")
OUTPUT_CSV = os.path.join(DATA_DIR, "event_study_data.csv")

# Election years in the panel (every 3 years from 1992 to 2022)
ELECTION_YEARS = [1992, 1995, 1998, 2001, 2004, 2007, 2010, 2013, 2016, 2019, 2022]

# ============================================================
# 1. LOAD AND CLEAN DATA
# ============================================================
print("Loading fiscal-electoral data...")
df = pd.read_excel(INPUT_FILE, sheet_name=0)
print(f"Loaded {len(df)} rows.")
print("Columns:", df.columns.tolist())

# Keep only Governor rows (by filtering on 'position' if available; otherwise assume all rows are governor)
if 'position' in df.columns:
    df = df[df['position'] == 'Governor'].copy()
    print(f"Kept only Governor rows: {len(df)}")
else:
    # If no position column, keep only rows where candidate equals incumbent (winner)
    if 'candidate' in df.columns and 'incumbent' in df.columns:
        df = df[df['candidate'] == df['incumbent']].copy()
        print(f"Kept incumbent rows: {len(df)}")
    else:
        # Fallback: keep first row per province-year (assuming it's the winner)
        df = df.drop_duplicates(subset=['lgu', 'year'], keep='first')
        print(f"Kept first row per province-year: {len(df)}")

# Ensure we have necessary columns
required_cols = ['lgu', 'year', 'sex', 'healthexp', 'pubwelf', 'ira', 'totlocsrc', 'ENC_lt']
missing = [c for c in required_cols if c not in df.columns]
if missing:
    raise KeyError(f"Missing columns: {missing}")

# Clean the 'sex' column: map non-standard codes and fill NaNs
# Observed unique values: 1.0, 0.0, 66.0, nan
print(f"Unique sex values before cleaning: {df['sex'].unique()}")
# Map 66.0 to 1 (assuming it means female), leave 0 and 1 as is, fill others with 0
def clean_sex(x):
    if pd.isna(x):
        return 0
    if x == 0:
        return 0
    if x == 1:
        return 1
    if x == 66:
        return 1
    return 0  # any other value -> male

df['sex'] = df['sex'].apply(clean_sex).astype(int)
print(f"Unique sex values after cleaning: {df['sex'].unique()}")

# Clean numeric columns (remove commas if present)
numeric_cols = ['healthexp', 'pubwelf', 'ira', 'totlocsrc', 'ENC_lt']
for col in numeric_cols:
    if col in df.columns:
        df[col] = df[col].astype(str).str.replace(',', '').str.strip()
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Log transform outcome variables (add 1 to avoid log(0))
df['log_healthexp'] = np.log(df['healthexp'] + 1)
df['log_pubwelf'] = np.log(df['pubwelf'] + 1)

# Keep only needed columns
df = df[['lgu', 'year', 'sex', 'log_healthexp', 'log_pubwelf', 
         'ira', 'totlocsrc', 'ENC_lt']].copy()
df = df.dropna(subset=['lgu', 'year', 'sex'])  # drop rows with missing essential info

# ============================================================
# 2. IDENTIFY FIRST SEX CHANGE PER PROVINCE (ELECTION YEARS ONLY)
# ============================================================
print("Identifying first sex change events...")

# Create a separate dataframe for election years only
election_df = df[df['year'].isin(ELECTION_YEARS)].copy()
election_df = election_df.sort_values(['lgu', 'year'])

# For each province, compute previous sex and change flag
election_df['prev_sex'] = election_df.groupby('lgu')['sex'].shift(1)
election_df['sex_change'] = (election_df['sex'] != election_df['prev_sex']).astype(int)
# First election year for each province has no previous -> change = 0
election_df['sex_change'] = election_df['sex_change'].fillna(0)

# Find the year of first change (if any)
first_change = election_df[election_df['sex_change'] == 1].groupby('lgu')['year'].min().reset_index()
first_change.columns = ['lgu', 'first_change_year']
print(f"Provinces with at least one sex change: {len(first_change)}")

# Merge first change year back to the full yearly panel
df = df.merge(first_change, on='lgu', how='left')

# For provinces that never changed, first_change_year remains NaN
# We will keep them as controls (event_time = NaN)

# ============================================================
# 3. CREATE EVENT TIME RELATIVE TO FIRST CHANGE
# ============================================================
def assign_event_time(row):
    if pd.isna(row['first_change_year']):
        return np.nan
    else:
        return row['year'] - row['first_change_year']

df['event_time'] = df.apply(assign_event_time, axis=1)

# Treatment indicator: 1 if event_time >= 0 (i.e., after the change year inclusive)
df['treated'] = (df['event_time'] >= 0).astype(int)

# Exclude years after a second change (if any)
# Compute second change year (optional)
second_change = election_df[election_df['sex_change'] == 1].groupby('lgu').nth(1).reset_index()
if not second_change.empty:
    second_change = second_change[['lgu', 'year']].rename(columns={'year': 'second_change_year'})
    df = df.merge(second_change, on='lgu', how='left')
    # Keep only rows where year < second_change_year (or second_change_year is NaN)
    df = df[(df['second_change_year'].isna()) | (df['year'] < df['second_change_year'])]
    print(f"Dropped years after second change for {len(second_change)} provinces.")

# ============================================================
# 4. CREATE LEADS AND LAGS DUMMIES (event_time dummies)
# ============================================================
time_points = [-3, -2, -1, 0, 1, 2, 3]
for t in time_points:
    df[f'lead_lag_{t}'] = (df['event_time'] == t).astype(int)

# ============================================================
# 5. EXPORT TO CSV
# ============================================================
output_cols = ['lgu', 'year', 'sex', 'log_healthexp', 'log_pubwelf', 
               'ira', 'totlocsrc', 'ENC_lt', 
               'first_change_year', 'event_time', 'treated',
               'lead_lag_-3', 'lead_lag_-2', 'lead_lag_-1', 
               'lead_lag_0', 'lead_lag_1', 'lead_lag_2', 'lead_lag_3']

df[output_cols].to_csv(OUTPUT_CSV, index=False)
print(f"Saved event study data to {OUTPUT_CSV}")
print(f"Total rows: {len(df)}")
print(f"Number of provinces with a first change: {df['first_change_year'].notna().sum()}")