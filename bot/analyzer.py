import analysis_content as analysis_content
import analysis_sprite as analysis_sprite
from analysis import Analysis, generate_file_from_image, get_autogen_file
from discord.message import Message, Attachment
from discord import User

from bot.setup import ctx
from enums import AnalysisType, Severity

MAX_SEVERITY = [Severity.refused, Severity.controversial]


def generate_analysis(
        message: Message,
        specific_attachment: Attachment|None = None,
        analysis_type: AnalysisType|None = None):
    # TODO: Use is_assets and is_reply to detect
    # custom bases in sprite gallery
    analysis = Analysis(message, specific_attachment, analysis_type)
    analysis_content.main(analysis)
    analysis_sprite.main(analysis)
    analysis.generate_embed()
    return analysis


# Methods to send messages in #fusion-bot

async def send_bot_logs(analysis: Analysis, author: User):
    if analysis.severity in MAX_SEVERITY:
        await send_analysis_in_fusion_bot(analysis, author)
    else:
        await send_analysis_in_fusion_bot(analysis)
    await send_bonus_content(analysis)


async def send_bonus_content(analysis: Analysis):
    if analysis.transparency_issue:
        await ctx().pif.logs.send(
            embed=analysis.transparency_embed,
            file=generate_file_from_image(analysis.transparency_image)
        )
    if analysis.half_pixels_issue:
        await ctx().pif.logs.send(
            embed=analysis.half_pixels_embed,
            file=generate_file_from_image(analysis.half_pixels_image)
        )


async def send_analysis_in_fusion_bot(analysis: Analysis, author: User | None = None):
    if author:
        ping_owner = author.mention
    else:
        ping_owner = None

    if analysis.autogen_available:
        autogen_file = get_autogen_file(analysis.fusion_id)
        if autogen_file:
            await ctx().pif.logs.send(embed=analysis.embed, content=ping_owner, file=autogen_file)
            return

    await ctx().pif.logs.send(embed=analysis.embed, content=ping_owner)
