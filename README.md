# DiscordPythonBot

### Installation

DiscordPythonBot requires [Python 3.5.3](https://www.python.org/downloads/) or higher and [FFmpeg](https://ffmpeg.org/download.html) to run.

Create a Discord app by visiting the [Discord Developer Portal](https://discord.com/developers/applications)\
Make a note of your bot token\
[Create a new system variable](https://docs.oracle.com/en/database/oracle/r-enterprise/1.5.1/oread/creating-and-modifying-environment-variables-on-windows.html#GUID-DD6F9982-60D5-48F6-8270-A27EC53807D0) called "discord_token", setting the value to be your bot token

Download [FFmpeg](https://ffmpeg.org/download.html#build-windows)\
Unzip to C:\ or any other easy to access location, rename the folder to 'ffmpeg'\
[Add "C:\ffmpeg" to Path](https://www.architectryan.com/2018/03/17/add-to-the-path-on-windows-10/)

Clone from git, create a virtual environment, install packages, and run the bot

```sh
$ git clone https://github.com/aqua109/DiscordPythonBot.git
$ cd DiscordPythonBot
$ python venv venv
$ venv\scripts\activate
$ (venv) pip install -r requriements.txt
$ (venv) python bot.py
```
