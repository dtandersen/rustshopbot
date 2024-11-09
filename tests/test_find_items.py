from typing import List
from hamcrest import (
    assert_that,
    contains_inanyorder,
)

from rustshopbot.command.search_items import SearchItems
from rustshopbot.repository.item_repository import Item, JsonItemRepository


class TestFindItems:
    def test_answer(self):
        items = JsonItemRepository()

        command = SearchItems(items=items)
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
