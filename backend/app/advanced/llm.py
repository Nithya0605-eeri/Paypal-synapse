"""Optional LLM commentary. Never sends payments or executes purchasing actions."""
import os
import httpx

def explain_recommendation(context: dict):
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return {"mode": "template", "explanation": (
            f"Predicted demand: {context['forecast']['predicted_units']} units. "
            f"Projected shortage: {context['simulation']['projected_shortage']} units. "
            f"Recommended purchase: {context['optimization']['total_quantity']} units. "
            "A merchant must approve any payment."), "requires_human_approval": True}
    payload = {"model": os.getenv("SYNAPSE_LLM_MODEL", "gpt-4o-mini"),
               "messages": [{"role": "system", "content": "You are a merchant analytics assistant. Summarize only supplied data. Do not invent facts. Never authorize or execute payments. Keep under 120 words."},
                            {"role": "user", "content": str(context)[:5000]}], "max_tokens": 220}
    try:
        with httpx.Client(timeout=12) as client:
            response = client.post("https://api.openai.com/v1/chat/completions", json=payload,
                                   headers={"Authorization": f"Bearer {key}"})
            response.raise_for_status()
            answer = response.json()["choices"][0]["message"]["content"]
        return {"mode": "llm", "explanation": answer, "requires_human_approval": True}
    except (httpx.HTTPError, KeyError, IndexError, ValueError):
        return {"mode": "unavailable", "explanation": "LLM unavailable. Review the structured results instead.", "requires_human_approval": True}
