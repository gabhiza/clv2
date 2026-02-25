import os
import joblib
import cloudpickle

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bg_path = os.path.join(base_dir, "models", "bg_nbd_model.pkl")
gg_path = os.path.join(base_dir, "models", "gamma_gamma_model.pkl")

with open(bg_path, "rb") as f:
    bgf = cloudpickle.load(f)
with open(gg_path, "rb") as f:
    ggf = cloudpickle.load(f)

def predict_clv(customer_row, horizon_months=6):
    # Flexible mapping to support both internal and lab input names
    freq = float(customer_row.get("frequency", customer_row.get("Frequency", 0)))
    recency = float(customer_row.get("recency", customer_row.get("Recency", 0)))
    tenure = float(customer_row.get("T", customer_row.get("TenureDays", 0)))
    
    # Logic for monetary value:
    # Model (Gamma-Gamma) expects Average Order Value (AOV).
    # If user provides total revenue (Monetary), we must divide.
    # If user provides average (clv_df['monetary_value']), we use it.
    raw_monetary = float(customer_row.get("monetary_value", customer_row.get("monetary", 0)))
    
    # Heuristic: If raw_monetary is much larger than typical AOV and freq > 0, 
    # it's likely total revenue.
    # In the lab, we'll be explicit: assume "Monetary Value" is AOV for precision,
    # but handle the case from customers_df.csv where 'monetary' is Total Revenue.
    if "monetary" in customer_row and "monetary_value" not in customer_row:
        # Coming from customers_df.csv or simple dict with 'monetary'
        avg_order_value = raw_monetary / freq if freq > 0 else 0
    else:
        # Coming from Lab (explicitly named 'monetary_value')
        avg_order_value = raw_monetary
    
    import pandas as pd
    clv = ggf.customer_lifetime_value(
        bgf,
        pd.Series([freq]),
        pd.Series([recency]),
        pd.Series([tenure]),
        pd.Series([avg_order_value]),
        time=horizon_months,
        discount_rate=0.01
    ).iloc[0]

    return round(float(clv), 2)