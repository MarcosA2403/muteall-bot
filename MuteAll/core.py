import discord
from MuteAll.utils import can_do, get_affected_users


async def safe_respond(ctx, content, delete_after=3):
    try:
        # 🔹 Para botones (interaction defer)
        msg = await ctx.interaction.followup.send(content)
        await msg.delete(delay=delete_after)
    except:
        try:
            # 🔹 Para slash commands normales
            await ctx.respond(content, delete_after=delete_after)
        except:
            pass


async def do(task="mute", members=None):
    if members is None:
        return

    for member in members:
        try:
            match task:
                case "mute":
                    await member.edit(mute=True)
                case "unmute":
                    await member.edit(mute=False)
                case "end":
                    await member.edit(mute=False)
                case "deafen":
                    await member.edit(deafen=True)
                case "undeafen":
                    await member.edit(deafen=False)
                case "all":
                    await member.edit(mute=True)
                    await member.edit(deafen=True)
                case "unall":
                    await member.edit(mute=False)
                    await member.edit(deafen=False)
        except:
            pass  # evita errores si alguien no está en voz


# =========================
# COMANDOS
# =========================

async def do_mute(ctx, mentions):
    canDo = can_do(ctx, requiredPermissions=["mute"])
    if canDo != "OK":
        return await safe_respond(ctx, canDo)

    members = ctx.author.voice.channel.members if len(mentions) == 0 else get_affected_users(ctx, mentions)

    await do("mute", members)
    await safe_respond(ctx, "👍")


async def do_unmute(ctx, mentions):
    canDo = can_do(ctx)
    if canDo != "OK":
        return await safe_respond(ctx, canDo)

    members = ctx.author.voice.channel.members if len(mentions) == 0 else get_affected_users(ctx, mentions)

    await do("unmute", members)
    await safe_respond(ctx, "👍")


async def do_deafen(ctx, mentions):
    canDo = can_do(ctx, requiredPermissions=["deafen"])
    if canDo != "OK":
        return await safe_respond(ctx, canDo)

    members = ctx.author.voice.channel.members if len(mentions) == 0 else get_affected_users(ctx, mentions)

    await do("deafen", members)
    await safe_respond(ctx, "👍")


async def do_undeafen(ctx, mentions):
    canDo = can_do(ctx)
    if canDo != "OK":
        return await safe_respond(ctx, canDo)

    members = ctx.author.voice.channel.members if len(mentions) == 0 else get_affected_users(ctx, mentions)

    await do("undeafen", members)
    await safe_respond(ctx, "👍")


async def do_all(ctx, mentions):
    canDo = can_do(ctx, requiredPermissions=["mute", "deafen"])
    if canDo != "OK":
        return await safe_respond(ctx, canDo)

    members = ctx.author.voice.channel.members if len(mentions) == 0 else get_affected_users(ctx, mentions)

    await do("all", members)
    await safe_respond(ctx, "<:mute:1487259209849638923>")


async def do_unall(ctx, mentions):
    canDo = can_do(ctx)
    if canDo != "OK":
        return await safe_respond(ctx, canDo)

    members = ctx.author.voice.channel.members if len(mentions) == 0 else get_affected_users(ctx, mentions)

    await do("unall", members)
    await safe_respond(ctx, "<:unmute:1487265179547996270>")


# =========================
# REACCIONES
# =========================

async def add_reactions(ctx, emojis):
    canDo = can_do(ctx, requiredPermissions=["mute", "deafen"])
    if canDo != "OK":
        return await safe_respond(ctx, canDo)

    embed = discord.Embed()
    embed.set_author(name="Reaction Commands")
    embed.add_field(name=emojis["MUTE"], value="mute")
    embed.add_field(name=emojis["UNMUTE"], value="un-mute")
    embed.add_field(name=emojis["DEAFEN"], value="deafen")
    embed.add_field(name=emojis["UNDEAFEN"], value="un-deafen")
    embed.add_field(name=emojis["ALL"], value="mute + deafen")
    embed.add_field(name=emojis["UNALL"], value="un-mute + un-deafen")

    msg = await ctx.respond("React with an emoji below!", delete_after=5)

    message = await ctx.send(embed=embed)

    for emoji in emojis.values():
        await message.add_reaction(emoji)
