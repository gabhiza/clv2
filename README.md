# 📊 Customer Lifetime Value Prediction System

## 📌 Project Overview

A comprehensive customer analytics system that predicts customer lifetime value (CLV), identifies churn risk, and provides actionable retention strategies. The system processes retail transaction data to segment customers, forecast future revenue, and optimize marketing spend through data-driven decision making.

---

# 🚀 Why This Project Matters

This system directly impacts business profitability by:

* Identifying high-value customers for targeted retention efforts
* Predicting churn risk before customers disengage
* Optimizing marketing spend based on expected ROI
* Providing real-time customer insights for strategic decision-making
* Reducing customer acquisition costs through improved retention

---

# 📂 Data Understanding

The system uses the **Online Retail II** dataset containing:

* **1,067,371 transactions** from December 2009 to December 2011
* **5,878 unique customers** across 41 countries

### Transaction features

* Invoice
* StockCode
* Description
* Quantity
* InvoiceDate
* Price
* Customer ID
* Country

### Primary market

* United Kingdom (majority of transactions)

### Product categories

* Home goods
* Decorations
* Seasonal items
* Gifts

### Key Data Quality Issues Addressed

* Removed duplicate records and null values
* Filtered out negative quantities and prices (returns/cancellations)
* Converted InvoiceDate to datetime format

**Final clean dataset:** **779,425 transactions**

---

# ⚙️ Feature Engineering

Created comprehensive customer-level features through RFM analysis and behavioral metrics.

## Core RFM Features

* **Recency:** Days since last purchase (calculated from latest transaction date)
* **Frequency:** Number of unique invoices per customer
* **Monetary:** Total revenue per customer

## Advanced Behavioral Features

* **Purchase Rate:** Transactions per day of customer tenure
* **Average Interpurchase Days:** Mean time between consecutive purchases
* **Active Months:** Number of unique months with purchases
* **Tenure Days:** Duration from first to last purchase
* **Inactivity Ratio:** Recency divided by tenure (risk indicator)

## Derived Business Metrics

* **Profitability Score:** Weighted combination of monetary, frequency, and purchase rate
* **Expected Revenue (30D):** Projected revenue based on daily averages
* **Retention ROI:** Expected revenue minus retention costs

---

# 🤖 Modeling Approach

## Churn Prediction

* XGBoost classifier trained on behavioral features

### Features

* Frequency
* Monetary
* Purchase Rate
* Interpurchase Days
* Active Months
* Tenure
* Inactivity Ratio

### Risk categorization

* High (>70% probability)
* Medium (40-70%)
* Low (<40%)

### Evaluation metrics

* AUC-ROC
* Precision-recall curves

---

## CLV Prediction

* BG/NBD (Beta Geometric Negative Binomial Distribution) for transaction frequency
* Gamma-Gamma model for monetary value prediction
* 6-month CLV horizon with 1% discount rate
* Handles irregular purchase patterns and varying order values

---

## Customer Segmentation

* RFM scoring (1-4 scale for each dimension)

### Four key segments

* Champion

* At Risk

* Potential Loyalist

* Lost

* Automated action recommendations based on segment profitability

---

# 📈 Results & Insights

## Customer Distribution

| Segment             |     Customers |
| ------------------- | ------------: |
| Lost customers      | 2,736 (46.5%) |
| Potential Loyalists | 1,843 (31.4%) |
| Champions           | 1,110 (18.9%) |
| At Risk             |    189 (3.2%) |

---

## Key Findings

* Top 10 customers generate disproportionate revenue share
* Peak purchasing hours: 10 AM - 3 PM
* Strong seasonal patterns around holidays
* International markets show lower frequency but higher average order values
* Customer tenure strongly correlates with lifetime value

---

# 🏗️ System Design

## Web Application Architecture

* Flask-based dashboard with real-time analytics
* RESTful APIs for customer predictions and simulations
* Interactive customer database with filtering and sorting
* Retention ROI simulator for scenario planning
* Laboratory module for testing RFM calculations

---

## Data Pipeline

1. Raw transaction ingestion and cleaning
2. Feature engineering and customer-level aggregation
3. Model training and validation
4. Real-time prediction serving
5. Decision engine for action recommendations

---

## Key Components

* **app.py:** Main Flask application and API endpoints
* **services/:** Churn prediction, CLV calculation, and decision logic
* **models/:** Trained XGBoost, BG/NBD, and Gamma-Gamma models
* **templates/:** Interactive dashboard and customer views

---

# ▶️ How to Run

## Installation

```bash
# Install main requirements
pip install -r requirements.txt

# Install Flask app requirements
cd flask_app
pip install -r requirements.txt
```

## Data Preparation

```bash
# Run exploratory analysis and feature engineering
jupyter notebook Exploratory_Data_Analysis.ipynb

# Train models (if not already trained)
python flask_app/retrain_models.py
```

## Start Application

```bash
cd flask_app
python app.py
```

Access the dashboard at ** http://127.0.0.1:5000**

---

# 🌐 Deployment

**Live Application:** The system is deployed on Render and available at:

* **Dashboard:** https://clv3-dashboard.onrender.com
* **API endpoints:** https://clv3-dashboard.onrender.com/api/

---

## Deployment Configuration

* Uses Gunicorn WSGI server for production
* Automatic builds from GitHub repository
* Configured via render.yaml in flask_app directory
* Environment variables for model paths and data sources

---

# 📁 Project Structure

```text
CLV3/
|-- Exploratory_Data_Analysis.ipynb    # Data analysis and feature engineering
|-- online_retail_II.csv.xls          # Raw transaction dataset
|-- requirements.txt                   # Main Python dependencies
|-- flask_app/                        # Web application
|   |-- app.py                        # Main Flask application
|   |-- services/                     # Business logic modules
|   |   |-- churn_service.py          # Churn prediction logic
|   |   |-- clv_service.py           # CLV calculation
|   |   |-- decision_engine.py        # Action recommendations
|   |   -- pipeline.py                # Data processing utilities
|   |-- models/                       # Trained ML models
|   |   |-- xgb_churn_model.pkl       # XGBoost churn classifier
|   |   |-- bg_nbd_model.pkl          # BG/NBD frequency model
|   |   |-- gamma_gamma_model.pkl     # Gamma-Gamma monetary model
|   |   -- churn_features.pkl         # Feature names for churn model
|   |-- templates/                    # HTML templates
|   |-- data/                         # Processed customer data
|   -- requirements.txt               # Flask app dependencies
```

---

# 🔮 Future Improvements

## Model Enhancements

* Incorporate temporal dynamics with LSTM/sequence models
* Add product category preferences to segmentation
* Implement multi-touch attribution for marketing channels
* Ensemble modeling for improved prediction accuracy

---

## Business Intelligence

* Automated A/B testing for retention campaigns
* Real-time alert system for high-value customer churn
* Integration with email marketing platforms
* Customer lifetime value cohort analysis

---

## Technical Scalability

* Database integration for larger datasets
* API rate limiting and caching
* Docker containerization for deployment
* Cloud deployment with auto-scaling

---

## Advanced Analytics

* Market basket analysis for cross-selling opportunities
* Geographic expansion recommendations
* Price elasticity modeling
* Competitor analysis integration
