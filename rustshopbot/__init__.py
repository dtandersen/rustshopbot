from rustshopbot.gateway.rust import RustPlusPyRustGatewayFactory
from rustshopbot.repository.item_repository import JsonItemRepository
from rustshopbot.repository.server_repository import JsonServerRepository


item_repository = JsonItemRepository()
server_repository = JsonServerRepository()
rust_gateway_factory = RustPlusPyRustGatewayFactory()
