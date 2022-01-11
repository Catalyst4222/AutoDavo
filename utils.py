"""This file contains a bunch of utility functions, for various purposes"""

import discord
from typing import List, Optional

SafeMentions = discord.AllowedMentions(
    everyone=False, users=True, roles=False, replied_user=True
)  # A set of mention perms which don't allow dangerous mentions


# TODO: add in **kwargs or similar to use full power of send (e.x. embeds) -Cata
async def send_safe(message, channel: discord.abc.Messageable) -> discord.Message:
    """
    Sends a message, without risking an @everyone or role ping
    :param message: The message content to send
    :param channel: Where to send the message
    :return: The message sent
    """
    return await channel.send(message, allowed_mentions=SafeMentions)


def split_space(
    args: str,
) -> List[str]:  # Seems to do the same thing twice, different quotes don't matter -Cata
    out = args.split(" ")
    try:
        out.remove("")
    except ValueError:
        pass  # ValueError occurs if no such values exist, which doesn't matter'

    try:
        out.remove("")
    except ValueError:
        pass  # ValueError occurs if no such values exist, which doesn't matter

    if out is None:
        return []

    return out


def split_args(args: str) -> list:
    """
    Splits all arguments given to a function.
    Generally if more than 1 argument is required, they will be split by spaces, but arguments with spaces can be split with quotes ("")
    :param args:
    :return:
    """

    quotesplit = args.split('"')

    if (
        len(quotesplit) == 1
    ):  # If quotes were not used the rest of the code is redundant
        return split_space(
            args
        )  # Remove any blank entries from the array (in case someone double-spaces by mistake)

    unquoted = quotesplit[::2]
    quoted = quotesplit[1::2]

    out = []

    out.extend(split_space(unquoted[0]))
    # The first element in the array will always be an unquoted argument (or an empty string), so add that to the
    # array first

    # Alternate elements from now on will be single quoted arguments and space-separated arrays of unquoted arguments, so add each in turn
    for i in range(len(quoted)):
        out.append(quoted[i])
        out.extend(split_space(unquoted[i + 1]))

    try:  # Seems to do the same thing twice, different quotes don't matter -Cata
        out.remove("")
    except ValueError:
        pass  # ValueError occurs if no such values exist, which doesn't matter

    try:
        out.remove("")
    except ValueError:
        pass  # ValueError occurs if no such values exist, which doesn't matter

    return out


def get_user(arg, src: discord.Message) -> Optional[discord.User]:

    if arg[0:3] == "<@!":
        arg = arg[
            3:-1
        ]  # If the argument is a ping, it will start with "<&!" and end with ">", so remove those characters to extract the ID

    try:
        iarg = int(arg)  # Can throw ValueError
        mem = src.guild.get_member(iarg)  # Try to find the member from their ID

        if (
            mem is None
        ):  # searching for a name here wouldn't work unless their name is a number -Cata
            mem = src.guild.get_member_named(
                arg
            )  # If finding them from their ID fails, try instead treating it as a name

        return mem

    except ValueError:  # Arg might not be an int, in which case it will throw ValueError. Try treating it as a name and search for that
        return src.guild.get_member_named(arg)


# Gets all users (Members) mentioned in a command message
def get_users(args: str, src: discord.Message) -> List[discord.Member]:
    args = split_args(args)

    users = []

    reply = src.reference

    if reply is not None:
        users.append(reply.resolved.author)

    for arg in args:
        u = get_user(arg, src)
        if u is not None:
            users.append(u)

    return users
