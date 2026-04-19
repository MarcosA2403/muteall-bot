import discord
import os

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
# PANEL DE CONTROL (FIXED)
# =========================
class MuteAllPanel(discord.ui.View):
    def __init__(self, enabled=True):
        super().__init__(timeout=None)
        self.enabled = enabled

        if self.enabled:
            self.add_item(self.button_on())
        else:
            self.add_item(self.button_off())

    def button_on(self):
        button = discord.ui.Button(
            label="🟢 MuteAll ON",
            style=discord.ButtonStyle.green
        )

        async def callback(interaction: discord.Interaction):
            ctx = await bot.get_application_context(interaction)

            await do_unall(ctx, "")

            # mensaje
            await interaction.followup.send("Shut Up", ephemeral=False)

            await interaction.response.edit_message(
                view=MuteAllPanel(enabled=False)
            )

        button.callback = callback
        return button

    def button_off(self):
        button = discord.ui.Button(
            label="🔴 MuteAll OFF",
            style=discord.ButtonStyle.red
        )

        async def callback(interaction: discord.Interaction):
            ctx = await bot.get_application_context(interaction)

            await do_all(ctx, "")

            # mensaje
            await interaction.followup.send("Shut Up", ephemeral=False)

            await interaction.response.edit_message(
                view=MuteAllPanel(enabled=True)
            )

        button.callback = callback
        return button


# =========================
# BOT START
# =========================
def run():
    bot.run(os.getenv("DISCORD_TOKEN"), reconnect=True)


@bot.event
async def on_ready():
    await handle_ready(bot)

    # registrar botones persistentes
    bot.add_view(MuteAllPanel())

    channel_id = 1495518779000492143
    channel = bot.get_channel(channel_id)

    if channel:
        async for msg in channel.history(limit=10):
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
    guilds, members = get_stats(bot)
    await ctx.respond(f"`{members}` users in `{guilds}` servers!")


# =========================
# COMMANDS
# =========================
@bot.slash_command(name="all")
async def all_command(ctx, mentions: discord.Option(str, "") = ""):
    await handle_errors(ctx, bot, do_all, mentions)


@bot.slash_command(name="unall")
async def unall(ctx, mentions: discord.Option(str, "") = ""):
    await handle_errors(ctx, bot, do_unall, mentions)


# =========================
# REACTIONS MODE
# =========================
@bot.slash_command(name="react")
async def react(ctx):
    try:
        emojis = get_emojis(bot)
        await add_reactions(ctx, emojis)

        @bot.event
        async def on_reaction_add(reaction, user):
            await handle_reaction(reaction, user, bot, ctx)

    except discord.Forbidden:
        return await show_permission_error(ctx)
    except Exception as e:
        return await show_common_error(ctx, bot, e)

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
