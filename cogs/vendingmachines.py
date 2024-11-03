from collections import defaultdict
import time
from discord import app_commands
from discord.ext import commands
import discord
import json
from typing import Dict, List
from command.item import Order
from command.list_items import ListItems
from gateway.rust import RustPlusRustGatewayFactory, ServerConfig
from repository.item_repository import JsonItemRepository
from repository.server_repository import JsonServerRepository


def get_server_names():
    with open("./json/config.json", "r") as f:
        config = json.load(f)
    list_of_servers = config["servers"]
    server_names = []
    count = 1
    for server in list_of_servers:
        servername = server["name"]
        server_names.append(app_commands.Choice(name=f"{servername}", value=count))
        count += 1
    return server_names


class vending(commands.Cog):
    def __init__(self, client):
        print("[Cog] Vending Machines has been initiated")
        self.socket_factory = RustPlusRustGatewayFactory()
        self.item_repository = JsonItemRepository()
        self.cogs_color = "0x9b59b6"

    server_names = get_server_names()

    @commands.Cog.listener()
    async def on_ready(self):
        print("[Cog] Vending Machines is ready")

    async def autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> List[app_commands.Choice[str]]:
        choices = []
        for item in self.item_repository.all():
            choices.append(item.name)
        if current:
            choicelist = []
            for choice in choices:
                if current.lower() in choice.lower():
                    choicelist.append(choice)
                if len(choicelist) > 10:
                    break
            return [app_commands.Choice(name=c, value=c) for c in choicelist]
        else:
            default = ["Start typing an item name!"]
            return [app_commands.Choice(name=d, value=d) for d in default]

    @app_commands.command(
        name="vendingsearch", description="Searches The Rust Server's Vending Machine"
    )
    @app_commands.guild_only()
    @app_commands.describe(item="List of items")
    @app_commands.describe(server="Select a server")
    @app_commands.choices(server=[*server_names])
    @app_commands.autocomplete(item=autocomplete)
    async def search(
        self,
        interaction: discord.Interaction,
        server: app_commands.Choice[int],
        item: str,
    ):
        print(f"Searching for {item} on {server.name}")

        await interaction.response.defer()
        thumbnail = None
        command = ListItems(
            self.socket_factory, JsonServerRepository(), JsonItemRepository()
        )
        orders = await command.execute(server.name, item)

        # group orders by grid
        orders_by_grid = group_by_key(orders)
        # print(orders_by_grid)

        for orders in orders_by_grid.values():
            messages = []
            for order in orders:
                sell_order_item = order.item
                currency_name = order.currency
                grid = order.grid

                message = f"Selling: {sell_order_item} x{order.quantity}\nBuying: {currency_name} x{order.cost_per_item}\nStock: {order.amount_in_stock}"
                if len("\n---\n".join(messages + [message])) > 1024:
                    embed = await self.setup_embed(
                        item_list="\n---\n".join(messages),
                        thumbnail=thumbnail,
                        item=item,
                        servername=server.name,
                        grid=grid,
                    )
                    messages = [message]
                    time.sleep(2)
                else:
                    messages.append(message)

            if len(messages) > 0:
                embed = await self.setup_embed(
                    item_list="\n---\n".join(messages),
                    thumbnail=thumbnail,
                    item=item,
                    servername=server.name,
                    grid=grid,
                )
                time.sleep(2)
            await interaction.followup.send(embed=embed)

    async def setup_embed(self, item_list, thumbnail, item, servername, grid):
        embed = discord.Embed(
            title=f"{item} on {servername}",
            color=int(self.cogs_color, base=16),
        )
        # embed.set_footer(
        #     text="Discord bot created by Gnomeslayer, using Rust+ wrapper created by Ollie."
        # )
        embed.set_thumbnail(url=thumbnail)
        embed.add_field(
            # name=f"{servername} vending machine data!",
            name=f"Found in {grid}",
            value=f"```{item_list}```",
            inline=True,
        )
        return embed


async def setup(client):
    await client.add_cog(vending(client))


def key_func(k: Order):
    return k.grid


def group_by_key(orders: List[Order]) -> Dict[str, List[Order]]:
    v = {}

    for order in orders:
        if order.grid not in v:
            v[order.grid] = []
        v[order.grid].append(order)

    return v
