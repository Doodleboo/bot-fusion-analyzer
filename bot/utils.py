import json
import os
import re

from discord import Interaction, TextChannel, Guild, Client
from discord.message import Message
from discord.asset import Asset
from discord.user import User, ClientUser
from discord.member import Member
from discord.threads import Thread

from analysis import Analysis
from bot import setup

MAX_DEX_ID = 565
MISSING_DEX_ID = 420

PATTERN_ICON = r'[iI]con'
PATTERN_CUSTOM = r'[cC]ustom'
PATTERN_BASE = r'[bB]ase'
PATTERN_EGG = r'[eE]gg'
PATTERN_CUSTOM_BASE = r'[cC]ustom [bB]ase'

LETTER_AND_PNG_PATTERN = r'[a-z]{0,1}\.png$'

# 123.456
NUMBER_PATTERN_FUSION_ID = r'([1-9]\d{0,2})\.([1-9]\d{0,2})'
# 123
NUMBER_PATTERN_CUSTOM_ID = r'([1-9]\d{0,2})'

# (123.456a)
TEXT_PATTERN_FUSION_ID = r'\(([1-9]\d{0,2})\.([1-9]\d{0,2})[a-z]{0,1}\)'
# (123a)
TEXT_PATTERN_CUSTOM_ID = r'\(([1-9]\d{0,2})[a-z]{0,1}\)'

FILENAME_FUSION_ID = NUMBER_PATTERN_FUSION_ID + LETTER_AND_PNG_PATTERN
FILENAME_CUSTOM_ID = NUMBER_PATTERN_CUSTOM_ID + LETTER_AND_PNG_PATTERN

REGULAR_PATTERN_FUSION_ID = rf'^{FILENAME_FUSION_ID}'
SPOILER_PATTERN_FUSION_ID = rf'^SPOILER_{FILENAME_FUSION_ID}'

REGULAR_PATTERN_CUSTOM_ID = rf'^{FILENAME_CUSTOM_ID}'
SPOILER_PATTERN_CUSTOM_ID = rf'^SPOILER_{FILENAME_CUSTOM_ID}'

RAW_GITHUB = "https://raw.githubusercontent.com"
RAW_GITLAB = "https://gitlab.com"

AUTOGEN_FUSION_URL = f"{RAW_GITLAB}/pokemoninfinitefusion/autogen-fusion-sprites/-/raw/master/Battlers/"
QUESTION_URL = f"{RAW_GITHUB}/Doodleboo/bot-fusion-analyzer/main/bot/question.png"

LCB = "{"
RCB = "}"

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
NAMES_JSON_FILE = os.path.join(CURRENT_DIR, "..", "data", "PokemonNames.json")


def log_event(decorator: str, event: Message | Thread):
    if isinstance(event, Message):
        _log_message(decorator, event)


def _log_message(decorator: str, message: Message):
    channel_name = get_channel_name_from_message(message)
    print(f"{decorator} [{message.author.name}] {LCB}{channel_name}{RCB} {message.content}")


def get_channel_name_from_message(message: Message):
    try:
        channel_name = message.channel.name  # type: ignore
        if not isinstance(channel_name, str):
            channel_name = "INVALID"
    except SystemExit:
        raise
    except BaseException:
        channel_name = "INVALID"
    return channel_name


def log_command(decorator: str, interaction: Interaction, command: str):
    channel_name = get_channel_name_from_interaction(interaction)
    print(f"{decorator} [{interaction.user.name}] {LCB}{channel_name}{RCB} {command}")


def get_channel_name_from_interaction(interaction: Interaction):
    try:
        channel_name = interaction.channel.name  # type: ignore
        if not isinstance(channel_name, str):
            channel_name = "INVALID"
    except SystemExit:
        raise
    except BaseException:
        channel_name = "INVALID"
    return channel_name


def is_message_from_itself(message: Message):
    return message.author.id == setup.bot_id


def get_thread(message: Message) -> (Thread | None):
    thread = message.channel
    if isinstance(thread, Thread):
        return thread
    return None


def get_filename(analysis: Analysis):
    if analysis.specific_attachment is None:
        return analysis.message.attachments[0].filename
    return analysis.specific_attachment.filename


