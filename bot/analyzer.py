import analysis_content as analysis_content
import analysis_sprite as analysis_sprite
from analysis import Analysis, generate_file_from_image, get_autogen_file
from discord.message import Message, Attachment
from discord import User, TextChannel, Thread, DMChannel

from bot.opt_out_options import HideAutoAnalysis
from enums import AnalysisType, Severity

MAX_SEVERITY = [Severity.refused, Severity.controversial]


def generate_analysis(
        message: Message,
        specific_attachment: Attachment|None = None,
        analysis_type: AnalysisType|None = None):

    analysis = Analysis(message, specific_attachment, analysis_type)
    analysis_content.main(analysis)
    analysis_sprite.main(analysis)
    analysis.generate_embed()
    return analysis


# Methods to send messages in #fusion-bot

async def send_full_analysis(analysis: Analysis,
                             channel: TextChannel|Thread|DMChannel,
                             author: User):
    if (analysis.severity in MAX_SEVERITY) and analysis.type.is_gallery():
        await send_analysis(analysis, channel, author)
    else:
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
                        channel: TextChannel|Thread|DMChannel,
                        author: User|None = None):
    if author:
        ping_owner = author.mention
    else:
        ping_owner = None

    if analysis.type.is_automatic_spritework_analysis():
        buttons_view = HideAutoAnalysis(analysis.message.author)
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
