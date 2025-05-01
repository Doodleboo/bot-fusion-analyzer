# Message identifying methods
import discord
from discord import Message, Thread

from bot import setup
from bot.bot_context import id_channel_gallery_pif, id_channel_assets_pif, id_channel_gallery_doodledoo, \
    id_spriter_apps_pif
from bot.setup import get_bot_id
from bot.utils import have_custom_base_in_message, get_reply_message

ZIGZAG_ID = 1185671488611819560 #1185671488611819560
YANMEGA_ID = 204255221017214977


def is_sprite_gallery(message: Message):
    return message.channel.id == id_channel_gallery_pif


def is_assets_custom_base(message: Message):
    return is_assets_gallery(message) and have_custom_base_in_message(message)


def is_assets_gallery(message: Message):
    return message.channel.id == id_channel_assets_pif


def is_test_gallery(message: Message):
    return message.channel.id == id_channel_gallery_doodledoo


def is_mentioning_reply(message: Message):
    return is_mentioning_bot(message) and is_reply(message)


def is_reply(message: Message):
    return message.reference is not None


def is_zigzag_galpost(message: Message):
    return is_zigzag_message(message) and (is_sprite_gallery(message) or is_assets_gallery(message))


def is_zigzag_message(message: Message):
    return message.author.id == ZIGZAG_ID


def is_message_from_ignored_bots(message: Message):
    bot_id = setup.get_bot_id()
    return message.author.id in [bot_id, YANMEGA_ID]


def is_mentioning_bot(message: Message):
    result = False
    fusion_bot_id = get_bot_id()
    for user in message.mentions:
        if fusion_bot_id == user.id:
            result = True
            break
    return result


def is_spriter_application(thread: Thread):
    if thread.parent.type != discord.ChannelType.forum:
        return False
    return thread.parent_id == id_spriter_apps_pif