def get_attachment_url(analysis: Analysis):
    if analysis.type.is_zigzag_galpost():
        return get_attachment_url_from_embed(analysis)
    else:
        return get_attachment_url_from_message(analysis)


def get_attachment_url_from_message(analysis: Analysis):
    if analysis.specific_attachment is None:
        return analysis.message.attachments[0].url
    return analysis.specific_attachment.url


def get_attachment_url_from_embed(analysis: Analysis):
    if not analysis.message.embeds:
        return None
    embed = analysis.message.embeds[0]
    if embed.image is None:
        return None
    return embed.image.url


def interesting_results(results: list):
    return results[1] is not None


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


def have_attachment(analysis: Analysis):
    return len(analysis.message.attachments) >= 1


def have_zigzag_embed(analysis: Analysis) -> bool:
    if not analysis.type.is_zigzag_galpost():
        return False
    return analysis.embed is not None


def is_missing_autogen(fusion_id: str):
    split_fusion_id = fusion_id.split(".")
    head_id = int(split_fusion_id[0])
    body_id = int(split_fusion_id[1])
    return head_id > MISSING_DEX_ID or body_id > MISSING_DEX_ID


def get_autogen_url(fusion_id: str):
    # If it starts working again, it should adapt to work with custom bases
    if is_missing_autogen(fusion_id):
        return QUESTION_URL
    return AUTOGEN_FUSION_URL + fusion_id.split(".")[0] + "/" + fusion_id + ".png"


def is_invalid_fusion_id(fusion_id: str):
    head, body = fusion_id.split(".")
    head_id, body_id = int(head), int(body)
    return head_id > MAX_DEX_ID or body_id > MAX_DEX_ID


def is_invalid_base_id(base_id: str):
    pokemon_id = int(base_id)
    return pokemon_id > MAX_DEX_ID


def get_display_avatar(user: User | Member | ClientUser) -> Asset:
    return user.display_avatar.with_format("png").with_size(256)


def extract_fusion_id_from_filename(analysis: Analysis):
    fusion_id = None
    is_custom_base = False
    if have_attachment(analysis):
        filename = get_filename(analysis)
        fusion_id, is_custom_base = get_fusion_id_from_filename(filename)
    return fusion_id, is_custom_base


def get_fusion_id_from_filename(filename: str):
    result = re.match(REGULAR_PATTERN_FUSION_ID, filename)
    if result is not None:
        return get_clean_id_from_result(result[0], False), False

    result = re.match(SPOILER_PATTERN_FUSION_ID, filename)
    if result is not None:
        return get_clean_id_from_result(result[0], False), False

    result = re.match(REGULAR_PATTERN_CUSTOM_ID, filename)
    if result is not None:
        return get_clean_id_from_result(result[0], True), True

    result = re.match(SPOILER_PATTERN_CUSTOM_ID, filename)
    if result is not None:
        return get_clean_id_from_result(result[0], True), True
    else:
        return None, False


def extract_fusion_ids_from_content(message: Message, custom_base: bool = False):
    content = message.content
    id_list = []
    if custom_base:
        search_pattern = TEXT_PATTERN_CUSTOM_ID
    else:
        search_pattern = TEXT_PATTERN_FUSION_ID

    iterator = re.finditer(search_pattern, content)
    for result in iterator:
        clean_id = get_clean_id_from_result(result[0], custom_base)
        id_list.append(clean_id)

    return id_list


def get_clean_id_from_result(text: str, custom_base: bool = False):
    fusion_id = None
    if custom_base:
        search_pattern = NUMBER_PATTERN_CUSTOM_ID
    else:
        search_pattern = NUMBER_PATTERN_FUSION_ID
    result = re.search(search_pattern, text)
    if result:
        fusion_id = result[0]
    return fusion_id



def id_to_name_map():  # Thanks Greystorm for the util and file
    """Returns dictionary mapping id numbers to display names"""
    with open(NAMES_JSON_FILE) as f:
        data = json.loads(f.read())
        return {element["id"]: element["display_name"] for element in data["pokemon"]}



# Message and channel utilities


async def get_reply_message(message: Message):
    if message.reference is None:
        raise RuntimeError(message)

    reply_id = message.reference.message_id
    if reply_id is None:
        raise RuntimeError(message)

    return await message.channel.fetch_message(reply_id)



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

