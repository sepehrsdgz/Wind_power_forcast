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
TRAIN_CITY = "Chicago"
TEST_CITY = "Detroit"

TRAIN_FILE = "prepared_chicago.csv"
TEST_FILE = "prepared_detroit.csv"  # Ensure this file exists!
OUTPUT_FOLDER = "Case3_Transferability"

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# ==========================================
# 2. LOAD & PREPARE DATA
# ==========================================
print(f"--- CASE 3: Transferability ({TRAIN_CITY} -> {TEST_CITY}) ---")

# Load Training Data (Chicago)
if not os.path.exists(TRAIN_FILE):
    raise FileNotFoundError(f"Could not find {TRAIN_FILE}")
df_train = pd.read_csv(TRAIN_FILE, parse_dates=['Date'], index_col='Date')
X_train = df_train[['Mean_WindSpeed', 'Std_WindSpeed']]
y_train = df_train['Total_Power_kW']

# Load Testing Data (Detroit)
if not os.path.exists(TEST_FILE):
    print(f"\n[WARNING] {TEST_FILE} not found!")
    print("Please generate it using 'Data_prep.py' with the Detroit wind data.")
    print("For now, we cannot proceed with the actual calculation.")
    exit()

df_test = pd.read_csv(TEST_FILE, parse_dates=['Date'], index_col='Date')
X_test = df_test[['Mean_WindSpeed', 'Std_WindSpeed']]
y_test = df_test['Total_Power_kW']

print(f"Training on {len(df_train)} days of {TRAIN_CITY} data...")
print(f"Testing on {len(df_test)} days of {TEST_CITY} data...")

# Scale Data
# IMPORTANT: Fit scaler on CHICAGO, apply same scaling to DETROIT
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

# ==========================================
# 3. DEFINE MODELS (Case 1 Config)
# ==========================================
# We use the configuration from Case 1 (Mean+Std) as it was the best performer
models = {
    'LASSO': Lasso(alpha=0.1),
    'kNN': KNeighborsRegressor(n_neighbors=4, metric='minkowski'),
    'XGBoost': xgb.XGBRegressor(n_estimators=500, learning_rate=0.1, n_jobs=-1),
    'Random_Forest': RandomForestRegressor(n_estimators=10, random_state=50, n_jobs=-1),
    'SVR': SVR(kernel='rbf', C=3000, gamma=0.1, epsilon=0.1),
    'LightGBM_Tuned': lgb.LGBMRegressor(
        n_estimators=447, num_leaves=39, learning_rate=0.0216,
        feature_fraction=0.91, bagging_fraction=0.99, bagging_freq=1, verbose=-1
    )
}

# ==========================================
# 4. TRAIN & TEST LOOP
# ==========================================
results_list = []

# For plotting, we'll take a 1-year slice of Detroit (Year 5) to keep plots readable
# Assuming Detroit data is also 5 years, we take the last 365 days
test_slice_start = len(df_test) - 365
days_slice = np.arange(365)
X_test_slice_s = X_test_s[test_slice_start:]
y_test_slice = y_test.iloc[test_slice_start:]

for name, model in models.items():
    print(f"Transferring {name}...")

    # 1. Train on ALL Chicago Data
    model.fit(X_train_s, y_train)

    # 2. Predict on ALL Detroit Data
    y_pred_full = model.predict(X_test_s)
    y_pred_full = np.maximum(y_pred_full, 0)  # Physics constraint

    # 3. Metrics
    r2 = r2_score(y_test, y_pred_full)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred_full))
    mae = mean_absolute_error(y_test, y_pred_full)

    results_list.append({'Model': name, 'R2': r2, 'RMSE': rmse, 'MAE': mae})

    # 4. Plotting (Subsection of Detroit Data)
    y_pred_slice = y_pred_full[test_slice_start:]

    plt.figure(figsize=(16, 4))
    plt.plot(days_slice, y_test_slice.values, color='green', linewidth=1.1, label=f'Real {TEST_CITY} Power', alpha=0.8)
    plt.plot(days_slice, y_pred_slice, color='red', linestyle='--', linewidth=1.0,
             label=f'{name} Prediction (Trained on {TRAIN_CITY})')

    plt.title(f'Case 3 (Transferability): {name} Predicting {TEST_CITY} (Trained on {TRAIN_CITY})', fontsize=12)
    plt.xlabel('Day (Year 5)', fontsize=10)
    plt.ylabel('Power (kW)', fontsize=10)
    plt.legend(loc='upper right', fontsize='small')
    plt.grid(True, alpha=0.3)
    plt.xlim(0, 365)
    plt.tight_layout()

    plt.savefig(os.path.join(OUTPUT_FOLDER, f"Case3_Transfer_{name}.png"), dpi=300)
    plt.close()

# ==========================================
# 5. SAVE RESULTS
# ==========================================
results_df = pd.DataFrame(results_list)
csv_path = os.path.join(OUTPUT_FOLDER, "Case3_Transferability_Results.csv")
results_df.to_csv(csv_path, index=False)

print("\n=== CASE 3 RESULTS (Transferability) ===")
print(results_df)
print(f"\nSaved to: {OUTPUT_FOLDER}")