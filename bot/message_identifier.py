import re
import discord
from discord import Message, Thread

from bot import setup
from bot.bot_context import (id_channel_gallery_pif, id_channel_assets_pif,
                             id_channel_gallery_doodledoo, id_spriter_apps_pif, id_spritework)
from bot.setup import get_bot_id

ZIGZAG_ID = 1185671488611819560 #1185671488611819560
YANMEGA_ID = 204255221017214977

PATTERN_ICON = r'[iI]con'
PATTERN_CUSTOM = r'[cC]ustom'
PATTERN_BASE = r'[bB]ase'
PATTERN_EGG = r'[eE]gg'
PATTERN_TRIPLE = r'[tT]riple'
PATTERN_CUSTOM_BASE = r'[cC]ustom [bB]ase'


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


def is_spritework_post(thread: Thread):
    if thread.parent.type != discord.ChannelType.forum:
        return False
    return thread.parent_id == id_spritework


def have_icon_in_message(message: Message):
    result = re.search(PATTERN_ICON, message.content)
    return result is not None


def have_custom_base_in_message(message: Message):
    result = re.search(PATTERN_CUSTOM_BASE, message.content)
    return result is not None


def have_custom_in_message(message: Message):
    result = re.search(PATTERN_CUSTOM, message.content)
    return result is not None


def have_base_in_message(message: Message):
    result = re.search(PATTERN_BASE, message.content)
    return result is not None


def have_egg_in_message(message: Message):
    result = re.search(PATTERN_EGG, message.content)
    return result is not None

def have_triple_in_message(message: Message):
    result = re.search(PATTERN_TRIPLE, message.content)
    return result is not None
