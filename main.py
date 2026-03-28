import discord
from discord import app_commands
from discord.ext import commands, tasks
from transformers import pipeline
import os
from flask import Flask
from threading import Thread

# --- WEB SERVER FOR UPTIME CRON ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online"

def run(): app.run(host='0.0.0.0', port=10000)
def keep_alive():
    t = Thread(target=run)
    t.start()

# --- BOT SETUP ---
class ShapeBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        # Load model with timm support
        self.detector = pipeline("object-detection", model="facebook/detr-resnet-50")

    async def setup_hook(self):
        await self.tree.sync()
        self.health_check.start()

    @tasks.loop(minutes=30)
    async def health_check(self):
        print("Internal Cron: Bot heartbeat active.")

# UI Components
class ResultView(discord.ui.View):
    def __init__(self, url):
        super().__init__()
        self.add_item(discord.ui.Button(label="View Original Image", url=url))

bot = ShapeBot()

@bot.tree.command(name="scan", description="Scan image for shapes/objects")
async def scan(interaction: discord.Interaction, url: str):
    await interaction.response.defer()
    
    try:
        results = bot.detector(url)
        embed = discord.Embed(title="AI Analysis", color=0x2ecc71)
        embed.set_image(url=url)
        
        if results:
            for res in results[:5]:
                embed.add_field(name=res['label'], value=f"Confidence: {round(res['score'], 2)}", inline=True)
        else:
            embed.description = "No objects detected."
            
        await interaction.followup.send(embed=embed, view=ResultView(url))

    except Exception as e:
        error_msg = f"Failed to process image: {e}"
        # Send to channel
        await interaction.followup.send("An error occurred. Checking DMs...", ephemeral=True)
        # Send to User's DM
        try:
            await interaction.user.send(f"⚠️ **Scan Failed**\nURL: {url}\nError: `{error_msg}`")
        except discord.Forbidden:
            print("Could not DM user.")

if __name__ == "__main__":
    keep_alive() # Starts the web link for Render
    bot.run(os.getenv('DISCORD_TOKEN'))
