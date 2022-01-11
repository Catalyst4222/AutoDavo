import random as r
import discord
import utils

# 8x8 with 10 mines
# 16x16 with 40 mines
# 16x30 with 99 mines

minemoji = [
    "||:zero:||",
    "||:one:||",
    "||:two:||",
    "||:three:||",
    "||:four:||",
    "||:five:||",
    "||:six:||",
    "||:seven:||",
    "||:eight:||",
    "||:bomb:||",
    ":zero:",  # Entry 10 also corresponds to entry -1, the open tile
]


def clamp(val, btm, top):
    return max(btm, min(val, top))


async def minesweeper(cmd, args: str, src: discord.Message):
    width = 8
    height = 8
    minecount = 10

    argsplit = args.split(" ")

    # Work out what the user arguments are, and use them to define the parameters for the minesweeper board (whether using presets or custom design)
    if len(argsplit) == 0:
        width = 8
        height = 8
        minecount = 10
    elif len(argsplit) == 1:
        if argsplit[0] == "easy":
            width = 8
            height = 8
            minecount = 10
        elif argsplit[0] == "intermediate":
            width = 16
            height = 16
            minecount = 40
        elif argsplit[0] == "hard":
            width = 30
            height = 16
            minecount = 99
        else:
            await utils.send_safe(
                "Error: Invalid difficulty selected! "
                "Valid options are: `easy`, `intermediate` & `hard`!",
                src.channel,
            )
            return

    elif len(argsplit) == 3:
        width = int(argsplit[0])
        height = int(argsplit[1])
        minecount = int(argsplit[2])

        if width > 38:
            await utils.send_safe(
                "Invalid width! The maximum is **38** tiles", src.channel
            )
            return
        elif height > 50:
            await utils.send_safe(
                "Invalid height! The maximum is **50** tiles", src.channel
            )
            return
        elif minecount > (width * height) / 2:
            await utils.send_safe(
                "Invalid mine-count! The maximum is **50%** of tiles", src.channel
            )
            return

    grid = [[0 for y in range(height)] for x in range(width)]
    mines = 0

    # Randomly place the required number of mines in the grid, updating surrounding tiles.
    while mines < minecount:
        rx = r.randrange(width)
        ry = r.randrange(height)

        if grid[rx][ry] == 9:  # If there is already a mine, don't place another
            continue

        grid[rx][ry] = 9  # This square is now a mine
        mines += 1  # One more mine has been placed

        for x in range(
            clamp(rx - 1, 0, width), clamp(rx + 2, 0, width)
        ):  # Check all neighbouring cells in case they need incrementing
            for y in range(clamp(ry - 1, 0, height), clamp(ry + 2, 0, height)):
                if (x == rx and y == ry) or grid[x][y] == 9:
                    # The actual mine cell and any other nearby mines can be disregarded
                    continue
                grid[x][y] += 1

    # Find the zeros in the grid, and randomly make one of them start open, to give a starting-point.
    zeros = []
    for x in range(width):
        for y in range(height):
            if grid[x][y] == 0:
                zeros.append([x, y])

    emptyzero = zeros[r.randrange(len(zeros))]

    grid[emptyzero[0]][emptyzero[1]] = -1

    # Begin sending the output messages corresponding to the minesweeper board. Each message is allowed only 80 tiles, as Discord limits the number of emoji per message

    curtiles = 0  # Max can be set to 80 per message
    msg = ""

    for y in range(height):
        for x in range(width):
            msg += minemoji[grid[x][y]]

        curtiles += width

        if curtiles + width > 80:
            await utils.send_safe(msg, src.channel)
            msg = ""
            curtiles = 0
        else:
            msg += "\n"

    if len(msg) > 0:
        await utils.send_safe(msg, src.channel)
