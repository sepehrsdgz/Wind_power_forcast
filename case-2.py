import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

# Models
from sklearn.linear_model import Lasso
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
import xgboost as xgb
import lightgbm as lgb

# ==========================================
# 1. SETUP & DATA LOADING
# ==========================================
CSV_PATH = "prepared_chicago.csv"
OUTPUT_FOLDER = "Case2_Results"

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# Load Data
df = pd.read_csv(CSV_PATH, parse_dates=['Date'], index_col='Date')

# ---------------------------------------------------------
# CASE 2 MODIFICATION: USE ONLY MEAN WIND SPEED
# ---------------------------------------------------------
# We use double brackets [['...']] to keep it as a DataFrame (2D array)
X = df[['Mean_WindSpeed']]
y = df['Total_Power_kW']

print(f"Features selected for Case 2: {X.columns.tolist()}")

# Split (Years 1-4 Train, Year 5 Test)
# Maintaining exact same split as Case 1 for fair comparison
split = int(len(df) * 0.80)
X_train = X.iloc[:split]
y_train = y.iloc[:split]
X_test = X.iloc[split:]
y_test = y.iloc[split:]

# Scale Data (Standardization is still crucial for SVR/Lasso/kNN)
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

# ==========================================
# 2. DEFINE MODELS
# ==========================================
# Using the same hyperparameters as Case 1 to isolate the effect of the feature change
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
# 3. TRAINING & EVALUATION LOOP
# ==========================================
results_list = []
days = np.arange(len(y_test))

print(f"Training {len(models)} models for Case 2...")

for name, model in models.items():
    print(f"Processing {name}...")

    # Train
    model.fit(X_train_s, y_train)

    # Predict
    y_pred = model.predict(X_test_s)
    y_pred = np.maximum(y_pred, 0)  # Physics constraint: Power >= 0

    # Calculate Metrics
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)

    results_list.append({
        'Model': name,
        'R2': r2,
        'RMSE': rmse,
        'MAE': mae
    })

    # ---------------------------------------------------------
    # PLOT TYPE 1: TIME SERIES (Long Format)
    # ---------------------------------------------------------
    plt.figure(figsize=(16, 4))
    plt.plot(days, y_test.values, color='black', linewidth=1.1, label='Real Value', alpha=0.8)
    plt.plot(days, y_pred, color='red', linestyle='--', linewidth=1.0, label=f'{name} Forecast')

    plt.title(f'Case 2 (Mean Speed Only): {name} Forecast vs Real (1-Year)', fontsize=12)
    plt.xlabel('Day', fontsize=10)
    plt.ylabel('Power (kW)', fontsize=10)
    plt.legend(loc='upper right', fontsize='small')
    plt.grid(True, alpha=0.3)
    plt.xlim(0, 365)
    plt.tight_layout()

    plt.savefig(os.path.join(OUTPUT_FOLDER, f"Case2_TimeSeries_{name}.png"), dpi=300)
    plt.close()

    # ---------------------------------------------------------
    # PLOT TYPE 2: SCATTER PLOT
    # ---------------------------------------------------------
    plt.figure(figsize=(8, 6))

    # X-axis is the unscaled Mean Wind Speed
    wind_x = X_test['Mean_WindSpeed'].values

    plt.scatter(wind_x, y_test.values, color='red', s=15, alpha=0.6, label='Real Value')
    plt.scatter(wind_x, y_pred, color='blue', s=15, alpha=0.6, label='Predicted Value')

    plt.title(f'Case 2: Power vs Mean Wind Speed ({name})', fontsize=12)
    plt.xlabel('Mean Wind Speed (m/s)', fontsize=10)
    plt.ylabel('Power (kW)', fontsize=10)
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.savefig(os.path.join(OUTPUT_FOLDER, f"Case2_Scatter_{name}.png"), dpi=300)
    plt.close()

# ==========================================
# 4. SAVE RESULTS TABLE
# ==========================================
results_df = pd.DataFrame(results_list)
csv_path = os.path.join(OUTPUT_FOLDER, "Case2_Results_Table.csv")
results_df.to_csv(csv_path, index=False)

print("\n=== CASE 2 RESULTS ===")
print(results_df)
print(f"\nAll plots and results saved to: {OUTPUT_FOLDER}")