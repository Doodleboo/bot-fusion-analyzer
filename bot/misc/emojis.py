from discord import Message, HTTPException

from bot.core.analysis import Analysis

ERROR_EMOJI = ":NANI:770390673664114689"
GOOD_EMOJIS = [":HeartMail:901794946967801896", ":ohyes:686653537911832661", "❤️", ":Venopog:1011728739073261638",
               ":allthethings:308453755672592384", ":oddlove:1095144043194892298", ":spheal_pog:1445961061378560040",
               ":slowdab:1054688142646583326", ":smilemeowth:763742948860887050", ":LETSTATICGO:1165798800653303869"]


async def react_with_emoji(analysis: Analysis, message: Message):
    custom_emoji = grab_custom_emoji(analysis)
    try:
        await message.add_reaction(custom_emoji)
    except HTTPException:
        fallback_emoji = grab_fallback_emoji(analysis)
        await message.add_reaction(fallback_emoji)


def grab_custom_emoji(analysis: Analysis) -> str:
    if analysis.severity.is_warn_severity():
        return f"<{ERROR_EMOJI}>"
    else:
        return "👍"   #TODO


def grab_fallback_emoji(analysis: Analysis) -> str:
    if analysis.severity.is_warn_severity():
        return "😡"
    else:
        return "👍"