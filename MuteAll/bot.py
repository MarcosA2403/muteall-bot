import discord
import os
import asyncio
import time
import sys

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
# VARIABLES DEMONIO
# =========================
AUTO_MODE = False
MIN_USERS_TRIGGER = 3
LAST_EVENT = "Sistema iniciado..."

# =========================
# PROTECCIÓN GLOBAL
# =========================
@bot.event
async def on_error(event, *args, **kwargs):
    print(f"⚠️ Error en evento {event}:", sys.exc_info())

@bot.event
async def on_application_command_error(ctx, error):
    print("❌ Error comando:", error)
    try:
        await ctx.respond("⚠️ Ocurrió un error", ephemeral=True)
    except:
        pass

# =========================
# EMBED DASHBOARD
# =========================
def get_dashboard_embed(enabled: bool):
    global LAST_EVENT

    if enabled:
        status = "🔴 MUTE ACTIVADO"
        bar = "██████████"
        color = discord.Color.red()
    else:
        status = "🟢 VOZ ACTIVADA"
        bar = "░░░░░░░░░░"
        color = discord.Color.green()

    embed = discord.Embed(
        title="👿 PANEL DEMONIO - CONTROL TOTAL",
        description="```diff\n+ Sistema en tiempo real\n```",
        color=color
    )

    embed.add_field(
        name="📡 Estado",
        value=f"```ini\n[{status}]\n```",
        inline=False
    )

    embed.add_field(
        name="⚡ Intensidad",
        value=f"`{bar}`",
        inline=False
    )

    embed.add_field(
        name="🚨 EVENT LOG",
        value=f"```diff\n{LAST_EVENT}\n```",
        inline=False
    )

    embed.add_field(
        name="🎮 Modo Auto",
        value=f"`{'ACTIVO' if AUTO_MODE else 'APAGADO'}`",
        inline=False
    )

    embed.set_footer(text="MuteAll Demon System")
    return embed

# =========================
# PANEL
# =========================
class MuteAllPanel(discord.ui.View):
    def __init__(self, enabled=True):
        super().__init__(timeout=None)
        self.enabled = enabled

    def is_admin(self, interaction):
        return interaction.user.guild_permissions.administrator

    @discord.ui.button(label="🔇 Shut Up", style=discord.ButtonStyle.red, custom_id="muteall_toggle")
    async def toggle(self, button, interaction):

        global LAST_EVENT

        if not self.is_admin(interaction):
            return await interaction.response.send_message("❌ Solo admins", ephemeral=True)

        await interaction.response.defer()
        ctx = await bot.get_application_context(interaction)

        try:
            if self.enabled:
                await do_all(ctx, "")
                self.enabled = False
                LAST_EVENT = "- Voz silenciada globalmente"

                button.label = "🔊 Speak"
                button.style = discord.ButtonStyle.green
            else:
                await do_unall(ctx, "")
                self.enabled = True
                LAST_EVENT = "+ Voz restaurada"

                button.label = "🔇 Shut Up"
                button.style = discord.ButtonStyle.red

        except Exception as e:
            print("Error:", e)

        await interaction.message.edit(embed=get_dashboard_embed(self.enabled), view=self)

    @discord.ui.button(label="🎮 Game Mode", style=discord.ButtonStyle.blurple, custom_id="game_mode")
    async def game_mode(self, button, interaction):

        global AUTO_MODE, LAST_EVENT

        if not self.is_admin(interaction):
            return await interaction.response.send_message("❌ Solo admins", ephemeral=True)

        AUTO_MODE = not AUTO_MODE
        LAST_EVENT = f"{'+' if AUTO_MODE else '-'} AutoMode {'activado' if AUTO_MODE else 'desactivado'}"

        await interaction.response.defer()

        await interaction.message.edit(embed=get_dashboard_embed(self.enabled), view=self)

# =========================
# VOICE INTELIGENTE
# =========================
@bot.event
async def on_voice_state_update(member, before, after):
    global AUTO_MODE, LAST_EVENT

    if not AUTO_MODE:
        return

    channel = after.channel or before.channel
    if not channel:
        return

    members = channel.members

    try:
        if len(members) >= MIN_USERS_TRIGGER:
            for m in members:
                await m.edit(mute=True)

            LAST_EVENT = f"+ AUTO-MUTE ({len(members)} users)"

        else:
            for m in members:
                await m.edit(mute=False)

            LAST_EVENT = f"- AUTO-UNMUTE ({len(members)} users)"

    except:
        pass

# =========================
# BOT START (INMORTAL)
# =========================
def run():
    while True:
        try:
            print("🔥 Iniciando...")
            bot.run(os.getenv("DISCORD_TOKEN"), reconnect=True)
        except Exception as e:
            print("💥 Crash:", e)
            time.sleep(5)

# =========================
# READY
# =========================
@bot.event
async def on_ready():
    await handle_ready(bot)

    bot.add_view(MuteAllPanel())

    channel_id = 1495931349809496254
    channel = bot.get_channel(channel_id)

    if channel:
        async for msg in channel.history(limit=20):
            if msg.author == bot.user:
                await msg.edit(embed=get_dashboard_embed(True), view=MuteAllPanel(True))
                return

        await channel.send(embed=get_dashboard_embed(True), view=MuteAllPanel(True))

# =========================
# COMANDOS
# =========================
@bot.slash_command(name="ping")
async def ping(ctx):
    await ctx.respond(f"Pong! {round(bot.latency * 1000)} ms")

@bot.slash_command(name="help")
async def help_command(ctx):
    await ctx.respond(embed=get_help())

@bot.slash_command(name="stats")
async def stats(ctx):
    guilds, members = get_stats(bot)
    await ctx.respond(f"{members} usuarios en {guilds} servidores")

@bot.slash_command(name="all")
async def all_command(ctx, mentions: discord.Option(str, "") = ""):
    await handle_errors(ctx, do_all, mentions)

@bot.slash_command(name="unall")
async def unall(ctx, mentions: discord.Option(str, "") = ""):
    await handle_errors(ctx, do_unall, mentions)
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
