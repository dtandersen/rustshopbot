from dataclasses import dataclass


@dataclass(frozen=True)
class RustOrder:
    item_id: int
    quantity: int
    amount_in_stock: int
    currency_id: int
    cost_per_item: int
    x: int
    y: int


@dataclass(frozen=True)
class Order:
    item: str
    quantity: int
    amount_in_stock: int
    currency: str
    cost_per_item: int
    grid: str
