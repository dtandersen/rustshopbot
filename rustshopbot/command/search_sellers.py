import logging
from typing import List

from rustshopbot.entity.order import Order
from rustshopbot.gateway.rust import RustGatewayFactory
from rustshopbot.repository.item_repository import ItemRepository
from rustshopbot.repository.server_repository import ServerRepository
from rustshopbot.util import convert_xy_to_grid


class SearchSellers:
    def __init__(
        self,
        socket_factory: RustGatewayFactory,
        servers: ServerRepository,
        items: ItemRepository,
    ) -> None:
        self.socket_factory = socket_factory
        self.servers = servers
        self.items = items
        self.logger = logging.getLogger(__name__)

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

            if item_name.lower() == query.lower():
                orders.append(
                    Order(
                        name=rust_order.name,
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
            self.logger.warn(f"Item with id {item_id} not found")
            return f"{item_id}"
