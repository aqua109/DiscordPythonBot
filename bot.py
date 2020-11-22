import asyncio
import discord
import os
import sqlite3
import re
from discord.ext import commands
from datetime import date

client = discord.Client()

command_dict = \
    {
        "aoe2": [],
        "quake": [],
        "misc": [],
        "help": []
    }

command_queue = []


class Command:
    def __init__(self, voice_channel, text_channel, message, mp3_string):
        self.voice_channel = voice_channel
        self.text_channel = text_channel
        self.message = message
        self.mp3_string = mp3_string


# Update command_dict with values from sound_clips.db
def refresh_command_dict():
    conn = sqlite3.connect("sound_clips.db")
    c = conn.cursor()
    for key, value in command_dict.items():
        table = clean_table_name(key)
        c.execute(f"SELECT command, flavour FROM {table}")
        for command, flavour in c.fetchall():
            value.append([command, flavour])
    c.close()


def check_message(msg):
    for key, value in command_dict.items():
        for item in value:
            if msg.lower() == item[0]:
                return key
    return None


# Not currently in use, can be used to add new voice clips during runtime
def create_new_command(category, command, flavour):
    conn = sqlite3.connect("sound_clips.db")
    c = conn.cursor()
    table = clean_table_name(category)
    c.execute(f"INSERT INTO {table} (command, flavour) VALUES (?, ?)", (str(command), str(flavour)))
    conn.commit()
    c.close()


def clean_table_name(table):
    return "".join(c for c in table if c.isalnum())


# Convert user id (<@!74004712172560384>) to client.user
async def parse_user(unparsed_user_id):
    # Returns just the user id
    regex_search = re.search(r"[0-9]+", unparsed_user_id)
    user_id = regex_search.group()
    return client.get_user(int(user_id))


async def tk_recorder(msg, text_channel, user):
    # Add a new tk record
    if msg[:3] == "tk ":
        conn = sqlite3.connect("tk.db")
        c = conn.cursor()
        # @aidanigbo is read as <@!74004712172560384>
        # Find all users that match this pattern in the message
        users = re.findall("<@![0-9]+>", msg)
        try:
            killer = await parse_user(users[0])
            victim = await parse_user(users[1])
        except IndexError:
            return

        now = date.today().strftime("%d/%m/%Y")
        print(f"Adding record of {killer.name} killing {victim.name} at {now} as requested by {user}")

        c.execute("INSERT INTO tk_record (killer, victim, date) VALUES (?, ?, ?)", (killer.name, victim.name, now))
        conn.commit()
        c.close()

    # tk leaderboard
    elif msg == "tk-leaderboard":
        conn = sqlite3.connect("tk.db")
        c = conn.cursor()
        c.execute("SELECT killer, COUNT(killer) FROM tk_record GROUP BY killer ORDER BY count(killer) DESC")
        result = c.fetchall()
        c.close()

        print(f"Showing TK Leaderboard as requested by {user}")

        embed=discord.Embed(title="TK Leaderboard", description="💀💀💀", color=0x3c6382)
        for str in result:
            embed.add_field(name=str[0], value=str[1], inline=False)

        await text_channel.send(embed=embed)

    # un-targeted tk query
    elif "tk-record" in msg and len(msg.split("@")) == 2:
        # @aidanigbo is read as <@!74004712172560384>
        # Find all users that match this pattern in the message
        users = re.findall("<@![0-9]+>", msg)
        killer = await parse_user(users[0])
        conn = sqlite3.connect("tk.db")
        c = conn.cursor()
        c.execute("SELECT killer, COUNT(killer) FROM tk_record WHERE killer == ?", (killer.name,))
        result = c.fetchall()
        c.close()

        print(f"Showing record of {killer.name}'s teamkills as requested by {user}")

        if result[0][1] == 0:
            await text_channel.send(f"{killer.name} has never teamkilled \n\nprobably")
        elif result[0][1] == 1:
            await text_channel.send(f"{killer.name} has teamkilled once")
        else:
            await text_channel.send(f"{killer.name} has teamkilled {result[0][1]} times")

    # targeted tk query
    elif "tk-record" in msg and len(msg.split("@")) == 3:
        # @aidanigbo is read as <@!74004712172560384>
        # Find all users that match this pattern in the message
        users = re.findall("<@![0-9]+>", msg)
        killer = await parse_user(users[0])
        victim = await parse_user(users[1])
        print(killer)
        conn = sqlite3.connect("tk.db")
        c = conn.cursor()
        c.execute("SELECT killer, COUNT(killer) FROM tk_record WHERE killer == ? AND victim == ?", (killer.name, victim.name))
        result = c.fetchall()
        c.close()

        print(f"Showing record of {killer.name} killing {victim.name} as requested by {user}")

        if result[0][1] == 0:
            await text_channel.send(f"{killer.name} has never teamkilled {victim.name} \n\nprobably")
        elif result[0][1] == 1:
            await text_channel.send(f"{killer.name} has teamkilled {victim.name} once")
        else:
            await text_channel.send(f"{killer.name} has teamkilled {victim.name} {result[0][1]} times")


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message):
    # Don't parse messages sent by ourselves
    if message.author == client.user:
        return

    user = message.author
    text_channel = message.channel
    voice_channel = user.voice

    command = check_message(message.content)

    if command is not None or "tk" in message.content:
        # Prevents the bot joining the voice channel or requiring the requesting user to be in a voice channel
        if "tk" in message.content:
            await tk_recorder(message.content, text_channel, user)
            await message.delete(delay=5)
        else:
            # If the bot is not in a channel join the voice channel that the user who sent the command is in
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

                # Needs to be changed to be similar to tk commands, i.e. doesn't require the user to be in a voice channel
                elif command == "help":
                    if message.content == "disconnect":
                        await vc.disconnect()
                    elif message.content == "help":
                        await help(text_channel)
                    else:
                        await dm(user, message.content)

                    await message.delete(delay=5)
                    print(f"\"{message.content}\" command requested by {user}")



# Connects the bot to the voice channel that the user who sent the command is in
# If the user isn't in a voice channel a message is sent and nothing further happens
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


# Use https://cog-creators.github.io/discord-embed-sandbox/ to make nice embed messages
async def help(text_channel):
    embed = discord.Embed(title="Mr Roboto Commands", description="⠀", color=0x0dffe7)
    embed.add_field(name="Age of Empires 2 Taunts", value="Command: aoe2help", inline=False)
    embed.add_field(name="Quake", value="Command: quakehelp", inline=False)
    embed.add_field(name="Misc", value="Command: mischelp", inline=False)
    await text_channel.send(embed=embed)


# Function to direct message the requesting user a list of avaiable commands
async def dm(user, msg):
    help_requested = None
    for value in command_dict["help"]:
        if value[0] == msg.lower():
            help_requested = value[1]

    if (help_requested):
        embed = discord.Embed(title=f"{help_requested} Commands", description="⠀", color=0x0dffe7)
        count = 1
        for command, flavour in command_dict[help_requested.lower()]:
            if count >= 26:
                await user.send(embed=embed)
                embed = discord.Embed(title=f"{help_requested} Commands cont...", description="⠀", color=0x0dffe7)
                count = 1
            embed.add_field(name=flavour, value=command, inline=False)
            count += 1
        await user.send(embed=embed)


if __name__ == "__main__":
    # Discord bot token stored as a system variable
    token = os.environ["discord_token"]
    refresh_command_dict()
    client.run(token)
