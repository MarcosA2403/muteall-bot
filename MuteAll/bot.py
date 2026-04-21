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
    if enabled:
        status = "🔴 MUTE ACTIVADO"
        bar = "██████████"
        color = discord.Color.red()
    else:
        status = "🟢 VOZ ACTIVADA"
        bar = "░░░░░░░░░░"
        color = discord.Color.green()

    embed = discord.Embed(
        title="🎮 PANEL DE CONTROL - VOZ",
        description="```diff\n+ Sistema en tiempo real\n```",
        color=color
    )

    embed.add_field(
        name="📡 Estado del Sistema",
        value=f"```ini\n[{status}]\n```",
        inline=False
    )

    embed.add_field(
        name="⚡ Intensidad",
        value=f"`{bar}`",
        inline=False
    )

    embed.add_field(
        name="🎛️ Control",
        value="🔇 Mute All\n🔊 Unmute All",
        inline=False
    )

    embed.set_footer(text="MuteAll System • Live Control Panel")
    return embed


# =========================
# PANEL DE CONTROL
# =========================
class MuteAllPanel(discord.ui.View):
    def __init__(self, enabled=True):
        super().__init__(timeout=None)
        self.enabled = enabled

    def is_admin(self, interaction: discord.Interaction):
        return interaction.user.guild_permissions.administrator

    @discord.ui.button(
        label="🔇 Shut Up",
        style=discord.ButtonStyle.red,
        custom_id="muteall_toggle"
    )
    async def toggle(self, button: discord.ui.Button, interaction: discord.Interaction):

        if not self.is_admin(interaction):
            return await interaction.response.send_message(
                "❌ Solo administradores",
                ephemeral=True
            )

        await interaction.response.defer()

        ctx = await bot.get_application_context(interaction)

        try:
            if self.enabled:
                await do_all(ctx, "")
                self.enabled = False

                button.label = "🔊 Speak"
                button.style = discord.ButtonStyle.green

            else:
                await do_unall(ctx, "")
                self.enabled = True

                button.label = "🔇 Shut Up"
                button.style = discord.ButtonStyle.red

        except Exception as e:
            print("🔥 Error en botón:", e)

        # 🔥 actualizar embed + botón
        await interaction.message.edit(
            embed=get_dashboard_embed(self.enabled),
            view=self
        )


# =========================
# BOT START (MODO INMORTAL)
# =========================
def run():
    while True:
        try:
            print("🔥 Iniciando bot...")
            bot.run(os.getenv("DISCORD_TOKEN"), reconnect=True)
        except Exception as e:
            print("💥 Bot crasheó:", e)
            print("🔁 Reiniciando en 5 segundos...")
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
            if msg.author == bot.user and "CONTROL DEL CIRCO" in msg.content:
                await msg.edit(
                    content=None,
                    embed=get_dashboard_embed(True),
                    view=MuteAllPanel(True)
                )
                return

        await channel.send(
            embed=get_dashboard_embed(True),
            view=MuteAllPanel(True)
        )


# =========================
# INFO COMMANDS
# =========================
@bot.slash_command(name="ping")
async def ping(ctx: discord.ApplicationContext):
    await ctx.respond(f"Pong! {round(bot.latency * 1000)} ms")


@bot.slash_command(name="help")
async def help_command(ctx: discord.ApplicationContext):
    await ctx.respond(embed=get_help())


@bot.slash_command(name="stats")
async def stats(ctx: discord.ApplicationContext):
    guilds, members = get_stats(bot)
    await ctx.respond(
        f"MuteAll is used by `{members}` users in `{guilds}` servers!"
    )


# =========================
# MAIN COMMANDS
# =========================
@bot.slash_command(name="mute")
async def mute(ctx: discord.ApplicationContext, mentions: discord.Option(str, "") = ""):
    await handle_errors(ctx, do_mute, mentions)


@bot.slash_command(name="unmute")
async def unmute(ctx: discord.ApplicationContext, mentions: discord.Option(str, "") = ""):
    await handle_errors(ctx, do_unmute, mentions)


@bot.slash_command(name="deafen")
async def deafen(ctx: discord.ApplicationContext, mentions: discord.Option(str, "") = ""):
    await handle_errors(ctx, do_deafen, mentions)


@bot.slash_command(name="undeafen")
async def undeafen(ctx: discord.ApplicationContext, mentions: discord.Option(str, "") = ""):
    await handle_errors(ctx, do_undeafen, mentions)


@bot.slash_command(name="all")
async def all_command(ctx: discord.ApplicationContext, mentions: discord.Option(str, "") = ""):
    await handle_errors(ctx, do_all, mentions)


@bot.slash_command(name="unall")
async def unall(ctx: discord.ApplicationContext, mentions: discord.Option(str, "") = ""):
    await handle_errors(ctx, do_unall, mentions)


# =========================
# REACTIONS MODE
# =========================
@bot.slash_command(name="react")
async def react(ctx: discord.ApplicationContext):
    try:
        emojis = get_emojis(bot)
        await add_reactions(ctx, emojis)

        @bot.event
        async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
            await handle_reaction(reaction, user, bot, ctx)

    except discord.Forbidden:
        return await show_permission_error(ctx)
    except Exception as e:
        return await show_common_error(ctx, e)
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
