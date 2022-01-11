"""This file holds the base classes used to manage commands and command groups"""
import discord

import restrictions as r
from typing import List, Optional, Callable, Coroutine, Any, Awaitable


# Object representing a grouped collection of commands
class CommandGroup(object):
    def __init__(
        self,
        name: str,
        desc: str,
        useParentPerms: bool = True,
        restrict: r.RestrictLevel = r.RES_EMPTY,
    ):
        self.name = name
        self.desc = desc
        self.useParentPerms = useParentPerms
        self.restrict = restrict
        self.parent: Optional[CommandGroup] = None  # To be set when added to a group

        self.commands: List[Command] = []
        self.subgroups: List[CommandGroup] = []

    def addCommand(self, c: "Command"):
        c.parent = self
        self.commands.append(c)

    def command(
        self,
        *,
        name: Optional[str] = None,
        desc: Optional[str] = None,
        args: List[str] = None,
        useGroupPerms: bool = True,
        restrict: r.RestrictLevel = r.RES_EMPTY
    ) -> Callable[[Callable[["Command", List[str], discord.Message], Any]], "Command"]:
        return command(
            name=name,
            desc=desc,
            args=args,
            useGroupPerms=useGroupPerms,
            restrict=restrict,
            group=self,
        )

    def addSubgroup(self, sg: "CommandGroup"):
        sg.parent = self
        self.subgroups.append(sg)

    def subgroup(
        self,
        name: str,
        desc: str,
        useParentPerms: bool = True,
        restrict: r.RestrictLevel = r.RES_EMPTY,
    ) -> "CommandGroup":
        sub = CommandGroup(
            name=name, desc=desc, useParentPerms=useParentPerms, restrict=restrict
        )
        self.subgroups.append(sub)
        return sub

    async def run_cmd(self, name, args, src, perms) -> bool:
        """
        Iterative function to find a command in a command group or its subgroups & execute it
        :param self: The group to run
        :param name: The name of the command
        :param args: The arguments given
        :param src: The invoking message
        :param perms:
        :return: True if a command ran, False otherwise
        """
        for (
            g
        ) in (
            self.subgroups
        ):  # Check all subgroups first, and break out of the function if a command is found there
            if await g.run_cmd(
                name, args, src, perms if g.useParentPerms else g.restrict
            ):
                return True

        for c in self.commands:  # Now check all functions in the current group
            if c.name == name:
                await c.execute(args, src, perms if c.useGroupPerms else c.restrict)
                return True

        return False


# Basic object which stores the command's name and corresponding function
class Command(object):
    def __init__(
        self,
        name: str,
        func: Callable[["Command", str, discord.Message], Awaitable[Any]],
        args,
        desc: str,
        useGroupPerms: bool = True,
        restrict: r.RestrictLevel = r.RES_EMPTY,
        group: Optional[CommandGroup] = None,
    ):
        self.name = name  # Refactored from cmd
        self.func = func
        self.desc = desc
        self.args = args
        self.useGroupPerms = useGroupPerms
        self.restrict = restrict

        self.parent = group  # Can be set when added to a group
        if group is not None and self not in group.commands:
            group.addCommand(self)

    # Runs the actual command itself, after checking it's allowed to do so (TODO)
    async def execute(self, args, src, perms):
        """
        Run the command after going through the required checks
        :param args: The args to pass
        :param src: The invoking message
        :param perms: The user's permissions
        :return:
        """
        # You could raise errors here if you want, it should go to Client.on_error -Cata
        await self.func(self, args, src)


# TODO add command decorator -Cata
def command(
    *,
    name: Optional[str] = None,
    desc: Optional[str] = None,
    args: List[str] = None,
    useGroupPerms: bool = True,
    restrict: r.RestrictLevel = r.RES_EMPTY,
    group=None
) -> Callable[
    [Callable[[Command, List[str], discord.Message], Any]], Command
]:  # Weird return value b/c decorator
    """
    Decorator to turn a function into a command
    :param name: Name of the command. If not passed, uses the function name
    :param desc: Description of the command. If not passed,uses the function docstring
    :param args: The expected arguments for the help command
    :param useGroupPerms: If the command should use the restrictions of the group
    :param restrict: The restriction level needed to run the command
    :return: A Command object
    """

    def decorator(
        coro: Callable[[Command, str, discord.Message], Awaitable[Any]]
    ) -> Command:
        return Command(
            name=name or coro.__name__,
            func=coro,
            args=args or ["None"],
            desc=desc or coro.__doc__ or "Unknown",
            useGroupPerms=useGroupPerms,
            restrict=restrict,
            group=group,
        )

    return decorator
