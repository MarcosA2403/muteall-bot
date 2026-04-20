import discord
import os
import asyncio

from MuteAll.core import do_all, do_unall
from MuteAll.events import handle_ready

bot = discord.AutoShardedBot()

# =========================
# AUDIO
# =========================
async def play_sound(interaction, file_path):
    if not interaction.user.voice:
        return

    channel = interaction.user.voice.channel
    vc = discord.utils.get(bot.voice_clients, guild=interaction.guild)

    try:
        if vc and vc.is_connected():
            if vc.channel != channel:
                await vc.move_to(channel)
        else:
            vc = await channel.connect()

        if vc.is_playing():
            vc.stop()

        source = discord.FFmpegPCMAudio(file_path)
        vc.play(source)

        while vc.is_playing():
            await asyncio.sleep(0.5)

    except Exception as e:
        print("Audio error:", e)

    finally:
        if vc and vc.is_connected():
            await vc.disconnect()


# =========================
# PANEL
# =========================
class MuteAllPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.enabled = True

    def is_admin(self, interaction):
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

        if self.enabled:
            await play_sound(interaction, "sounds/shutup.mp3")
            await do_all(ctx, "")

            self.enabled = False
            button.label = "🔊 Speak"
            button.style = discord.ButtonStyle.green

        else:
            await play_sound(interaction, "sounds/speak.mp3")
            await do_unall(ctx, "")

            self.enabled = True
            button.label = "🔇 Shut Up"
            button.style = discord.ButtonStyle.red

        await interaction.edit_original_response(view=self)


# =========================
# BOT START
# =========================
@bot.event
async def on_ready():
    await handle_ready(bot)
    bot.add_view(MuteAllPanel())

    channel = bot.get_channel(1493790351914438747)

    if channel:
        await channel.send(
            "⚙️ Panel de control MuteAll",
            view=MuteAllPanel()
        )


def run():
    bot.run(os.getenv("DISCORD_TOKEN"))

# =========================
# INFO COMMANDS
# =========================
@bot.slash_command(name="ping", description="show latency of the bot")
async def ping(ctx: discord.ApplicationContext):
    await ctx.respond(f"Pong! {round(bot.latency * 1000)} ms")


@bot.slash_command(name="help", description="get some help!")
async def help_command(ctx: discord.ApplicationContext):
    help_embed = get_help()
    await ctx.respond(embed=help_embed)


@bot.slash_command(name="stats", description="show stats")
async def stats(ctx: discord.ApplicationContext):
    guilds, members = get_stats(bot)
    await ctx.respond(
        f"MuteAll is used by `{members}` users in `{guilds}` servers!"
    )


# =========================
# MAIN COMMANDS
# =========================
@bot.slash_command(name="mute", description="server mute people!")
async def mute(ctx: discord.ApplicationContext,
               mentions: discord.Option(str, "") = ""):
    await handle_errors(ctx, bot, do_mute, mentions)


@bot.slash_command(name="m", description="server mute people!")
async def mute_short(ctx: discord.ApplicationContext,
                     mentions: discord.Option(str, "") = ""):
    await handle_errors(ctx, bot, do_mute, mentions)


@bot.slash_command(name="unmute", description="unmute people!")
async def unmute(ctx: discord.ApplicationContext,
                 mentions: discord.Option(str, "") = ""):
    await handle_errors(ctx, bot, do_unmute, mentions)


@bot.slash_command(name="u", description="unmute people!")
async def unmute_short(ctx: discord.ApplicationContext,
                       mentions: discord.Option(str, "") = ""):
    await handle_errors(ctx, bot, do_unmute, mentions)


@bot.slash_command(name="um", description="unmute people!")
async def unmute_short2(ctx: discord.ApplicationContext,
                        mentions: discord.Option(str, "") = ""):
    await handle_errors(ctx, bot, do_unmute, mentions)


@bot.slash_command(name="deafen", description="deafen people!")
async def deafen(ctx: discord.ApplicationContext,
                 mentions: discord.Option(str, "") = ""):
    await handle_errors(ctx, bot, do_deafen, mentions)


@bot.slash_command(name="d", description="deafen people!")
async def deafen_short(ctx: discord.ApplicationContext,
                       mentions: discord.Option(str, "") = ""):
    await handle_errors(ctx, bot, do_deafen, mentions)


@bot.slash_command(name="undeafen", description="undeafen people!")
async def undeafen(ctx: discord.ApplicationContext,
                   mentions: discord.Option(str, "") = ""):
    await handle_errors(ctx, bot, do_undeafen, mentions)


@bot.slash_command(name="ud", description="undeafen people!")
async def undeafen_short(ctx: discord.ApplicationContext,
                         mentions: discord.Option(str, "") = ""):
    await handle_errors(ctx, bot, do_undeafen, mentions)


@bot.slash_command(name="all", description="mute and deafen people!")
async def all_command(ctx: discord.ApplicationContext,
                      mentions: discord.Option(str, "") = ""):
    await handle_errors(ctx, bot, do_all, mentions)


@bot.slash_command(name="a", description="mute and deafen people!")
async def all_short(ctx: discord.ApplicationContext,
                    mentions: discord.Option(str, "") = ""):
    await handle_errors(ctx, bot, do_all, mentions)


@bot.slash_command(name="unall", description="unmute and undeafen people!")
async def unall(ctx: discord.ApplicationContext,
                mentions: discord.Option(str, "") = ""):
    await handle_errors(ctx, bot, do_unall, mentions)


@bot.slash_command(name="ua", description="unmute and undeafen people!")
async def unall_short(ctx: discord.ApplicationContext,
                      mentions: discord.Option(str, "") = ""):
    await handle_errors(ctx, bot, do_unall, mentions)


# =========================
# REACTIONS MODE
# =========================
@bot.slash_command(name="react", description="do everything using reactions!")
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
