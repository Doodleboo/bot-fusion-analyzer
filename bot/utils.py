import json
import os
import re

from discord import Interaction, TextChannel, Guild, Client
from discord.message import Message
from discord.asset import Asset
from discord.user import User, ClientUser
from discord.member import Member
from discord.threads import Thread

from bot.enums import IdType

MAX_DEX_ID = 565
AUTOGEN_MAX_ID = 501


LETTER_AND_PNG_PATTERN = r'[a-z]{0,1}\.png$'

# 123.456
NUMBER_PATTERN_FUSION_ID = r'([1-9]\d{0,2})\.([1-9]\d{0,2})'
# 123
NUMBER_PATTERN_CUSTOM_ID = r'([1-9]\d{0,2})'
# 123.456.789
NUMBER_PATTERN_TRIPLE_ID = r'([1-9]\d{0,2})\.([1-9]\d{0,2})\.([1-9]\d{0,2})'

# (123.456a)
TEXT_PATTERN_FUSION_ID = r'\(([1-9]\d{0,2})\.([1-9]\d{0,2})[a-z]{0,1}\)'
# (123a)
TEXT_PATTERN_CUSTOM_ID = r'\(([1-9]\d{0,2})[a-z]{0,1}\)'
# (123.456.789a)
TEXT_PATTERN_TRIPLE_ID = r'\(([1-9]\d{0,2})\.([1-9]\d{0,2})\.([1-9]\d{0,2})[a-z]{0,1}\)'

FILENAME_FUSION_ID = NUMBER_PATTERN_FUSION_ID + LETTER_AND_PNG_PATTERN
FILENAME_CUSTOM_ID = NUMBER_PATTERN_CUSTOM_ID + LETTER_AND_PNG_PATTERN
FILENAME_TRIPLE_ID = NUMBER_PATTERN_TRIPLE_ID + LETTER_AND_PNG_PATTERN

REGULAR_PATTERN_FUSION_ID = rf'^{FILENAME_FUSION_ID}'
SPOILER_PATTERN_FUSION_ID = rf'^SPOILER_{FILENAME_FUSION_ID}'

REGULAR_PATTERN_CUSTOM_ID = rf'^{FILENAME_CUSTOM_ID}'
SPOILER_PATTERN_CUSTOM_ID = rf'^SPOILER_{FILENAME_CUSTOM_ID}'

REGULAR_PATTERN_TRIPLE_ID = rf'^{FILENAME_TRIPLE_ID}'
SPOILER_PATTERN_TRIPLE_ID = rf'^SPOILER_{FILENAME_TRIPLE_ID}'

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
    split_lines = message.content.splitlines()
    if split_lines:
        first_line = split_lines[0]
    else:
        first_line = ""

    print(f"{decorator} [{message.author.name}] {LCB}{channel_name}{RCB} {first_line}")


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


def get_filename_from_image_url(url: str):
    url_parts = url.split(".png")  # Getting everything before the ? and url parameters
    url_parts = url_parts[0].split("/")  # Grabbing only the filename: 1.1_by_doodledoo
    dex_id = url_parts[-1].split("_")[0]  # Filtering the credit to keep only the dex id
    return dex_id + ".png"


def is_missing_autogen(fusion_id: str):
    split_fusion_id = fusion_id.split(".")
    head_id = int(split_fusion_id[0])
    body_id = int(split_fusion_id[1])
    return head_id > AUTOGEN_MAX_ID or body_id > AUTOGEN_MAX_ID


def is_invalid_fusion_id(fusion_id: str):
    fusion_id_list = fusion_id.split(".")
    for id in fusion_id_list:
        id_int = int(id)
        if id_int > MAX_DEX_ID:
            return True
    return False


def is_invalid_base_id(base_id: str):
    pokemon_id = int(base_id)
    return pokemon_id > MAX_DEX_ID


def get_display_avatar(user: User | Member | ClientUser) -> Asset:
    return user.display_avatar.with_format("png").with_size(256)


def get_fusion_id_from_filename(filename: str) -> (str, IdType):

    # Search for fusion pattern
    result = re.match(REGULAR_PATTERN_FUSION_ID, filename)
    if result is not None:
        return get_clean_id_from_result(result[0], IdType.fusion), IdType.fusion

    result = re.match(SPOILER_PATTERN_FUSION_ID, filename)
    if result is not None:
        return get_clean_id_from_result(result[0], IdType.fusion), IdType.fusion

    # Search for custom base or egg pattern
    result = re.match(REGULAR_PATTERN_CUSTOM_ID, filename)
    if result is not None:
        return get_clean_id_from_result(result[0], IdType.base_or_egg), IdType.base_or_egg

    result = re.match(SPOILER_PATTERN_CUSTOM_ID, filename)
    if result is not None:
        return get_clean_id_from_result(result[0], IdType.base_or_egg), IdType.base_or_egg

    # Search for triple fusion pattern
    result = re.match(REGULAR_PATTERN_TRIPLE_ID, filename)
    if result is not None:
        return get_clean_id_from_result(result[0], IdType.triple), IdType.triple

    result = re.match(SPOILER_PATTERN_TRIPLE_ID, filename)
    if result is not None:
        return get_clean_id_from_result(result[0], IdType.triple), IdType.triple
    else:
        return None, False


def extract_fusion_ids_from_content(message: Message, id_type: IdType):
    content = message.content
    id_list = []
    if id_type == IdType.base_or_egg:
        search_pattern = TEXT_PATTERN_CUSTOM_ID
    elif id_type == IdType.triple:
        search_pattern = TEXT_PATTERN_TRIPLE_ID
    else:
        search_pattern = TEXT_PATTERN_FUSION_ID

    iterator = re.finditer(search_pattern, content)
    for result in iterator:
        clean_id = get_clean_id_from_result(result[0], id_type)
        id_list.append(clean_id)

    return id_list


def get_clean_id_from_result(text: str, id_type: IdType):
    fusion_id = None
    if id_type == IdType.base_or_egg:
        search_pattern = NUMBER_PATTERN_CUSTOM_ID
    elif id_type == IdType.triple:
        search_pattern = NUMBER_PATTERN_TRIPLE_ID
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

