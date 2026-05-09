import re
import string
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from discord import Message

from bot.context.setup import ctx
from bot.core.analysis import Analysis
from bot.core.content_analysis import handle_dex_verification
from bot.core.filename_analysis import FusionFilename
from bot.core.issues import MissingMessageId, UnknownSprite, DifferentFilenameIds, IncorrectGallery, \
    FileName, OutOfDex, PokemonNameNotFound, MoreThanOneImage
from bot.gallery.emojis import check_for_custom_emoji
from bot.misc import utils
from bot.misc.exceptions import DifferentFusionsInSameGalleryMessage, MisnumberedGalleryID

NAME_MAP: dict[str, str] = utils.id_to_name_map()
TYPOS_MAP: dict[str, list[str]] = utils.id_to_typos_map()


async def main(analysis_list: list[Analysis]):
    """Does some checks from content_analysis with harsher restrictions and some entirely different checks"""
    if (not analysis_list) or (len(analysis_list) == 0):
        return
    check_for_multiple_images(analysis_list)
    try:
        same_id_checks(analysis_list)
    except DifferentFusionsInSameGalleryMessage:
        return
    if analysis_list[0].issues.has_issue(UnknownSprite):
        return
    correct_gallery = correct_gallery_checks(analysis_list)
    if not correct_gallery:
        return
    pokemon_name_checks(analysis_list)
    await filename_letter_checks(analysis_list)
    await check_for_custom_emoji(analysis_list[0])


def check_for_multiple_images(analysis_list: list[Analysis]):
    if len(analysis_list) == 1:
        return
    for analysis in analysis_list[1:]:
        analysis.add_issue(MoreThanOneImage())


def same_id_checks(analysis_list: list[Analysis]):
    """Ensures that all images in a single gallery message have the same fusion/base IDs"""
    first_analysis = analysis_list[0]
    first_filename = first_analysis.fusion_filename
    if first_filename.id_type.is_unknown():
        unknown_sprite(first_analysis)
        return
    if not correct_content_ids(first_analysis, first_filename):
        return
    for analysis in analysis_list:
        compare_with_first_filename(analysis, first_filename)


def correct_content_ids(first_analysis: Analysis, first_filename: FusionFilename) -> bool:
    content_ids = utils.extract_fusion_ids_from_content(first_analysis.message, first_filename.id_type)
    if not content_ids:
        return exact_content_id_found(first_analysis, first_filename.dex_ids)
    if first_filename.dex_ids not in content_ids:
        raise MisnumberedGalleryID(first_filename.dex_ids, content_ids[0])
    return True


def exact_content_id_found(analysis: Analysis, filename_id: str) -> bool:
    exact_content_id_result = re.search(filename_id, analysis.message.content)
    if exact_content_id_result is not None:
        return True
    analysis.add_issue(MissingMessageId())
    return False


def unknown_sprite(analysis: Analysis):
    analysis.add_issue(UnknownSprite())
    filename = analysis.get_filename()
    analysis.add_issue(FileName(filename))


def compare_with_first_filename(analysis: Analysis, first_filename: FusionFilename):
    if analysis.fusion_filename.id_type.is_unknown():
        unknown_sprite(analysis)
        return
    if analysis.fusion_filename.dex_ids != first_filename.dex_ids:
        analysis.add_issue(DifferentFilenameIds())
        raise DifferentFusionsInSameGalleryMessage


def correct_gallery_checks(analysis_list: list[Analysis]):
    """Ensures that the sprites have been sent to the correct gallery: either Sprite Gallery or Assets Gallery"""
    first_analysis = analysis_list[0]
    if first_analysis.type.is_sprite_gallery():
        return ensure_sprite_gallery_type(first_analysis)
    else:
        return ensure_assets_gallery_type(first_analysis)


def ensure_sprite_gallery_type(analysis: Analysis) -> bool:
    id_type = analysis.fusion_filename.id_type
    if id_type.is_fusion() or id_type.is_triple_fusion():
        return True
    analysis.add_issue(IncorrectGallery(id_type, "Sprite Gallery"))
    return False


def ensure_assets_gallery_type(analysis: Analysis) -> bool:
    id_type = analysis.fusion_filename.id_type
    if id_type.is_custom_base() or id_type.is_egg():
        return True
    analysis.add_issue(IncorrectGallery(id_type, "Assets Gallery"))
    return False


def pokemon_name_checks(analysis_list: list[Analysis]):
    """Ensures that the Pokémon in question are mentioned in the gallery message, to avoid misnumbered IDs"""
    for analysis in analysis_list:
        handle_dex_verification(analysis, analysis.fusion_filename.dex_ids)
    first_analysis = analysis_list[0]   # We only need to check the message for one analysis
    if first_analysis.issues.has_issue(OutOfDex):
        return
    ensure_pokemon_names_appear(first_analysis)


