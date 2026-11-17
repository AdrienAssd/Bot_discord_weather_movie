import discord
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

class EchoClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user.name} (ID: {self.user.id})')

    async def on_message(self, message):
        if message.author == self.user:
            return

        await message.channel.send(message.content)

intents = discord.Intents.default()
intents.message_content = True

client = EchoClient(intents=intents)
client.run(TOKEN)
