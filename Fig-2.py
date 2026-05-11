import pandas as pd
import matplotlib.pyplot as plt

"""
this file generates the Wind speed characteristics of selected locations. 
Averages every day of 5 year ex 1 january 2012,2013,2014,2015,2016,2017 to one day.
and plots
"""




# ==========================================
# 1. SETUP - Load your prepared data
# ==========================================


file_chicago = "prepared_chicago.csv"
file_detroit = "prepared_detroit.csv"


def get_typical_year_profile(csv_path):
    """
    Calculates the 365-day 'Typical Year' profile by averaging
    wind speeds across all 5 years for each day of the year.
    Ref: Section 5.1 of Demolli et al. (Page 7)
    """
    # Load Data
    try:
        df = pd.read_csv(csv_path, parse_dates=['Date'])
    except Exception as e:
        print(f"Could not load {csv_path}: {e}")
        return None

    # Extract 'Day of Year' (1 to 366)
    df['DayOfYear'] = df['Date'].dt.dayofyear

    # Exclude Leap Day (366) to keep it clean at 365 days (Standard practice)
    df = df[df['DayOfYear'] <= 365]

    # Group by DayOfYear and calculate Mean
    typical_profile = df.groupby('DayOfYear')['Mean_WindSpeed'].mean()

    return typical_profile


# ==========================================
# 2. GENERATE PROFILES
# ==========================================

profile_chicago = get_typical_year_profile(file_chicago)
profile_detroit = get_typical_year_profile(file_detroit)

# ==========================================
# 3. PLOTTING
# ==========================================

if profile_chicago is not None and profile_detroit is not None:

    # Create subplots (2 rows, 1 column) - Expand figsize if you add more cities
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(10, 8), sharex=True)

    # --- PLOT 1: CHICAGO ---
    ax1 = axes[0]
    ax1.plot(profile_chicago.index, profile_chicago.values, color='black', linewidth=1)
    ax1.set_title('Chicago', fontsize=10, fontweight='bold', pad=-14, y=0.95)  # Title inside plot like paper
    ax1.set_ylabel('Wind Speed (m/s)', fontsize=9)
    # Remove top and right spines to look like the paper
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.set_ylim(0, 12)  # Adjust based on your data max

    # --- PLOT 2: DETROIT ---
    ax2 = axes[1]
    ax2.plot(profile_detroit.index, profile_detroit.values, color='black', linewidth=1)
    ax2.set_title('Detroit', fontsize=10, fontweight='bold', pad=-14, y=0.95)
    ax2.set_ylabel('Wind Speed (m/s)', fontsize=9)
    ax2.set_xlabel('Day', fontsize=10, fontweight='bold')
    # Remove top and right spines
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.set_ylim(0, 12)

    # General Layout adjustments
    plt.xlim(0, 365)
    plt.tight_layout()

    # Save
    plt.savefig("Figure2_WindCharacteristics.png", dpi=300)
    print("Figure 4 saved successfully.")

    plt.show()
else:
    print("Error: Could not generate plots because data files were missing.")