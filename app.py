import asyncio
import discord
import os
import sqlite3
from discord.ext import commands

client = commands.Bot(command_prefix="!")
quake_list = ["dominating", "godlike", "holyshit", "humiliation", "killing spree", "ludicrouskill", "monsterkill", "rampage", "teamkiller", "ultrakill", "unstoppable", "wickedsick"]

command_dict = \
    {
        "aoe2": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42"],
        "quake": ["dominating", "godlike", "holyshit", "humiliation", "killing spree", "ludicrouskill", "monsterkill", "rampage", "teamkiller", "ultrakill", "unstoppable", "wickedsick"],
        "misc": ["how", "disgusting", "penis", "foodplease", "dialup", "aeugh", "brrringha", "idiotsandwich", "bruh", "supersuit", "quickscope", "petruh"],
        "help": ["help", "disconnect"]
    }

command_queue = []


class Command:
    def __init__(self, voice_channel, text_channel, message, mp3_string):
        self.voice_channel = voice_channel
        self.text_channel = text_channel
        self.message = message
        self.mp3_string = mp3_string


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    user = message.author
    text_channel = message.channel
    voice_channel = user.voice

    command = None

    for key, value in command_dict.items():
        if message.content in value:
            command = key

    if command is not None:
        if not client.voice_clients:
            vc = await connect(voice_channel, text_channel, message)
        else:
            vc = client.voice_clients[0]
        if vc:
            if command == "aoe2":
                print(f"AoE2 command \"{message.content}\" requested by {user}")
                cmd = Command(voice_channel, text_channel, message, f"AoE2\\{message.content}")
                command_queue.append(cmd)
                await play_voice_line(vc)
            elif command == "quake":
                print(f"Quake command \"{message.content}\" requested by {user}")
                cmd = Command(voice_channel, text_channel, message, f"Quake\\{message.content}")
                command_queue.append(cmd)
                await play_voice_line(vc)
            elif command == "misc":
                print(f"Misc command \"{message.content}\" requested by {user}")
                if message.content == "how":
                    conn = sqlite3.connect("how.db")
                    c = conn.cursor()
                    c.execute("SELECT count FROM how_count WHERE user is ?", (str(user),))
                    result = c.fetchall()
                    if result:
                        count = result[0][0]
                        count += 1
                        print(f"{str(user)} has asked how {count} times")
                        msg = await text_channel.send(f"{str(user)} has asked how {count} times")
                        await msg.delete(delay=5)
                        c.execute("UPDATE how_count SET count = ? WHERE user = ?", (count, str(user)))
                        conn.commit()
                    else:
                        count = 1
                        print(f"{str(user)} has asked how {count} times")
                        msg = await text_channel.send(f"{str(user)} has asked how {count} times")
                        await msg.delete(delay=5)
                        c.execute("INSERT INTO how_count (user, count) VALUES (?, ?)", (str(user), count))
                        conn.commit()
                    c.close()
                cmd = Command(voice_channel, text_channel, message, f"Misc\\{message.content}")
                command_queue.append(cmd)
                await play_voice_line(vc)
            elif command == "help":
                if message.content == "disconnect":
                    await vc.disconnect()
                    await message.delete(delay=5)
                if message.content == "help":
                    await help(text_channel)
                print(f"Help command requested by {user}")


async def connect(voice_channel, text_channel, message):
    if voice_channel is not None:
        vc = await voice_channel.channel.connect()
        return vc
    else:
        msg = await text_channel.send(f"{message.author} is not in a voice channel")
        await msg.delete(delay=5)
        await message.delete(delay=5)
        return None


async def play_voice_line(vc):
    while command_queue:
        try:
            vc.play(discord.FFmpegPCMAudio(f"{command_queue[0].mp3_string}.mp3"), after=lambda e: print(f"Error: {e}") if e is not None else None)
            await command_queue[0].message.delete(delay=5)
            command_queue.pop(0)
        except discord.errors.ClientException:
            await asyncio.sleep(1)


async def help(text_channel):
    embed = discord.Embed(title="Mr Roboto Commands", description="---", color=0x0dffe7)
    embed.add_field(name="Age of Empires 2 Taunts", value="Command: aoe2help", inline=False)
    embed.add_field(name="Quake", value="Command: quakehelp", inline=False)
    embed.add_field(name="Misc", value="Command: mischelp", inline=False)
    await text_channel.send(embed=embed)


async def dm(user):
    pass

if __name__ == "__main__":
    token = os.environ["discord_token"]
    client.run(token)
