import pandas as pd
import numpy as np
import os
import joblib
import cloudpickle
from xgboost import XGBClassifier
from lifetimes import BetaGeoFitter, GammaGammaFitter
from lifetimes.utils import summary_data_from_transaction_data

# Paths
base_dir = os.path.dirname(os.path.abspath(__file__))
raw_data_path = os.path.join(base_dir, "data", "online_retail_II.csv.xls")
engineered_data_path = os.path.join(base_dir, "data", "customers_df.csv")
models_dir = os.path.join(base_dir, "models")

if not os.path.exists(models_dir):
    os.makedirs(models_dir)

print("--- Step 1: Retraining CLV Models (Lifetimes) ---")
# 1. Load and Clean Raw Data
df = pd.read_csv(raw_data_path)
df.drop_duplicates(inplace=True)
df.dropna(inplace=True)
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df['TotalPrice'] = df['Quantity'] * df['Price']

# 2. Prepare Lifetimes Summary Data
clv_df = summary_data_from_transaction_data(
    transactions=df,
    customer_id_col='Customer ID',
    datetime_col='InvoiceDate',
    monetary_value_col='TotalPrice',
    observation_period_end=df['InvoiceDate'].max()
)

# 3. Fit BG/NBD Model
bgf = BetaGeoFitter(penalizer_coef=0.001)
bgf.fit(clv_df['frequency'], clv_df['recency'], clv_df['T'])
with open(os.path.join(models_dir, "bg_nbd_model.pkl"), "wb") as f:
    cloudpickle.dump(bgf, f)
print("Saved BG/NBD model.")

# 4. Fit Gamma-Gamma Model
gg_df = clv_df[clv_df['monetary_value'] > 0]
ggf = GammaGammaFitter(penalizer_coef=0.001)
ggf.fit(gg_df['frequency'], gg_df['monetary_value'])
with open(os.path.join(models_dir, "gamma_gamma_model.pkl"), "wb") as f:
    cloudpickle.dump(ggf, f)
print("Saved Gamma-Gamma model.")

print("\n--- Step 2: Retraining Churn Model (XGBoost) ---")
# 1. Load Engineered Data
customers_df = pd.read_csv(engineered_data_path)

# 2. Features and Target
FEATURES = [
    'Frequency', 
    'monetary', 
    'PurchaseRate', 
    'AvgInterpurchaseDays', 
    'ActiveMonths', 
    'TenureDays', 
    'InactivityRatio'
]
TARGET = 'ChurnLabel'

# 3. Fit XGBoost Model
xgb_model = XGBClassifier(
    n_estimators=300,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective='binary:logistic',
    eval_metric='auc',
    random_state=42
)

X = customers_df[FEATURES]
y = customers_df[TARGET]

xgb_model.fit(X, y)
joblib.dump(xgb_model, os.path.join(models_dir, "xgb_churn_model.pkl"))
joblib.dump(FEATURES, os.path.join(models_dir, "churn_features.pkl"))
print("Saved XGBoost churn model and features list.")

print("\nRetraining Complete!")
