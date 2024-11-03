import asyncio
from discord import app_commands
from discord.ext import commands
import discord
import json
from typing import Dict, List
from rustshopbot.command.search_buyers import SearchBuyers
from rustshopbot.command.search_sellers import SearchSellers
from rustshopbot.entity.order import Order
from rustshopbot.gateway.rust import RustPlusPyRustGatewayFactory
from rustshopbot.repository.item_repository import JsonItemRepository
from rustshopbot.repository.server_repository import JsonServerRepository


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
        self.socket_factory = RustPlusPyRustGatewayFactory()
        self.item_repository = JsonItemRepository()
        self.server_repository = JsonServerRepository()
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
        name="buy", description="Searches The Rust Server's Vending Machine"
    )
    @app_commands.guild_only()
    @app_commands.describe(item="List of items")
    @app_commands.describe(server="Select a server")
    @app_commands.choices(server=[*server_names])
    @app_commands.autocomplete(item=autocomplete)
    async def search_sellers(
        self,
        interaction: discord.Interaction,
        server: app_commands.Choice[int],
        item: str,
    ):
        print(f"Searching for sellers of {item} on {server.name}")

        await interaction.response.defer()
        command = SearchSellers(
            self.socket_factory, self.server_repository, self.item_repository
        )
        orders = await command.execute(server.name, item)
        await self.present_orders(orders, item, server.name, interaction)

    @app_commands.command(
        name="sell", description="Searches The Rust Server's Vending Machine"
    )
    @app_commands.guild_only()
    @app_commands.describe(item="List of items")
    @app_commands.describe(server="Select a server")
    @app_commands.choices(server=[*server_names])
    @app_commands.autocomplete(item=autocomplete)
    async def search_buyers(
        self,
        interaction: discord.Interaction,
        server: app_commands.Choice[int],
        item: str,
    ):
        print(f"Searching for buyers of {item} on {server.name}")

        await interaction.response.defer()
        command = SearchBuyers(
            self.socket_factory, self.server_repository, self.item_repository
        )
        orders = await command.execute(server.name, item)
        await self.present_orders(orders, item, server.name, interaction)

    async def present_orders(self, orders, item, servername, interaction):
        thumbnail = None
        orders_by_grid = group_by_key(orders)
        if len(orders_by_grid) == 0:
            await interaction.followup.send(
                f"No orders found for {item} on {servername}",
            )
            return
        embed = await self.start_embed(
            item_list="",
            thumbnail=thumbnail,
            item=item,
            servername=servername,
            grid="",
            count=len(orders),
        )
        count = 0
        for orders in orders_by_grid.values():
            messages = []
            for order in orders:
                sell_order_item = order.item
                currency_name = order.currency
                grid = order.grid

                message = f"Sells: {sell_order_item} x{order.quantity}\nBuys: {currency_name} x{order.cost_per_item}\nStock: {order.amount_in_stock}"
                if len(self.format_messages(messages + [message])) > 1024:
                    # embed = await self.setup_embed(
                    #     item_list=self.format_messages(messages),
                    #     thumbnail=thumbnail,
                    #     item=item,
                    #     servername=servername,
                    #     grid=grid,
                    # )
                    embed.add_field(
                        # name=f"{servername} vending machine data!",
                        name=f"{grid}.",
                        value=f"```{self.format_messages(messages)}```",
                        inline=True,
                    )
                    messages = [message]
                    await asyncio.sleep(0.1)
                else:
                    messages.append(message)

            if len(messages) > 0:
                # embed = await self.setup_embed(
                #     item_list=self.format_messages(messages),
                #     thumbnail=thumbnail,
                #     item=item,
                #     servername=servername,
                #     grid=grid,
                # )
                # if count % 3 == 2:
                #     embed.add_field(
                #         # name=f"{servername} vending machine data!",
                #         name=f"\t",
                #         value=f"\t",
                #         inline=True,
                #     )
                inline = count <= 1 or count % 2 == 1
                # print(f"count: {count} Inline: {inline}")
                embed.add_field(
                    # name=f"{servername} vending machine data!",
                    name=f"{order.name} [{grid}]",
                    value=f"```{self.format_messages(messages)}```",
                    inline=True,
                )
                if count % 2 == 1:
                    # print(f"break")
                    embed.add_field(
                        # name=f"{servername} vending machine data!",
                        name=f"\t",
                        value=f"\t",
                        inline=False,
                    )
                count = count + 1

                await asyncio.sleep(0.1)

        await interaction.followup.send(embed=embed)

    async def start_embed(self, item_list, thumbnail, item, servername, grid, count):
        embed = discord.Embed(
            title=f"Found {count} results for {item} on {servername}",
            color=int(self.cogs_color, base=16),
        )
        # embed.set_footer(
        #     text="Discord bot created by Gnomeslayer, using Rust+ wrapper created by Ollie."
        # )
        embed.set_thumbnail(url=thumbnail)
        return embed

    def format_messages(self, messages):
        return "\n---\n".join(messages)


async def setup(client):
    await client.add_cog(vending(client))


def key_func(k: Order):
    return k.grid


def group_by_key(orders: List[Order]) -> Dict[str, List[Order]]:
    v = {}
    sorted_orders = sorted(
        orders, key=lambda order: f"{9999999-order.amount_in_stock:07d}-{order.grid}"
    )
    # sorted_orders = sorted(sorted_orders, key=lambda x: x.name)
    for order in sorted_orders:
        key = f"{order.name}-{order.grid}"
        if key not in v:
            v[key] = []
        v[key].append(order)

    return v
