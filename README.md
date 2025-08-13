# Physics Bot
This bot serves to relay user messages from DMs to a modmail channel and replies from the latter back to the user's DMs. It also periodically posts a reminder to read rules and adds archiving options to forum posts.

## Installation
1. Create a discord app in https://discord.com/developers/applications. Follow your favourite tutorial to create the app and add it to a discord server (e.g. https://realpython.com/how-to-make-a-discord-bot-python/).
2. Generate a token for the app and copy it.
3. Download the code for the bot.
4. Insert the token, IDs for the channel.
5. In the OAuth2 section of the app's page, set the scope to bot, select the following permissions: Manage Webhooks, Send Messages, Send Messages in Threads, Embed Links, Attach Files, Add Reactions, Use External Emojis, Manage Threads, Read Message History; then add the bot to the server.
6. Run bot.py on your machine, raspberry pi, cloud service, wherever.
