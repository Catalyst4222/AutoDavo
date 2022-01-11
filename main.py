import discord
import commandlist as cl

# PROGRAM ENTRYPOINT
cl.init_list()
client = discord.Client(
    activity=discord.Game("Subscribe to Superdavo0001!"),
    intents=discord.Intents.default(),
)  # (activity=discord.CustomActivity("Hello World!"))


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


@client.event
async def on_message(message):
    if message.author == client.user:  # Ignore own messages
        return

    if message.content.startswith("$"):
        msgstr = message.content[1:]
        msgsplit = msgstr.split()
        msgcmd = msgsplit[0]
        msgargs = " ".join(msgsplit[1:])

        await cl.CommandRoot.run_cmd(msgcmd, msgargs, message, cl.CommandRoot.restrict)

    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")


client.run("")
