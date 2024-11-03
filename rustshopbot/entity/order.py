from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    name: str
    item: str
    quantity: int
    amount_in_stock: int
    currency: str
    cost_per_item: int
    grid: str
