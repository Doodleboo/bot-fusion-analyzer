from discord import TextChannel, Thread, DMChannel
from discord.message import Message, Attachment

from bot.misc.enums import AnalysisType, OptedType
from bot.spritework.opt_out_options import HideFeature
from . import content_analysis, sprite_analysis
from .analysis import Analysis, generate_file_from_image, get_autogen_file
from .issues import RetriedAnalysis
from ..gallery import gallery_analysis
from ..misc.utils import attachment_not_an_image


def generate_analysis(
        message: Message,
        specific_attachment: Attachment|None = None,
        analysis_type: AnalysisType|None = None,
        reply_text: str|None = None) -> Analysis:

    analysis = Analysis(message, specific_attachment, analysis_type, reply_text)
    content_analysis.main(analysis)
    sprite_analysis.main(analysis)
    analysis.generate_embed()
    return analysis


async def generate_gallery_analysis_list(
        message: Message,
        analysis_type: AnalysisType|None = None,
        retried_analysis: bool = False) -> list[Analysis]:

    if message.attachments is None:
        return no_attachment_analysis(message, analysis_type)

    analysis_list = []
    for attachment in message.attachments:
        if attachment_not_an_image(attachment):
            continue
        analysis = Analysis(message, attachment, analysis_type)
        if retried_analysis:
            analysis.is_retried_analysis = True
            analysis.add_issue(RetriedAnalysis())
        analysis_list.append(analysis)

    await gallery_analysis.main(analysis_list)

    for analysis in analysis_list:
        if analysis.severity.is_warn_severity():
            analysis.can_be_retried = True  # It can be retried if it has content/message issues
        sprite_analysis.main(analysis)
        analysis.generate_embed()

    return analysis_list


def no_attachment_analysis(
        message: Message,
        analysis_type: AnalysisType|None = None)  -> list[Analysis]:
    analysis = Analysis(message, None, analysis_type)
    content_analysis.handle_no_content(analysis)
    return [analysis]


# Methods to send messages in #fusion-bot

async def send_full_analysis(analysis: Analysis,
                             channel: TextChannel|Thread|DMChannel):
    await send_analysis(analysis, channel)
    await send_extra_embeds(analysis, channel)


async def send_extra_embeds(analysis: Analysis,
                            channel: TextChannel|Thread|DMChannel):
    if analysis.transparency_issue:
        await channel.send(
            embed=analysis.transparency_embed,
            file=generate_file_from_image(analysis.transparency_image)
        )
    if analysis.half_pixels_issue:
        await channel.send(
            embed=analysis.half_pixels_embed,
            file=generate_file_from_image(analysis.half_pixels_image)
        )


async def send_analysis(analysis: Analysis,
                        channel: TextChannel|Thread|DMChannel):
    if analysis.severity.is_warn_severity() and analysis.type.is_gallery():
        ping_owner = analysis.message.author.mention
    else:
        ping_owner = None

    if analysis.type.is_automatic_spritework_analysis():
        buttons_view = HideFeature(analysis.message.author, OptedType.auto_analysis)
    elif analysis.type.is_gallery() and analysis.can_be_retried:
        buttons_view = analysis.view
    else:
        buttons_view = None

    if analysis.autogen_available:
        autogen_file = get_autogen_file(analysis.fusion_id)
    else:
        autogen_file = None

    if autogen_file:
        sent_message = await channel.send(embed=analysis.embed, content=ping_owner, file=autogen_file, view=buttons_view)
    else:
        sent_message = await channel.send(embed=analysis.embed, content=ping_owner, view=buttons_view)

    if buttons_view:
        buttons_view.message = sent_message
