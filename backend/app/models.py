from datetime import datetime, timezone

from sqlalchemy import Integer, String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    name: Mapped[str] = mapped_column(
        String(150), nullable=False
    )

    category: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    price: Mapped[float] = mapped_column(
        Float, nullable=False
    )

    stock_quantity: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )

    reorder_level: Mapped[int] = mapped_column(
        Integer, default=10, nullable=False
    )

class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    name: Mapped[str] = mapped_column(
        String(150), nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(150), nullable=False
    )

    lead_time_days: Mapped[int] = mapped_column(
        Integer, default=3, nullable=False
    )

    reliability_score: Mapped[float] = mapped_column(
        Float, default=0.95, nullable=False
    )

class SupplierProduct(Base):
    __tablename__ = "supplier_products"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    supplier_id: Mapped[int] = mapped_column(
        ForeignKey("suppliers.id"), nullable=False
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"), nullable=False
    )

    unit_cost: Mapped[float] = mapped_column(
        Float, nullable=False
    )

    available_quantity: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )

class ProcurementApproval(Base):
    __tablename__ = "procurement_approvals"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"), nullable=False
    )

    amount_cents: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30), default="pending", nullable=False
    )

    paypal_order_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    paypal_request_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        unique=True
    )
    paypal_capture_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        unique=True
    )
    paypal_capture_request_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        unique=True
    )
    payment_status: Mapped[str] = mapped_column(
        String(30),
        default="not_captured",
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    approved_at: Mapped[datetime | None] = mapped_column(
        nullable=True
    )