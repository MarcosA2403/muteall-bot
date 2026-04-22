import discord
from MuteAll.errors import show_common_error, show_permission_error


def get_help():
    embed = discord.Embed()

    embed.set_author(name="Help")

    embed.add_field(
        name="Slash Commands",
        value="Press / to view all the available commands",
        inline=False
    )

    embed.add_field(
        name="Bot not muting everyone?",
        value="Ask everyone to reconnect to the voice channel.",
        inline=False
    )

    embed.add_field(
        name="Need more help?",
        value="[Join support server](https://discord.gg/8hrhffR6aX)",
        inline=False
    )

    return embed


# =========================
# ERROR HANDLER (FIXED)
# =========================
async def handle_errors(ctx, function, mentions=""):
    try:
        await function(ctx, mentions)

    except discord.Forbidden:
        return await show_permission_error(ctx)

    except Exception as e:
        return await show_common_error(ctx, e)


# =========================
# PERMISSION CHECKS
# =========================
def can_do(ctx, requiredPermissions=None):

    if requiredPermissions is None:
        requiredPermissions = []

    if not ctx.guild:
        return "This does not work in DMs"

    if not ctx.author.voice:
        return "You must join a voice channel first"

    if "mute" in requiredPermissions:
        if not ctx.author.guild_permissions.mute_members:
            return "You don't have the `Mute Members` permission"

    if "deafen" in requiredPermissions:  # FIX typo (defean → deafen)
        if not ctx.author.guild_permissions.deafen_members:
            return "You don't have the `Deafen Members` permission"

    return "OK"


# =========================
# ROLE CHECK
# =========================
def has_role(member, role_id):
    return any(role.id == role_id for role in member.roles)


# =========================
# GET USERS FROM MENTIONS
# =========================
def get_affected_users(ctx, mentions):

    mentions_list = mentions.split(" ")
    affected_users = []

    for mention in mentions_list:

        if len(mention) < 4:
            continue

        try:
            if mention.startswith("<@&"):  # ROLE
                role_id = int(mention[3:-1])
                for member in ctx.author.voice.channel.members:
                    if has_role(member, role_id):
                        affected_users.append(member)

            elif mention.startswith("<@"):  # USER
                user_id = int(mention[3:-1])
                for member in ctx.author.voice.channel.members:
                    if member.id == user_id:
                        affected_users.append(member)

        except:
            continue

    return affected_users


# =========================
# STATS
# =========================
def get_stats(bot):

    guilds = bot.guilds
    no_of_guilds = len(guilds)
    no_of_members = 0

    for guild in guilds:
        no_of_members += guild.member_count

    return no_of_guilds, no_of_members

# def remove_empty_items(arr: list):
#     non_empty_arr: list = []

#     for item in arr:
#         if len(item) > 1:
#             non_empty_arr.append(item)

#     return non_empty_arr


# async def help(ctx):
#     embed = discord.Embed(color=discord.Color.lighter_grey())

#     embed.set_author(name="Available Commands")

#     embed.add_field(name="`.ping`", value="latency of the bot", inline=False)

#     embed.add_field(name="`.changeprefix <your prefix here>`",
#                     value="change the prefix for your server (only admin can use this!)", inline=False)

#     embed.add_field(name="`.viewprefix`",
#                     value="view prefix for your server", inline=False)

#     embed.add_field(name="`.mute` / `.m`", value="Mute humans and un-mute bots in your current voice channel.",
#                     inline=False)

#     embed.add_field(name="`.unmute` / `.u`", value="Un-mute humans and mute bots in your current voice channel.",
#                     inline=False)

#     embed.add_field(name="`.deafen` / `.d`", value="Deafen everyone in your current voice channel.",
#                     inline=False)

#     embed.add_field(name="`.undeafen` / `.ud`", value="Un-deafen everyone in your current voice channel.",
#                     inline=False)

#     embed.add_field(name="`.undeafenme` / `.udme`", value="Un-deafen only yourself.",
#                     inline=False)

#     embed.add_field(name="`.all` / `.a`", value="Mute and Deafen everyone in your current voice channel.",
#                     inline=False)

#     embed.add_field(name="`.unall` / `.ua`", value="Un-mute and Un-deafen everyone in your current voice channel.",
#                     inline=False)

#     embed.add_field(name="`.end` / `.e`",
#                     value="End the game, un-mute and un-deafen everyone (including bots)", inline=False)

#     embed.add_field(name="Bot not muting everyone?",
#                     value="Ask everyone to reconnect to the voice channel.", inline=False)

#     embed.add_field(
#         name="_", value="[Join support server](https://discord.gg/8hrhffR6aX)", inline=False)

#     await ctx.send(embed=embed)
