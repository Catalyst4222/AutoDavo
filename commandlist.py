import discord
import restrictions as r
import command as c
import utils

import games.minesweeper as mines

SafeMentions = discord.AllowedMentions(
    everyone=False, users=True, roles=False, replied_user=False
)


# Commands are temporarily placed here but will be moved to other files


async def repeat(cmd, args, src):
    await utils.send_safe(args, src.channel)
    print(args)


async def d_args(
    cmd, args, src
):  # Send a separated list of all arguments, for debug of argument split functionality
    split = utils.split_args(args)
    out = "Arguments: [" + split[0]
    split = split[1:]

    for s in split:
        out += "," + s
    out += "]"

    print(out)
    await utils.send_safe(out, src.channel)


async def help_string_group(src, group, level=0):
    newline = "\n"
    # for i in range(level):
    #    newline += "\t"

    msg = (
        "\n"
        + newline
        + "__**"
        + group.name
        + "**__"
        + newline
        + "*"
        + group.desc
        + "*\n"
    )
    # newline += "\t"

    for c in group.commands:
        msg += newline + "**• " + c.name + "**"
        if len(c.args) > 0:
            msg += "{"
            msg += "*" + c.args[0] + "*"
            for a in c.args[1:]:
                msg += ",*" + a + "*"
            msg += "}: " + c.desc

    for g in group.subgroups:
        msg += await help_string_group(src, g, level + 1)

    return msg


async def help_search(src, group, name):
    if group.name == name:
        await utils.send_safe(await help_string_group(src, group), src.channel)

    for c in group.commands:
        if c.name == name:
            await utils.send_safe(
                "Command " + name + " located TODO implement full functionality",
                src.channel,
            )
            return True

    return any(await help_search(src, g, name) for g in group.subgroups)


"""Define all the groups and their commands"""

CommandRoot = c.CommandGroup(
    "General", "Contains basic commands! See the subgroups for more specific types"
)


@CommandRoot.command(name="ping", desc="Basic test command",)
async def ping(cmd, args, src):
    print(*args)
    await src.channel.send("Pong!")


@CommandRoot.command(
    name="help",
    args=["Entry (optional)"],
    desc="Gives information on the usage of different commands. Can be narrowed to a "
    "specific category or even a single command for more detail.",
)
async def helpc(cmd, args, src):
    args = args.split()
    if len(args) == 0:
        await utils.send_safe(await help_string_group(src, CommandRoot), src.channel)
    elif len(args) == 1:
        await help_search(src, CommandRoot, args[0])
    else:
        await utils.send_safe("[Error] More than 1 argument given!", src.channel)


g_games = CommandRoot.subgroup(
    "Games", "Contains various interactive game commands!", r.RES_EMPTY
)
g_games.addCommand(
    c.Command(
        "minesweeper",
        mines.minesweeper,
        ["Width", "Height"],
        "Generates a random Minesweeper board for you to complete!",
    )
)


g_misc = CommandRoot.subgroup(
    "misc",
    "Contains various random commands which don't fit into any other group",
)


@g_misc.command(
    name="avatar", args=["User"], desc="Obtains the avatar for a given account!"
)
async def avatar(cmd, args, src):
    mems = utils.get_users(args, src)

    if len(mems) == 0:
        user = src.author
    elif len(mems) > 1:
        await utils.send_safe(
            "[Error] Too many arguments given! The maximum is 1 member per command", src
        )
        return
    elif mems[0] is None:
        await utils.send_safe(
            "[Error] Argument does not contain a valid user! Please try again", src
        )
        return
    else:
        user = mems[0]

    await utils.send_safe(user.avatar_url_as(static_format="png"), src.channel)


@g_misc.command(
    name="defaultavatar",
    args=["User"],
    desc="Obtains the default avatar for a given account!",
)
async def defaultavatar(cmd, args, src):
    mems = utils.get_users(args, src)

    if len(mems) == 0:
        return utils.send_safe(src.author.default_avatar_url, src.channel)
    elif len(mems) > 1:
        await utils.send_safe(
            "[Error] Too many arguments given! The maximum is 1 member per command", src
        )
    elif mems[0] is None:
        await utils.send_safe(
            "[Error] Argument does not contain a valid user! Please try again", src
        )

    await utils.send_safe(mems[0].default_avatar_url, src.channel)


@g_misc.command(name="hug", args=["Target"], desc="Send somebody a big hug!")
async def hug(cmd, args, src):
    auth = src.author.mention
    await utils.send_safe("**" + auth + "** hugs **" + args + "!**", src.channel)


@g_misc.command(
    name="unformat",
    args=["Text"],
    desc="Undoes any markdown format in the requested message",
)
async def unformat(cmd, args, src):
    out = discord.utils.escape_markdown(args)
    await utils.send_safe(out, src.channel)


def init_list():

    # g_misc.commands = [
    #     c.Command(
    #         "avatar", avatar, ["User"], "Obtains the avatar for a given account!"
    #     ),
    #     c.Command(
    #         "defaultavatar",
    #         defaultavatar,
    #         ["User"],
    #         "Obtains the default avatar for a given account!",
    #     ),
    #     c.Command("hug", hug, ["Target"], "Send somebody a big hug!"),
    #     c.Command(
    #         "unformat",
    #         unformat,
    #         ["Text"],
    #         "Undoes any markdown format in the requested message",
    #     ),
    # ]

    # g_games = c.CommandGroup(
    #     "Games", "Contains various interactive game commands!", r.RES_EMPTY
    # )
    # g_games.commands = [
    #     c.Command(
    #         "minesweeper",
    #         mines.minesweeper,
    #         ["Width", "Height"],
    #         "Generates a random Minesweeper board for you to complete!",
    #     )
    # ]

    g_debug = c.CommandGroup(
        "Debug", "Contains commands used for debugging the bot", r.RES_EMPTY
    )
    g_debug.commands = [
        c.Command(
            "args",
            d_args,
            ["Argument1", "Argument2[...]"],
            "Lists the individual arguments in a given message",
        ),
        c.Command(
            "repeat",
            repeat,
            ["Text"],
            "Sends back the requested message, and also logs it to console",
        ),
        ping,
    ]

    CommandRoot.addSubgroup(g_misc)
    # CommandRoot.addSubgroup(g_games)
    CommandRoot.addSubgroup(g_debug)
