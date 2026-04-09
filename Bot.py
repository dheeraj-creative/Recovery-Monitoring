import discord
from discord.ext import commands, tasks
import requests
import time
import os
import re
from datetime import datetime

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

tracking_ban = {}
tracking_unban = {}

# ⏱ time format
def format_time(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}h {m:02d}m {s:02d}s"

# 🔍 Instagram data + DP
def get_data(username):
    try:
        url = f"https://www.instagram.com/{username}/"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers)

        if r.status_code == 404:
            return None

        text = r.text

        # DP extract
        dp_match = re.search(r'"profile_pic_url_hd":"(.*?)"', text)
        dp = dp_match.group(1).replace("\\u0026", "&") if dp_match else None

        if f'"username":"{username}"' in text:
            return {"dp": dp}

        return "error"

    except:
        return "error"

# 🔴 BAN command
@bot.command()
async def ban(ctx, username):
    tracking_ban[username] = time.time()

    embed = discord.Embed(
        description=f"🚫 Monitoring BAN for @{username}...",
        color=0xED4245
    )
    await ctx.send(embed=embed)

# 🟢 UNBAN command
@bot.command()
async def unban(ctx, username):
    tracking_unban[username] = time.time()

    embed = discord.Embed(
        description=f"🟢 Monitoring UNBAN for @{username}...",
        color=0x57F287
    )
    await ctx.send(embed=embed)

# 🔁 LOOP
@tasks.loop(seconds=15)
async def check_accounts():
    for guild in bot.guilds:
        for channel in guild.text_channels:

            # 🔴 BAN CHECK
            for username in list(tracking_ban.keys()):
                data = get_data(username)

                if data is None:
                    total = int(time.time() - tracking_ban[username])

                    embed = discord.Embed(
                        title="🚫 Account Banned",
                        color=0xED4245
                    )

                    embed.add_field(name="👤 Username", value=f"@{username}", inline=False)
                    embed.add_field(name="🔒 Status", value="Banned", inline=True)
                    embed.add_field(name="⏱ Time Taken", value=format_time(total), inline=True)

                    embed.set_footer(text=f"Detected at {datetime.now().strftime('%H:%M:%S')}")

                    await channel.send(embed=embed)
                    tracking_ban.pop(username)

            # 🟢 UNBAN CHECK
            for username in list(tracking_unban.keys()):
                data = get_data(username)

                if isinstance(data, dict):
                    total = int(time.time() - tracking_unban[username])

                    embed = discord.Embed(
                        title="🏆 Account Recovered",
                        color=0x57F287
                    )

                    embed.add_field(name="👤 Username", value=f"@{username}", inline=False)
                    embed.add_field(name="🔓 Status", value="Active", inline=True)
                    embed.add_field(name="⏱ Time Taken", value=format_time(total), inline=True)

                    # DP add
                    if data["dp"]:
                        embed.set_thumbnail(url=data["dp"])

                    embed.set_footer(text=f"Recovered at {datetime.now().strftime('%H:%M:%S')}")

                    await channel.send(embed=embed)
                    tracking_unban.pop(username)

@bot.event
async def on_ready():
    print(f"🔥 Bot Online: {bot.user}")
    check_accounts.start()

bot.run(TOKEN)
