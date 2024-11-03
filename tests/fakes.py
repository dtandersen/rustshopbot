from typing import List

from rustshopbot.gateway.rust import (
    RustGateway,
    RustGatewayFactory,
    RustOrder,
    ServerConfig,
)


class FakeRustGateway(RustGateway):
    def __init__(self, map_size: int) -> None:
        self.closed = False
        self.map_size = map_size
        self.items = []

    async def get_map_size(self) -> int:
        return self.map_size

    async def list_orders(self) -> List[RustOrder]:
        return self.items

    def add_order(self, item: RustOrder) -> None:
        self.items.append(item)

    async def close(self) -> None:
        self.closed = True


class FakeRustGatewayFactory(RustGatewayFactory):
    def __init__(self) -> None:
        self.gateways = {}

    async def connect(self, server: ServerConfig) -> FakeRustGateway:
        return self.gateways[server]

    def add_socket(self, server: ServerConfig, socket: FakeRustGateway) -> None:
        self.gateways[server] = socket
