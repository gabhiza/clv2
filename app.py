from flask import Flask, jsonify, request, render_template
import pandas as pd

import os

import services.churn_service as churn_service
import services.clv_service as clv_service
import services.decision_engine as decision_engine

app = Flask(__name__)

# ✅ Load ENGINEERED customer-level table
base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, "data", "customers_df.csv")

print(f"DEBUG: base_dir = {base_dir}")
print(f"DEBUG: data_path = {data_path}")

if not os.path.exists(data_path):
    print(f"ERROR: Data file not found at {data_path}")
    # Create empty df as fallback to prevent crash, but log error
    customer_df = pd.DataFrame(columns=["Customer ID", "CLV_6M", "RFM_Segment", "ChurnRisk"])
else:
    try:
        customer_df = pd.read_csv(data_path)
        print(f"DEBUG: Successfully loaded {len(customer_df)} customers.")
    except Exception as e:
        print(f"ERROR feeding data: {e}")
        customer_df = pd.DataFrame(columns=["Customer ID", "CLV_6M", "RFM_Segment", "ChurnRisk"])


@app.route("/")
@app.route("/dashboard")
def dashboard():
    # 1. Churn Prediction Analytics
    churn_counts = customer_df.groupby(["RFM_Segment", "ChurnRisk"]).size().unstack(fill_value=0).to_dict(orient="index")
    
    # 2. CLV Analytics
    avg_clv_segment = customer_df.groupby("RFM_Segment")["CLV_6M"].mean().to_dict()
    
    # 3. Short-term Revenue Prediction (30D)
    total_expected_revenue = customer_df["ExpectedRevenue30D"].sum()
    revenue_by_segment = customer_df.groupby("RFM_Segment")["ExpectedRevenue30D"].sum().to_dict()
    
    summary = {
        "total_customers": len(customer_df),
        "total_expected_revenue": round(total_expected_revenue, 2),
        "avg_clv": round(customer_df["CLV_6M"].mean(), 2),
        "high_risk_count": len(customer_df[customer_df["ChurnRisk"] == "High Risk"])
    }
    
    return render_template(
        "dashboard.html", 
        churn_counts=churn_counts,
        avg_clv_segment=avg_clv_segment,
        revenue_by_segment=revenue_by_segment,
        summary=summary
    )


@app.route("/api/customer/<customer_id>", methods=["GET"])
def api_customer(customer_id):
    try:
        cid = int(float(customer_id))
        customer = customer_df[customer_df["Customer ID"] == cid]
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid customer ID"}), 400

    if customer.empty:
        return jsonify({"error": "Customer not found"}), 404

    row = customer.iloc[0]

    churn_info = churn_service.predict_churn(row)
    clv_value = row["CLV_6M"]

    decision = decision_engine.generate_decision(row, churn_info, clv_value)

    return jsonify({
        "customer_id": customer_id,
        "clv_6m": clv_value,
        **churn_info,
        **decision
    })


@app.route("/api/simulate-retention", methods=["POST"])
def simulate_retention():
    data = request.json

    clv = data["clv"]
    retention_cost = data["retention_cost"]
    success_prob = data.get("success_probability", 0.3)

    roi = (clv * success_prob) - retention_cost

    return jsonify({
        "expected_gain": round(clv * success_prob, 2),
        "roi": round(roi, 2),
        "recommend": roi > 0
    })


@app.route("/customers")
def customers():
    data = customer_df.sort_values(
        by=["ChurnRisk", "CLV_6M"],
        ascending=[True, False]
    ).to_dict(orient="records")

    return render_template("customers.html", customers=data)

@app.route("/customers/<customer_id>")
def customer_detail(customer_id):
    try:
        cid = int(float(customer_id))
        customer = customer_df[customer_df["Customer ID"] == cid]
    except (ValueError, TypeError):
        return "Invalid customer ID", 400

    if customer.empty:
        return "Customer not found", 404

    return render_template(
        "customer_detail.html",
        customer=customer.iloc[0].to_dict()
    )

@app.route("/simulator")
def simulator():
    return render_template("simulator.html")

@app.route("/api/predict-churn-lab", methods=["POST"])
def predict_churn_lab():
    data = request.json
    try:
        result = churn_service.predict_churn(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/predict-clv-lab", methods=["POST"])
def predict_clv_lab():
    data = request.json
    try:
        # Expecting frequency, recency, T, monetary_value
        clv_6m = clv_service.predict_clv(data)
        return jsonify({"clv_6m": clv_6m})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/calculate-lab", methods=["POST"])
def calculate_lab():
    data = request.json
    try:
        # Basic RFM Logic (normalized to 100 for simulation)
        # Assuming typical max values for scaling: F=50, M=5000, R=365
        f = float(data.get("Frequency", 0))
        m = float(data.get("monetary", data.get("monetary_value", 0)))
        r = float(data.get("Recency", 0))
        
        # Simple weighted score (Higher F and M is better, Lower R is better)
        f_norm = min(f / 50.0, 1.0)
        m_norm = min(m / 5000.0, 1.0)
        r_norm = max(1.0 - (r / 365.0), 0.0)
        
        rfm_score = (f_norm * 0.4 + m_norm * 0.4 + r_norm * 0.2) * 100
        
        # Profitability Score (Example: 30% margin - estimated servicing cost)
        profitability = (m * 0.3) - 15.0
        
        # Segment Mapping based on RFM score
        if rfm_score >= 80:
            segment = "Champion"
        elif rfm_score >= 60:
            segment = "Loyalist"
        elif rfm_score >= 40:
            segment = "Potential Loyalist"
        elif rfm_score >= 20:
            segment = "At Risk"
        else:
            segment = "Hibernating"
        
        # Strategic Recommendation using decision engine
        # We estimate risk based on Recency for the lab
        risk_level = "Low Risk" if r < 60 else ("Medium Risk" if r < 180 else "High Risk")
        
        # Estimated CLV for decision logic (simple proxy)
        clv_proxy = profitability * 12
        
        decision = decision_engine.generate_decision(
            {"RFM_Segment": segment},
            {"churn_risk": risk_level},
            clv_proxy
        )

        return jsonify({
            "rfm_score": round(rfm_score, 1),
            "segment": segment,
            "profitability_score": round(profitability, 2),
            "recommendation": decision["recommended_action"],
            "priority": decision["priority"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/simulate", methods=["POST"])
def api_simulate():
    data = request.json
    
    # Mock row to satisfy engine interface
    customer_row = {
        "RFM_Segment": data.get("segment", "Champion")
    }
    
    churn_info = {
        "churn_risk": data.get("risk", "Low Risk")
    }
    
    clv_val = float(data.get("clv", 0))
    
    decision = decision_engine.generate_decision(customer_row, churn_info, clv_val)
    
    return jsonify({
        "input": data,
        **decision
    })

if __name__ == "__main__":
    import os
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

