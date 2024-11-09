from abc import ABCMeta
from dataclasses import dataclass
import json
from typing import List


@dataclass
class Item:
    name: str
    thumbnail_url: str


class ItemRepository(metaclass=ABCMeta):
    def all(self) -> list[Item]:
        pass

    def get_item(self, id: int) -> Item:
        pass

    def find_by_name(self, query: str) -> List[Item]:
        pass


class JsonItemRepository(ItemRepository):
    def __init__(self):
        with open("./json/items.json", "r") as f:
            self.items = json.load(f)

    def get_item(self, id: int) -> Item:
        item = self.items.get(str(id))

        if item is not None:
            return Item(name=item["name"], thumbnail_url=item["link"])
        else:
            raise ValueError(f"Item with id {id} not found")

    def all(self) -> list[Item]:
        return [
            Item(name=item["name"], thumbnail_url=item["link"])
            for item in self.items.values()
        ]

    def find_by_name(self, query: str, limit: int) -> List[Item]:
        all_items = self.all()
        items = [item for item in all_items if query.lower() in item.name.lower()]
        sort_by_length = sorted(items, key=lambda x: len(x.name))
        return sort_by_length[:limit]
