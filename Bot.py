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

tracking_unban = {}
tracking_ban = {}

def get_data(username):
    try:
        r = requests.get(f"https://www.instagram.com/{username}/")
        if r.status_code != 200:
            return None

        text = r.text

        dp_match = re.search(r'"profile_pic_url_hd":"(.*?)"', text)
        dp = dp_match.group(1).replace("\\u0026", "&") if dp_match else None

        if f'"username":"{username}"' in text:
            return {"dp": dp}

        return None
    except:
        return None

@bot.event
async def on_ready():
    print("Bot Online")
    monitor.start()

@bot.command()
async def track(ctx, username: str):
    tracking_unban[username] = {
        "start": time.time(),
        "channel": ctx.channel
    }
    await ctx.send(f"📡 Monitoring UNBAN for @{username}...")

@bot.command()
async def ban(ctx, username: str):
    tracking_ban[username] = {
        "start": time.time(),
        "channel": ctx.channel
    }
    await ctx.send(f"🚨 Monitoring BAN for @{username}...")

@tasks.loop(seconds=90)
async def monitor():

    for username in list(tracking_unban.keys()):
        data = tracking_unban[username]
        result = get_data(username)

        if result:
            time_taken = int(time.time() - data["start"])

            embed = discord.Embed(
                title=f"Account Recovered | @{username} 🏆",
                description=f"🔓 Status: Unbanned\n⏱ Time Taken: {time_taken} sec",
                color=0x57F287
            )

            if result["dp"]:
                embed.set_thumbnail(url=result["dp"])

            embed.set_footer(text=f"Recovered at {datetime.now().strftime('%H:%M:%S')}")

            await data["channel"].send(embed=embed)
            del tracking_unban[username]

    for username in list(tracking_ban.keys()):
        data = tracking_ban[username]
        result = get_data(username)

        if not result:
            time_taken = int(time.time() - data["start"])

            embed = discord.Embed(
                title=f"Account Banned | @{username} 🚫",
                description=f"🔒 Status: Banned\n⏱ Time Taken: {time_taken} sec",
                color=0xED4245
            )

            embed.set_footer(text=f"Detected at {datetime.now().strftime('%H:%M:%S')}")

            await data["channel"].send(embed=embed)
            del tracking_ban[username]

bot.run(TOKEN)
