# External libs import
# execute command `pip install -r requirements.txt` to install all the dependencies
import asyncio

# utils import
from utils import create_new_member_welcome_card, check, update_json_file_from_dict

# constants import
from globals import *

from LogLevel import LogLevel

bot_strings = strings["discord_bot"]


def reload_strings():
    """
    Reloads the strings that could have been updated during the script execution.
    """
    global bot_strings
    bot_strings = strings["discord_bot"]


@bot.event
async def on_ready():
    """
    Updates the current status of the bot, when fully loaded by discord.
    """
    if STATUS.casefold() == "MAINT".casefold():
        await bot.change_presence(
            status=discord.Status.do_not_disturb,
            activity=discord.CustomActivity(
                name=bot_strings["on_ready"]["statuses"]["maintenance"]
            )
        )
    else:
        await bot.change_presence(
            activity=discord.CustomActivity(
                name=bot_strings["on_ready"]["statuses"]["online"]
            )
        )

    """
    print("Syncing commands to global tree...")
    bot.tree.copy_global_to(guild=discord.Object(id=DISCORD_GUILD_ID))
    await bot.tree.sync(guild=discord.Object(id=DISCORD_GUILD_ID))
    print("Synced commands to global tree")
    """

    print(f"{bot_strings['on_ready']['ready_message']} | {bot_strings['version']}")


@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    # Add the member role when rules are accepted
    if DISCORD_RULES_CHANNEL == payload.channel_id:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if str(payload.emoji) == "✅":
            role = discord.utils.get(guild.roles, name=DISCORD_MEMBER_ROLE)
            await member.add_roles(role)


@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    # Remove the member role if the rules are not accepted
    if DISCORD_RULES_CHANNEL == payload.channel_id:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if str(payload.emoji) == "✅":
            role = discord.utils.get(guild.roles, name=DISCORD_MEMBER_ROLE)
            await member.remove_roles(role)


@bot.event
async def on_message(message: discord.Message):
    # MiaouBot id
    if '<@1300938645108297779>' in message.content:
        await bot.get_channel(message.channel.id).send(bot_strings["on_message"]["automatic_bot_message"])


@bot.event
async def on_member_join(member: discord.Member):
    channel = bot.get_channel(DISCORD_WELCOME_CHANNEL)

    card = create_new_member_welcome_card(member)

    # map welcome message
    welcome_message = bot_strings["on_member_join"]["welcome_message"].replace("{member.mention}", member.mention).replace("{server.name}", bot.get_guild(DISCORD_GUILD_ID).name)

    # Sending welcome message
    await asyncio.sleep(delay=0)
    await channel.send(
        content=f"{welcome_message}",
        file=card
    )

    # free memory and disk space
    card.close()
    os.remove(f"{member.id}_card.html")
    os.remove("page.png")


@bot.hybrid_command(name="setup_welcome_background_image", description="Met à jour l'image de fond du message de bienvenue")
@commands.has_any_role("membre IUT", 1264408428931977223, 1264408428931977221)
async def setup_welcome_background_image(ctx: commands.Context, file: discord.Attachment):
    if os.path.isfile('./background.png'):
        os.remove('./background.png')

    await file.save('./background.png')
    await ctx.send(bot_strings["setup_welcome_background_image"]["action_success"])


@bot.hybrid_command(name="edit_welcome_message", description="Modifie le message de bienvenue")
@commands.has_any_role("membre IUT", 1264408428931977223, 1264408428931977221)
async def edit_welcome_message(ctx: commands.Context):
    await ctx.defer()
    card = create_new_member_welcome_card(ctx.author)
    bot_message = await ctx.send(
        bot_strings["edit_welcome_message"]["what_to_edit"],
        file=card,
        ephemeral=True
    )

    # free memory and disk space
    card.close()
    os.remove(f"{ctx.author.id}_card.html")
    os.remove("page.png")

    user_edit_choice = await bot.wait_for('message', check=check)

    while user_edit_choice.content.casefold() not in ['message'.casefold(), 'background'.casefold()]:
        await user_edit_choice.delete()
        await bot_message.edit(content=bot_strings["edit_welcome_message"]["wrong_user_input"], attachments=[])
        user_edit_choice = await bot.wait_for('message', check=check)

    await user_edit_choice.delete()

    if user_edit_choice.content.casefold() == "message".casefold():
        await bot_message.edit(content=bot_strings["edit_welcome_message"]["user_choice_message"], attachments=[])
        new_message = await bot.wait_for('message', check=check)
        new_message_content = new_message.content

        await new_message.delete()

        strings["discord_bot"]["on_member_join"]["welcome_message"] = new_message_content
        update_json_file_from_dict("./strings.json", strings)
        reload_strings()

    if user_edit_choice.content.casefold() == "background".casefold():
        await bot_message.edit(content=bot_strings["edit_welcome_message"]["user_choice_background"], attachments=[])
        new_background = await bot.wait_for('message', check=check)
        new_background_file = new_background.attachments[0]

        if os.path.isfile('./background.png'):
            os.remove('./background.png')

        await new_background_file.save('./background.png')
        await new_background.delete()

    await bot_message.edit(content=bot_strings["edit_welcome_message"]["action_success"])


