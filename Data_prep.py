import pandas as pd
import numpy as np
from path import win_to_wsl as ws

def calculate_power(wind_speed):
    """
    Calculates power (kW) based on Equation 9.82.
    Turbine: 1 MW (1000 kW)
    """

    v_ci = 3.0  # Cut-in (m/s)
    v_r = 15.0  # Rated (m/s)
    v_co = 25.0  # Cut-out (m/s)
    P_r = 1000.0  # Rated Power (kW)

    if wind_speed < v_ci or wind_speed > v_co:
        return 0.0
    elif wind_speed >= v_r:
        return P_r
    else:

        numerator = (wind_speed ** 3) - (v_ci ** 3)
        denominator = (v_r ** 3) - (v_ci ** 3)
        return P_r * (numerator / denominator)


def extrapolate_height(v_10m):
    """
    Extrapolates wind speed from 10m (measured) to 50m (turbine hub).
    Based on Eq. (9) in Demolli et al. (2019).
    alpha = 0.14 (Hellman exponent for open terrain)
    """
    return v_10m * ((50 / 10) ** 0.14)



def prepare_wind_data(csv_path, city_name):
    """
    Reads the CSV, processes a specific city, and returns a Clean DataFrame
    ready for Machine Learning (Daily samples).
    """
    print(f"--- Processing data for {city_name} ---")

    # 1. Load Data
    # Assumes Kaggle format: 'datetime' column + city columns
    try:
        df = pd.read_csv(csv_path, parse_dates=['datetime'])
    except Exception as e:
        return f"Error loading file: {e}"

    # 2. Filter for specific city
    if city_name not in df.columns:
        return f"City '{city_name}' not found in CSV columns."

    # Create a clean dataframe with just Date and WindSpeed
    data = df[['datetime', city_name]].copy()
    data.columns = ['Date', 'WindSpeed_10m']  # Rename for clarity

    #filters out the dataset to have exactly 5 years of data
    start_date = '2012-10-02'
    end_date = '2017-10-02'

    # Filter rows between start and end date
    data = data[(data['Date'] >= start_date) & (data['Date'] <= end_date)].copy()

    if data.empty:
        return f"Error: No data found between {start_date} and {end_date}."

    print(f"  - Filtered Timeframe: {start_date} to {end_date} ({len(data)} hourly rows)")
   # 3. Handle Missing Values
    """There is no missing Values in the cities of Chicago and Detroit but these rows can be used for future use"""

    missing_count = data['WindSpeed_10m'].isna().sum()
    print(f"Missing hours found: {missing_count}. Filling with interpolation...")
    data['WindSpeed_10m'] = data['WindSpeed_10m'].interpolate(method='linear')

    # Drop any remaining NaNs (e.g., if the start of the file is empty)
    data.dropna(inplace=True)

    # 4. Extrapolate Height (10m -> 50m)
    # this formula is based on the paper itself
    data['WindSpeed_50m'] = data['WindSpeed_10m'].apply(extrapolate_height)

    # 5. Synthesize Target Variable (Power Output)
    # We calculate power for every single HOUR first
    data['Hourly_Power_kW'] = data['WindSpeed_50m'].apply(calculate_power)

    # 6. Resample to Daily Data
    # Inputs: Daily Mean Wind Speed, Daily Standard Deviation
    # Output: Daily Total Power

    data.set_index('Date', inplace=True)

    daily_data = data.resample('D').agg({
        'WindSpeed_50m': ['mean', 'std'],  # Input Features
        'Hourly_Power_kW': 'sum'  # Target Variable (Total Energy per day)
    })

    # Flatten MultiIndex columns (e.g., ('WindSpeed_50m', 'mean') -> 'Mean_WindSpeed')
    daily_data.columns = ['Mean_WindSpeed', 'Std_WindSpeed', 'Total_Power_kW']

    # again this row is for feature use there is no null Values in the dataset
    daily_data.dropna(inplace=True)

    print(f"Successfully created {len(daily_data)} daily samples.")
    print(f"Head of prepared data:\n{daily_data.head()}")

    return daily_data


# ==========================================
# 3. USAGE EXAMPLE
# ==========================================

if __name__ == "__main__":
    # CHANGE THIS PATH to your actual file location
    # If using Windows, use double backslashes: "C:\\Users\\Name\\Downloads\\wind_speed.csv"
    path_to_csv = ws(R"C:\ITU\25-26Guz\Renewble energy\wind_speed_org.csv")

    # 1. Get Data for Chicago (Renamed variable to match city)
    df_chicago = prepare_wind_data(path_to_csv, 'Chicago')

    # 2. Get Data for Detroit (Renamed variable to match city)
    df_detroit = prepare_wind_data(path_to_csv, 'Detroit')

    # 3. Save files
    if isinstance(df_chicago, pd.DataFrame):
        df_chicago.to_csv("prepared_chicago.csv")
        print("Saved prepared_chicago.csv")

    if isinstance(df_detroit, pd.DataFrame):
        df_detroit.to_csv("prepared_detroit.csv")
        print("Saved prepared_detroit.csv")