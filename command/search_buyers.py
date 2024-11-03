import string
from typing import Dict, List, Tuple
from command.item import Order, RustOrder
from gateway.rust import RustGatewayFactory, ServerConfig


from repository.item_repository import ItemRepository
from repository.server_repository import ServerRepository


class SearchBuyers:
    def __init__(
        self,
        socket_factory: RustGatewayFactory,
        servers: ServerRepository,
        items: ItemRepository,
    ) -> None:
        self.socket_factory = socket_factory
        self.servers = servers
        self.items = items

    async def execute(self, server_name: str, query: str) -> List[Order]:
        server = self.servers.get_server(server_name)
        socket = await self.socket_factory.connect(server)
        rust_orders = await socket.list_orders()
        map_size = await socket.get_map_size()
        await socket.close()

        orders = []
        for rust_order in rust_orders:
            grid = convert_xy_to_grid((rust_order.x, rust_order.y), map_size, False)
            grid = "".join(str(item) for item in grid)

            item_name = self.get_item_name(rust_order.item_id)
            currency_name = self.get_item_name(rust_order.currency_id)

            if currency_name.lower() == query.lower():
                orders.append(
                    Order(
                        item=item_name,
                        quantity=rust_order.quantity,
                        amount_in_stock=rust_order.amount_in_stock,
                        currency=currency_name,
                        cost_per_item=rust_order.cost_per_item,
                        grid=grid,
                    )
                )

        return orders

    def get_item_name(self, item_id: int) -> str:
        try:
            item = self.items.get_item(item_id)
            return item.name
        except ValueError:
            print(f"Item with id {item_id} not found")
            return f"{item_id}"


def convert_xy_to_grid(
    coords: tuple, map_size: float, catch_out_of_bounds: bool = True
) -> Tuple[int, int]:
    grid_size = 146.3
    grids = list(string.ascii_uppercase) + [
        f"A{letter}" for letter in list(string.ascii_uppercase)
    ]

    if coords[0] > map_size or coords[0] < 0 or coords[1] > map_size or coords[1] < 0:
        if catch_out_of_bounds:
            raise ValueError("Out of bounds")

    return grids[int(coords[0] // grid_size)], int((map_size - coords[1]) // grid_size)
