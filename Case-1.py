import pandas as pd
import numpy as np
import optuna
import xgboost as xgb
import lightgbm as lgb
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler


"""
this is where the magic happens haha :) in this file the models are trained based on case 1 in the paper. except There are some changes,
the parameter optimisation is made by optuna algorithm instead  of "trial-and-error approach" ; and another ml model is added to the list " lightgbm ".
there is a smal change in the data split as well, i splited the data to 80-20, secuerd the 20 (test)(year 5)  then, i made another set (validation);
Time-Series Cross-Validation. 
Fold 1: Train on Year 1 → Validate on Year 2.
Fold 2: Train on Years 1-2 → Validate on Year 3.
Fold 3: Train on Years 1-3 → Validate on Year 4.

"""


# ==========================================
# 1. LOAD DATA
# ==========================================
CSV_PATH = "prepared_chicago.csv"
df = pd.read_csv(CSV_PATH, parse_dates=['Date'], index_col='Date')

X = df[['Mean_WindSpeed', 'Std_WindSpeed']]
y = df['Total_Power_kW']

# --- THE SPLIT ---
split = int(len(df) * 0.80)

X_train_full = X.iloc[:split]  # Years 1-4 (For Optuna)
y_train_full = y.iloc[:split]

X_test_final = X.iloc[split:]  # Year 5 (Locked away)
y_test_final = y.iloc[split:]

# Scale the data based on Training stats only
scaler = StandardScaler()
X_train_full_s = scaler.fit_transform(X_train_full)
X_test_final_s = scaler.transform(X_test_final)


# ==========================================
# 2. DEFINE CROSS-VALIDATION OBJECTIVE
# ==========================================

def objective_lgb_cv(trial):
    # 1. Define Search Space
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
        'num_leaves': trial.suggest_int('num_leaves', 20, 100),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
        'feature_fraction': trial.suggest_float('feature_fraction', 0.6, 1.0),
        'bagging_fraction': trial.suggest_float('bagging_fraction', 0.6, 1.0),
        'bagging_freq': trial.suggest_int('bagging_freq', 1, 7),
        'verbose': -1,
        'n_jobs': -1
    }

    # 2. Setup Time-Series Cross-Validation (3 Folds)
    # This respects time: it never trains on the future to predict the past.
    tscv = TimeSeriesSplit(n_splits=3)

    scores = []

    # 3. The CV Loop
    for train_index, val_index in tscv.split(X_train_full_s):
        # Split into inner Train and Validation
        X_tr, X_val = X_train_full_s[train_index], X_train_full_s[val_index]
        y_tr, y_val = y_train_full.iloc[train_index], y_train_full.iloc[val_index]

        # Train Model
        model = lgb.LGBMRegressor(**params)
        model.fit(X_tr, y_tr)

        # Predict on Validation
        preds = model.predict(X_val)
        rmse = np.sqrt(mean_squared_error(y_val, preds))
        scores.append(rmse)

    # Return the Average RMSE across the 3 folds
    return np.mean(scores)


# ==========================================
# 3. RUN OPTIMIZATION
# ==========================================

if __name__ == "__main__":
    print("--- Starting Robust Cross-Validation Optimization (LightGBM) ---")

    # Run Optuna
    study = optuna.create_study(direction='minimize')
    study.optimize(objective_lgb_cv, n_trials=30)  # 30 trials is usually enough

    print("\nBest Parameters Found:")
    print(study.best_params)

    # ==========================================
    # 4. FINAL TEST (The moment of truth)
    # ==========================================

    print("\n--- Final Evaluation on Year 5 (Hidden Test Set) ---")

    # Re-train on ALL of Years 1-4 using Best Params
    best_model = lgb.LGBMRegressor(**study.best_params)
    best_model.fit(X_train_full_s, y_train_full)

    # Predict on Year 5
    final_preds = best_model.predict(X_test_final_s)
    final_rmse = np.sqrt(mean_squared_error(y_test_final, final_preds))

    print(f"Final Test RMSE: {final_rmse:.2f} kW")

    # Compare to default
    default_model = lgb.LGBMRegressor()
    default_model.fit(X_train_full_s, y_train_full)
    def_preds = default_model.predict(X_test_final_s)
    def_rmse = np.sqrt(mean_squared_error(y_test_final, def_preds))

    print(f"Default Model RMSE: {def_rmse:.2f} kW")
    print(f"Improvement: {def_rmse - final_rmse:.2f} kW")