import discord
import os
import asyncio
from discord import FFmpegPCMAudio

from MuteAll.core import (
    do_mute, do_unmute, do_deafen, do_undeafen,
    do_all, do_unall, add_reactions
)
from MuteAll.errors import show_common_error, show_permission_error
from MuteAll.events import handle_ready, handle_reaction
from MuteAll.utils import get_help, get_stats, handle_errors
from MuteAll.emojis import get_emojis

bot = discord.AutoShardedBot()

# =========================
# 🔊 FUNCIÓN DE AUDIO
# =========================
async def play_sound(interaction, file):
    if not interaction.user.voice:
        return

    channel = interaction.user.voice.channel

    vc = await channel.connect()

    vc.play(FFmpegPCMAudio(file))

    while vc.is_playing():
        await asyncio.sleep(1)

    await vc.disconnect()


# =========================
# PANEL DE CONTROL
# =========================
class MuteAllPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.enabled = True

    def is_admin(self, interaction: discord.Interaction):
        return interaction.user.guild_permissions.administrator

    @discord.ui.button(
    label="🔇 Shut Up",
    style=discord.ButtonStyle.red,
    custom_id="muteall_toggle"
)
async def toggle(self, button: discord.ui.Button, interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(
            "❌ Solo administradores",
            ephemeral=True
        )

    ctx = await bot.get_application_context(interaction)

    # 🧠 detectar estado REAL por el texto
    if "Shut Up" in button.label:
        # 🔇 MUTEAR
        await do_all(ctx, "")

        button.label = "🔊 Speak"
        button.style = discord.ButtonStyle.green

    else:
        # 🔊 DESMUTEAR
        await do_unall(ctx, "")

        button.label = "🔇 Shut Up"
        button.style = discord.ButtonStyle.red

    await interaction.edit_original_response(view=self)

# =========================
# BOT START
# =========================
def run():
    bot.run(os.getenv("DISCORD_TOKEN"), reconnect=True)


@bot.event
async def on_ready():
    await handle_ready(bot)

    bot.add_view(MuteAllPanel())

    channel_id = 1493790351914438747
    channel = bot.get_channel(channel_id)

    if channel:
        async for msg in channel.history(limit=20):
            if msg.author == bot.user and "Panel de control MuteAll" in msg.content:
                await msg.edit(view=MuteAllPanel())
                return

        await channel.send(
            "⚙️ Panel de control MuteAll",
            view=MuteAllPanel()
        )


# =========================
# INFO COMMANDS
# =========================
@bot.slash_command(name="ping")
async def ping(ctx):
    await ctx.respond(f"Pong! {round(bot.latency * 1000)} ms")


@bot.slash_command(name="help")
async def help_command(ctx):
    await ctx.respond(embed=get_help())


@bot.slash_command(name="stats")
async def stats(ctx):
    g, m = get_stats(bot)
    await ctx.respond(f"MuteAll usado por `{m}` usuarios en `{g}` servidores!")


# =========================
# MAIN COMMANDS
# =========================
@bot.slash_command(name="mute")
async def mute(ctx, mentions: str = ""):
    await handle_errors(ctx, bot, do_mute, mentions)


@bot.slash_command(name="m")
async def mute_short(ctx, mentions: str = ""):
    await handle_errors(ctx, bot, do_mute, mentions)


@bot.slash_command(name="unmute")
async def unmute(ctx, mentions: str = ""):
    await handle_errors(ctx, bot, do_unmute, mentions)


@bot.slash_command(name="u")
async def unmute_short(ctx, mentions: str = ""):
    await handle_errors(ctx, bot, do_unmute, mentions)


@bot.slash_command(name="deafen")
async def deafen(ctx, mentions: str = ""):
    await handle_errors(ctx, bot, do_deafen, mentions)


@bot.slash_command(name="undeafen")
async def undeafen(ctx, mentions: str = ""):
    await handle_errors(ctx, bot, do_undeafen, mentions)


@bot.slash_command(name="all")
async def all_command(ctx, mentions: str = ""):
    await handle_errors(ctx, bot, do_all, mentions)


@bot.slash_command(name="unall")
async def unall(ctx, mentions: str = ""):
    await handle_errors(ctx, bot, do_unall, mentions)

# DEPRECATED #################################################

# # respond a help msg when the bot joins a server
# @bot.event
# async def on_guild_join(guild):
#     await on_guild_join(guild)


# @bot.command()
# async def changeprefix(ctx, prefix):
#     await prefixes.changeprefix(ctx, prefix)


# @bot.command(aliases=["prefix"])
# async def viewprefix(ctx):
#     await prefixes.viewprefix(ctx)

# @bot.command(aliases=["e", "E", "End"])
# async def end(ctx, *args):

#     if len(args) == 0:
#         members = ctx.author.voice.channel.members
#     else:
#         members = await get_affected_users(ctx, args)

#     await do(ctx, task="end", members=members)

# @bot.command(aliases=["udme", "Undeafenme"])
# async def undeafenme(ctx):
#     await do(ctx, task="undeafen", members=[ctx.author])

# DEPRECATED #################################################
