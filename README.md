# Long-Term Wind Power Generation Forecasting

> **Role:** Machine Learning Engineer / Data Analyst
> **Domain:** Renewable Energy Infrastructure & Performance Simulation

This repository contains a complete machine learning pipeline for forecasting long-term wind power generation. By extending existing methodologies (Demolli et al., 2019) with modern gradient boosting frameworks and Bayesian optimization, this project evaluates the geographical transferability of predictive models.

## 🎯 Project Objective
To develop and evaluate highly accurate machine learning models capable of forecasting wind turbine power output using standard meteorological data, and to test the universality of these models by applying them to new geographical climates (Blind Testing).

## 🧠 Machine Learning Architecture
* **Benchmark Models:** LASSO Regression, k-Nearest Neighbors (kNN), Random Forest, XGBoost, and Support Vector Regression (SVR).
* **Algorithmic Extension:** Integrated **LightGBM**, optimized via Bayesian hyperparameter tuning using the **Optuna** framework.
* **Performance Metrics:** Evaluated using RMSE, MAE, and R².

## ⚙️ Physics & Data Pipeline
A critical challenge in energy forecasting is the lack of public power output datasets. This project synthesized target variables mathematically:
1. **Vertical Extrapolation:** Standard 10m meteorological wind speeds were extrapolated to a 50m turbine hub height using the Power Law (Hellman exponent).
2. **Cubic Power Curve:** Power generation was synthesized for a theoretical 1 MW turbine utilizing the Four-Region logic and physical cubic law of kinetic energy (Cut-in: 3 m/s, Rated: 15 m/s, Cut-out: 25 m/s).

## 🧪 Experimental Design
The study is divided into three analytical cases:
* **Case 1: Baseline Forecasting (Chicago):** Establishing baseline performance using the complete feature set (Daily Mean Wind Speed + Daily Standard Deviation).
* **Case 2: Input Sensitivity Analysis:** Quantifying the impact of wind volatility by removing the Standard Deviation feature.
* **Case 3: Geographical Transferability (Detroit):** Testing the generalizability of the models by freezing the Chicago-trained models and predicting power generation in Detroit as an independent blind test.

## 📂 Repository Structure

```text
Wind_power_forcast/
├── Case2_Results/            # Output tables and plots for Case 2
├── Case3_Transferability/    # Output tables and plots for Case 3 (Detroit transfer)
├── Final_Plots/              # Generated visualization assets (scatter plots, time series)
├── Final_Report_Outputs/     # Compiled analytical reports and documents
├── Data_prep.py              # Extrapolates wind speed and synthesizes cubic power curve
├── benchmark_models.py       # Configuration for LASSO, kNN, RF, XGBoost, SVR
├── Case-1.py                 # Execution script for Case 1 (Baseline)
├── case-2.py                 # Execution script for Case 2 (Sensitivity)
├── Case-3.py                 # Execution script for Case 3 (Transferability)
├── Case3_Final_Comparison.py # Analyzes and compares blind test results
├── Figure-*.py               # Scripts for generating specific data visualizations
├── prepared_chicago.csv      # Processed dataset for Base Location
├── prepared_detroit.csv      # Processed dataset for Blind Test Location
└── environment.yml           # Conda environment dependencies