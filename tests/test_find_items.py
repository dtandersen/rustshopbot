from typing import List
from hamcrest import (
    assert_that,
    contains_inanyorder,
    equal_to,
)
import pytest

from rustshopbot.command.search_items import SearchItems
from rustshopbot.command.search_sellers import SearchSellers
from rustshopbot.entity.order import Order
from rustshopbot.gateway.rust import RustOrder, ServerConfig
from rustshopbot.repository.item_repository import Item, JsonItemRepository
from rustshopbot.repository.server_repository import JsonServerRepository
from tests.fakes import FakeRustGateway, FakeRustGatewayFactory


# @pytest.mark.asyncio
class TestFindItems:
    def test_answer(self):
        items = JsonItemRepository()

        command = SearchItems(
            items=JsonItemRepository(),
        )
        result = command.execute(query="jack", limit=2)
        assert_that(
            result,
            contains_inanyorder(
                Item(
                    name="Jacket",
                    thumbnail_url="https://rustlabs.com/img/items180/jacket.png",
                ),
                Item(
                    name="Pump Jack",
                    thumbnail_url="https://rustlabs.com/img/items180/mining.pumpjack.png",
                ),
            ),
        )
