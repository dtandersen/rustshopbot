from typing import List
from hamcrest import (
    assert_that,
    contains_inanyorder,
    equal_to,
)
import pytest

from rustshopbot.command.search_sellers import SearchSellers
from rustshopbot.entity.order import Order
from rustshopbot.gateway.rust import RustOrder, ServerConfig
from rustshopbot.repository.item_repository import JsonItemRepository
from rustshopbot.repository.server_repository import JsonServerRepository
from tests.fakes import FakeRustGateway, FakeRustGatewayFactory


@pytest.mark.asyncio
class TestSearchSellers:
    async def test_answer(self):
        socket = FakeRustGateway(3500)
        # sell: 1 sar, buy: 20 hqm
        socket.add_order(
            RustOrder(
                name="Shop 2",
                item_id=-904863145,
                quantity=1,
                amount_in_stock=1,
                currency_id=317398316,
                cost_per_item=20,
                x=1,
                y=2,
            ),
        )

        # sell: 1 diesel, buy: 1 sar
        socket.add_order(
            RustOrder(
                name="Shop 2",
                item_id=1568388703,
                quantity=1,
                amount_in_stock=1,
                currency_id=-904863145,
                cost_per_item=1,
                x=1,
                y=2,
            ),
        )
        # sell: 1000 cloth, buy: 50 scrap
        socket.add_order(
            RustOrder(
                name="Shop 3",
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
        command = SearchSellers(
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
                    name="Shop 2",
                    item="Semi-Automatic Rifle",
                    quantity=1,
                    amount_in_stock=1,
                    currency="High Quality Metal",
                    cost_per_item=20,
                    grid="A23",
                ),
            ),
        )
        assert_that(socket.closed, equal_to(True))
