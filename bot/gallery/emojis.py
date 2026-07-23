import random

from discord import Message, HTTPException

from bot.context.setup import ctx
from bot.core.analysis import Analysis

ERROR_EMOJI = ":NANI:770390673664114689"
ERROR_FALLBACK_EMOJI = "😡"
GOOD_EMOJIS = [":HeartMail:901794946967801896", ":ohyes:686653537911832661", "❤️", ":Venopog:1011728739073261638",
               ":allthethings:308453755672592384", ":oddlove:1095144043194892298", ":spheal_pog:1445961061378560040",
               ":slowdab:1054688142646583326", ":smilemeowth:763742948860887050", ":LETSTATICGO:1165798800653303869"]
SPECIAL_EMOJIS = {
    43: ":oddlove:1095144043194892298",
    50: ":gigachadiglett:1087067482096926820",
    52: ":smilemeowth:763742948860887050",
    53: ":malicious:940987474761613323",
    54: ":pogduck:902560462737125449",
    70: ":allthethings:308453755672592384",
    79: ":slowdab:1054688142646583326",
    109: ":heehee:945800365457149992",
    116: ":NootNoot:994282680600498267",
    132: ":ditto:415314839456579585",
    137: ":PorySpin:1488702100035866694",
    181: ":Smirkball:1084226737430347877",
    184: ":george:702893280769081364",
    189: ":yes:807751771246034984",
    195: ":Quagless:1277334887178702959",
    198: ":welcome:958550882394447882",
    213: ":Fancy:1184389686635003994",
    215: ":SmugCatSneasel:1277335087863562371",
    252: ":AzuGasp:1277338067170230335",
    348: ":Genesus:871309710895218688",
    355: ":happo:1058708428425535559",
    365: "🕯️",
    369: ":Nice:1277341236847448114",
    371: "🔑",
    410: ":dealwithit:1012739798924001360",
    463: ":kekruff:1303505414842748979",
    489: "🎃",
    544: "🌙",
    545: "🌞",
    556: "🍌",
    559: ":spheal_pog:1445961061378560040",
    574: "🐌",
    576: "🐌"
}
RAREST_EMOJI = ":payatest:1315843862555660328"


async def replace_emoji(analysis_list: list[Analysis], message: Message):
    if retried_analysis_has_errors(analysis_list):
        return
    await remove_error_emoji(message)
    await react_with_emoji(analysis_list, message)


def retried_analysis_has_errors(analysis_list: list[Analysis]) -> bool:
    for analysis in analysis_list:
        if analysis.severity.is_warn_severity():
            return True
    return False


async def remove_error_emoji(message: Message):
    for reaction in message.reactions:
        if reaction.emoji == ERROR_EMOJI:
            await message.clear_reaction(ERROR_EMOJI)
            return
        if reaction.emoji == ERROR_FALLBACK_EMOJI:
            await message.clear_reaction(ERROR_FALLBACK_EMOJI)
            return


async def react_with_emoji(analysis_list: list[Analysis], message: Message):
    if not analysis_list:
        return
    custom_emoji = grab_custom_emoji(analysis_list)
    try:
        await message.add_reaction(custom_emoji)

    except HTTPException:
        fallback_emoji = grab_fallback_emoji(analysis_list)
        await message.add_reaction(fallback_emoji)


async def check_for_custom_emoji(analysis: Analysis):
    for pokemon_id in analysis.fusion_filename.ids_list():
        try:
            pokemon_id_number = int(pokemon_id)
        except ValueError:
            await ctx().doodledoo.debug.send(f"EMOJI ERROR: Could not cast '{pokemon_id}' into a number")
            return
        if SPECIAL_EMOJIS.get(pokemon_id_number) is not None:
            analysis.special_gallery_emoji = pokemon_id_number


def grab_custom_emoji(analysis_list: list[Analysis]) -> str:
    for analysis in analysis_list:
        if analysis.severity.is_warn_severity():
            return f"<{ERROR_EMOJI}>"

    first_analysis = analysis_list[0]
    if random.randint(0, 100) == 100:
        return f"<{RAREST_EMOJI}>"

    if first_analysis.special_gallery_emoji > 0:
        return SPECIAL_EMOJIS.get(first_analysis.special_gallery_emoji)

    return random.choice(GOOD_EMOJIS)


def grab_fallback_emoji(analysis_list: list[Analysis]) -> str:
    for analysis in analysis_list:
        if analysis.severity.is_warn_severity():
            return ERROR_FALLBACK_EMOJI
    return "❤️"