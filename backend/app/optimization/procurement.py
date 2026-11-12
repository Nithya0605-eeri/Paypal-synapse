from ortools.sat.python import cp_model


def optimize_procurement(
    offers: list[dict],
    required_quantity: int,
    budget: float
):
    if required_quantity < 0:
        raise ValueError("Required quantity cannot be negative.")

    if budget < 0:
        raise ValueError("Budget cannot be negative.")

    if not offers and required_quantity > 0:
        raise ValueError("No supplier offers available.")

    model = cp_model.CpModel()
    quantities = []

    for i, offer in enumerate(offers):
        available = int(offer["available_quantity"])

        if available < 0 or float(offer["unit_cost"]) < 0:
            raise ValueError("Invalid supplier offer.")

        quantities.append(
            model.new_int_var(0, available, f"supplier_{i}")
        )

    costs_cents = [
        int(round(float(offer["unit_cost"]) * 100))
        for offer in offers
    ]
    budget_cents = int(round(budget * 100))

    total_quantity = sum(quantities)
    total_cost = sum(
        quantities[i] * costs_cents[i]
        for i in range(len(offers))
    )

    model.add(total_quantity <= required_quantity)
    model.add(total_cost <= budget_cents)

    # Prioritize fulfilling demand, then minimize cost.
    max_cost = sum(
        int(offer["available_quantity"]) * costs_cents[i]
        for i, offer in enumerate(offers)
    )
    weight = max_cost + 1

    model.maximize(total_quantity * weight - total_cost)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10.0

    status = solver.solve(model)

    if status not in (
        cp_model.OPTIMAL,
        cp_model.FEASIBLE
    ):
        return {
            "status": "no_solution",
            "purchase_plan": [],
            "total_quantity": 0,
            "total_cost": 0,
            "unfulfilled_quantity": required_quantity
        }

    purchase_plan = []

    for i, offer in enumerate(offers):
        quantity = solver.value(quantities[i])

        if quantity > 0:
            purchase_plan.append({
                "supplier_id": offer["supplier_id"],
                "supplier_name": offer["supplier_name"],
                "quantity": quantity,
                "unit_cost": offer["unit_cost"],
                "subtotal": round(
                    quantity * float(offer["unit_cost"]), 2
                )
            })

    purchased = sum(
        item["quantity"] for item in purchase_plan
    )

    total_spent = sum(
        item["subtotal"] for item in purchase_plan
    )

    return {
        "status": (
            "optimal" if status == cp_model.OPTIMAL
            else "feasible"
        ),
        "purchase_plan": purchase_plan,
        "total_quantity": purchased,
        "total_cost": round(total_spent, 2),
        "unfulfilled_quantity": max(
            required_quantity - purchased, 0
        ),
        "budget": budget
    }