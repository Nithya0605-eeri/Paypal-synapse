def score_procurement(amount_usd: float, supplier_reliability: float, stockout_probability: float, budget: float):
    if amount_usd < 0 or budget < 0 or not 0 <= supplier_reliability <= 1 or not 0 <= stockout_probability <= 1:
        raise ValueError("Invalid risk inputs")
    reasons = []
    score = 0
    if budget == 0 or amount_usd > budget:
        score += 45; reasons.append("Purchase exceeds available budget")
    if supplier_reliability < 0.8:
        score += 30; reasons.append("Supplier reliability below 80%")
    if stockout_probability > 0.75:
        score += 20; reasons.append("High projected stockout probability")
    if amount_usd > 5000:
        score += 15; reasons.append("High-value purchase requires extra review")
    score = min(score, 100)
    return {"risk_score": score, "risk_level": "high" if score >= 50 else "medium" if score >= 20 else "low",
            "reasons": reasons or ["No rule-based flags"], "method": "Transparent rule-based risk assessment",
            "requires_human_approval": True}
