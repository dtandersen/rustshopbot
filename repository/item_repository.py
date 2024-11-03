from abc import ABCMeta
from dataclasses import dataclass
import json


@dataclass
class Item:
    name: str
    thumbnail_url: str


class ItemRepository(metaclass=ABCMeta):
    def all(self) -> list[Item]:
        pass

    def get_item(self, id: int) -> Item:
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
