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
# 1. SETUP
# ==========================================
TRAIN_FILE = "prepared_chicago.csv"
TEST_FILE = "prepared_detroit.csv"
OUTPUT_FOLDER = "Final_Report_Outputs"

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# Load Data
df_train = pd.read_csv(TRAIN_FILE, parse_dates=['Date'], index_col='Date')
df_test = pd.read_csv(TEST_FILE, parse_dates=['Date'], index_col='Date')

# Define Models (Fixed Parameters as per Paper/Case 1)
models = {
    'LASSO': Lasso(alpha=0.1),
    'kNN': KNeighborsRegressor(n_neighbors=4, metric='minkowski'),
    'XGBoost': xgb.XGBRegressor(n_estimators=500, learning_rate=0.1, n_jobs=-1),
    'Random_Forest': RandomForestRegressor(n_estimators=10, random_state=50, n_jobs=-1),
    'SVR': SVR(kernel='rbf', C=3000, gamma=0.1, epsilon=0.1),
    'LightGBM': lgb.LGBMRegressor(n_estimators=447, num_leaves=39, learning_rate=0.0216, verbose=-1)
}


# ==========================================
# 2. EVALUATION FUNCTION
# ==========================================
def run_scenario(scenario_name, feature_cols, suffix):
    print(f"\n--- Running {scenario_name} (Features: {feature_cols}) ---")

    # Select Features
    X_train = df_train[feature_cols]
    y_train = df_train['Total_Power_kW']
    X_test = df_test[feature_cols]
    y_test = df_test['Total_Power_kW']

    # Scale
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    results = {}

    for name, model in models.items():
        # Train on Chicago
        model.fit(X_train_s, y_train)

        # Test on Detroit
        y_pred = model.predict(X_test_s)
        y_pred = np.maximum(y_pred, 0)  # Physics fix

        # Metrics
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)

        results[name] = {'R2': r2, 'RMSE': rmse, 'MAE': mae}

        # --- GENERATE SCATTER PLOT (Power vs Wind Speed) ---
        plt.figure(figsize=(8, 6))

        # Use Mean Wind Speed for X-axis (even if trained on only Mean)
        wind_speed_x = df_test['Mean_WindSpeed'].values

        plt.scatter(wind_speed_x, y_test.values, color='red', s=15, alpha=0.5, label='Real (Detroit)')
        plt.scatter(wind_speed_x, y_pred, color='blue', s=15, alpha=0.5, label=f'Predicted ({name})')

        plt.title(f'{scenario_name}: {name} Transferability', fontsize=12)
        plt.xlabel('Mean Wind Speed (m/s)', fontsize=10)
        plt.ylabel('Power (kW)', fontsize=10)
        plt.legend()
        plt.grid(True, alpha=0.3)

        filename = f"Scatter_Transfer_{name}_{suffix}.png"
        plt.savefig(os.path.join(OUTPUT_FOLDER, filename), dpi=300)
        plt.close()

    return results


# ==========================================
# 3. RUN BOTH SCENARIOS
# ==========================================
# Scenario A: With Standard Deviation (WS + STD)
results_ws_std = run_scenario("Transfer (WS + STD)", ['Mean_WindSpeed', 'Std_WindSpeed'], "WS_STD")

# Scenario B: Only Wind Speed (WS)
results_ws = run_scenario("Transfer (WS Only)", ['Mean_WindSpeed'], "WS_Only")

# ==========================================
# 4. COMPILE FINAL TABLE
# ==========================================
final_data = []
for name in models.keys():
    row = {
        'Algorithm': name,
        # WS + STD Columns
        'R2 (WS+STD)': results_ws_std[name]['R2'],
        'RMSE (WS+STD)': results_ws_std[name]['RMSE'],
        # WS Only Columns
        'R2 (WS)': results_ws[name]['R2'],
        'RMSE (WS)': results_ws[name]['RMSE']
    }
    final_data.append(row)

df_final = pd.DataFrame(final_data)
csv_path = os.path.join(OUTPUT_FOLDER, "Table_Transferability_Comparison.csv")
df_final.to_csv(csv_path, index=False)

print("\n=== FINAL COMPARISON TABLE (Saved to CSV) ===")
print(df_final.round(4))