from abc import ABCMeta
from dataclasses import dataclass
import logging
from typing import List
from rustplus import RustMarker, RustSocket, ServerDetails
from rustplus.structs import RustInfo


@dataclass(frozen=True)
class ServerConfig:
    host: str
    port: int
    playerId: int
    playerToken: int


@dataclass(frozen=True)
class RustOrder:
    name: str
    item_id: int
    quantity: int
    amount_in_stock: int
    currency_id: int
    cost_per_item: int
    x: int
    y: int


class RustGateway(metaclass=ABCMeta):
    async def list_orders(self) -> List[RustOrder]:
        pass

    async def close(self) -> None:
        pass

    async def get_map_size(self) -> int:
        pass


class RustGatewayFactory(metaclass=ABCMeta):
    async def connect(self, config: ServerConfig) -> RustGateway:
        pass


class RustPlusPyRustGateway(RustGateway):
    def __init__(self, socket: RustSocket) -> None:
        self.socket: RustSocket = socket
        self.logger = logging.getLogger(__name__)

    async def list_orders(self) -> List[RustOrder]:
        self.logger.info("Listing orders")
        markers = await self.socket.get_markers()

        # dump markers to file for debugging
        # f = open("markers.json", "w")
        # for m in markers:
        #     # obj_vars = dir(m)
        #     # sells = m.sell_orders
        #     # obj_vars["sell_orders"] = vars(sells[0])
        #     # pprint.pp(obj_vars, stream=f)
        #     f.write(objstr(m))
        #     for so in m.sell_orders:
        #         f.write(objstr(so))

        orders = []
        for marker in markers:
            if marker.type != RustMarker.VendingMachineMarker:
                continue
            # obj_vars = vars(marker)
            # pprint.pp(obj_vars)
            for marker_sell_order in marker.sell_orders:
                # obj_vars = vars(marker_sell_order)
                # pprint.pp(obj_vars)

                order = RustOrder(
                    name=marker.name,
                    item_id=marker_sell_order.item_id,
                    quantity=marker_sell_order.quantity,
                    amount_in_stock=marker_sell_order.amount_in_stock,
                    currency_id=marker_sell_order.currency_id,
                    cost_per_item=marker_sell_order.cost_per_item,
                    x=marker.x,
                    y=marker.y,
                )
                orders.append(order)

        return orders

    async def get_map_size(self) -> int:
        self.logger.info("Getting map size")
        info: RustInfo = await self.socket.get_info()
        return info.size

    async def close(self) -> None:
        self.logger.info("Closing RustPlusRustGateway")
        await self.socket.disconnect()


class RustPlusPyRustGatewayFactory(RustGatewayFactory):
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    async def connect(self, config: ServerConfig) -> RustGateway:
        self.logger.info(f"Connecting to {config.host}:{config.port}...")
        server_details = ServerDetails(
            config.host, config.port, config.playerId, config.playerToken
        )
        socket = RustSocket(server_details)
        await socket.connect()

        return RustPlusPyRustGateway(socket)
