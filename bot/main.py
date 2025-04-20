# coding: utf-8

import os

import discord
import utils
import command_actions
import random
from analysis import generate_bonus_file
from analyzer import Analysis, generate_analysis
from discord import Client, PartialEmoji, app_commands, HTTPException
from discord.channel import TextChannel
from discord.guild import Guild
from discord.message import Message
from discord.user import User
from enums import DiscordColour, Severity
from exceptions import MissingBotContext
from models import GlobalContext, ServerContext

ERROR_EMOJI_NAME = "NANI"
ERROR_EMOJI_ID = f"<:{ERROR_EMOJI_NAME}:770390673664114689>"
ERROR_EMOJI = PartialEmoji(name=ERROR_EMOJI_NAME).from_str(ERROR_EMOJI_ID)
MAX_SEVERITY = [Severity.refused, Severity.controversial]
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
OLD_FUSION_BOT_ID = 836686828215992430

intents = discord.Intents.default()
intents.guild_messages = True
intents.members = True
intents.message_content = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

bot_id = None
bot_avatar_url = None
bot_context = None

ping_doodledoo = "<@!171301358186659841>"
worksheet_name = "Full dex"

# Doodledoo test server
id_server_doodledoo = 446241769462562827
id_channel_gallery_doodledoo = 1360964111718158498
id_channel_assets_doodledoo = 1363610399064330480
id_channel_logs_doodledoo = 1360969318296322328  # Here, debug and logs share a channel

# Pokémon Infinite Fusion
id_server_pif = 446241769462562827 #302153478556352513
id_channel_gallery_pif = 1360964111718158498 #543958354377179176
id_channel_assets_pif = 1363610399064330480 #1094790320891371640
id_channel_logs_pif = 1360969318296322328 #999653562202214450
id_channel_debug_pif = 1360969318296322328 #703351286019653762


def get_channel_from_id(server: Guild, channel_id) -> TextChannel:
    channel = server.get_channel(channel_id)
    if channel is None:
        raise KeyError(channel_id)
    if not isinstance(channel, TextChannel):
        raise TypeError(channel)
    return channel


def get_server_from_id(client: Client, server_id) -> Guild:
    server = client.get_guild(server_id)
    if server is None:
        raise KeyError(server_id)
    return server


class BotContext:
    def __init__(self, client: Client):
        server_doodledoo = get_server_from_id(client, id_server_doodledoo)
        channel_gallery_doodledoo = get_channel_from_id(server_doodledoo, id_channel_gallery_doodledoo)
        channel_log_doodledoo = get_channel_from_id(server_doodledoo, id_channel_logs_doodledoo)

        doodledoo_context = ServerContext(
            server=server_doodledoo,
            gallery=channel_gallery_doodledoo,
            logs=channel_log_doodledoo,
            debug=channel_log_doodledoo
        )

        server_pif = get_server_from_id(client, id_server_pif)
        channel_gallery_pif = get_channel_from_id(server_pif, id_channel_gallery_pif)
        channel_log_pif = get_channel_from_id(server_pif, id_channel_logs_pif)
        channel_debug_pif = get_channel_from_id(server_pif, id_channel_debug_pif)

        pif_context = ServerContext(
            server=server_pif,
            gallery=channel_gallery_pif,
            logs=channel_log_pif,
            debug=channel_debug_pif
        )

        self.context = GlobalContext(
            doodledoo=doodledoo_context,
            pif=pif_context
        )


def ctx() -> GlobalContext:
    if bot_context is not None:
        return bot_context.context
    else:
        raise MissingBotContext


async def send_bot_logs(analysis: Analysis, author_id: int):
    if analysis.severity in MAX_SEVERITY:
        await send_with_content(analysis, author_id)
    else:
        await send_without_content(analysis)
    await send_bonus_content(analysis)


async def send_bonus_content(analysis: Analysis):
    if analysis.transparency_issue:
        await ctx().pif.logs.send(
            embed=analysis.transparency_embed,
            file=generate_bonus_file(analysis.transparency_image)
        )
    if analysis.half_pixels_issue:
        await ctx().pif.logs.send(
            embed=analysis.half_pixels_embed,
            file=generate_bonus_file(analysis.half_pixels_image)
        )


async def send_with_content(analysis: Analysis, author_id: int):
    ping_owner = f"<@!{author_id}>"
    await ctx().pif.logs.send(embed=analysis.embed, content=ping_owner)


async def send_without_content(analysis: Analysis):
    await ctx().pif.logs.send(embed=analysis.embed)


async def handle_sprite_gallery(message: Message):
    await handle_gallery(message, is_assets=False)


async def handle_assets_gallery(message: Message):
    await handle_gallery(message, is_assets=True)