@bot.hybrid_command(name="setup_rules", description="Crée les règles.")
@commands.has_any_role("testrole", "membre IUT", 1264408428931977223, 1264408428931977221)
async def setup_rules(ctx: commands.Context):
    embed = discord.Embed(
        title="**Règles du serveur**",
        color=discord.Color.from_rgb(245, 188, 243),
        description=bot_strings["rules"].replace("{server.name}", ctx.guild.name)
    )
    embed.set_thumbnail(url="https://i.imgur.com/40JzMOH.png")
    bot_rules_message = await ctx.channel.last_message.edit(embed=embed)
    await bot_rules_message.add_reaction("✅")

    await ctx.message.delete()


@bot.hybrid_command(name="simulate_member_join", description="Simule l'évent on_member_join")
@commands.has_any_role("membre IUT", 1264408428931977223, 1264408428931977221, 1264408428931977220)
async def simulate_member_join(ctx: commands.Context, member: discord.Member):
    await ctx.defer()
    await asyncio.sleep(1)
    await on_member_join(member)
    await ctx.interaction.followup.send(bot_strings["simulate_member_join"]["action_success"], ephemeral=True)


@bot.hybrid_command(name="setup_role_reaction", description="Rajoute, supprime ou modifie des roles reactions")
@commands.has_any_role("membre IUT", 1264408428931977223, 1264408428931977221, 1264408428931977220)
async def setup_role_reaction(ctx: commands.Context):
    await ctx.defer()
    raise Exception


@bot.hybrid_command(name="sync", description="Synchronise les commandes avec l'arbre courant.")
@commands.has_any_role("membre IUT", 1264408428931977223, 1264408428931977221, 1264408428931977220)
async def sync(ctx: commands.Context):
    bot.tree.copy_global_to(guild=discord.Object(id=DISCORD_GUILD_ID))
    await bot.tree.sync(guild=discord.Object(id=DISCORD_GUILD_ID))
    await ctx.send(bot_strings["sync"]["action_success"])


@bot.hybrid_command()
async def ping(ctx: commands.Context):
    await ctx.typing()
    await asyncio.sleep(1)
    await ctx.send(bot_strings["ping"]["message"])


@bot.event
async def on_command_error(ctx, error):
    logger.exception(f"Exception raised inside code. exception: {str(error)}")

    embed = discord.Embed(
        title=f"{bot_strings['on_command_error']['unknown_error']}"
    )
    embed.add_field(
        name=f"{bot_strings['on_command_error']['error']}",
        value=str(error)
    )
    embed.add_field(
        name=f"{bot_strings['on_command_error']['error_line']}",
        value=str(error.__traceback__.tb_lineno)
    )

    await send_discord_log(LogLevel.ERROR, custom_embed=embed)

    raise error


async def send_discord_log(level: LogLevel, title: str = None, content: str = None, custom_embed: discord.Embed = None):
    assert content is not None or custom_embed is not None, "Either content or custom_embed has to be NoneType."

    embed = None if custom_embed is None else custom_embed

    if custom_embed is None:
        embed = discord.Embed(
            title=title if title is not None else level.name,
            description=content,
            color=level.value[0]  # value is an instance of discord.Color => value : (<Colour>, )
        )

    channel = await bot.fetch_channel(DISCORD_LOG_CHANNEL_ID)
    await channel.send(embed=embed)


bot.run(DISCORD_BOT_TOKEN)
