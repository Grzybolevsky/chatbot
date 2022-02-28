import os
import requests

from discord import Client
from dotenv import load_dotenv

load_dotenv()

TOKEN: str = os.environ['DISCORD_TOKEN']
client = Client()


@client.event
async def on_ready():
    print(f'{client.user} jumped into server.')


@client.event
async def on_message(msg):
    if str(msg.author) == str(client.user):
        return
    print("Got:")
    print(msg)
    response = requests.post('http://localhost:5005/webhooks/rest/webhook',
                             json={"sender": str(msg.author), "message": msg.content})
    print("Response:")
    print(response.json())
    lines = response.json()
    message = '\n'.join([line.get('text') for line in lines])
    await msg.channel.send(message)


client.run(TOKEN)
