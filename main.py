import discord
from discord import app_commands
from discord.ext import commands, tasks
from transformers import pipeline
import os

class ShapeBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        # Load Hugging Face Model
        self.detector = pipeline("object-detection", model="facebook/detr-resnet-50")

    async def setup_hook(self):
        await self.tree.sync()
        self.daily_cron.start()

    # CRON-JOB: Runs every 24 hours
    @tasks.loop(hours=24)
    async def daily_cron(self):
        print("Cron-Job: Performing daily maintenance and model check.")

# UI: The Link Button
class BotView(discord.ui.View):
    def __init__(self, url):
        super().__init__()
        self.add_item(discord.ui.Button(label="Source Image", url=url))

bot = ShapeBot()

@bot.tree.command(name="scan", description="Scan an image for shapes and objects")
async def scan(interaction: discord.Interaction, image_url: str):
    await interaction.response.defer() # Prevent timeout
    
    try:
        results = bot.detector(image_url)
        embed = discord.Embed(title="🔍 AI Scan Results", color=0x00ff00)
        embed.set_image(url=image_url)

        if results:
            for res in results[:5]:
                embed.add_field(
                    name=res['label'].capitalize(), 
                    value=f"Confidence: {round(res['score']*100, 1)}%", 
                    inline=True
                )
        else:
            embed.description = "No shapes or objects identified."

        await interaction.followup.send(embed=embed, view=BotView(image_url))
    except Exception as e:
        await interaction.followup.send(f"Error: `{e}`", ephemeral=True)

# Run using Environment Variable
bot.run(os.getenv('DISCORD_TOKEN'))
