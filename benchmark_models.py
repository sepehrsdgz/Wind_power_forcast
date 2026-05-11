import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Models
from sklearn.linear_model import Lasso
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
import xgboost as xgb
import lightgbm as lgb

# ==========================================
# 1. SETUP
# ==========================================
CSV_PATH = "prepared_chicago.csv"  # Ensure this matches your file
OUTPUT_FOLDER = "Final_Plots"

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# Load Data
df = pd.read_csv(CSV_PATH, parse_dates=['Date'], index_col='Date')
X = df[['Mean_WindSpeed', 'Std_WindSpeed']]
y = df['Total_Power_kW']

# Split (Years 1-4 Train, Year 5 Test)
split = int(len(df) * 0.80)
X_train = X.iloc[:split]
y_train = y.iloc[:split]
X_test = X.iloc[split:]  # We need this original X_test for the Scatter Plots (Wind Speed axis)
y_test = y.iloc[split:]

# Scale Data (For Models)
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

# ==========================================
# 2. DEFINE MODELS
# ==========================================
# Using the exact settings we established
models = {
    'LASSO': Lasso(alpha=0.1),
    'kNN': KNeighborsRegressor(n_neighbors=4, metric='minkowski'),
    'XGBoost': xgb.XGBRegressor(n_estimators=500, learning_rate=0.1, n_jobs=-1),
    'Random_Forest': RandomForestRegressor(n_estimators=10, random_state=50, n_jobs=-1),
    'SVR': SVR(kernel='rbf', C=3000, gamma=0.1, epsilon=0.1),
    'LightGBM_Tuned': lgb.LGBMRegressor(
        n_estimators=447,
        num_leaves=39,
        learning_rate=0.0216,
        feature_fraction=0.91,
        bagging_fraction=0.99,
        bagging_freq=1,
        verbose=-1
    )
}

# ==========================================
# 3. GENERATE PLOTS LOOP
# ==========================================
print(f"Generating plots for {len(models)} models...")

days = np.arange(len(y_test))

for name, model in models.items():
    print(f"Processing {name}...")

    # Train and Predict
    model.fit(X_train_s, y_train)
    y_pred = model.predict(X_test_s)
    y_pred = np.maximum(y_pred, 0)

    # ---------------------------------------------------------
    # TYPE 1: FIGURE 11 REPLICATION (Time Series - One Year)
    # ---------------------------------------------------------
    # CHANGED: Increased width to 16 and decreased height to 4
    plt.figure(figsize=(16, 4))

    plt.plot(days, y_test.values, color='black', linewidth=1.1, label='Real Value', alpha=0.8)
    plt.plot(days, y_pred, color='red', linestyle='--', linewidth=1.0, label=f'{name} Forecast')

    plt.title(f'Figure 11 Style: Daily Generated Power vs {name} Forecast (1-Year)', fontsize=12)
    plt.xlabel('Day', fontsize=10)
    plt.ylabel('Power (kW)', fontsize=10)
    plt.legend(loc='upper right', fontsize='small')
    plt.grid(True, alpha=0.3)
    plt.xlim(0, 365)

    # Tight layout helps prevent label clipping on wide figures
    plt.tight_layout()

    ts_filename = os.path.join(OUTPUT_FOLDER, f"Fig11_TimeSeries_{name}.png")
    plt.savefig(ts_filename, dpi=300, bbox_inches='tight')
    plt.close()

    # ---------------------------------------------------------
    # TYPE 2: FIGURE 6a REPLICATION (Scatter Plot)
    # ---------------------------------------------------------
    # (Kept original 8x6 ratio as scatter plots usually look better more square)
    plt.figure(figsize=(8, 6))

    wind_speed_x = X_test['Mean_WindSpeed'].values
    plt.scatter(wind_speed_x, y_test.values, color='red', s=15, alpha=0.6, label='Real Value')
    plt.scatter(wind_speed_x, y_pred, color='blue', s=15, alpha=0.6, label='Predicted Value')

    plt.title(f'Figure 6a Style: Forecasted Power vs Wind Speed ({name})', fontsize=12)
    plt.xlabel('Wind Speed (m/s)', fontsize=10)
    plt.ylabel('Power (kW)', fontsize=10)
    plt.legend()
    plt.grid(True, alpha=0.3)

    sc_filename = os.path.join(OUTPUT_FOLDER, f"Fig6a_Scatter_{name}.png")
    plt.savefig(sc_filename, dpi=300, bbox_inches='tight')
    plt.close()

print(f"\nDone! Check the folder: {OUTPUT_FOLDER}")