def ensure_pokemon_names_appear(analysis: Analysis):
    for pokemon_id in analysis.fusion_filename.ids_list():
        check_name_in_message(pokemon_id, analysis)


def check_name_in_message(pokemon_id: str, analysis: Analysis):
    message_content = analysis.message.content.lower()
    clean_name = NAME_MAP.get(pokemon_id)
    clean_name_result = re.search(clean_name.lower(), message_content)
    if clean_name_result is not None:
        return
    typos_found = check_typos_in_message(pokemon_id, message_content)
    if not typos_found:
        analysis.add_issue(PokemonNameNotFound(clean_name))


def check_typos_in_message(pokemon_id: str, message_content: str) -> bool:
    typos: list[str] = TYPOS_MAP.get(pokemon_id)
    for typo in typos:
        typo_result = re.search(typo.lower(), message_content)
        if typo_result is not None:
            return True
    return False


async def filename_letter_checks(analysis_list: list[Analysis]):
    """Ensures that in a given month, the same fusion by the same user follows a certain alt letter pattern"""
    past_instances = await search_in_same_month(analysis_list[0])
    if past_instances > 26:
        await ctx().doodledoo.debug.send(f"Too many gallery instances: ({analysis_list[0].message.jump_url})")
        return
    if len(analysis_list) == 1:
        await ensure_correct_letter(analysis_list[0], past_instances)
    else:
        await ensure_filled_letters(analysis_list, past_instances)


async def search_in_same_month(analysis: Analysis) -> int:
    if analysis.type.is_sprite_gallery():
        gallery_channel = ctx().pif.gallery
    else:
        gallery_channel = ctx().pif.assets

    match_count = 0
    async for message in gallery_channel.history(after=last_day_of_previous_month(), oldest_first=True):
        match_count += same_fusion_and_author_instances(message, analysis.message, analysis.fusion_filename.dex_ids)
    return match_count


def last_day_of_previous_month() -> datetime:
    # Gallery cutoff: Midnight EST when a new month starts
    est_tz = ZoneInfo("America/New_York")
    now = datetime.now(est_tz)
    first_day_of_current_month = datetime(now.year, now.month, 1, tzinfo=est_tz)
    return first_day_of_current_month - timedelta(days=1)


def same_fusion_and_author_instances(message: Message, og_message: Message, id_to_find: str) -> int:
    same_message_id = og_message.id
    author_id = og_message.author.id
    if message.author.id != author_id:
        return 0
    if message.id == same_message_id:
        return 0
    if utils.find_specific_fusion_id(message, id_to_find):
        return len(message.attachments)
    return 0


async def ensure_correct_letter(analysis: Analysis, past_instances: int):
    if analysis.fusion_filename.letter == "a":  # "A" isn't a problem if there is no letterless version
        return
    if past_instances == 0:
        correct_letter = ""
    elif past_instances > 26:
        await ctx().doodledoo.debug.send(f"Too many gallery instances: ({analysis.message.jump_url})")
        return
    else:
        correct_letter = string.ascii_lowercase[past_instances - 1]
    if correct_letter != analysis.fusion_filename.letter:
        await ctx().doodledoo.debug.send(f"Potentially wrong letter **{analysis.fusion_filename.letter}** shold be {correct_letter}: ({analysis.message.jump_url})")
        #analysis.add_issue(WrongLetter(correct_letter))


async def ensure_filled_letters(analysis_list: list[Analysis], past_instances: int):
    starting_letter_pos = past_instances
    final_letter_pos = past_instances + len(analysis_list)
    letter_range = get_letter_range(starting_letter_pos, final_letter_pos)
    new_range = await check_letters_are_in_range(analysis_list, letter_range)
    if len(new_range) > 0:
        await ctx().doodledoo.debug.send(f"Missing letters in {new_range} ({analysis_list[0].message.jump_url})")
        #analysis_list[0].add_issue(MissingLetters(new_range))


def get_letter_range(starting_letter_pos: int, final_letter_pos: int) -> list[str]:
    letter_range = []
    for letter_pos in range(starting_letter_pos, final_letter_pos):
        correct_letter = get_correct_letter(letter_pos)
        letter_range.append(correct_letter)
    return letter_range


async def check_letters_are_in_range(analysis_list: list[Analysis], letter_range: list[str]) -> list[str]:
    for analysis in analysis_list:
        letter = analysis.fusion_filename.letter
        if letter not in letter_range:
            await ctx().doodledoo.debug.send(f"{letter} not in: {letter_range} ({analysis_list[0].message.jump_url})")
            #analysis.add_issue(WrongLetter(f"one of these: {letter_range}"))
        else:
            letter_range.remove(letter)
    return letter_range


def get_correct_letter(current_instance: int) -> str:
    if current_instance == 0:
        return ""
    else:
        return string.ascii_lowercase[current_instance - 1]