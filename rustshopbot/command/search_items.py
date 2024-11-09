from typing import List
from rustshopbot.repository.item_repository import Item, ItemRepository


class SearchItems:
    def __init__(self, items: ItemRepository):
        self.items = items

    def execute(self, query: str, limit: int) -> List[Item]:
        items = self.items.find_by_name(query, limit)
        return items
