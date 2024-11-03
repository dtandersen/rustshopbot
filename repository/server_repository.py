from abc import ABCMeta
import json
from gateway.rust import ServerConfig


class ServerRepository(metaclass=ABCMeta):
    def get_server(self, id: int) -> ServerConfig:
        pass


class JsonServerRepository(ServerRepository):
    def __init__(self, file: str = "./json/config.json"):
        with open(file, "r") as f:
            self.config = json.load(f)

    def get_server(self, name: str) -> ServerConfig:
        # print(self.config.get("servers"))
        servers = self.config.get("servers")
        server = next((server for server in servers if server["name"] == name), None)
        # print(server)
        if server is not None:
            return ServerConfig(
                host=server["ip"],
                port=int(server["port"]),
                playerId=int(server["playerId"]),
                playerToken=int(server["playerToken"]),
            )
        else:
            raise ValueError(f"Server with name {name} not found")