async def handle_gallery(message: Message, is_assets: bool = False):
    if is_assets:
        utils.log_event("AG>", message)
    else:
        utils.log_event("SG>", message)

    for specific_attachment in message.attachments:
        analysis = generate_analysis(message, specific_attachment, is_reply=False, is_assets=is_assets)
        if analysis.severity in MAX_SEVERITY:
            try:
                await message.add_reaction(ERROR_EMOJI)
            except HTTPException:
                await message.add_reaction("😡")  # Nani failsafe
        await send_bot_logs(analysis, message.author.id)


async def handle_reply_message(message: Message, old_bot: bool = False):
    if not old_bot:
        utils.log_event("R>", message)
        channel = message.channel
    else:
        utils.log_event("OLD_R>", message)
        channel = message.channel
    for specific_attachment in message.attachments:
        analysis = generate_analysis(message, specific_attachment, True)
        try:
            await channel.send(embed=analysis.embed)
            if analysis.transparency_issue:
                await channel.send(
                    embed=analysis.transparency_embed,
                    file=generate_bonus_file(analysis.transparency_image)
                )
            if analysis.half_pixels_issue:
                await channel.send(
                    embed=analysis.half_pixels_embed,
                    file=generate_bonus_file(analysis.half_pixels_image)
                )
        except discord.Forbidden:
            if not old_bot:
                print(f"R> Missing permissions in {channel}")
            else:
                print(f"OLD_R> Missing permissions in {channel}")


@tree.command(name="help", description="Fusion bot help")
async def help_command(interaction: discord.Interaction):
    utils.log_command("C>", interaction, "/help")
    await command_actions.help_action(interaction)


@tree.command(name="similar", description="Get the list of similar colors")
async def similar_command(interaction: discord.Interaction, sprite: discord.Attachment):
    utils.log_command("C>", interaction, "/similar")
    await command_actions.similar_action(interaction, sprite)


@bot.event
async def on_ready():
    await tree.sync()

    global bot_id
    app_info = await bot.application_info()
    bot_id = app_info.id
    permission_id = "17179929600"

    global bot_avatar_url

    bot_user = bot.user
    if bot_user is not None:
        bot_avatar_url = utils.get_display_avatar(bot_user).url

    global bot_context
    bot_context = BotContext(bot)

    invite_parameters = f"client_id={str(bot_id)}&permissions={permission_id}&scope=bot"
    invite_link = f"https://discordapp.com/api/oauth2/authorize?{invite_parameters}"
    print(f"\n\nReady! bot invite:\n\n{invite_link}\n\n")

    await ctx().doodledoo.logs.send(content="Bot online")


@bot.event
async def on_message(message: Message):
    try:
        if not utils.is_message_from_human(message, bot_id):
            return

        if is_sprite_gallery(message):
            await handle_sprite_gallery(message)
        elif is_assets_custom_base(message):
            await handle_assets_gallery(message)
        elif is_mentioning_reply(message):
            await handle_reply(message, old_bot=False)
        elif is_mentioning_old_bot(message) and is_reply(message):
            await handle_reply(message, old_bot=True)

    except Exception as message_exception:
        print(" ")
        print(message)
        print(" ")
        ping_author = f"<@!{message.author.id}>"
        error_message = "An error occurred while processing your message from"
        await ctx().doodledoo.debug.send(
            f"{ping_doodledoo}/{ping_author} : {error_message} #{message.channel} ({message.jump_url})")  # type: ignore
        raise RuntimeError from message_exception


def is_sprite_gallery(message: Message):
    return message.channel.id == id_channel_gallery_pif


def is_assets_custom_base(message: Message):
    return is_assets_gallery(message) and utils.have_custom_base_in_message(message)


def is_assets_gallery(message: Message):
    return message.channel.id == id_channel_assets_pif


def is_test_gallery(message: Message):
    return message.channel.id == id_channel_gallery_doodledoo


def is_mentioning_reply(message: Message):
    return is_mentioning_bot(message) and is_reply(message)


def is_reply(message: Message):
    return message.reference is not None


def is_mentioning_bot(message: Message):
    result = False
    for user in message.mentions:
        if bot_id == user.id:
            result = True
            break
    return result


def is_mentioning_old_bot(message: Message):
    result = False
    for user in message.mentions:
        if OLD_FUSION_BOT_ID == user.id:
            result = True
            break
    return result


async def handle_reply(message: Message, old_bot: bool):
    reply_message = await get_reply_message(message)
    await handle_reply_message(reply_message, old_bot)


async def get_reply_message(message: Message):
    if message.reference is None:
        raise RuntimeError(message)

    reply_id = message.reference.message_id
    if reply_id is None:
        raise RuntimeError(message)

    return await message.channel.fetch_message(reply_id)


def get_user(user_id) -> (User | None):
    return bot.get_user(user_id)


def get_discord_token():
    token_dir = os.path.join(CURRENT_DIR, "..", "token", "discord.txt")
    token = open(token_dir).read().rstrip()
    return token


if __name__ == "__main__":
    discord_token = get_discord_token()
    bot.run(discord_token)

