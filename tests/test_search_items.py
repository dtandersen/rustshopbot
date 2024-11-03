from typing import List
from hamcrest import (
    assert_that,
    contains_inanyorder,
    equal_to,
)
import pytest

from command.item import Order, RustOrder
from command.list_items import ListItems
from gateway.rust import ServerConfig
from repository.item_repository import JsonItemRepository
from repository.server_repository import JsonServerRepository
from tests.fakes import FakeRustGateway, FakeRustGatewayFactory


@pytest.mark.asyncio
class TestListItems:
    async def test_answer(self):
        socket = FakeRustGateway(3500)
        # sar for 20 hqm
        socket.add_order(
            RustOrder(
                item_id=-904863145,
                quantity=1,
                amount_in_stock=1,
                currency_id=317398316,
                cost_per_item=20,
                x=1,
                y=2,
            ),
        )

        # 1 diesel for a sar
        socket.add_order(
            RustOrder(
                item_id=1568388703,
                quantity=1,
                amount_in_stock=1,
                currency_id=-904863145,
                cost_per_item=1,
                x=1,
                y=2,
            ),
        )
        # 1000 cloth for 50 scrap
        socket.add_order(
            RustOrder(
                item_id=-858312878,
                quantity=1000,
                amount_in_stock=5,
                currency_id=-932201673,
                cost_per_item=50,
                x=1000,
                y=1000,
            ),
        )

        socket_factory = FakeRustGatewayFactory()
        socket_factory.add_socket(
            ServerConfig(
                host="127.0.0.1", port=28082, playerId=12345, playerToken=67890
            ),
            socket,
        )
        command = ListItems(
            socket_factory=socket_factory,
            servers=JsonServerRepository("tests/test-config.json"),
            items=JsonItemRepository(),
        )
        result = await command.execute(
            server_name="Test Server", query="Semi-Automatic Rifle"
        )
        assert_that(
            result,
            contains_inanyorder(
                Order(
                    item="Semi-Automatic Rifle",
                    quantity=1,
                    amount_in_stock=1,
                    currency="High Quality Metal",
                    cost_per_item=20,
                    grid="A23",
                ),
                Order(
                    item="Diesel Fuel",
                    quantity=1,
                    amount_in_stock=1,
                    currency="Semi-Automatic Rifle",
                    cost_per_item=1,
                    grid="A23",
                ),
            ),
        )
        assert_that(socket.closed, equal_to(True))
