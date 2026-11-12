from app.ml.predict import predict_next_day
from app.advanced.llm import explain_recommendation

def merchant_chat(product_id: int, question: str, stock: int):
    if not question.strip() or len(question) > 500:
        raise ValueError("Question must contain 1 to 500 characters")
    forecast = predict_next_day(product_id)
    context = {"forecast": forecast, "simulation": {"projected_shortage": max(0, round(forecast['predicted_units']*7-stock))},
               "optimization": {"total_quantity": 0}, "merchant_question": question}
    answer = explain_recommendation(context)
    return {"question": question, "product_id": product_id, "answer": answer["explanation"],
            "mode": answer["mode"], "note": "Read-only assistant; does not place orders"}
