import discord
import asyncio
from configparser import ConfigParser
import sys, getopt

opts, args = getopt.getopt(sys.argv[1:], "f:")
opt, arg = opts[0]
assert opt == '-f'
configfile = arg

config = ConfigParser()
config.read(configfile)
token = config.get('Bot','token')
monitor_channel = config.getint('Bot', 'monitor_channel')
modmail_channel = config.getint('Bot', 'modmail_channel')
max_count = config.getint('Bot', 'max_count')

intents = discord.Intents.default()
intents.messages = True
#intents.message_content = True
intents.members = True
intents.reactions = True

class Timer:
    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.ensure_future(self._job())

    async def _job(self):
        await asyncio.sleep(self._timeout)
        await self._callback()

    def cancel(self):
        self._task.cancel()

class MyClient(discord.Client):
    last_message = None
    active_timer = None
    current_count = 0

    async def on_ready(self):
        print('Logged in as',self.user)
        activity = discord.Activity(name='DM me to message the mods', type=discord.ActivityType.watching)
        await client.change_presence(activity=activity)
        await self.send_reminder()

    async def on_message(self, message):
        if message.author.bot:
            return

        if isinstance(message.channel, discord.TextChannel):
            # if conceptual physics
            if message.channel.id == monitor_channel:
                self.current_count = self.current_count + 1
                # if there is an ongoing timer, cancel it
                if self.active_timer != None:
                    self.active_timer.cancel()
                    self.active_timer = None
                # if we are at or above the message limit, prepare to send the reminder
                if self.current_count >= max_count:
                    self.active_timer = Timer(600, self.send_reminder)

            # if modmail channel
            if message.channel.id == modmail_channel:
                # check if this is a reply to an open modmail
                if message.reference is not None:
                    ref = await message.channel.fetch_message(message.reference.message_id)
                    if ref.author == self.user and ref.content.startswith("New modmail created by"):
                        pings = ref.mentions[0]
                        # relay mod response
                        response_channel = pings.dm_channel
                        if response_channel is None:
                            response_channel = await pings.create_dm()
                        embed = discord.Embed(description=message.content, color=0x686868)
                        # embed.set_author(name=message.author, icon_url=message.author.avatar.url)
                        embed.set_author(name=message.author)
                        files = [await attachment.to_file() for attachment in message.attachments]
                        await response_channel.send(f"Response received from {message.author.mention}", embed=embed, files=files)
                        # confirm in modmail channel
                        await message.reply(f"Reply sent to **{pings.display_name}**")

        # if in DMs
        elif isinstance(message.channel, discord.DMChannel):
            channel = await self.fetch_channel(modmail_channel)
            embed = discord.Embed(description=message.content, color=0x686868)
            # embed.set_author(name= message.author, icon_url=message.author.avatar.url)
            embed.set_author(name= message.author)
            files = [await attachment.to_file() for attachment in message.attachments]
            await channel.send(f"New modmail created by {message.author.mention}",embed=embed,files=files)
            await message.channel.send("Your message has been relayed to the staff of the Physics server.")

    async def send_reminder(self):
        #print("sending reminder")
        self.current_count = 0
        await self.delete_last_message()
        channel = await self.fetch_channel(monitor_channel)
        self.last_message = await channel.send("**Do you need help?** If you are posting a question, you must first read <#762779815492190268>. This channel is for conceptual discussion only, not for help with homework questions. Repeated violations will result in administrative action.\n\n_I post this reminder periodically; this is not in response to any particular message_")

    async def delete_last_message(self):
        if self.last_message != None:
            #print("deleting message")
            await self.last_message.delete()
            self.last_message = None

    # for handling questions-forum posts
    async def on_raw_reaction_add(self, payload):
        # this can only happen in forums
        if not payload.channel_id == payload.message_id:
            return

        channel = await self.fetch_channel(payload.channel_id)
        if not isinstance(channel, discord.Thread):
            print('ERROR: not a thread',payload)

        message = await channel.fetch_message(payload.message_id)
        member = channel.guild.get_member(payload.user_id)

        is_moderator = member.get_role(894754014707744778) or member.get_role(302411215651471375)

        # thread lock command
        if payload.emoji.name == "✅" or payload.emoji.name == "✔️" or payload.emoji.name =="☑️":
            if channel.owner_id == payload.user_id or is_moderator:
                await channel.edit(locked=True, archived=True, reason=f"Reaction-locked by {member.name} ({member.id})")
        # thread delete command
        if payload.emoji.id == 1042517384617001100:
            if channel.owner_id == payload.user_id or is_moderator:
                await channel.delete()

client=MyClient(intents=intents)
client.run(token)
