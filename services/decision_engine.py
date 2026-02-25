def generate_decision(customer_row, churn_info, clv_value):
    """
    Realistic decision logic based on multiple customer metrics.
    RFM Segments: Champion, Potential Loyalist, At Risk, Lost, etc.
    Churn Risk: Low Risk, Medium Risk, High Risk
    """
    segment = customer_row.get("RFM_Segment", "New Customer")
    risk = churn_info.get("churn_risk", "Low Risk")
    
    # Priority defaults
    priority = "Low"
    action = "Standard Nurture"

    if risk == "High Risk":
        if clv_value > 1000:
            action = "Personal Concierge Call + VIP Retention Bonus"
            priority = "Critical"
        elif segment in ["Champion", "Loyalist"]:
            action = "Immediate Re-engagement Reward"
            priority = "High"
        else:
            action = "Automated Win-back Campaign"
            priority = "Medium"
            
    elif risk == "Medium Risk":
        if clv_value > 500:
            action = "Exclusive Upsell Offer"
            priority = "High"
        elif segment == "Potential Loyalist":
            action = "Loyalty Program Invitation"
            priority = "Medium"
        else:
            action = "Feedback Survey + Discount Coupon"
            priority = "Low"
            
    else: # Low Risk
        if clv_value > 2000:
            action = "VIP Loyalty Perks (Platinum Tier)"
            priority = "High"
        elif segment == "Champion":
            action = "Early Access to New Products"
            priority = "Medium"
        else:
            action = "Stay-in-touch Newsletter"
            priority = "Low"

    return {
        "recommended_action": action,
        "priority": priority
    }