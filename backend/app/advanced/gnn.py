"""A trainable one-layer GCN demonstration on the supplier-product graph.
Labels are heuristic reliability targets, NOT measured supplier outcomes.
"""

def supplier_graph(db, product_id: int):
    from app.models import Supplier, SupplierProduct
    offers = db.query(SupplierProduct, Supplier).join(Supplier, SupplierProduct.supplier_id == Supplier.id).filter(SupplierProduct.product_id == product_id).all()
    if not offers:
        raise ValueError("No suppliers for this product")
    import torch
    torch.manual_seed(42)
    costs = [float(o.unit_cost) for o, _ in offers]
    maximum = max(max(costs), 1)
    features = [[1., 0., 0., 0.]]
    for offer, supplier in offers:
        features.append([0., float(supplier.reliability_score), float(offer.unit_cost)/maximum, min(float(supplier.lead_time_days)/30, 1)])
    x = torch.tensor(features, dtype=torch.float32)
    n = len(features)
    adjacency = torch.eye(n)
    for j in range(1, n):
        adjacency[0,j] = adjacency[j,0] = 1
    degree = adjacency.sum(1).pow(-0.5)
    normalized = degree[:,None] * adjacency * degree[None,:]
    class GCN(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.layer1 = torch.nn.Linear(4, 8)
            self.layer2 = torch.nn.Linear(8, 1)
        def forward(self, inputs):
            h = torch.relu(self.layer1(normalized @ inputs))
            return torch.sigmoid(self.layer2(normalized @ h)).squeeze(-1)
    model = GCN()
    targets = torch.tensor([0.0] + [float(s.reliability_score) for _,s in offers])
    optimizer = torch.optim.Adam(model.parameters(), lr=0.03)
    for _ in range(120):
        optimizer.zero_grad()
        predictions = model(x)
        loss = ((predictions[1:] - targets[1:])**2).mean()
        loss.backward()
        optimizer.step()
    with torch.no_grad():
        predictions = model(x).tolist()
    return {"product_id": product_id, "model": "Two-layer graph convolution network (PyTorch)",
            "training": "In-request demonstration fit to supplier reliability scores; no real outcome labels",
            "suppliers": [{"supplier_id": s.id, "supplier_name": s.name,
              "graph_score": round(float(predictions[i+1]), 3), "reported_reliability": float(s.reliability_score)}
              for i,(_,s) in enumerate(offers)],
            "warning": "Illustrative graph model; scores are not independently validated risk predictions"}
