import discord
import requests
from PIL import UnidentifiedImageError
from colormath.color_objects import sRGBColor
from discord.embeds import Embed

import analysis_sprite

from PIL.Image import open as image_open

HELP_RESPONSE = ("Do you need help using the Fusion Bot to analyze sprites?\n"
            "You can use it by **mentioning the bot** (using @) **while replying to a sprite**!\n"
            "You can contact Doodledoo if you need help with anything related to the fusion bot. "
            "Let me know if you've got suggestions or ideas too!")
ERROR_RESPONSE = "**An error has occurred processing your command:**"
ERROR_ADDENUM = ("\n\nIf you believe this is incorrect, notify the error either to Doodledoo or here:\n"
                 "https://github.com/Doodleboo/bot-fusion-analyzer/issues")
NO_ATTACHMENT = "No suitable attachment was found."
WRONG_ATTACHMENT = "Couldn't parse the attachment as an image."
NO_COLOR_DICT = "Couldn't extract the list of colors from this image."
TIMEOUT = 10
ALL_COLOR_LIMIT = 256


async def help_action(interaction: discord.Interaction):
    await interaction.response.send_message(HELP_RESPONSE)


async def similar_action(interaction: discord.Interaction, attachment: discord.Attachment):
    if attachment is None:
        await error_embed(interaction, NO_ATTACHMENT)
        return

    raw_data = requests.get(attachment.url, stream = True, timeout = TIMEOUT).raw
    try:
        image = image_open(raw_data)
    except UnidentifiedImageError:
        await error_embed(interaction, WRONG_ATTACHMENT)
        return

    sorted_color_dict = get_sorted_color_dict(image)

    if not sorted_color_dict:
        await error_embed(interaction, NO_COLOR_DICT)
        return

    pair_list = []
    for color_pair in sorted_color_dict:
        rgb_pair = get_rgb_pair(color_pair)
        pair_list.append(rgb_pair)

    formatted_list = format_list(pair_list)
    similar_embed  = Embed(description = formatted_list)

    await interaction.response.send_message(embed = similar_embed)




def get_sorted_color_dict(image) -> frozenset[frozenset[tuple]]:
    sorted_color_dict = None
    try:
        if "P" == image.mode:  # Indexed mode
            useful_indexed_palette = analysis_sprite.get_useful_indexed_palette(image)
            rgb_color_list = analysis_sprite.get_indexed_to_rgb_color_list(useful_indexed_palette)
        else:
            all_colors = image.getcolors(ALL_COLOR_LIMIT)
            if not all_colors:  # Color count higher than 256
                raise ValueError
            useful_colors = analysis_sprite.remove_useless_colors(all_colors)
            rgb_color_list = analysis_sprite.get_rgb_color_list(useful_colors)

        similar_color_dict = analysis_sprite.get_similar_color_dict(rgb_color_list)
        sorted_color_dict = analysis_sprite.sort_color_dict(similar_color_dict)
    except ValueError:
        pass
    return sorted_color_dict

def get_rgb_pair(color_pair: frozenset[tuple]) -> tuple[str, str]:
    pair_list = list(color_pair)
    first_tuple = pair_list[0]
    second_tuple = pair_list[1]
    first_color = sRGBColor(first_tuple[0], first_tuple[1], first_tuple[2], True)
    second_color = sRGBColor(second_tuple[0], second_tuple[1], second_tuple[2], True)
    return first_color.get_rgb_hex(), second_color.get_rgb_hex()

def format_list(pair_list: [[str, str]]):
    formatted_list = "**Rank of most similar pairs:**\n"
    for pair in pair_list:
        temp_str = "- **" + pair[0] + "** and **" + pair[1] + "**\n"
        formatted_list = formatted_list + temp_str
    return  formatted_list

async def error_embed(interaction: discord.Interaction, message: str):
    error_description =  message + ERROR_ADDENUM
    new_error_embed = Embed(title = ERROR_RESPONSE, description = error_description)
    await interaction.response.send_message(embed = new_error_embed)