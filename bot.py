import discord
from discord.ext import commands
from discord.ext.commands import Context
from dotenv import load_dotenv
import os
import random

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)  # Disable the default help command

# Dictionary to store users' balance and inventory
economy = {}
inventory = {}

# Items available in the shop
shop_items = {
    "Sword": 1000,
    "Shield": 500,
    "Potion": 200
}

# Custom Help Command
@bot.command()
async def help(ctx: Context):
    help_message = """
    **Economy Bot Commands:**
    - `!balance`: Show your current balance.
    - `!work`: Work to earn money.
    - `!pay @user amount`: Send money to another user.
    - `!leaderboard`: Show the top 5 richest users.
    - `!bet amount`: Bet an amount of money to win or lose.
    - `!shop`: View items available for purchase in the shop.
    - `!buy <item>`: Buy an item from the shop.
    """
    await ctx.send(help_message)

# Command to check balance
@bot.command()
async def balance(ctx: Context):
    user = ctx.author
    if user.id not in economy:
        economy[user.id] = 0
    await ctx.send(f"{user.name}, your balance is: ${economy[user.id]}")

# Command to work and earn money
@bot.command()
async def work(ctx: Context):
    user = ctx.author
    earnings = random.randint(50, 500)
    if user.id not in economy:
        economy[user.id] = 0
    economy[user.id] += earnings
    await ctx.send(f"{user.name}, you worked and earned ${earnings}! Your new balance is: ${economy[user.id]}")

# Command to pay another user
@bot.command()
async def pay(ctx: Context, member: discord.Member, amount: int):
    user = ctx.author
    if user.id not in economy:
        economy[user.id] = 0
    if member.id not in economy:
        economy[member.id] = 0

    if economy[user.id] < amount:
        await ctx.send("You don't have enough money to complete this transaction.")
        return
    
    economy[user.id] -= amount
    economy[member.id] += amount
    await ctx.send(f"{user.name} paid ${amount} to {member.name}. Your new balance is ${economy[user.id]}.")

# Command to show the leaderboard (top 5 users)
@bot.command()
async def leaderboard(ctx: Context):
    sorted_users = sorted(economy.items(), key=lambda x: x[1], reverse=True)
    leaderboard_message = "Top 5 users:\n"
    
    for i, (user_id, balance) in enumerate(sorted_users[:5]):
        user = await bot.fetch_user(user_id)
        leaderboard_message += f"{i + 1}. {user.name}: ${balance}\n"

    await ctx.send(leaderboard_message)

# Command to bet money
@bot.command()
async def bet(ctx: Context, amount: int):
    user = ctx.author
    if user.id not in economy:
        economy[user.id] = 0

    if economy[user.id] < amount:
        await ctx.send("You don't have enough money to make that bet!")
        return

    # Random chance to win or lose
    outcome = random.choice(["win", "lose"])
    if outcome == "win":
        winnings = amount * 2  # User doubles their bet if they win
        economy[user.id] += winnings
        await ctx.send(f"{user.name} won the bet! You earned ${winnings}. Your new balance is: ${economy[user.id]}")
    else:
        economy[user.id] -= amount
        await ctx.send(f"{user.name} lost the bet! You lost ${amount}. Your new balance is: ${economy[user.id]}")

# Command to view the shop
@bot.command()
async def shop(ctx: Context):
    shop_message = "Welcome to the shop! Here are the items you can buy:\n"
    for item, price in shop_items.items():
        shop_message += f"- {item}: ${price}\n"
    await ctx.send(shop_message)

# Command to buy an item from the shop
@bot.command()
async def buy(ctx: Context, item: str):
    user = ctx.author
    if user.id not in economy:
        economy[user.id] = 0

    if item not in shop_items:
        await ctx.send("That item is not available in the shop!")
        return

    item_price = shop_items[item]
    if economy[user.id] < item_price:
        await ctx.send(f"You don't have enough money to buy a {item}!")
        return

    # Deduct money and add item to inventory
    economy[user.id] -= item_price
    if user.id not in inventory:
        inventory[user.id] = []
    inventory[user.id].append(item)

    await ctx.send(f"{user.name}, you bought a {item}! Your new balance is: ${economy[user.id]}")

# Event when the bot is ready
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

bot.run(TOKEN)
