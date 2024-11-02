import time
from discord import app_commands
from discord.ext import commands
import discord
import json
from typing import List
from rustplus import RustMarker, convert_xy_to_grid, RustSocket
import pprint

class vending(commands.Cog):
    def __init__(self, client):
        print("[Cog] Vending Machines has been initiated")
        self.client = client
        self.sockets = {}
        self.last_query = 0
        self.last_markers = None

    with open("./json/config.json", "r") as f:
        config = json.load(f)
    with open("./json/items.json", "r") as f:
        items_list = json.load(f)

    list_of_servers = [{'name': 'Friendly Seattle', 'id': 1234},{'name': 'Sanctum', 'id': 2345} ]
    server_names = []
    count = 1
    for server in list_of_servers:
        servername = server['name']
        
        server_names.append(app_commands.Choice(name=f"{servername}", value=count))
        count += 1

    @ commands.Cog.listener()
    async def on_ready(self):
        print("Establishing Rust+ connections..")
        servers = self.config['servers']
        for server in servers:
            print("\n=\n")
            print("Attempting to connect to server: ", server['name'])
            print("\n=\n")
            new_socket = RustSocket(server['ip'], int(server['port']),
                                    int(server['playerId']), int(server['playerToken']))
            await new_socket.connect()
            self.sockets[server['name']] = {"socket": new_socket, "map_size": (await new_socket.get_info()).size}
            print("Connected")
        print("Rust+ connections established.")

    async def autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        choices = []
        for item in self.items_list:
            choices.append(self.items_list[item]['name'])
        if current:
            choicelist = []
            for choice in choices:
                if current.lower() in choice.lower():
                    choicelist.append(choice)
                if len(choicelist) > 20:
                    break
            return [app_commands.Choice(name=c, value=c) for c in choicelist]
        else:
            default = ["Start typing an item name!"]
            return [app_commands.Choice(name=d, value=d) for d in default]

    @ app_commands.command(name="vendingsearch", description="Searches The Rust Server's Vending Machine")
    @ app_commands.guild_only()
    @ app_commands.describe(item="List of items")
    @ app_commands.describe(server="Select a server")
    @ app_commands.choices(server=[*server_names])
    @app_commands.autocomplete(item=autocomplete)
    async def search(self, interaction: discord.Interaction, server: app_commands.Choice[int], item: str):
        await interaction.response.defer()
        item = item.lower()

        thumbnail = None
        for i in self.items_list:
            if self.items_list[i]['name'].lower() == item or self.items_list[i]['shortname'].lower() == item:
                thumbnail = self.items_list[i]['link']
                break
        servername = None
        for socket in self.sockets:
            if str(server.name).lower() == str(socket).lower():
                time_now = time.time()
                elapsed = time_now - self.last_query
                servername = socket
                sock = self.sockets[servername]['socket']

                if elapsed > 5*60:
                    print(f"Querying {servername}...")
                    socketmarkers = await sock.get_markers()
                    markers = []
                    for marker in socketmarkers:
                        markers.append(marker)
                    self.last_markers=markers
                    self.last_query=time_now
                else:
                    print("Using cache")
                    markers = self.last_markers

                item_list = []
                for marker in markers:
                    if marker.type != RustMarker.VendingMachineMarker:
                        continue
                    # print(f"marker={marker}")
                    # obj_vars = vars(marker)
                    # pprint.pp(obj_vars)
                    items_sold = None
                    for sell_order in marker.sell_orders:
                        # obj_vars = vars(sell_order)
                        # pprint.pp(obj_vars)

                        if str(sell_order.item_id) in self.items_list:
                            sell_order_item = str(
                                self.items_list[f"{sell_order.item_id}"]['name']).lower()
                        else:
                            sell_order_item = f"Unknown: {sell_order.item_id}"

                        if str(sell_order.currency_id) in self.items_list:
                            buy_item = str(
                                self.items_list[f"{sell_order.currency_id}"]['name']).lower()
                        else:
                            buy_item =  f"Unknown: {sell_order.currency_id}"

                        if sell_order_item == item or buy_item == item:
                            grid = convert_xy_to_grid(
                                (marker.x, marker.y), self.sockets[servername]['map_size'], False)
                            grid = ''.join(str(item) for item in grid)
                            if str(sell_order.currency_id) in self.items_list:
                                currency_name = self.items_list[f"{sell_order.currency_id}"]['name']
                            else:
                                currency_name = "Unknown."

                            message = f"[Grid: {grid}]\nSelling: {sell_order_item} x{sell_order.quantity}\nBuying: {currency_name} x{sell_order.cost_per_item}\nStock: {sell_order.amount_in_stock}"

                            if items_sold:
                                items_sold += f"\n{message}"
                            else:
                                items_sold = f"{message}"
                                
                            if len(items_sold) >= 750:
                                item_list.append(items_sold)
                                items_sold = None
                    if items_sold:
                        item_list.append(items_sold)
        # return                        
        if item_list:
            for items in item_list:
                embed = await self.setup_embed(item_list=items, thumbnail=thumbnail, item=item, servername=servername)
                await interaction.followup.send(embed=embed)
                time.sleep(2)
        else:
            embed = discord.Embed(title=f"Showing vending machine data for: '**{item}**'", color=int(
                self.config['cogs']['color'], base=16))
            embed.set_footer(
                text="Discord bot created by Gnomeslayer, using Rust+ wrapper created by Ollie.")
            embed.set_thumbnail(url=thumbnail)
            embed.add_field(name=f"{servername} vending machine data!",
                            value=f"```Item not being sold on this server. Start capitalizing on this right now!```", inline=False)
            await interaction.followup.send(embed=embed)
            # time.sleep(2)
        
    async def setup_embed(self, item_list, thumbnail, item, servername):
        embed = discord.Embed(title=f"Showing vending machine data for: '**{item}**'", color=int(
            self.config['cogs']['color'], base=16))
        embed.set_footer(
            text="Discord bot created by Gnomeslayer, using Rust+ wrapper created by Ollie.")
        embed.set_thumbnail(url=thumbnail)
        embed.add_field(name=f"{servername} vending machine data!",
                        value=f"```{item_list}```", inline=True)
        return embed
        
async def setup(client):
    await client.add_cog(vending(client))
