from app.database import SessionLocal, Base, engine
from app.models import Product, Supplier, SupplierProduct

Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    if db.query(Product).first() is None:
        products = [
            Product(
                name="Wireless Headphones",
                category="Electronics",
                price=79.99,
                stock_quantity=20,
                reorder_level=10
            ),
            Product(
                name="Bluetooth Speaker",
                category="Electronics",
                price=49.99,
                stock_quantity=15,
                reorder_level=10
            ),
            Product(
                name="Smart Watch",
                category="Electronics",
                price=129.99,
                stock_quantity=8,
                reorder_level=12
            )
        ]

        suppliers = [
            Supplier(
                name="TechSupply Co",
                email="tech@example.com",
                lead_time_days=3,
                reliability_score=0.95
            ),
            Supplier(
                name="Global Electronics",
                email="global@example.com",
                lead_time_days=5,
                reliability_score=0.90
            )
        ]

        db.add_all(products + suppliers)
        db.flush()

        offers = [
            SupplierProduct(
                supplier_id=suppliers[0].id,
                product_id=products[0].id,
                unit_cost=42.00,
                available_quantity=100
            ),
            SupplierProduct(
                supplier_id=suppliers[1].id,
                product_id=products[0].id,
                unit_cost=39.00,
                available_quantity=60
            ),
            SupplierProduct(
                supplier_id=suppliers[0].id,
                product_id=products[1].id,
                unit_cost=25.00,
                available_quantity=80
            ),
            SupplierProduct(
                supplier_id=suppliers[1].id,
                product_id=products[2].id,
                unit_cost=70.00,
                available_quantity=40
            )
        ]

        db.add_all(offers)
        db.commit()
        print("Sample merchant data added successfully!")
    else:
        print("Products already exist. Skipping sample data.")

finally:
    db.close()