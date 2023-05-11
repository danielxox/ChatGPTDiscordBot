import os
import discord
import requests
import json

# Load your Discord and OpenAI API tokens
DISCORD_TOKEN = "YOUR DISCORD TOKEN"
OPENAI_TOKEN = "YOUR OPEN API TOKEN"

# Set up the Discord bot
intents = discord.Intents.all()
intents.typing = False
intents.presences = False

class ChatGPTBot(discord.Client):
    async def on_ready(self):
        print(f"{self.user.name} has connected to Discord!")

    @staticmethod
    async def send_typing_indicator(message):
        async with message.channel.typing():
            pass

    async def on_message(self, message):
        # Ignore messages from the bot itself
        if message.author == self.user:
            return

        # If the message starts with '!chatgpt'
        if message.content.startswith('!chatgpt'):
            # Extract the text after the command
            input_text = message.content[len('!chatgpt'):].strip()

            # Send an initial message to inform the user that the bot is working on a response
            working_message = await message.channel.send("Thinking ...")

            # Calculate max tokens based on input message length and maximum allowed tokens
            max_reply_tokens = max(1, 1000 - len(input_text))

            # Call the ChatGPT 3.5+ API with the user's message
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_TOKEN}"},
                json={
                    "model": "gpt-3.5-turbo",  # Replace with the model of your choice
                    "messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": input_text}],
                    "max_tokens": max_reply_tokens,
                    "n": 1,
                    "stop": None, # Allow the model to complete the response without stopping at a newline character
                    "temperature": 1,
                },
            )

            if response.status_code != 200:
                print(f"OpenAI API Error: {response.status_code} - {response.text}")
                await message.channel.send("Sorry, there was an error processing your request.")
                return

            response_data = response.json()

            # Extract the generated response
            gpt_response = response_data['choices'][0]['message']['content'].strip()

            # Edit the initial message with the actual response and emoji
            await working_message.edit(content=gpt_response)

client = ChatGPTBot(intents=intents)
client.run(DISCORD_TOKEN)
